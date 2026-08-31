#!/usr/bin/env python3
"""Primary evaluator for the immutable Goal5774 raw cohort."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import statistics

from goal5774_prepared_three_way_frontdoors import LANES, V2, V4


def _bootstrap(values, seed):
    rng = random.Random(seed)
    draws = sorted(statistics.median(rng.choices(values, k=len(values)))
                   for _ in range(10_000))
    return draws[249], draws[9749]


def evaluate(raw_root: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    workers = [json.loads(path.read_text())
               for path in sorted((raw_root / "workers").glob("*.json"))]
    if len(workers) != 208 or len({row["parent_pid"] for row in workers}) != 208:
        raise RuntimeError("Goal5774 requires 208 fresh workers")
    for identity in (
        "bundle_sha256", "prepared_identity_sha256", "target_identity_sha256",
        "formal_identity_sha256", "native_library_sha256",
    ):
        if len({row.get(identity) for row in workers}) != 1:
            raise RuntimeError(f"Goal5774 mixed worker identity: {identity}")
    grouped = {}
    for row in workers:
        key = (row["lane_id"], int(row["block_index"]))
        grouped.setdefault(key, {})[row["method"]] = row
        if (
            row["formal_worker"] is not True
            or row["prepare_count"] != 1
            or row.get("activation_count") != 1
            or row["execute_count"] != 2
            or row["v3_used_or_required"] is not False
            or row.get("activation", {}).get("matched") is not True
            or row.get("activation", {}).get(
                "registered_performance_observation") is not False
            or row.get("activation", {}).get("activation_only") is not True
            or any(call["matched"] is not True for call in row["calls"])
            or any(call.get("registered_performance_observation") is not True
                   for call in row["calls"])
        ):
            raise RuntimeError("Goal5774 worker contract violation")
    results = []
    for lane_index, lane in enumerate(LANES):
        for call_index in (0, 1):
            ratios = []
            for block in range(8):
                pair = grouped[(lane.lane_id, block)]
                if set(pair) != {V2, V4}:
                    raise RuntimeError("Goal5774 pair is incomplete")
                if (
                    pair[V2]["activation"]["dynamic_input_sha256"]
                    != pair[V4]["activation"]["dynamic_input_sha256"]
                    or pair[V2]["activation"]["output_sha256"]
                    != pair[V4]["activation"]["output_sha256"]
                    or pair[V2]["calls"][call_index]["dynamic_input_sha256"]
                    != pair[V4]["calls"][call_index]["dynamic_input_sha256"]
                    or pair[V2]["calls"][call_index]["output_sha256"]
                    != pair[V4]["calls"][call_index]["output_sha256"]
                ):
                    raise RuntimeError("Goal5774 paired input/output mismatch")
                numerator = float(pair[V2]["calls"][call_index][
                    "registered_prepared_execution_seconds"])
                denominator = float(pair[V4]["calls"][call_index][
                    "registered_prepared_execution_seconds"])
                if not (math.isfinite(numerator) and numerator > 0.0
                        and math.isfinite(denominator) and denominator > 0.0):
                    raise RuntimeError("Goal5774 timing is invalid")
                ratios.append(numerator / denominator)
            median = statistics.median(ratios)
            lower, upper = _bootstrap(
                ratios, 57_740_000 + lane_index * 2 + call_index)
            results.append({
                "lane_id": lane.lane_id,
                "app": lane.app,
                "paper_algorithm": lane.paper_algorithm,
                "call_index": call_index,
                "pair_count": 8,
                "paired_v2_over_v4_ratios": ratios,
                "paired_ratio_median": median,
                "bootstrap_ci95": [lower, upper],
                "greater_than_one_favors": V4,
                "no_slower_pass": median >= 1.0,
                "independent_comparison_row": True,
            })
    payload = {
        "schema": "rtdl.goal5774.prepared_v2_v4_evaluation.v1",
        "worker_count": 208,
        "row_count": 26,
        "independent_row_count": 26,
        "pass_count": sum(row["no_slower_pass"] for row in results),
        "fail_count": sum(not row["no_slower_pass"] for row in results),
        "all_row_no_slower": all(row["no_slower_pass"] for row in results),
        "rows": results,
        "cross_lane_compensation_used": False,
        "fixed_speedup_target_used": False,
        "v3_result_created": False,
        "cold_result_replaced": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(evaluate(args.raw_root, args.output))


if __name__ == "__main__":
    main()
