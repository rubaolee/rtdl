from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .v4_goal4642_final_authorization_packet import validate_v4_goal4642_final_authorization_packet
from .v4_goal4643_publication_decision import validate_v4_goal4643_publication_decision
from .v4_release_decision import v4_goal4632_release_decision


V4_GOAL4644_DECISION = "activate_post_release_guardrails_and_debt_ledger"
V4_GOAL4644_STATUS = "v4_0_0_post_release_guardrails_active"


@dataclass(frozen=True)
class V4Goal4644PostReleaseGuardrails:
    status: str
    decision: str
    release_label: str
    publication_commit: str
    measured_surfaces_count: int
    candidate_surfaces_count: int
    guardrail_tests: tuple[str, ...]
    required_public_docs: tuple[str, ...]
    required_decision_records: tuple[str, ...]
    review_cadence_hours: int
    three_ai_consensus_cadence_hours: int
    external_review_status: str
    review_debt: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    next_scope: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "decision": self.decision,
            "release_label": self.release_label,
            "publication_commit": self.publication_commit,
            "measured_surfaces_count": self.measured_surfaces_count,
            "candidate_surfaces_count": self.candidate_surfaces_count,
            "guardrail_tests": self.guardrail_tests,
            "required_public_docs": self.required_public_docs,
            "required_decision_records": self.required_decision_records,
            "review_cadence_hours": self.review_cadence_hours,
            "three_ai_consensus_cadence_hours": self.three_ai_consensus_cadence_hours,
            "external_review_status": self.external_review_status,
            "review_debt": self.review_debt,
            "forbidden_claims": self.forbidden_claims,
            "next_scope": self.next_scope,
            "release_authorized": True,
            "formal_release_authorized": True,
            "release_scope_reopened": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "all_benchmark_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "tier3_callback_claim_authorized": False,
            "raw_optix_callback_claim_authorized": False,
            "cupy_performance_claim_authorized": False,
            "c_abi_or_embedding_claim_authorized": False,
            "non_python_host_claim_authorized": False,
            "app_specific_native_kernel_authorized": False,
        }


def v4_goal4644_post_release_guardrails(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    release_decision = v4_goal4632_release_decision()
    publication = validate_v4_goal4643_publication_decision(repo)
    validate_v4_goal4642_final_authorization_packet(repo)

    required_public_docs = (
        "README.md",
        "docs/current_v4_status.md",
        "docs/learn/performance_wording.md",
        "future/v4/README.md",
        "future/v4/tier2_operator_catalog.md",
        "future/v4/v4_0_scope_gate.md",
    )
    required_decision_records = (
        "future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md",
        "future/v4/v4_goal4643_publication_decision_2026-06-25.md",
        "future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md",
        "future/v4/reviews/call_for_review_v4_goal4644_post_release_guardrails_2026-06-25.md",
        "future/v4/reviews/claude_v4_goal4644_post_release_guardrails_review_2026-06-25.md",
        "future/v4/v4_goal4633_4644_completion_audit_2026-06-25.md",
        "tests/v4_goal4644_post_release_guardrails_test.py",
    )
    guardrail_tests = (
        "tests.v4_goal4644_post_release_guardrails_test",
        "tests.v4_goal4643_publication_decision_test",
        "tests.v4_frontdoor_test",
        "tests.v4_scope_gate_test",
        "tests.v4_catalog_regression_gate_test",
    )

    return V4Goal4644PostReleaseGuardrails(
        status=V4_GOAL4644_STATUS,
        decision=V4_GOAL4644_DECISION,
        release_label=publication["authorized_release_label"],
        publication_commit="c58642326f57f6326274b448caa8d75b3c7ef9de",
        measured_surfaces_count=release_decision["measured_surfaces_count"],
        candidate_surfaces_count=release_decision["candidate_surfaces_count"],
        guardrail_tests=guardrail_tests,
        required_public_docs=required_public_docs,
        required_decision_records=required_decision_records,
        review_cadence_hours=6,
        three_ai_consensus_cadence_hours=24,
        external_review_status="claude_accept_goal4644_post_release_guardrails_no_amendments",
        review_debt=(
            "Antigravity review is optional debt for Goal4644 because Claude completed the current 6h external review seat.",
            "The next Antigravity or Claude review is due after another 6h of continued V4 work or at the next major decision.",
            "No review debt expands or weakens the bounded V4.0.0 release label.",
        ),
        forbidden_claims=release_decision["forbidden_claims"],
        next_scope=(
            "V4.x may extend partner coverage, Tier-3 callbacks, CuPy, C ABI, or non-Python hosts only through new goals.",
            "V4.0.0 remains limited to documented measured generic RT-core operator surfaces.",
        ),
    ).as_dict()


def validate_v4_goal4644_post_release_guardrails(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    decision = v4_goal4644_post_release_guardrails(repo)
    if decision["status"] != V4_GOAL4644_STATUS:
        raise ValueError("Goal4644 status drift")
    if decision["decision"] != V4_GOAL4644_DECISION:
        raise ValueError("Goal4644 decision drift")
    if not decision["release_authorized"] or not decision["formal_release_authorized"]:
        raise ValueError("Goal4644 must inherit the already-authorized formal V4 release")
    if decision["release_scope_reopened"]:
        raise ValueError("Goal4644 must not reopen V4.0 release scope")
    if decision["measured_surfaces_count"] != 8:
        raise ValueError("Goal4644 measured surface count drift")
    if decision["candidate_surfaces_count"] != 0:
        raise ValueError("Goal4644 must not count candidates as release surfaces")
    for path in (*decision["required_public_docs"], *decision["required_decision_records"]):
        if not (repo / path).exists():
            raise ValueError(f"Goal4644 missing required record: {path}")
    for claim in (
        "broad V4 speedup",
        "whole-application speedup",
        "all-benchmark speedup",
        "public true-zero-copy",
        "Tier-3 callback support",
        "raw OptiX callback support",
        "CuPy performance",
        "C ABI / embedding / non-Python host",
        "app-specific native kernels",
        "Barnes-Hut covered by V4.0",
        "Spatial RayJoin covered by V4.0",
        "LibRTS paper reproduction",
    ):
        if claim not in decision["forbidden_claims"]:
            raise ValueError(f"Goal4644 missing forbidden claim: {claim}")
    for flag in (
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "all_benchmark_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "raw_optix_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "non_python_host_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4644 must not authorize {flag}")
    if decision["review_cadence_hours"] != 6:
        raise ValueError("Goal4644 must preserve the 6h external-review cadence")
    if decision["three_ai_consensus_cadence_hours"] != 24:
        raise ValueError("Goal4644 must preserve the 24h 3-AI consensus cadence")
    if decision["external_review_status"] != "claude_accept_goal4644_post_release_guardrails_no_amendments":
        raise ValueError("Goal4644 external review status drift")
    return decision


__all__ = [
    "V4_GOAL4644_DECISION",
    "V4_GOAL4644_STATUS",
    "V4Goal4644PostReleaseGuardrails",
    "v4_goal4644_post_release_guardrails",
    "validate_v4_goal4644_post_release_guardrails",
]
