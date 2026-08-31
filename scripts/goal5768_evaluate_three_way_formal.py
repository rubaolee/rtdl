#!/usr/bin/env python3
"""Primary row-local evaluation for the Goal5768 three-way cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


V2 = "v2_direct_true_optix_backport"
V3 = "v3_compiler_true_optix"
V4 = "v4_restricted_callback_true_optix"
BASELINES = (V2, V3)
BOOTSTRAP_DRAWS = 10_000
CI_LOW_INDEX = 249
CI_HIGH_INDEX = 9749
SEED_BASE = 57_680_000


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _load_plan(path: Path) -> dict[str, object]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    body = dict(plan)
    claimed = body.pop("plan_sha256", None)
    if claimed != _digest(body):
        raise RuntimeError("plan digest mismatch")
    return plan


def _validate_receipt(receipt: object) -> None:
    if not isinstance(receipt, dict):
        raise RuntimeError("traversal receipt is not a mapping")
    body = dict(receipt)
    claimed = body.pop("receipt_sha256", None)
    if claimed != _digest(body):
        raise RuntimeError("traversal receipt digest mismatch")
    if receipt.get("physical_executor_classification") != "optix_traversal_observed":
        raise RuntimeError("timed endpoint lacks behavioral OptiX traversal")
    snapshot = receipt.get("native_snapshot")
    if not isinstance(snapshot, dict):
        raise RuntimeError("traversal receipt lacks native snapshot")
    successful = snapshot.get("successful_launch_count")
    complete = snapshot.get("complete_context_launch_count")
    if not isinstance(successful, int) or successful <= 0 or complete != successful:
        raise RuntimeError("traversal launches were not all context-bound")
    for name in (
        "failed_launch_count", "incomplete_context_launch_count",
        "pending_context_at_finish", "session_error",
    ):
        if snapshot.get(name) != 0:
            raise RuntimeError(f"traversal receipt {name} is nonzero")
    if snapshot.get("first_traversable") in (None, 0) \
            or snapshot.get("last_traversable") in (None, 0):
        raise RuntimeError("traversal receipt lacks nonzero traversables")
    if snapshot.get("first_program_bundle_id") in (None, 0) \
            or snapshot.get("last_program_bundle_id") in (None, 0):
        raise RuntimeError("traversal receipt lacks program-bundle binding")


def _bootstrap(values: tuple[float, ...], seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    medians = sorted(
        statistics.median(rng.choices(values, k=len(values)))
        for _ in range(BOOTSTRAP_DRAWS)
    )
    return medians[CI_LOW_INDEX], medians[CI_HIGH_INDEX]


def evaluate(plan_path: Path, raw_root: Path) -> dict[str, object]:
    plan = _load_plan(plan_path)
    expected_units = {row["unit_id"]: row for row in plan["units"]}
    paths = tuple(sorted(raw_root.glob("*/RESULT.json")))
    if len(paths) != 312:
        raise RuntimeError(f"expected 312 raw workers, found {len(paths)}")
    observed = {}
    parent_pids = set()
    native_ids = set()
    for path in paths:
        row = json.loads(path.read_text(encoding="utf-8"))
        unit = row.get("unit")
        if not isinstance(unit, dict) or unit.get("unit_id") not in expected_units:
            raise RuntimeError("raw worker has unknown unit")
        unit_id = unit["unit_id"]
        if unit != expected_units[unit_id] or unit_id in observed:
            raise RuntimeError("raw worker unit drift or duplicate")
        if row.get("plan_sha256") != plan["plan_sha256"] \
                or row.get("formal_identity_sha256") != plan["formal_identity_sha256"]:
            raise RuntimeError("raw worker plan identity drift")
        pid = row.get("parent_pid")
        if not isinstance(pid, int) or pid <= 0 or pid in parent_pids:
            raise RuntimeError("fresh-process PID contract failed")
        parent_pids.add(pid)
        endpoint = row.get("endpoint")
        if not isinstance(endpoint, dict) or endpoint.get("matched") is not True:
            raise RuntimeError("raw endpoint correctness failed")
        if endpoint.get("lane_id") != unit["lane_id"] \
                or endpoint.get("method") != unit["method"]:
            raise RuntimeError("raw endpoint lane/method label drift")
        if endpoint.get("stock_v2_or_v3_claimed") is not False \
                or endpoint.get("default_selected_between_application_algorithms") is not False:
            raise RuntimeError("raw endpoint provenance/selection claim drift")
        seconds = endpoint.get("registered_complete_seconds")
        if not isinstance(seconds, (int, float)) or not math.isfinite(seconds) \
                or seconds <= 0.0:
            raise RuntimeError("raw endpoint timer is invalid")
        if endpoint.get("comparator_inside_registered_timer") is not False:
            raise RuntimeError("comparator entered registered timer")
        _validate_receipt(endpoint.get("traversal_receipt"))
        native = endpoint.get("native_library_sha256")
        if native != plan["native_library_sha256"]:
            raise RuntimeError("raw endpoint native identity drift")
        native_ids.add(native)
        observed[unit_id] = row
    if set(observed) != set(expected_units) or len(native_ids) != 1:
        raise RuntimeError("raw cohort is incomplete or mixes native identities")

    rows = []
    row_index = 0
    for lane_id in plan["lane_ids"]:
        lane_workers = [row for row in observed.values()
                        if row["unit"]["lane_id"] == lane_id]
        input_ids = {row["endpoint"]["input_sha256"] for row in lane_workers}
        output_ids = {row["endpoint"]["output_sha256"] for row in lane_workers}
        expected_ids = {row["endpoint"]["expected_sha256"] for row in lane_workers}
        if len(input_ids) != 1 or len(output_ids) != 1 or output_ids != expected_ids:
            raise RuntimeError(f"{lane_id} methods do not share exact input/output")
        contract = plan["lane_contracts"][lane_id]
        if input_ids != {contract["input_sha256"]} \
                or output_ids != {contract["output_sha256"]} \
                or expected_ids != {contract["expected_sha256"]}:
            raise RuntimeError(f"{lane_id} differs from its prepared lane contract")
        by_block_method = {
            (row["unit"]["block_index"], row["unit"]["method"]): row
            for row in lane_workers
        }
        for baseline in BASELINES:
            ratios = tuple(
                float(by_block_method[(block, baseline)]["endpoint"][
                    "registered_complete_seconds"])
                / float(by_block_method[(block, V4)]["endpoint"][
                    "registered_complete_seconds"])
                for block in range(8)
            )
            median = float(statistics.median(ratios))
            low, high = _bootstrap(ratios, SEED_BASE + row_index)
            rows.append({
                "row_index": row_index,
                "lane_id": lane_id,
                "baseline": baseline,
                "candidate": V4,
                "ratio": "baseline_complete_seconds_over_v4_complete_seconds",
                "greater_than_one_favors": V4,
                "pair_count": len(ratios),
                "pair_ratios": ratios,
                "paired_ratio_median": median,
                "bootstrap_ci95": (low, high),
                "row_local_no_slower_pass": median >= 1.0,
                "ci_interpretation": (
                    "wholly_above_one" if low > 1.0
                    else "wholly_below_one" if high < 1.0
                    else "crosses_one"
                ),
                "independent_comparison_row": True,
            })
            row_index += 1
    pass_count = sum(row["row_local_no_slower_pass"] for row in rows)
    result = {
        "schema": "rtdl.goal5768.three_way_formal_evaluation.v1",
        "plan_sha256": plan["plan_sha256"],
        "formal_identity_sha256": plan["formal_identity_sha256"],
        "worker_count": len(observed),
        "unique_parent_pid_count": len(parent_pids),
        "correctness_pass_count": len(observed),
        "behavioral_true_optix_count": len(observed),
        "lane_count": len(plan["lane_ids"]),
        "independent_row_count": len(rows),
        "pass_count": pass_count,
        "fail_count": len(rows) - pass_count,
        "all_row_no_slower": pass_count == len(rows),
        "rows": rows,
        "cross_row_aggregate_or_compensation_used": False,
        "fixed_speedup_target_used": False,
        "retry_resume_replacement_row_dropping_or_relabeling_used": False,
        "claim_boundary": {
            "author_performance_compared": False,
            "hardware_rt_core_utilization_claimed": False,
            "cross_gpu_generalization_claimed": False,
            "publication_claimed": False,
        },
    }
    result["evaluation_sha256"] = _digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    payload = evaluate(args.plan, args.raw_root)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")


if __name__ == "__main__":
    main()
