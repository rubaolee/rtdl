#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


GROUP_WIDTH = 8

TEACHING_CONTEXT = {
    "concept_tutorials": [
        "examples/tutorial_programs/bounded_witness_collection.py",
        "examples/tutorial_programs/contact_manifold_lowering.py",
    ],
    "manual_data_flow": [
        "User supplies ray, triangle, group, value, and candidate-index columns on the Torch CUDA device.",
        "RTDL keeps the closest accepted hit per group.",
        "The continuation emits group_has_value and group_index columns.",
    ],
    "input_columns": {
        "triangle_columns": "triangle ids and 3D vertices",
        "ray_columns": "ray id, origin, direction, and tmax columns",
        "per_ray_group_ids": "uint32 group id per ray",
        "candidate_values": "float64 value used for argmin",
        "candidate_indices": "uint32 witness id to keep for the winning value",
    },
    "relation_output": "accepted hit rows with group id, candidate value, and witness id",
    "continuation": "per-group argmin witness",
    "benchmark_bridge": "contact and bounded-witness collection stages",
}


def make_torch_fixture(torch, ray_count: int) -> dict[str, object]:
    if ray_count <= 0:
        raise ValueError("ray_count must be positive")
    if ray_count % GROUP_WIDTH != 0:
        raise ValueError(f"ray_count must be divisible by {GROUP_WIDTH}")
    device = torch.device("cuda:0")
    ids_i64 = torch.arange(ray_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    centers = ids_i64.to(torch.float64) * 2.0
    zero = torch.zeros((ray_count,), dtype=torch.float64, device=device)
    one = torch.ones((ray_count,), dtype=torch.float64, device=device)
    half = torch.full((ray_count,), 0.45, dtype=torch.float64, device=device)
    local = ids_i64 % GROUP_WIDTH
    group_count = ray_count // GROUP_WIDTH

    return {
        "triangle_columns": {
            "ids": ids,
            "x0": (centers - half).contiguous(),
            "y0": (-half).contiguous(),
            "z0": zero.contiguous(),
            "x1": (centers + half).contiguous(),
            "y1": (-half).contiguous(),
            "z1": zero.contiguous(),
            "x2": centers.contiguous(),
            "y2": half.contiguous(),
            "z2": zero.contiguous(),
        },
        "ray_columns": {
            "ids": ids,
            "ox": centers.contiguous(),
            "oy": zero.contiguous(),
            "oz": one.contiguous(),
            "dx": zero.contiguous(),
            "dy": zero.contiguous(),
            "dz": (-one).contiguous(),
            "tmax": torch.full((ray_count,), 2.0, dtype=torch.float64, device=device),
        },
        "per_ray_group_ids": (ids_i64 // GROUP_WIDTH).to(torch.uint32).contiguous(),
        "candidate_values": (GROUP_WIDTH - local).to(torch.float64).contiguous(),
        "candidate_indices": (ids_i64 + 1000000).to(torch.uint32).contiguous(),
        "group_count": group_count,
        "expected_group_index": (
            torch.arange(group_count, dtype=torch.int64, device=device) * GROUP_WIDTH
            + GROUP_WIDTH
            - 1
            + 1000000
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V4 closest-hit grouped-argmin Torch device-array example.")
    parser.add_argument("--ray-count", type=int, default=8192)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan: dict[str, Any] = {
        "example": "v4_closest_hit_grouped_argmin_torch_device_arrays",
        "ray_count": int(args.ray_count),
        "triangle_count": int(args.ray_count),
        "group_width": GROUP_WIDTH,
        "group_count": int(args.ray_count) // GROUP_WIDTH,
        "input_contract": "caller_supplied_torch_device_triangle_ray_and_group_columns",
        "output_contract": "caller_owned_torch_device_grouped_argmin_columns",
        "teaching_context": TEACHING_CONTEXT,
        "release_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
    }
    if args.dry_run:
        payload = {"status": "dry_run", **plan}
    else:
        import torch
        import rtdsl.v4_ray_triangle as rt_v4

        fixture = make_torch_fixture(torch, int(args.ray_count))
        torch.cuda.synchronize()
        with rt_v4.prepare_closest_hit_grouped_argmin_3d_device_arrays_v4(
            fixture["triangle_columns"],
            fixture["ray_columns"],
            per_ray_group_ids=fixture["per_ray_group_ids"],
            candidate_values=fixture["candidate_values"],
            candidate_indices=fixture["candidate_indices"],
            group_count=fixture["group_count"],
            partner="torch",
        ) as session:
            output_columns = session.allocate_outputs()
            session.run(output_columns=output_columns, return_metadata=True)
            torch.cuda.synchronize()
            start = time.perf_counter()
            result = session.run(output_columns=output_columns, return_metadata=True)
            torch.cuda.synchronize()
            elapsed_s = time.perf_counter() - start

        index_match = bool(torch.equal(output_columns["group_index"].to(torch.int64), fixture["expected_group_index"]))
        has_value_count = int(torch.sum(output_columns["group_has_value"]).detach().cpu().item())
        payload = {
            "status": "measured",
            **plan,
            "elapsed_s": elapsed_s,
            "has_value_count": has_value_count,
            "correctness_passed": index_match and has_value_count == fixture["group_count"],
            "metadata": result["metadata"],
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"dry_run", "measured"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
