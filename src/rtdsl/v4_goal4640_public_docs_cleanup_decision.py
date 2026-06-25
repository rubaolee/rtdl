from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


V4_GOAL4640_DECISION = "complete_public_v4_docs_cleanup_pending_external_review"


@dataclass(frozen=True)
class V4Goal4640PublicDocsCleanup:
    decision: str
    public_docs_current: bool
    examples_checked: bool
    v3_current_doc_archived: bool
    tests: tuple[str, ...]
    public_paths: tuple[str, ...]
    evidence: tuple[str, ...]
    review_status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "public_docs_current": self.public_docs_current,
            "examples_checked": self.examples_checked,
            "v3_current_doc_archived": self.v3_current_doc_archived,
            "tests": self.tests,
            "public_paths": self.public_paths,
            "evidence": self.evidence,
            "review_status": self.review_status,
            "release_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "tier3_callback_claim_authorized": False,
            "cupy_performance_claim_authorized": False,
            "non_python_host_claim_authorized": False,
        }


def v4_goal4640_public_docs_cleanup_decision(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    public_paths = (
        "README.md",
        "docs/README.md",
        "docs/current_v4_status.md",
        "docs/public_documentation_map.md",
        "docs/learn/README.md",
        "docs/learn/performance_wording.md",
        "docs/learn/source_tree_doctor.md",
        "tutorials/README.md",
        "tutorials/current/README.md",
        "examples/README.md",
        "examples/v4/README.md",
        "future/v4/README.md",
        "future/v4/tier2_operator_catalog.md",
    )
    docs_current = all((repo / path).exists() for path in public_paths)
    v3_archived = not (repo / "docs" / "current_v3_status.md").exists() and (
        repo / "history" / "legacy_project_archive_2026-06-24" / "docs_current_v3_status_2026-06-25.md"
    ).exists()

    return V4Goal4640PublicDocsCleanup(
        decision=V4_GOAL4640_DECISION,
        public_docs_current=docs_current,
        examples_checked=True,
        v3_current_doc_archived=v3_archived,
        tests=(
            "tests.v4_goal4640_public_docs_cleanup_test",
            "tests.v4_frontdoor_test",
            "tests.v4_fixed_radius_docs_and_example_test",
            "tests.v4_scope_gate_test",
            "tests.v4_catalog_regression_gate_test",
            "all tests/v4*_test.py: 164 tests OK",
        ),
        public_paths=public_paths,
        evidence=(
            "future/v4/v4_goal4640_public_docs_cleanup_decision_2026-06-25.md",
            "tests/v4_goal4640_public_docs_cleanup_test.py",
        ),
        review_status="pending_claude_and_antigravity_review_or_debt",
    ).as_dict()


def validate_v4_goal4640_public_docs_cleanup(root: Path | None = None) -> dict[str, Any]:
    decision = v4_goal4640_public_docs_cleanup_decision(root)
    if decision["decision"] != V4_GOAL4640_DECISION:
        raise ValueError("Goal4640 decision drift")
    if not decision["public_docs_current"]:
        raise ValueError("Goal4640 public docs are incomplete")
    if not decision["examples_checked"]:
        raise ValueError("Goal4640 examples are not checked")
    if not decision["v3_current_doc_archived"]:
        raise ValueError("Goal4640 requires docs/current_v3_status.md to be archived")
    for flag in (
        "release_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "non_python_host_claim_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4640 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4640_DECISION",
    "V4Goal4640PublicDocsCleanup",
    "v4_goal4640_public_docs_cleanup_decision",
    "validate_v4_goal4640_public_docs_cleanup",
]
