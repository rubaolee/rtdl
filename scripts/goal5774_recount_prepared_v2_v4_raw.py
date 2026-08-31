#!/usr/bin/env python3
"""Independent raw recount; imports no Goal5774 controller/evaluator/frontdoor."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


LANES = (
    "triangle__rt_1a2", "triangle__rt_2a1", "raydb__q21",
    "librts__range_rows", "librts__overlap_filter", "rtnn__ranked_window",
    "rtdbscan__components", "xhd__global_witness",
    "rayjoin__point_location", "rayjoin__segment_pairs",
    "rayjoin__grouped_events", "rtbh__force", "particle__cell_transition",
)
V2 = "v2_direct_true_optix_backport"
V4 = "v4_restricted_callback_true_optix"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recount(raw_root: Path, evaluation: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    paths = sorted((raw_root / "workers").glob("*.json"))
    if len(paths) != 208:
        raise RuntimeError("independent recount requires 208 workers")
    rows = [json.loads(path.read_text()) for path in paths]
    if len({row["parent_pid"] for row in rows}) != 208:
        raise RuntimeError("independent recount found reused parent PID")
    for identity in (
        "bundle_sha256", "prepared_identity_sha256", "target_identity_sha256",
        "formal_identity_sha256", "native_library_sha256",
    ):
        if len({row.get(identity) for row in rows}) != 1:
            raise RuntimeError(f"independent recount found mixed {identity}")
    by_key = {}
    for row in rows:
        if row["schema"] != "rtdl.goal5774.prepared_v2_v4_formal_worker.v1":
            raise RuntimeError("unexpected raw schema")
        if (
            row["method"] not in {V2, V4}
            or row.get("prepare_count") != 1
            or row.get("activation_count") != 1
            or row.get("execute_count") != 2
            or len(row["calls"]) != 2
        ):
            raise RuntimeError("unexpected raw method/call shape")
        activation = row.get("activation", {})
        if (
            activation.get("matched") is not True
            or activation.get("activation_only") is not True
            or activation.get("registered_performance_observation") is not False
            or activation.get("dynamic_input_sha256") in {
                call.get("dynamic_input_sha256") for call in row["calls"]
            }
        ):
            raise RuntimeError("raw activation admission failed")
        for call in (activation, *row["calls"]):
            receipt = call["behavioral_traversal_receipt"]
            snapshot = receipt["native_snapshot"]
            successful = int(snapshot["successful_launch_count"])
            if (
                call["matched"] is not True
                or receipt["physical_executor_classification"]
                != "optix_traversal_observed"
                or successful <= 0
                or int(snapshot["complete_context_launch_count"]) != successful
                or any(int(snapshot[name]) != 0 for name in (
                    "failed_launch_count", "incomplete_context_launch_count",
                    "pending_context_at_finish", "session_error"))
            ):
                raise RuntimeError("raw behavioral/correctness admission failed")
        if any(call.get("registered_performance_observation") is not True
               for call in row["calls"]):
            raise RuntimeError("raw timed call registration contract failed")
        by_key.setdefault(
            (row["lane_id"], int(row["block_index"])), {})[row["method"]] = row

    recounted = []
    for lane_index, lane_id in enumerate(LANES):
        for call_index in (0, 1):
            ratios = []
            for block in range(8):
                pair = by_key[(lane_id, block)]
                if (
                    set(pair) != {V2, V4}
                    or pair[V2]["activation"]["dynamic_input_sha256"]
                    != pair[V4]["activation"]["dynamic_input_sha256"]
                    or pair[V2]["activation"]["output_sha256"]
                    != pair[V4]["activation"]["output_sha256"]
                    or pair[V2]["calls"][call_index]["dynamic_input_sha256"]
                    != pair[V4]["calls"][call_index]["dynamic_input_sha256"]
                    or pair[V2]["calls"][call_index]["output_sha256"]
                    != pair[V4]["calls"][call_index]["output_sha256"]
                ):
                    raise RuntimeError("raw paired input/output mismatch")
                numerator = float(pair[V2]["calls"][call_index][
                    "registered_prepared_execution_seconds"])
                denominator = float(pair[V4]["calls"][call_index][
                    "registered_prepared_execution_seconds"])
                if min(numerator, denominator) <= 0 or not all(map(
                    math.isfinite, (numerator, denominator))):
                    raise RuntimeError("raw timing invalid")
                ratios.append(numerator / denominator)
            median = statistics.median(ratios)
            rng = random.Random(57_740_000 + lane_index * 2 + call_index)
            draws = sorted(statistics.median(rng.choices(ratios, k=8))
                           for _ in range(10_000))
            recounted.append({
                "lane_id": lane_id, "call_index": call_index,
                "paired_ratio_median": median,
                "bootstrap_ci95": [draws[249], draws[9749]],
                "no_slower_pass": median >= 1.0,
            })
    submitted = json.loads(evaluation.read_text())
    submitted_core = [{
        "lane_id": row["lane_id"], "call_index": row["call_index"],
        "paired_ratio_median": row["paired_ratio_median"],
        "bootstrap_ci95": row["bootstrap_ci95"],
        "no_slower_pass": row["no_slower_pass"],
    } for row in submitted["rows"]]
    if recounted != submitted_core:
        raise RuntimeError("independent raw recount differs from evaluation")
    payload = {
        "schema": "rtdl.goal5774.independent_raw_recount.v1",
        "worker_count": 208,
        "unique_parent_pid_count": 208,
        "row_count": 26,
        "pass_count": sum(row["no_slower_pass"] for row in recounted),
        "fail_count": sum(not row["no_slower_pass"] for row in recounted),
        "evaluation_sha256": _sha(evaluation),
        "all_rows_exactly_matched": True,
        "rows": recounted,
        "imports_controller_evaluator_or_frontdoor": False,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(recount(args.raw_root, args.evaluation, args.output))


if __name__ == "__main__":
    main()
