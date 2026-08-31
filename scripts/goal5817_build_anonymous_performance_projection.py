#!/usr/bin/env python3
"""Export the Goal5817 timing population without identifying custody fields."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    controller = json.loads(args.controller.read_text(encoding="utf-8"))
    evaluation = json.loads(args.evaluation.read_text(encoding="utf-8"))
    rows = controller.get("workers")
    if not isinstance(rows, list) or len(rows) != 324:
        raise RuntimeError("worker universe differs")
    if evaluation.get("row_count") != 18 \
            or evaluation.get("gated_pass_count") != 2:
        raise RuntimeError("evaluation universe differs")

    projected = []
    for row in rows:
        raw = row["raw_result"]
        timings = (
            raw["execute_or_regime_durations_ns"]
            if row["arm"] == "DIRECT" else raw["durations_ns"]
        )
        expected = 64 if row["regime"] == "STEADY_E2E" else 1
        if raw.get("status") != "PASS" or len(timings) != expected \
                or row["metric_ns"] != int(statistics.median(timings)):
            raise RuntimeError(f"worker timing differs: {row['ordinal']}")
        if row["arm"] == "DIRECT" and raw["correctness"]["oracle_exact"] is not True:
            raise RuntimeError(f"Direct correctness differs: {row['ordinal']}")
        projected.append({
            "worker_id": f"w{row['ordinal']:03d}",
            "ordinal": row["ordinal"],
            "task": row["task"],
            "regime": row["regime"],
            "block": row["block"],
            "position": row["position"],
            "arm": row["arm"],
            "status": "PASS",
            "oracle_exact": True,
            "timings_ns": timings,
            "metric_median_ns": row["metric_ns"],
            "registered_performance_timing_count": expected,
        })

    reported = []
    for row in evaluation["rows"]:
        reported.append({key: row[key] for key in (
            "task", "regime", "numerator", "denominator", "ratio", "ci95",
            "bootstrap_seed", "threshold", "pass", "claim_mode",
        )})

    value = {
        "schema": "rtdl.artifact.performance_workers.v4",
        "target_class": "NVIDIA RTX 4000 Ada",
        "arm_definitions": {
            "DIRECT": {
                "paper_label": "Direct CUDA/OptiX",
                "role": "MATCHED_EXPERT_CPP_ARM",
            },
            "PYOPTIX": {
                "paper_label": "PyOptiX-compat",
                "distribution": "NVIDIA otk-pyoptix",
                "distribution_version": "9.1.0",
                "optix_api_version": "9.0.0",
                "role": "OPTIX_9_0_COMPATIBILITY_SCALAR_ARM",
                "stock_current_9_1_api_claimed": False,
            },
            "RTDL": {
                "paper_label": "RTDL",
                "role": "CURRENT_RTDL_ARM",
            },
        },
        "ratio_orientation": "NUMERATOR_OVER_DENOMINATOR__LOWER_FAVORS_NUMERATOR",
        "worker_count": 324,
        "registered_performance_timing_count": sum(
            row["registered_performance_timing_count"] for row in projected),
        "reported_row_count": len(reported),
        "gated_row_count": sum(row["threshold"] is not None for row in reported),
        "gated_pass_count": sum(row["pass"] is True for row in reported),
        "current_source_direct_cuda_optix_arm_present": True,
        "prior_timing_values_used": False,
        "registration_lineage": {
            "observed_predecessors": [
                {
                    "block_count": 24,
                    "arm_count": 3,
                    "arms": ["DIRECT", "PYOPTIX", "RTDL"],
                    "target_class": "NVIDIA RTX A4500",
                    "rtdl_pyoptix_gate_pass_count": 0,
                    "rtdl_pyoptix_gate_row_count": 6,
                    "result_known_before_successor_freeze": True,
                },
                {
                    "block_count": 16,
                    "arm_count": 2,
                    "arms": ["PYOPTIX", "RTDL"],
                    "target_class": "NVIDIA RTX 4000 Ada",
                    "rtdl_pyoptix_gate_pass_count": 2,
                    "rtdl_pyoptix_gate_row_count": 6,
                    "result_known_before_successor_freeze": True,
                },
            ],
            "withdrawn_asymmetric_predecessor": {
                "observed_before_successor_freeze": True,
                "disposition": (
                    "WITHDRAWN__AVOIDABLE_BASELINE_SIDE_PYTHON_WORK_"
                    "EXCEEDED_APPARENT_ADVANTAGE"
                ),
                "timings_reused": False,
                "claim_reused": False,
            },
            "successor_block_count": 18,
            "all_listed_predecessor_results_known_before_successor_freeze": True,
            "successor_frozen_before_own_timings": True,
            "prior_rows_reused": False,
            "unconditional_outcome_acceptance": True,
            "interpretation": (
                "REGISTERED_REPLICATION_EXTENSION_AFTER_OBSERVED_PREDECESSORS__"
                "NOT_UNTOUCHED_ORIGINAL_PREREGISTRATION"
            ),
        },
        "reported_rows": reported,
        "workers": projected,
        "claim_ceiling": {
            "steady_rtdl_within_five_percent_of_pyoptix_on_two_tasks": True,
            "cold_or_prepare_rtdl_within_ten_percent_of_pyoptix": False,
            "direct_rows_have_registered_pass_fail_threshold": False,
            "cross_application_or_cross_target_performance": False,
        },
    }
    if value["registered_performance_timing_count"] != 7_128:
        raise RuntimeError("registered timing count differs")

    args.output.write_bytes(json.dumps(
        value, indent=2, allow_nan=False, sort_keys=True,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "workers": value["worker_count"],
        "timings": value["registered_performance_timing_count"],
        "rows": value["reported_row_count"],
        "passes": value["gated_pass_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
