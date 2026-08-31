#!/usr/bin/env python3
"""Close the immutable Goal5774 prepared V2-direct/V4 formal result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-root", type=Path, required=True)
    parser.add_argument("--formal-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    prepared = json.loads((args.prepare_root / "result/PREPARED.json").read_text())
    runtime = json.loads((args.prepare_root / "result/RUNTIME.json").read_text())
    plan = json.loads((args.prepare_root / "result/PLAN.json").read_text())
    evaluation_path = args.formal_root / "EVALUATION.json"
    recount_path = args.formal_root / "INDEPENDENT_RECOUNT.json"
    evaluation = json.loads(evaluation_path.read_text())
    recount = json.loads(recount_path.read_text())
    controller_path = args.formal_root / "CONTROLLER_RECEIPT.json"
    controller = json.loads(controller_path.read_text())
    paths = sorted((args.formal_root / "workers").glob("*.json"))
    if len(paths) != 208:
        raise RuntimeError("Goal5774 closeout requires exactly 208 workers")
    workers = [json.loads(path.read_text()) for path in paths]
    if len({row["parent_pid"] for row in workers}) != 208:
        raise RuntimeError("Goal5774 closeout requires 208 unique PIDs")
    identities = (
        "bundle_sha256", "prepared_identity_sha256", "target_identity_sha256",
        "formal_identity_sha256", "native_library_sha256",
    )
    for key in identities:
        values = {row[key] for row in workers}
        expected = runtime[key]
        if values != {expected}:
            raise RuntimeError(f"Goal5774 mixed or drifted {key}")
    if controller.get("worker_count") != 208 or controller.get("v3_worker_count") != 0:
        raise RuntimeError("Goal5774 controller receipt is invalid")
    if evaluation.get("row_count") != 26 or recount.get("row_count") != 26 \
            or recount.get("all_rows_exactly_matched") is not True:
        raise RuntimeError("Goal5774 statistics did not close")
    if recount.get("evaluation_sha256") != _sha(evaluation_path):
        raise RuntimeError("Goal5774 evaluation/recount binding failed")
    correct = 0
    behavioral = 0
    registered = 0
    for worker in workers:
        for call in (worker["activation"], *worker["calls"]):
            if call.get("matched") is not True:
                raise RuntimeError("Goal5774 output mismatch")
            correct += 1
            receipt = call.get("behavioral_traversal_receipt", {})
            snapshot = receipt.get("native_snapshot", {})
            launches = snapshot.get("successful_launch_count")
            if receipt.get("physical_executor_classification") \
                    != "optix_traversal_observed" or not isinstance(launches, int) \
                    or launches <= 0 or snapshot.get("complete_context_launch_count") != launches:
                raise RuntimeError("Goal5774 behavioral traversal mismatch")
            if any(snapshot.get(name) != 0 for name in (
                    "failed_launch_count", "incomplete_context_launch_count",
                    "pending_context_at_finish", "session_error")):
                raise RuntimeError("Goal5774 failed traversal state")
            behavioral += 1
        registered += sum(
            call.get("registered_performance_observation") is True
            for call in worker["calls"])
        if worker["activation"].get("registered_performance_observation") is not False:
            raise RuntimeError("Goal5774 activation entered formal timing")

    rows = evaluation["rows"]
    ci_below = sum(row["bootstrap_ci95"][1] < 1.0 for row in rows)
    ci_cross = sum(row["bootstrap_ci95"][0] <= 1.0 <= row["bootstrap_ci95"][1]
                   for row in rows)
    ci_above = sum(row["bootstrap_ci95"][0] > 1.0 for row in rows)
    ratios = [float(row["paired_ratio_median"]) for row in rows]
    payload = {
        "schema": "rtdl.goal5774.v2_v4_prepared_formal_result.v1",
        "measurement_scope": (
            "nine_paper_apps_thirteen_frozen_representative_contract_lanes_"
            "prepared_same_owner_two_registered_calls_rtx4000ada"
        ),
        "bundle_sha256": runtime["bundle_sha256"],
        "source_archive_sha256": prepared["source_archive_sha256"],
        "execution_source_sha256": runtime["execution_source_sha256"],
        "execution_tree_sha256": runtime["execution_tree_sha256"],
        "native_library_sha256": runtime["native_library_sha256"],
        "prepared_identity_sha256": runtime["prepared_identity_sha256"],
        "target_identity_sha256": runtime["target_identity_sha256"],
        "formal_identity_sha256": runtime["formal_identity_sha256"],
        "paper_app_count": 9,
        "lane_count": 13,
        "formal_worker_count": 208,
        "unique_parent_pid_count": 208,
        "correct_call_count": correct,
        "behavioral_true_optix_call_count": behavioral,
        "registered_prepared_execution_count": registered,
        "activation_call_count": 208,
        "activation_registered_timing_count": 0,
        "v2_worker_count": 104,
        "v4_worker_count": 104,
        "v3_worker_count": 0,
        "independent_row_count": 26,
        "pass_count": evaluation["pass_count"],
        "fail_count": evaluation["fail_count"],
        "all_row_no_slower": evaluation["all_row_no_slower"],
        "ratio_direction": "v2_direct_over_v4__greater_than_one_favors_v4",
        "paired_ratio_median_min": min(ratios),
        "paired_ratio_median_max": max(ratios),
        "paired_ratio_median_across_rows_descriptive_only": statistics.median(ratios),
        "ci_wholly_below_one_count": ci_below,
        "ci_crosses_one_count": ci_cross,
        "ci_wholly_above_one_count": ci_above,
        "rows": rows,
        "primary_evaluation_sha256": _sha(evaluation_path),
        "independent_recount_sha256": _sha(recount_path),
        "controller_receipt_sha256": _sha(controller_path),
        "independent_recount_exact": True,
        "cold_goal5769_result_replaced": False,
        "cold_goal5769_v2_v4_subset_status": "0_of_13_immutable",
        "preparation_reported_separately_not_free": True,
        "application_cross_call_amortization_claimed": False,
        "full_paper_dataset_performance_claimed": False,
        "cross_lane_compensation_used": False,
        "retry_resume_replacement_row_drop_relabel_used": False,
        "create_only_zero_worker_failure_count_before_prepare_success": 2,
        "claim_boundary": {
            "prepared_v2_v4_scoped_measurement_complete": True,
            "prepared_all_row_no_slower_claimed": False,
            "cold_no_slower_claimed": False,
            "v4_outperforms_v2_claimed": False,
            "v3_result_or_claim_created": False,
            "author_performance_claimed": False,
            "rt_silicon_utilization_claimed": False,
            "production_public_or_submission_claimed": False,
        },
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
