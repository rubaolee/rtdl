#!/usr/bin/env python3
"""Primary Goal5784 evaluator using the frozen Goal5776 statistics implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import goal5776_evaluate_real_scale_v2_v4 as base
from goal5784_targeted_formal_contract import (
    UNIT_BY_ID, UNITS, V4, contract_document, contract_sha256, schedule,
    statistical_rows,
)


def evaluate(raw_root: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    base.UNIT_BY_ID = UNIT_BY_ID
    base.UNITS = UNITS
    base.contract_document = contract_document
    base.contract_sha256 = contract_sha256
    base.schedule = schedule
    base.statistical_rows = statistical_rows
    workers = [json.loads(path.read_text(encoding="utf-8"))
               for path in sorted((raw_root / "workers").glob("*.json"))]
    triangle_v4 = [row for row in workers
                   if row.get("method") == V4
                   and UNIT_BY_ID[str(row.get("unit_id"))].app
                       == "triangle_counting"]
    if len(triangle_v4) != 48:
        raise RuntimeError("Goal5784 evaluator lacks 48 Triangle V4 workers")
    for worker in triangle_v4:
        binding = worker.get("mechanism_binding")
        if not isinstance(binding, dict) or (
            binding.get("mechanism_id")
                != "compiler_fused_checked_u64_device_reduction"
            or binding.get("evidence_level")
                != "actual_per_segment_device_reduction_receipts"
            or binding.get("all_segments_one_device_kernel_one_host_sync") is not True
            or binding.get("all_segments_bounds_validated_before_sum_trust") is not True
            or binding.get("observation_outside_registered_endpoint_timer") is not True
        ):
            raise RuntimeError("Goal5784 evaluator lacks fused mechanism binding")
    temporary = output.with_name(f".{output.name}.goal5776_base")
    if temporary.exists():
        raise FileExistsError(temporary)
    base.evaluate(raw_root, temporary)
    payload = json.loads(temporary.read_text(encoding="utf-8"))
    payload["schema"] = "rtdl.goal5784.targeted_v2_v4_evaluation.v1"
    payload["run_goal_id"] = 5784
    payload["goal5776_replaced_or_relabelled"] = False
    payload["triangle_clear_fusion_rows"] = [
        row["row_id"] for row in payload["rows"]
        if row["app"] == "triangle_counting" and row["bootstrap_ci95"][0] > 1.0
    ]
    payload["triangle_second_named_fusion_family_earned"] = bool(
        payload["triangle_clear_fusion_rows"])
    payload["triangle_v4_mechanism_bound_worker_count"] = len(triangle_v4)
    payload["triangle_v4_mechanism_binding_complete"] = True
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    temporary.unlink()
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(evaluate(args.raw_root, args.output))


if __name__ == "__main__":
    main()
