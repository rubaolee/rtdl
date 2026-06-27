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
from .v4_operator_catalog import measured_v4_tier2_operator_catalog


V4_GOAL4632_STATUS = "goal4744_release_decision_current_frontdoor_local_gate"
V4_GOAL4632_DECISION = "authorize_v4_python_edsl_operator_pushdown_release_candidate_pending_external_review_debt"
V4_CURRENT_APP_LEVEL_DECISION_LABEL = (
    "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim"
)
V4_AUTHORIZED_RELEASE_LABEL = (
    "RTDL V4.0 Python eDSL/operator-pushdown release candidate and V2/V3 "
    "superset: complete 10-app NVIDIA RT-core V2.14/V3.0.2/V4.0 matrix, "
    "bounded material wins, and measured generic operator/workflow surfaces; "
    "broad all-benchmark speedup remains unauthorized"
)


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
    measured_surface_count = len(measured_v4_tier2_operator_catalog())

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
            status="complete_bounded_operator_release_coverage",
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md",
                "future/v4/reviews/goal4627_completion_consensus_and_review_debt_2026-06-24.md",
                "future/v4/v4_goal4635_component_union_promotion_decision_2026-06-25.md",
            ),
            note="Coverage audit shows 4 strong measured, 4 partial measured, 0 candidate, and 2 deferred rows; this passes the bounded operator release scope, not broad app coverage.",
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
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md",
                "future/v4/reviews/antigravity_v4_goal4642_final_3ai_release_authorization_review_amended_2026-06-25.md",
                "future/v4/reviews/antigravity_v4_goal4642_amendment_recheck_2026-06-25.md",
                "future/v4/reviews/codex_independent_v4_goal4642_final_authorization_review_and_amendment_recheck_2026-06-25.md",
                "future/v4/reviews/codex_main_v4_goal4642_final_release_owner_authorization_2026-06-25.md",
            ),
            note=(
                "The earlier bounded operator authorization is superseded for current "
                "user-facing truth by Goal4756: V4 is a Python eDSL/operator-pushdown "
                "release candidate and V2/V3 superset with a complete 10-app RT-core "
                "matrix, while broad all-benchmark speedup remains unauthorized."
            ),
        ),
        V4ReleaseGate(
            gate="G12_custom_predicate_early_exit_workflow",
            status=V4_CURRENT_APP_LEVEL_DECISION_LABEL,
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_2026-06-26.md",
                "future/v4/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md",
                "future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.json",
            ),
            note=(
                "Custom predicate early-exit is the V4-only workflow win: 4.633x "
                "serious-scale geomean over V2.14/V3.0.2 materialized-device fallback."
            ),
        ),
        V4ReleaseGate(
            gate="G13_public_docs_current_frontdoor_cleanup",
            status="public_v4_docs_examples_match_goal4742_current_boundary",
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4743_public_docs_current_framing_cleanup_2026-06-26.md",
                "future/v4/evidence/v4_goal4743_public_docs_current_framing_cleanup_2026-06-26.json",
                "examples/v4/custom_predicate_early_exit_planning.py",
                "docs/current_v4_status.md",
            ),
            note=(
                "Current public docs and runnable examples now describe Goal4756 truth: "
                "10 measured app rows across V2.14/V3.0.2/V4.0, V4 eDSL/operator-pushdown "
                "release candidate, and broad all-benchmark speedup forbidden."
            ),
        ),
        V4ReleaseGate(
            gate="G14_full_v4_local_gate_after_current_frontdoor_cleanup",
            status="full_v4_local_gate_passes_after_goal4743_current_frontdoor_cleanup",
            passed_for_release=True,
            evidence=(
                "future/v4/v4_goal4744_full_v4_local_gate_after_current_frontdoor_cleanup_2026-06-26.md",
                "future/v4/evidence/v4_goal4744_full_v4_local_gate_after_current_frontdoor_cleanup_2026-06-26.json",
                "tests/v4_goal4744_full_v4_local_gate_record_test.py",
            ),
            note=(
                "Goal4744 records a 554-test V4 unittest discover pass plus public examples "
                "and catalog dry-run gate after the current front-door cleanup."
            ),
        ),
    )

    release_blockers: tuple[str, ...] = (
        "external_3ai_review_debt_open_for_goal4743_goal4744_current_release_candidate",
    )
    scope_limitations = (
        "legacy_all_app_speedup_wording_not_authorized",
        "arbitrary_python_callback_not_supported",
        "raw_optix_callback_not_supported",
        "public_tier3_deferred_not_supported",
        "no_true_zero_copy_public_claim_authorized",
        "no_c_abi_embedding_or_non_python_host_scope",
    )

    return {
        "status": V4_GOAL4632_STATUS,
        "decision": V4_GOAL4632_DECISION,
        "release_authorized": False,
        "formal_release_authorized": False,
        "authorized_release_label": V4_AUTHORIZED_RELEASE_LABEL,
        "release_candidate_authorized": True,
        "performance_preview_authorized": True,
        "development_state_authorized": False,
        "bounded_operator_surface_available": True,
        "app_level_high_performance_authorized": False,
        "v4_python_edsl_release_candidate_supported": True,
        "operator_pushdown_workflow_high_performance_supported": True,
        "legacy_all_app_high_performance_supported": False,
        "current_app_level_decision_label": V4_CURRENT_APP_LEVEL_DECISION_LABEL,
        "public_wording": (
            "RTDL V4 is a Python eDSL/operator-pushdown release candidate with "
            "10 measured generic operator/workflow surfaces and a complete 10-app "
            "NVIDIA RT-core V2.14/V3.0.2/V4.0 matrix. The constrained Numba "
            "custom predicate early-exit workflow measured 4.633x serious-scale "
            "geomean versus V2.14/V3.0.2 materialized-device fallback. Goal4756 "
            "shows bounded material wins plus parity/control app rows; it does "
            "not support broad legacy all-app high-performance wording."
        ),
        "measured_surfaces_count": measured_surface_count,
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
        "scope_limitations": scope_limitations,
        "allowed_claims": (
            "RTDL V4 is a Python eDSL/operator-pushdown release candidate.",
            "The V4 front door has 10 measured generic operator/workflow surfaces.",
            "The constrained Numba custom predicate early-exit workflow measured 4.633x serious-scale geomean versus V2.14/V3.0.2 materialized-device fallback.",
            "Legacy promoted-app all-suite high-performance remains unsupported by the current app-level boundary.",
            "Torch CUDA, Numba, RTDL native, and explicitly scoped CuPy continuation measurements exist only where named.",
            "The frozen Goal4639 scorecard passed for 8 measured surfaces and 4 strong benchmark families.",
            "The public V4 documentation and example entrypoints have been cleaned for the current Goal4756 front-door boundary.",
            "The full V4 local gate passed 554 V4 tests after the current front-door cleanup.",
            "The Goal4641 clean-tree reproducibility gate passed from a committed-only clean worktree.",
            "Fixed-radius, grouped-i64, weighted-sum, component-union, AABB, aggregate-frontier, and custom predicate early-exit have bounded performance evidence.",
            "A minimum push-down recognizer routes known generic operators and fails closed otherwise.",
            "Arbitrary callbacks and raw OptiX callbacks remain unsupported.",
        ),
        "forbidden_claims": (
            "broad V4 speedup",
            "whole-application speedup",
            "all-benchmark speedup",
            "public true-zero-copy",
            "Tier-3 callback support",
            "raw OptiX callback support",
            "CuPy performance",
            "C ABI / embedding / non-Python host",
            "app-specific native kernels",
            "Barnes-Hut new V4-over-V3 speedup",
            "Spatial RayJoin speedup",
            "LibRTS paper reproduction",
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
        raise ValueError("Formal public tag must not be authorized while external review debt is open")
    if decision["formal_release_authorized"]:
        raise ValueError("Formal V4.0.0 public tag must not be authorized while external review debt is open")
    if not decision["bounded_operator_surface_available"]:
        raise ValueError("Bounded operator surface must remain available")
    if decision["app_level_high_performance_authorized"]:
        raise ValueError("App-level high-performance claim must not be authorized")
    if not decision["v4_python_edsl_release_candidate_supported"]:
        raise ValueError("Goal4720 must support the V4 Python eDSL release candidate")
    if not decision["operator_pushdown_workflow_high_performance_supported"]:
        raise ValueError("Goal4720 must retain the custom predicate workflow win")
    if decision["legacy_all_app_high_performance_supported"]:
        raise ValueError("Legacy all-app high-performance wording must remain false")
    if decision["authorized_release_label"] != V4_AUTHORIZED_RELEASE_LABEL:
        raise ValueError("Authorized V4 release label drift")
    if not decision["release_candidate_authorized"]:
        raise ValueError("Goal4720 must authorize the release candidate state")
    if not decision["performance_preview_authorized"]:
        raise ValueError("V4 release should preserve bounded performance evidence visibility")
    gate_map = {gate["gate"]: gate for gate in decision["gates"]}
    if not gate_map["G4_weighted_sum_candidate"]["passed_for_release"]:
        raise ValueError("Weighted-sum should pass after Goal4633 promotion")
    if not gate_map["G2_operator_coverage_audit"]["passed_for_release"]:
        raise ValueError("Coverage gate must pass for the bounded operator release scope")
    if not gate_map["G10_clean_tree_reproducibility"]["passed_for_release"]:
        raise ValueError("Clean-tree reproducibility should pass after Goal4641")
    if not gate_map["G11_final_release_authorization"]["passed_for_release"]:
        raise ValueError("Final release authorization must pass after Goal4642")
    if not gate_map["G12_custom_predicate_early_exit_workflow"]["passed_for_release"]:
        raise ValueError("Custom predicate early-exit workflow gate must pass")
    if not gate_map["G13_public_docs_current_frontdoor_cleanup"]["passed_for_release"]:
        raise ValueError("Current front-door public docs gate must pass")
    if not gate_map["G14_full_v4_local_gate_after_current_frontdoor_cleanup"]["passed_for_release"]:
        raise ValueError("Goal4744 full V4 local gate must pass")
    if "weighted_sum_remains_candidate_not_measured" in decision["release_blockers"]:
        raise ValueError("Weighted-sum blocker must be removed after Goal4633")
    if "goal4636c_aabb_index_gate_passed_pending_frontdoor_catalog_goal" in decision["release_blockers"]:
        raise ValueError("Goal4636C pending front-door blocker must be removed after Goal4637")
    if "goal4641_clean_tree_reproducibility_gate_not_done" in decision["release_blockers"]:
        raise ValueError("Goal4641 clean-tree blocker must be removed after clean-tree validation")
    if "external_3ai_review_debt_open_for_goal4743_goal4744_current_release_candidate" not in decision["release_blockers"]:
        raise ValueError("External review debt blocker must be retained before public tag")
    for required_limitation in (
        "legacy_all_app_speedup_wording_not_authorized",
        "arbitrary_python_callback_not_supported",
        "raw_optix_callback_not_supported",
        "public_tier3_deferred_not_supported",
        "no_true_zero_copy_public_claim_authorized",
        "no_c_abi_embedding_or_non_python_host_scope",
    ):
        if required_limitation not in decision["scope_limitations"]:
            raise ValueError(f"Missing V4 scope limitation: {required_limitation}")
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
    "V4_CURRENT_APP_LEVEL_DECISION_LABEL",
    "V4_AUTHORIZED_RELEASE_LABEL",
    "V4ReleaseGate",
    "v4_goal4632_release_decision",
    "validate_v4_goal4632_release_decision",
]
