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
    "concept_tutorials": [
        "examples/tutorial_programs/ray_triangle_hits.py",
        "examples/tutorial_programs/continuation_grouped_sum.py",
        "examples/tutorial_programs/raydb_table_to_ray.py",
    ],
    "manual_data_flow": [
        "User supplies triangle, ray, and weight columns on the Torch CUDA device.",
        "RTDL traverses rays against triangle primitives.",
        "The fused continuation sums the weight for accepted hits without a separate Python loop.",
    ],
    "input_columns": {
        "triangle_columns": "triangle ids and 3D vertices",
        "ray_columns": "ray id, origin, direction, and tmax columns",
        "ray_weights": "uint64 weight payload per ray",
    },
    "relation_output": "accepted ray/triangle hit rows",
    "continuation": "one uint64 weighted-hit sum scalar",
    "benchmark_bridge": "RayDB and aggregation-after-hit patterns",
}


def make_torch_fixture(torch, ray_count: int) -> dict[str, object]:
    if ray_count <= 0:
        raise ValueError("ray_count must be positive")
    device = torch.device("cuda:0")
    ids_i64 = torch.arange(ray_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    coords = ids_i64.to(torch.float64)
    x = ((coords % 256) * 2.0).contiguous()
    y = (torch.div(coords, 256, rounding_mode="floor") * 2.0).contiguous()
    zero = torch.zeros((ray_count,), dtype=torch.float64, device=device)
    one = torch.ones((ray_count,), dtype=torch.float64, device=device)
    half = torch.full((ray_count,), 0.40, dtype=torch.float64, device=device)
    weights = (ids_i64 + 1).to(torch.uint64).contiguous()
    return {
        "triangle_columns": {
            "ids": ids,
            "x0": (x - half).contiguous(),
            "y0": (y - half).contiguous(),
            "z0": one.contiguous(),
            "x1": (x + half).contiguous(),
            "y1": (y - half).contiguous(),
            "z1": one.contiguous(),
            "x2": x.contiguous(),
            "y2": (y + half).contiguous(),
            "z2": one.contiguous(),
        },
        "ray_columns": {
            "ids": ids,
            "ox": x.contiguous(),
            "oy": y.contiguous(),
            "oz": zero.contiguous(),
            "dx": zero.contiguous(),
            "dy": zero.contiguous(),
            "dz": one.contiguous(),
            "tmax": torch.full((ray_count,), 10.0, dtype=torch.float64, device=device),
        },
        "ray_weights": weights,
        "expected_weighted_sum": ray_count * (ray_count + 1) // 2,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="V4 measured ray/triangle any-hit weighted-sum Torch device-array example."
    )
    parser.add_argument("--ray-count", type=int, default=8192)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan: dict[str, Any] = {
        "example": "v4_ray_triangle_any_hit_weighted_sum_torch_device_arrays",
        "surface": "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
        "surface_status": "tier2_measured_v4_0_0_release_surface",
        "ray_count": int(args.ray_count),
        "triangle_count": int(args.ray_count),
        "input_contract": "caller_supplied_torch_device_triangle_ray_and_weight_columns",
        "output_contract": "rtdl_allocated_or_caller_owned_torch_device_uint64_scalar",
        "output_scalar_primary_allocation": "rtdl_allocated_uint64_device_scalar",
        "teaching_context": TEACHING_CONTEXT,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "true_zero_copy_authorized": False,
    }
    if args.dry_run:
        payload = {"status": "dry_run", **plan}
    else:
        import torch
        import rtdsl.v4_ray_triangle as rt_v4

        fixture = make_torch_fixture(torch, int(args.ray_count))
        torch.cuda.synchronize()
        with rt_v4.prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4(
            fixture["triangle_columns"],
            fixture["ray_columns"],
            fixture["ray_weights"],
            partner="torch",
        ) as session:
            session.run(return_metadata=True)
            torch.cuda.synchronize()
            start = time.perf_counter()
            result = session.run(return_metadata=True)
            torch.cuda.synchronize()
            elapsed_s = time.perf_counter() - start

        output_scalar = result["columns"]["weighted_hit_sum"]
        weighted_sum = int(output_scalar.detach().cpu().item())
        expected = int(fixture["expected_weighted_sum"])
        payload = {
            "status": "measured",
            **plan,
            "elapsed_s": elapsed_s,
            "weighted_hit_sum": weighted_sum,
            "expected_weighted_sum": expected,
            "correctness_passed": weighted_sum == expected,
            "metadata": result["metadata"],
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"dry_run", "measured"} and payload.get("correctness_passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
