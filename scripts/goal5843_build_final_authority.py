#!/usr/bin/env python3
"""Build or verify Goal5843's final internal authority."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from experiments.goal5843_post_r1_baseline.contracts import (
    BOUND_ARTIFACTS_SCHEMA,
    EXECUTION_AUTHORITY_SCHEMA,
    FINAL_AUTHORITY_SCHEMA,
    PREREGISTRATION_PATH,
    RECOUNT_SCHEMA,
    digest,
    load_preregistration,
    sha256_file,
)
from experiments.goal5843_post_r1_baseline.runtime import create_json


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "history/internal_docs/goal5843_post_r1_fair_baseline_20260904"
AUTHORITY_PATH = EVIDENCE / "GOAL5843_FINAL_INTERNAL_AUTHORITY.json"


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def verify_seal(value: dict[str, object], field: str, label: str) -> None:
    observed = value.get(field)
    unsealed = dict(value)
    unsealed.pop(field, None)
    if not isinstance(observed, str) or digest(unsealed) != observed:
        raise RuntimeError(f"{label} seal mismatch")


def build() -> dict[str, object]:
    prereg_path = ROOT / PREREGISTRATION_PATH
    prereg = load_preregistration(prereg_path, ROOT, verify_files=True)
    pod = read_json(EVIDENCE / "POD_RECOUNT.json")
    local = read_json(EVIDENCE / "LOCAL_RECOUNT.json")
    if pod != local:
        raise RuntimeError("pod and local independent recounts differ")
    verify_seal(pod, "recount_sha256", "independent recount")
    if pod.get("schema") != RECOUNT_SCHEMA:
        raise RuntimeError("recount schema mismatch")
    if pod.get("preregistration_sha256") != prereg["preregistration_sha256"]:
        raise RuntimeError("recount preregistration mismatch")
    execution = read_json(EVIDENCE / "EXECUTION_AUTHORITY.json")
    verify_seal(execution, "authority_sha256", "execution authority")
    if (
        execution.get("schema") != EXECUTION_AUTHORITY_SCHEMA
        or execution.get("authority_sha256") != pod["execution_authority_sha256"]
    ):
        raise RuntimeError("execution authority differs from independent recount")
    transaction = read_json(EVIDENCE / "TRANSACTION_STATUS.json")
    expected_stages = [
        "00_prepare_formal_leaf_cache",
        "01_build_independent_oracle_witness",
        "02_bind_execution_authority",
        "03_preserve_bound_artifacts",
        "04_formal_worker_zero_and_baseline",
        "05_independent_pod_recount",
    ]
    if (
        transaction.get("status")
        != "PASS__FORMAL_TRANSACTION_AND_POD_RECOUNT_COMPLETE"
        or transaction.get("stage_count") != len(expected_stages)
        or [row.get("stage") for row in transaction.get("stages", [])]
        != expected_stages
        or any(
            row.get("returncode") != 0 or row.get("retry_permitted") is not False
            for row in transaction.get("stages", [])
        )
        or transaction.get("worker_zero_reached") is not True
        or transaction.get("post_worker_zero_retry_used") is not False
        or transaction.get("post_worker_zero_retry_permitted") is not False
        or transaction.get("all_adverse_rows_retained") is not True
        or transaction.get("failure_stage") is not None
    ):
        raise RuntimeError("formal transaction status is not a no-retry pass")
    custody = read_json(EVIDENCE / "BOUND_ARTIFACTS.json")
    verify_seal(custody, "custody_sha256", "bound-artifact custody")
    if (
        custody.get("schema") != BOUND_ARTIFACTS_SCHEMA
        or custody.get("execution_authority_sha256") != execution["authority_sha256"]
        or custody.get("source_commit") != execution["source_commit"]
        or custody.get("artifact_count") != len(custody.get("artifacts", []))
    ):
        raise RuntimeError("bound-artifact custody differs from execution authority")
    archive_verification = read_json(EVIDENCE / "ARCHIVE_VERIFICATION.json")
    verify_seal(
        archive_verification, "verification_sha256", "downloaded archive verification"
    )
    if (
        archive_verification.get("schema")
        != "rtdl.goal5843.downloaded_archive_verification.v1"
        or archive_verification.get("archive_sha256")
        != sha256_file(EVIDENCE / "FORMAL_TRANSACTION.tar.gz")
        or archive_verification.get("source_commit") != execution["source_commit"]
        or archive_verification.get("execution_authority_sha256")
        != execution["authority_sha256"]
        or archive_verification.get("pod_local_recount_byte_identical") is not True
        or archive_verification.get("public_performance_claim_authorized") is not False
        or archive_verification.get("manuscript_performance_claim_authorized") is not False
    ):
        raise RuntimeError("downloaded archive verification contract mismatch")
    source_commit = str(pod["source_commit"])
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source_commit, "HEAD"],
        cwd=ROOT,
        check=False,
    )
    if ancestor.returncode != 0:
        raise RuntimeError("formal source commit is not an ancestor of current HEAD")
    evidence_names = (
        "PREREGISTRATION.json",
        "DESIGN.md",
        "PRE_EXECUTION_INTERNAL_HOSTILE_SELF_REVIEW.md",
        "FORMAL_TRANSACTION.tar.gz",
        "CACHE_PREPARATION.json",
        "INDEPENDENT_ORACLE_WITNESS.json",
        "EXECUTION_AUTHORITY.json",
        "BOUND_ARTIFACTS.json",
        "TRANSACTION_STATUS.json",
        "POD_RECOUNT.json",
        "LOCAL_RECOUNT.json",
        "ARCHIVE_VERIFICATION.json",
        "FINAL_TECHNICAL_REPORT.md",
        "FINAL_INTERNAL_HOSTILE_SELF_REVIEW.md",
    )
    evidence = []
    for name in evidence_names:
        path = EVIDENCE / name
        if not path.is_file():
            raise RuntimeError(f"Goal5843 evidence missing: {name}")
        evidence.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    result: dict[str, object] = {
        "schema": FINAL_AUTHORITY_SCHEMA,
        "status": (
            "PASS__GOAL5843_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING"
        ),
        "formal_source_commit": source_commit,
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": pod["execution_authority_sha256"],
        "controller_result_sha256": pod["controller_result_sha256"],
        "recount_sha256": pod["recount_sha256"],
        "hardware": pod["hardware"],
        "counts": {
            "composites": pod["composite_count"],
            "subworker_receipts": pod["subworker_receipt_count"],
            "rtdl_triangle_receipt_gate_passes": pod[
                "rtdl_triangle_receipt_gate_pass_count"
            ],
            "bound_artifacts": custody["artifact_count"],
            "external_reviews": 0,
        },
        "results": pod["task_summaries"],
        "completion": {
            "fresh_post_r1_three_arm_transaction_complete": True,
            "same_input_and_public_output_exact": True,
            "all_preregistered_adverse_rows_retained": True,
            "independent_pod_recount_complete": True,
            "independent_local_recount_byte_identical": True,
            "safe_downloaded_archive_verification_complete": True,
            "exact_bound_executable_and_provider_bytes_preserved": True,
            "rtdl_triangle_scalar_receipt_gate_complete": True,
            "completion_depends_on_performance_threshold": False,
            "internal_hostile_self_review_complete": True,
        },
        "claim_boundary": {
            "internal_technical_evidence_only": True,
            "public_performance_claim_authorized": False,
            "manuscript_performance_claim_authorized": False,
            "external_review_or_consensus": False,
            "hardware_independent_claim": False,
            "general_language_performance_claim": False,
            "hidden_implementation_work_claimed_identical": False,
            "relation_relabelled_as_scalar_fast_path": False,
        },
        "evidence": evidence,
        "evidence_manifest_sha256": digest(evidence),
    }
    result["authority_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=AUTHORITY_PATH)
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.verify_stored:
        if read_json(args.output) != result:
            raise RuntimeError("stored Goal5843 final authority differs from rebuild")
    else:
        create_json(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
