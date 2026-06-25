from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v4_coverage_audit import v4_goal4627_coverage_summary
from .v4_second_gate_scorecard import v4_goal4628_second_gate_scorecard
from .v4_tier3_spike_decision import v4_goal4631_tier3_spike_decision
from .v4_goal4635_component_union_promotion_decision import v4_goal4635_component_union_promotion_decision
from .v4_goal4636_aabb_index_decision import v4_goal4636_aabb_index_decision
from .v4_goal4636_grouped_any_hit_decision import v4_goal4636_grouped_any_hit_decision
from .v4_goal4636_threshold_summary_decision import v4_goal4636_threshold_summary_decision
from .v4_goal4637_aabb_frontdoor_catalog_decision import v4_goal4637_aabb_frontdoor_catalog_decision
from .v4_goal4638_catalog_regression_decision import v4_goal4638_catalog_regression_decision
from .v4_goal4638_formal_scorecard_freeze import v4_goal4638_formal_scorecard_freeze
from .v4_goal4639_release_scorecard_decision import v4_goal4639_release_scorecard_decision
from .v4_goal4640_public_docs_cleanup_decision import v4_goal4640_public_docs_cleanup_decision
from .v4_goal4641_clean_tree_reproducibility_decision import v4_goal4641_clean_tree_reproducibility_decision
from .v4_weighted_sum_promotion_decision import v4_goal4633_weighted_sum_promotion_decision


V4_GOAL4632_STATUS = "goal4632_final_decision_goal4641_clean_tree_passed_not_release"
V4_GOAL4632_DECISION = "goal4641_clean_tree_passed_pending_3ai_not_release"


@dataclass(frozen=True)
class V4ReleaseGate:
    gate: str
    status: str
    passed_for_release: bool
    evidence: tuple[str, ...]
    note: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "status": self.status,
            "passed_for_release": self.passed_for_release,
            "evidence": self.evidence,
            "note": self.note,
        }


