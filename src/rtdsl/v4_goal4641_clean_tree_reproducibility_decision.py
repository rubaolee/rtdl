from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


V4_GOAL4641_DECISION = "complete_clean_tree_reproducibility_gate_pending_external_review"


@dataclass(frozen=True)
class V4Goal4641CleanTreeReproducibility:
    decision: str
    clean_worktree_path: str
    validated_commit: str
    final_revalidation_commit: str
    clean_status_before: bool
    clean_status_after: bool
    full_v4_tests_passed: bool
    catalog_dry_run_passed: bool
    quickstart_passed: bool
    tests: tuple[str, ...]
    evidence: tuple[str, ...]
    review_status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "clean_worktree_path": self.clean_worktree_path,
            "validated_commit": self.validated_commit,
            "final_revalidation_commit": self.final_revalidation_commit,
            "clean_status_before": self.clean_status_before,
            "clean_status_after": self.clean_status_after,
            "full_v4_tests_passed": self.full_v4_tests_passed,
            "catalog_dry_run_passed": self.catalog_dry_run_passed,
            "quickstart_passed": self.quickstart_passed,
            "tests": self.tests,
            "evidence": self.evidence,
            "review_status": self.review_status,
            "release_authorized": False,
            "release_candidate_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "tier3_callback_claim_authorized": False,
            "cupy_performance_claim_authorized": False,
            "non_python_host_claim_authorized": False,
        }


def v4_goal4641_clean_tree_reproducibility_decision(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    evidence = (
        "tools/_archive/future/v4/v4_goal4641_clean_tree_reproducibility_gate_2026-06-25.md",
        "tests/v4_goal4641_clean_tree_reproducibility_test.py",
    )
    evidence_exists = all((repo / path).exists() for path in evidence)

    return V4Goal4641CleanTreeReproducibility(
        decision=V4_GOAL4641_DECISION,
        clean_worktree_path="C:/Users/Lestat/Desktop/work/rtdl_v4_goal4641_clean_tree_check",
        validated_commit="35d04dbf0b1734e7c1fc323c366a046de51edee8",
        final_revalidation_commit="884aeda8084d4c84bae8ec858f4b7436461ee783",
        clean_status_before=True,
        clean_status_after=True,
        full_v4_tests_passed=True,
        catalog_dry_run_passed=True,
        quickstart_passed=True,
        tests=(
            "clean worktree: py -3 -m unittest tests.v4*_test.py",
            "clean worktree: py -3 scripts/v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16",
            "clean worktree: py -3 examples/tutorial_programs/v4_frontdoor_quickstart.py",
            "tests.v4_goal4641_clean_tree_reproducibility_test",
        ),
        evidence=evidence if evidence_exists else (),
        review_status="pending_claude_and_antigravity_review_or_debt",
    ).as_dict()


def validate_v4_goal4641_clean_tree_reproducibility(root: Path | None = None) -> dict[str, Any]:
    decision = v4_goal4641_clean_tree_reproducibility_decision(root)
    if decision["decision"] != V4_GOAL4641_DECISION:
        raise ValueError("Goal4641 decision drift")
    if not decision["clean_status_before"]:
        raise ValueError("Goal4641 clean worktree was not clean before validation")
    if not decision["clean_status_after"]:
        raise ValueError("Goal4641 clean worktree was not clean after validation")
    if not decision["full_v4_tests_passed"]:
        raise ValueError("Goal4641 full V4 tests did not pass")
    if not decision["catalog_dry_run_passed"]:
        raise ValueError("Goal4641 catalog dry-run did not pass")
    if not decision["quickstart_passed"]:
        raise ValueError("Goal4641 quickstart did not pass")
    if not decision["evidence"]:
        raise ValueError("Goal4641 evidence files are missing")
    for flag in (
        "release_authorized",
        "release_candidate_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "non_python_host_claim_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4641 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4641_DECISION",
    "V4Goal4641CleanTreeReproducibility",
    "v4_goal4641_clean_tree_reproducibility_decision",
    "validate_v4_goal4641_clean_tree_reproducibility",
]
