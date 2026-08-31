#!/usr/bin/env python3
"""Mechanically close the Goal5769 v33 result without a fourth statistic.

This script does not resample or recompute ratios.  It requires exact agreement
between the primary evaluator, packaged independent recount, and separately
implemented raw auditor, then copies the agreed row facts into one durable
result record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINEAGE_FILES = (
    "history/internal_docs/goal5769_v24_stage_a_rtx_particle_failure_evidence_20260813.tar.gz",
    "history/internal_docs/goal5769_v28_zero_worker_governance_failure_20260813.json",
    "history/internal_docs/goal5769_v29_stage_b_s1.tar.gz",
    "history/internal_docs/goal5769_v30_zero_worker_governance_failure_20260813.json",
    "history/internal_docs/goal5769_v32_zero_worker_test_manifest_governance_failure_20260813.json",
    "history/internal_docs/self_review_goal5769_v24_rtx_particle_hard_stop_and_v25_decision_20260813.md",
    "history/internal_docs/self_review_goal5769_v29_stage_b_s1_and_v30_environment_repair_20260813.md",
)

def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not a mapping: {path}")
    return value


def _row_core(row: dict[str, object]) -> tuple[object, ...]:
    return (
        row["row_index"], row["lane_id"], row["baseline"], row["candidate"],
        tuple(row["pair_ratios"]), row["paired_ratio_median"],
        tuple(row["bootstrap_ci95"]), row["row_local_no_slower_pass"],
    )


def close(
    *, plan_path: Path, controller_path: Path, primary_path: Path,
    recount_path: Path, audit_path: Path, stage_a_path: Path,
    bundle_path: Path,
) -> dict[str, object]:
    plan = _load(plan_path)
    controller = _load(controller_path)
    primary = _load(primary_path)
    recount = _load(recount_path)
    audit = _load(audit_path)
    stage_a = _load(stage_a_path)
    plan_sha = plan["plan_sha256"]
    formal_sha = plan["formal_identity_sha256"]
    for name, value in (
        ("controller", controller), ("primary", primary),
        ("recount", recount), ("audit", audit),
    ):
        if value.get("plan_sha256") != plan_sha \
                or value.get("formal_identity_sha256") != formal_sha:
            raise RuntimeError(f"{name} is not bound to the exact plan")
    if controller.get("completed_unit_count") != 312 \
            or controller.get("expected_unit_count") != 312 \
            or controller.get(
                "retry_resume_replacement_row_dropping_or_relabeling_used") is not False:
        raise RuntimeError("formal controller receipt is incomplete or drifted")
    for name, value in (("primary", primary), ("recount", recount), ("audit", audit)):
        if value.get("worker_count") != 312 \
                or value.get("unique_parent_pid_count") != 312 \
                or value.get("independent_row_count") != 26 \
                or value.get("cross_row_aggregate_or_compensation_used") is not False:
            raise RuntimeError(f"{name} cohort shape or compensation policy drift")
    if primary.get("correctness_pass_count") != 312 \
            or primary.get("behavioral_true_optix_count") != 312 \
            or audit.get("correctness_pass_count") != 312 \
            or audit.get("behavioral_true_optix_count") != 312:
        raise RuntimeError("correctness or behavioral OptiX closure failed")
    cores = [tuple(_row_core(row) for row in value["rows"])
             for value in (primary, recount, audit)]
    if not (cores[0] == cores[1] == cores[2]):
        raise RuntimeError("three result implementations disagree")
    if recount.get("primary_core_exact_match") is not True:
        raise RuntimeError("packaged recount did not record exact primary agreement")
    if stage_a.get("functional_smoke_count") != 39 \
            or stage_a.get("functional_correct_count") != 39 \
            or stage_a.get("functional_behavioral_true_optix_count") != 39 \
            or stage_a.get("formal_worker_count") != 0:
        raise RuntimeError("Stage-A functional identity is incomplete")
    if plan.get("native_library_sha256") != stage_a.get("native_library_sha256"):
        raise RuntimeError("Stage-A and formal plan native identities differ")
    if plan.get("bundle_sha256") != _file_sha(bundle_path):
        raise RuntimeError("executed bundle identity mismatch")
    lineage_hashes = {}
    for relative in LINEAGE_FILES:
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"required prior lineage is missing: {relative}")
        lineage_hashes[relative] = _file_sha(path)
    rows = primary["rows"]
    passed = int(primary["pass_count"])
    result: dict[str, object] = {
        "schema": "rtdl.goal5769.v33_rtx4000ada_three_way_formal_result.v1",
        "goal": 5769,
        "candidate": "v33",
        "endpoint": "RTX 4000 Ada CC8.9",
        "bundle_sha256": _file_sha(bundle_path),
        "execution_source_sha256": stage_a["source_archive_sha256"],
        "execution_source_tree_sha256": stage_a["source_tree_sha256"],
        "native_library_sha256": plan["native_library_sha256"],
        "plan_sha256": plan_sha,
        "formal_identity_sha256": formal_sha,
        "stage_a_functional_worker_count": 39,
        "formal_worker_count": 312,
        "unique_parent_pid_count": 312,
        "correctness_pass_count": 312,
        "behavioral_true_optix_count": 312,
        "lane_count": 13,
        "independent_row_count": 26,
        "pass_count": passed,
        "fail_count": 26 - passed,
        "all_row_no_slower": passed == 26,
        "ratio": "baseline_complete_seconds_over_v4_complete_seconds",
        "greater_than_one_favors": "v4_restricted_callback_true_optix",
        "rows": rows,
        "three_statistical_implementations_exact_match": True,
        "cross_row_aggregate_or_compensation_used": False,
        "retry_resume_replacement_row_dropping_or_relabeling_used": False,
        "prior_lineage_file_sha256": lineage_hashes,
        "claim_boundary": {
            "v4_functional_implementation_complete_at_scoped_nine_app_level": True,
            "v4_performance_objective_closed": passed == 26,
            "author_performance_compared": False,
            "hardware_rt_core_utilization_claimed": False,
            "cross_gpu_generalization_claimed": False,
            "production_or_publication_claimed": False,
            "external_review_complete": False,
        },
        "files": {
            "plan_sha256": _file_sha(plan_path),
            "controller_receipt_sha256": _file_sha(controller_path),
            "primary_evaluation_sha256": _file_sha(primary_path),
            "packaged_recount_sha256": _file_sha(recount_path),
            "independent_raw_audit_sha256": _file_sha(audit_path),
            "stage_a_result_sha256": _file_sha(stage_a_path),
        },
    }
    result["result_sha256"] = _canonical(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--controller", type=Path, required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--recount", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage-a", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    value = close(
        plan_path=args.plan, controller_path=args.controller,
        primary_path=args.primary, recount_path=args.recount,
        audit_path=args.audit, stage_a_path=args.stage_a,
        bundle_path=args.bundle,
    )
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")


if __name__ == "__main__":
    main()
