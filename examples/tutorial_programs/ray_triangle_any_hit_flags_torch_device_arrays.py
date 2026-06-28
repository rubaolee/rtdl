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

TEACHING_CONTEXT = {
    "concept_tutorial": "examples/tutorial_programs/ray_triangle_hits.py",
    "manual_data_flow": [
        "User supplies triangle AABBs and ray columns on the Torch CUDA device.",
        "RTDL traverses ray candidates against triangle bounds.",
        "The continuation writes one any-hit flag per ray.",
    ],
    "input_columns": {
        "triangle_columns": "triangle ids and 2D vertices",
        "triangle_aabbs": "float32 bounds used by traversal",
        "ray_columns": "ray id, origin, direction, and tmax columns",
    },
    "relation_output": "ray/triangle candidate hit rows",
    "continuation": "per-ray any-hit flag",
    "benchmark_bridge": "collision, visibility, and triangle-query decision stages",
}


def make_torch_fixture(torch, ray_count: int) -> dict[str, object]:
    if ray_count <= 0:
        raise ValueError("ray_count must be positive")
    device = torch.device("cuda:0")
    ids_i64 = torch.arange(ray_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    centers = ids_i64.to(torch.float64) * 2.0
    zero = torch.zeros((ray_count,), dtype=torch.float64, device=device)
    one = torch.ones((ray_count,), dtype=torch.float64, device=device)
    half = torch.full((ray_count,), 0.45, dtype=torch.float64, device=device)

    triangle_columns = {
        "ids": ids,
        "x0": (centers - half).contiguous(),
        "y0": (-half).contiguous(),
        "x1": (centers + half).contiguous(),
        "y1": (-half).contiguous(),
        "x2": centers.contiguous(),
        "y2": half.contiguous(),
    }
    triangle_aabbs = torch.stack(
        (
            triangle_columns["x0"],
            triangle_columns["y0"],
            torch.full((ray_count,), -1.0e-4, dtype=torch.float32, device=device),
            triangle_columns["x1"],
            triangle_columns["y2"],
            torch.full((ray_count,), 1.0e-4, dtype=torch.float32, device=device),
        ),
        dim=1,
    ).to(torch.float32).contiguous()
    ray_columns = {
        "ids": ids,
        "ox": centers.contiguous(),
        "oy": (-one).contiguous(),
        "dx": zero.contiguous(),
        "dy": one.contiguous(),
        "tmax": torch.full((ray_count,), 2.0, dtype=torch.float64, device=device),
    }
    return {
        "triangle_columns": triangle_columns,
        "triangle_aabbs": triangle_aabbs,
        "ray_columns": ray_columns,
        "expected_flags": torch.ones((ray_count,), dtype=torch.uint32, device=device),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V4 ray/triangle any-hit flag Torch device-array example.")
    parser.add_argument("--ray-count", type=int, default=8192)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan: dict[str, Any] = {
        "example": "v4_ray_triangle_any_hit_flags_torch_device_arrays",
        "ray_count": int(args.ray_count),
        "triangle_count": int(args.ray_count),
        "input_contract": "caller_supplied_torch_device_triangle_aabb_and_ray_columns",
        "output_contract": "caller_owned_torch_device_any_hit_flag_column",
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
        with rt_v4.prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4(
            fixture["triangle_columns"],
            fixture["triangle_aabbs"],
            partner="torch",
        ) as session:
            output_flags = session.allocate_outputs(int(args.ray_count), device=torch.device("cuda:0"))
            session.run(fixture["ray_columns"], output_flags=output_flags, return_metadata=True)
            torch.cuda.synchronize()
            start = time.perf_counter()
            result = session.run(fixture["ray_columns"], output_flags=output_flags, return_metadata=True)
            torch.cuda.synchronize()
            elapsed_s = time.perf_counter() - start

        correctness_passed = bool(torch.equal(output_flags, fixture["expected_flags"]))
        payload = {
            "status": "measured",
            **plan,
            "elapsed_s": elapsed_s,
            "hit_count": int(torch.sum(output_flags).detach().cpu().item()),
            "correctness_passed": correctness_passed,
            "metadata": result["metadata"],
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
