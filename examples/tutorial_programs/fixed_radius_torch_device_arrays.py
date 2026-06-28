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


RADIUS = 0.35
THRESHOLD = 3
BASE_POINTS_PER_COPY = 8

TEACHING_CONTEXT = {
    "tutorial_classification": "operator_companion_after_kernel_first_lesson",
    "not_first_lesson": True,
    "kernel_first_requirement": "Read and run fixed_radius_neighbors.py before this device-array surface.",
    "concept_tutorial": "examples/tutorial_programs/fixed_radius_neighbors.py",
    "manual_data_flow": [
        "User supplies point id, x, and y columns already on the Torch CUDA device.",
        "RTDL builds candidate point pairs whose distance is within the radius.",
        "The continuation counts neighbors per query point and marks threshold flags.",
    ],
    "input_columns": {
        "ids": "uint32 point id column",
        "x": "float64 point x coordinate",
        "y": "float64 point y coordinate",
    },
    "field_map": {
        "kernel_query_id": "ids",
        "kernel_neighbor_id": "ids from candidate search point",
        "kernel_distance": "computed from x/y columns",
        "output_neighbor_count": "neighbor_count per ids row",
        "output_threshold_flag": "neighbor_count >= threshold",
    },
    "relation_output": "candidate neighbor rows grouped by query point",
    "continuation": "per-point neighbor_count plus threshold_flag",
    "benchmark_bridge": "RTDBSCAN-style radius-neighbor discovery before component continuation",
}


def make_torch_columns(torch, copies: int) -> dict[str, object]:
    if copies < 1:
        raise ValueError("copies must be positive")
    device = torch.device("cuda:0")
    base_ids_i64 = torch.tensor([1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.int64, device=device)
    base_x = torch.tensor([0.00, 0.12, -0.10, 2.00, 2.14, 1.88, 4.50, -3.00], dtype=torch.float64, device=device)
    base_y = torch.tensor([0.00, 0.04, 0.08, 2.00, 2.05, 1.94, 0.00, 2.50], dtype=torch.float64, device=device)
    copy_ids_i64 = torch.arange(copies, dtype=torch.int64, device=device)
    copy_ids_f64 = torch.arange(copies, dtype=torch.float64, device=device)
    ids_i64 = base_ids_i64.repeat(copies) + torch.repeat_interleave(copy_ids_i64 * 100, BASE_POINTS_PER_COPY)
    x = base_x.repeat(copies) + torch.repeat_interleave(copy_ids_f64 * 7.0, BASE_POINTS_PER_COPY)
    y = base_y.repeat(copies)
    return {"ids": ids_i64.to(torch.uint32).contiguous(), "x": x.contiguous(), "y": y.contiguous()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V4 fixed-radius count-threshold Torch device-array example.")
    parser.add_argument("--copies", type=int, default=8192)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan: dict[str, Any] = {
        "example": "v4_fixed_radius_torch_device_arrays",
        "copies": int(args.copies),
        "point_count": int(args.copies) * BASE_POINTS_PER_COPY,
        "radius": RADIUS,
        "threshold": THRESHOLD,
        "input_contract": "caller_supplied_torch_device_point_columns",
        "teaching_context": TEACHING_CONTEXT,
        "claim_boundary": {
            "public_claim": "fixed-radius Torch device-array operator example",
            "not_claimed": [
                "whole-application speedup",
                "arbitrary callback support",
            ],
        },
    }
    if args.dry_run:
        payload = {"status": "dry_run", **plan}
    else:
        import torch
        import rtdsl.v4_fixed_radius as rt_v4

        columns = make_torch_columns(torch, int(args.copies))
        torch.cuda.synchronize()
        with rt_v4.prepare_fixed_radius_count_threshold_2d_device_arrays_v4(
            columns,
            max_radius=RADIUS,
            partner="torch",
        ) as session:
            output_columns = session.allocate_outputs(plan["point_count"])
            start = time.perf_counter()
            result = session.run(
                columns,
                radius=RADIUS,
                threshold=THRESHOLD,
                output_columns=output_columns,
                return_metadata=True,
            )
            elapsed_s = time.perf_counter() - start
        flags = result["columns"]["threshold_flags"]
        counts = result["columns"]["neighbor_counts"]
        threshold_reached_count = int(torch.sum(flags).detach().cpu().item())
        neighbor_count_sum = int(torch.sum(counts).detach().cpu().item())
        expected_threshold_reached = 6 * int(args.copies)
        expected_neighbor_count_sum = 20 * int(args.copies)
        payload = {
            "status": "measured",
            **plan,
            "elapsed_s": elapsed_s,
            "threshold_reached_count": threshold_reached_count,
            "neighbor_count_sum": neighbor_count_sum,
            "correctness_passed": (
                threshold_reached_count == expected_threshold_reached
                and neighbor_count_sum == expected_neighbor_count_sum
            ),
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