def v4_goal4632_release_decision() -> dict[str, Any]:
    coverage = v4_goal4627_coverage_summary()
    second_gate = v4_goal4628_second_gate_scorecard()
    weighted_sum_promotion = v4_goal4633_weighted_sum_promotion_decision()
    component_union_promotion = v4_goal4635_component_union_promotion_decision()
    threshold_summary_decision = v4_goal4636_threshold_summary_decision()
    grouped_any_hit_decision = v4_goal4636_grouped_any_hit_decision()
    aabb_index_decision = v4_goal4636_aabb_index_decision()
    aabb_frontdoor_decision = v4_goal4637_aabb_frontdoor_catalog_decision()
    catalog_regression_decision = v4_goal4638_catalog_regression_decision()
    formal_scorecard_freeze = v4_goal4638_formal_scorecard_freeze()
    release_scorecard_decision = v4_goal4639_release_scorecard_decision()
    docs_cleanup_decision = v4_goal4640_public_docs_cleanup_decision()
    clean_tree_decision = v4_goal4641_clean_tree_reproducibility_decision()
    tier3 = v4_goal4631_tier3_spike_decision()

    gates = (
        V4ReleaseGate(
            gate="G1_fixed_radius_anchor",
            status="pass_bounded_one_primitive",
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4626_section8_release_scorecard_protocol_2026-06-24.md",
                "future/v4/reviews/goal4626_completion_consensus_and_review_debt_2026-06-24.md",
            ),
            note="Fixed-radius has bounded Torch CUDA device-array evidence, not broad release proof.",
        ),
        V4ReleaseGate(
            gate="G2_operator_coverage_audit",
            status="complete_limited_coverage",
            passed_for_release=False,
            evidence=(
                "future/v4/v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md",
                "future/v4/reviews/goal4627_completion_consensus_and_review_debt_2026-06-24.md",
                "future/v4/v4_goal4635_component_union_promotion_decision_2026-06-25.md",
            ),
            note="Coverage audit shows 4 strong measured, 4 partial measured, 0 candidate, and 2 deferred rows; this is still not broad app coverage.",
        ),
        V4ReleaseGate(
            gate="G3_second_tier2_same_contract_gate",
            status="pass_grouped_i64_second_gate",
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4628_second_tier2_same_contract_gate_2026-06-24.md",
                "future/v4/reviews/goal4628_completion_consensus_2026-06-24.md",
            ),
            note=f"Grouped-i64 passed the second gate with min same-contract ratio {second_gate['min_same_contract_ratio']:.3f}x.",
        ),
        V4ReleaseGate(
            gate="G4_weighted_sum_candidate",
            status=weighted_sum_promotion["decision"],
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md",
                "future/v4/reviews/goal4629_completion_consensus_and_review_debt_2026-06-24.md",
                "future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md",
                "future/v4/reviews/goal4633_completion_consensus_and_review_debt_2026-06-25.md",
            ),
            note=(
                "Weighted-sum passed Goal4633 as measured Torch CUDA comparable-route surface; "
                "this does not authorize whole-app or broad V4 speedup wording."
            ),
        ),
        V4ReleaseGate(
            gate="G5_pushdown_recognizer",
            status="pass_minimum_slice",
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4630_pushdown_recognizer_minimum_slice_2026-06-24.md",
                "future/v4/reviews/goal4630_completion_consensus_and_review_debt_2026-06-24.md",
            ),
            note="Minimum recognizer routes measured/candidate generic operators and fails closed for unsupported logic.",
        ),
        V4ReleaseGate(
            gate="G6_tier3_boundary",
            status=tier3["decision"],
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4631_tier3_spike_execution_decision_2026-06-24.md",
                "future/v4/reviews/goal4631_completion_consensus_and_review_debt_2026-06-24.md",
            ),
            note="Tier-3 is explicitly out of the V4.0 release dependency path.",
        ),
        V4ReleaseGate(
            gate="G7_aabb_index_frontdoor_catalog",
            status=aabb_frontdoor_decision["decision"],
            passed_for_release=True,
            evidence=tuple(aabb_frontdoor_decision["evidence"]),
            note=(
                "AABB all-ops passed a material same-RT-hardware POD gate and now has "
                "a measured V4 front-door/catalog surface. This remains operator-level evidence only."
            ),
        ),
        V4ReleaseGate(
            gate="G8_formal_release_scorecard_freeze",
            status=formal_scorecard_freeze["decision"],
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md",
                "future/v4/reviews/goal4638_formal_release_scorecard_freeze_review_record_2026-06-25.md",
                *tuple(catalog_regression_decision["evidence"]),
            ),
            note=(
                "The controlling Goal4638 artifact is the formal release scorecard freeze. "
                "The AABB catalog GPU gate is supporting evidence only; Claude closed the "
                "required amendment, with Antigravity recorded as review debt."
            ),
        ),
        V4ReleaseGate(
            gate="G9_serious_release_scorecard_pod_gate",
            status=release_scorecard_decision["decision"],
            passed_for_release=True,
            evidence=tuple(release_scorecard_decision["evidence"]),
            note=(
                "Goal4639 passed the frozen serious scorecard: 8/8 measured surfaces and "
                "4/4 strong families passed. This is still not final release authorization."
            ),
        ),
        V4ReleaseGate(
            gate="G10_clean_tree_reproducibility",
            status=clean_tree_decision["decision"],
            passed_for_release=True,
            evidence=tuple(clean_tree_decision["evidence"]),
            note=(
                "Goal4641 validated committed-only V4 tests, catalog dry-run, and quickstart "
                "from a clean worktree with clean status before and after."
            ),
        ),
        V4ReleaseGate(
            gate="G11_final_release_authorization",
            status=V4_GOAL4632_DECISION,
            passed_for_release=False,
            evidence=("future/v4/v4_goal4632_final_release_decision_2026-06-24.md",),
            note="Final V4 release still requires 3-AI authorization.",
        ),
    )

    release_blockers = (
        "tier3_deferred_not_supported",
        "external_review_debt_remains_for_antigravity_goal4633_backfill",
        "external_review_debt_remains_for_goal4635_component_union_completion",
        "external_review_debt_remains_for_goal4637_aabb_frontdoor_catalog_completion",
        "external_review_debt_antigravity_goal4638_formal_scorecard_freeze",
        "external_review_debt_antigravity_goal4639_serious_release_scorecard",
        "external_review_debt_goal4640_public_docs_cleanup",
        "external_review_debt_goal4641_clean_tree_reproducibility",
        "goal4642_final_3ai_release_authorization_not_done",
        "whole_app_speedup_wording_still_requires_final_3ai_authorization",
        "cupy_performance_unmeasured",
        "no_true_zero_copy_public_claim_authorized",
        "no_c_abi_embedding_or_non_python_host_scope",
    )

    return {
        "status": V4_GOAL4632_STATUS,
        "decision": V4_GOAL4632_DECISION,
        "release_authorized": False,
        "release_candidate_authorized": False,
        "performance_preview_authorized": True,
        "development_state_authorized": True,
        "public_wording": "V4 high-performance scorecard passed for documented generic RT-core operator surfaces; final release authorization pending.",
        "measured_surfaces_count": 8,
        "candidate_surfaces_count": 0,
        "component_union_promotion": component_union_promotion,
        "threshold_summary_decision": threshold_summary_decision,
        "grouped_any_hit_decision": grouped_any_hit_decision,
        "aabb_index_decision": aabb_index_decision,
        "aabb_frontdoor_decision": aabb_frontdoor_decision,
        "catalog_regression_supporting_evidence": catalog_regression_decision,
        "formal_scorecard_freeze": formal_scorecard_freeze,
        "release_scorecard_decision": release_scorecard_decision,
        "public_docs_cleanup_decision": docs_cleanup_decision,
        "clean_tree_reproducibility_decision": clean_tree_decision,
        "coverage_summary": coverage,
        "gates": tuple(gate.as_dict() for gate in gates),
        "release_blockers": release_blockers,
        "allowed_claims": (
            "Torch CUDA measured Tier-2 device-array surfaces exist for the documented measured operators.",
            "The frozen Goal4639 scorecard passed for 8 measured surfaces and 4 strong benchmark families.",
            "The public V4 documentation and example entrypoints have been cleaned for Goal4640.",
            "The Goal4641 clean-tree reproducibility gate passed from a committed-only clean worktree.",
            "Fixed-radius, grouped-i64, weighted-sum, component-union, and AABB have bounded operator-level performance evidence.",
            "A minimum push-down recognizer routes known generic operators and fails closed otherwise.",
            "Tier-3 is spike-only/deferred and not V4.0 support.",
        ),
        "forbidden_claims": (
            "V4 release",
            "V4 release candidate",
            "broad V4 speedup",
            "whole-application speedup",
            "all-benchmark speedup",
            "public true-zero-copy",
            "Tier-3 callback support",
            "raw OptiX callback support",
            "CuPy performance",
            "C ABI / embedding / non-Python host",
            "app-specific native kernels",
        ),
        "release_claim_authorized": False,
        "broad_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "measured_catalog_promotion_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "non_python_host_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4632_release_decision() -> dict[str, Any]:
    decision = v4_goal4632_release_decision()
    if decision["decision"] != V4_GOAL4632_DECISION:
        raise ValueError("Goal4632 decision drift")
    if decision["release_authorized"]:
        raise ValueError("Goal4632 must not authorize V4 release")
    if decision["release_candidate_authorized"]:
        raise ValueError("Goal4632 must not authorize V4 release candidate")
    if not decision["performance_preview_authorized"]:
        raise ValueError("Goal4632 should preserve bounded performance-preview wording")
    gate_map = {gate["gate"]: gate for gate in decision["gates"]}
    if not gate_map["G4_weighted_sum_candidate"]["passed_for_release"]:
        raise ValueError("Weighted-sum should pass after Goal4633 promotion")
    if gate_map["G2_operator_coverage_audit"]["passed_for_release"]:
        raise ValueError("Limited coverage audit must not pass broad release by itself")
    if not gate_map["G10_clean_tree_reproducibility"]["passed_for_release"]:
        raise ValueError("Clean-tree reproducibility should pass after Goal4641")
    if gate_map["G11_final_release_authorization"]["passed_for_release"]:
        raise ValueError("Final release authorization must not pass before Goal4642")
    if "weighted_sum_remains_candidate_not_measured" in decision["release_blockers"]:
        raise ValueError("Weighted-sum blocker must be removed after Goal4633")
    if "whole_app_speedup_wording_still_requires_final_3ai_authorization" not in decision["release_blockers"]:
        raise ValueError("Whole-app wording final-authorization blocker must remain visible")
    if "goal4636c_aabb_index_gate_passed_pending_frontdoor_catalog_goal" in decision["release_blockers"]:
        raise ValueError("Goal4636C pending front-door blocker must be removed after Goal4637")
    if "external_review_debt_remains_for_goal4637_aabb_frontdoor_catalog_completion" not in decision["release_blockers"]:
        raise ValueError("Goal4637 review-debt blocker must remain visible")
    if "external_review_debt_antigravity_goal4638_formal_scorecard_freeze" not in decision["release_blockers"]:
        raise ValueError("Goal4638 Antigravity review-debt blocker must remain visible")
    if "external_review_debt_antigravity_goal4639_serious_release_scorecard" not in decision["release_blockers"]:
        raise ValueError("Goal4639 Antigravity review-debt blocker must remain visible")
    if "goal4641_clean_tree_reproducibility_gate_not_done" in decision["release_blockers"]:
        raise ValueError("Goal4641 clean-tree blocker must be removed after clean-tree validation")
    if "external_review_debt_goal4641_clean_tree_reproducibility" not in decision["release_blockers"]:
        raise ValueError("Goal4641 review-debt blocker must remain visible")
    if "goal4642_final_3ai_release_authorization_not_done" not in decision["release_blockers"]:
        raise ValueError("Final 3-AI release authorization blocker must remain visible")
    for flag in (
        "release_claim_authorized",
        "broad_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "all_benchmark_speedup_claim_authorized",
        "measured_catalog_promotion_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "raw_optix_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "non_python_host_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4632 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4632_STATUS",
    "V4_GOAL4632_DECISION",
    "V4ReleaseGate",
    "v4_goal4632_release_decision",
    "validate_v4_goal4632_release_decision",
]
