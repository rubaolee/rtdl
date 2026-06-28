#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


GROUP_WIDTH = 16

TEACHING_CONTEXT = {
    "tutorial_classification": "operator_companion_after_kernel_first_lesson",
    "not_first_lesson": True,
    "kernel_first_requirement": "Read triangle_counting_graph_lowering.py and continuation_grouped_sum.py before this surface.",
    "concept_tutorials": [
        "examples/tutorial_programs/triangle_counting_graph_lowering.py",
        "examples/tutorial_programs/continuation_grouped_sum.py",
    ],
    "manual_data_flow": [
        "User supplies ray and triangle columns on the Torch CUDA device.",
        "Each primitive also carries a group id and an integer payload.",
        "RTDL emits hit rows and reduces count plus sum per group.",
    ],
    "input_columns": {
        "triangle_columns": "triangle ids and 3D vertices",
        "ray_columns": "ray id, origin, direction, and tmax columns",
        "primitive_group_ids": "uint32 group id per primitive",
        "primitive_values": "uint64 payload per primitive",
    },
    "field_map": {
        "kernel_ray_id": "ray_columns.ids",
        "kernel_primitive_id": "triangle_columns.ids",
        "kernel_group_id": "primitive_group_ids",
        "kernel_value": "primitive_values",
        "group_invariant": "group ids are stable integer buckets for the continuation",
        "output_group_count": "number of accepted hits per group",
        "output_group_sum": "sum of primitive_values per group",
    },
    "relation_output": "accepted hit rows annotated with primitive group and payload",
    "continuation": "per-group count and integer sum",
    "benchmark_bridge": "triangle-counting and grouped graph/geometry reductions",
}


def make_torch_fixture(torch, ray_count: int) -> dict[str, object]:
    if ray_count <= 0:
        raise ValueError("ray_count must be positive")
    if ray_count % GROUP_WIDTH != 0:
        raise ValueError(f"ray_count must be divisible by {GROUP_WIDTH}")
    device = torch.device("cuda:0")
    ids_i64 = torch.arange(ray_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    coords = ids_i64.to(torch.float64)
    x = ((coords % 256) * 2.0).contiguous()
    y = (torch.div(coords, 256, rounding_mode="floor") * 2.0).contiguous()
    zero = torch.zeros((ray_count,), dtype=torch.float64, device=device)
    one = torch.ones((ray_count,), dtype=torch.float64, device=device)
    half = torch.full((ray_count,), 0.40, dtype=torch.float64, device=device)
    group_count = ray_count // GROUP_WIDTH

    first = torch.arange(group_count, dtype=torch.int64, device=device) * GROUP_WIDTH + 1
    last = first + GROUP_WIDTH - 1
    expected_counts = torch.full((group_count,), GROUP_WIDTH, dtype=torch.uint64, device=device)
    expected_sums = (((first + last) * GROUP_WIDTH) // 2).to(torch.uint64).contiguous()

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
        "primitive_group_ids": (np.arange(ray_count, dtype=np.uint32) // np.uint32(GROUP_WIDTH)).astype(np.uint32),
        "primitive_values": (np.arange(ray_count, dtype=np.uint64) + np.uint64(1)).astype(np.uint64),
        "group_count": group_count,
        "expected_counts": expected_counts,
        "expected_sums": expected_sums,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="V4 primitive grouped-i64 reduction Torch device-array example."
    )
    parser.add_argument("--ray-count", type=int, default=8192)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan: dict[str, Any] = {
        "example": "v4_primitive_grouped_i64_reduction_torch_device_arrays",
        "surface": "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        "ray_count": int(args.ray_count),
        "triangle_count": int(args.ray_count),
        "group_width": GROUP_WIDTH,
        "group_count": int(args.ray_count) // GROUP_WIDTH,
        "input_contract": "caller_supplied_torch_device_triangle_and_ray_columns_prepared_primitive_payload",
        "output_contract": "caller_owned_torch_device_grouped_i64_columns",
        "teaching_context": TEACHING_CONTEXT,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_partner_scope": "torch 2.8.0+cu128",
        "optix_9_1_validated": False,
        "claim_boundary": {
            "public_claim": "primitive grouped-i64 reduction Torch device-array operator example",
            "not_claimed": [
                "broad V4 speedup",
                "whole-application speedup",
                "arbitrary callback support",
            ],
        },
    }
    if args.dry_run:
        payload = {"status": "dry_run", **plan}
    else:
        import torch
        import rtdsl.v4_ray_triangle as rt_v4

        fixture = make_torch_fixture(torch, int(args.ray_count))
        torch.cuda.synchronize()
        with rt_v4.prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4(
            fixture["triangle_columns"],
            fixture["ray_columns"],
            primitive_group_ids=fixture["primitive_group_ids"],
            primitive_values=fixture["primitive_values"],
            group_count=fixture["group_count"],
            partner="torch",
        ) as session:
            output_columns = session.allocate_outputs()
            session.run(reduction="sum_count", output_columns=output_columns, return_metadata=True)
            torch.cuda.synchronize()
            start = time.perf_counter()
            result = session.run(reduction="sum_count", output_columns=output_columns, return_metadata=True)
            torch.cuda.synchronize()
            elapsed_s = time.perf_counter() - start

        counts_match = bool(torch.equal(output_columns["group_counts"], fixture["expected_counts"]))
        sums_match = bool(torch.equal(output_columns["group_sums"], fixture["expected_sums"]))
        payload = {
            "status": "measured",
            **plan,
            "elapsed_s": elapsed_s,
            "correctness_passed": counts_match and sums_match,
            "counts_match": counts_match,
            "sums_match": sums_match,
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
