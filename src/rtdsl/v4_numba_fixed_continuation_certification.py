from __future__ import annotations

from typing import Any

from .v4_goal4635_component_union_promotion_decision import V4_GOAL4635_EVIDENCE
from .v4_goal4635_component_union_promotion_decision import (
    validate_v4_goal4635_component_union_promotion_decision,
)
from .v4_operator_catalog import plan_v4_operator_request
from .v4_partner_promotion_contract import v4_partner_promotion_candidate_allowed
from .v4_partner_promotion_contract import v4_partner_promotion_contract


V4_GOAL4650_NUMBA_FIXED_CERTIFICATION_STATUS = (
    "goal4650_fixed_numba_continuation_certification_gate"
)
V4_GOAL4650_NUMBA_FIXED_CANDIDATE_ID = "numba_component_union_current_v4_surface"


def v4_goal4650_numba_fixed_certification() -> dict[str, Any]:
    """Return the Goal4650 fixed-Numba certification record.

    Goal4650 promotes only the already measured component-union continuation
    from Goal4635 into the V4 partner-certification chain. It deliberately does
    not broaden V4.0 into arbitrary Numba callback support.
    """

    decision = validate_v4_goal4635_component_union_promotion_decision()
    contract = v4_partner_promotion_contract("numba", fixed=True)
    gate = decision["same_contract_gate"]
    plan = plan_v4_operator_request("fixed_radius_graph_component_union", partner="numba")

    return {
        "status": V4_GOAL4650_NUMBA_FIXED_CERTIFICATION_STATUS,
        "source_goal": "Goal4635",
        "source_decision": decision["decision"],
        "candidate_id": V4_GOAL4650_NUMBA_FIXED_CANDIDATE_ID,
        "candidate_allowed_by_goal4648_contract": v4_partner_promotion_candidate_allowed(
            V4_GOAL4650_NUMBA_FIXED_CANDIDATE_ID,
            partner="numba",
        ),
        "partner": "numba",
        "contract_class": contract["contract_class"],
        "contract_status": contract["status"],
        "operator": decision["operator"],
        "api_surface": decision["api_surface"],
        "generic_primitive": decision["generic_primitive"],
        "target_coverage_row": decision["target_coverage_row"],
        "continuation_class": decision["continuation_class"],
        "planner_status": plan.status,
        "planner_tier": plan.tier,
        "planner_api_surface": plan.api_surface,
        "measured_partner": plan.measured_partner,
        "measured_partners": decision["measured_partners"],
        "declared_unmeasured_partners": decision["declared_unmeasured_partners"],
        "fixed_operator_only": contract["fixed_operator_only"],
        "arbitrary_callback_supported": contract["arbitrary_callback_supported"],
        "accepted_signatures": contract["accepted_signatures"],
        "compile_cache_timing_boundary": contract["compile_cache_timing_boundary"],
        "telemetry_required": contract["telemetry_required"],
        "validated_scope": decision["validated_scope"],
        "certification_gates": {
            "status": gate["status"],
            "failed_checks": gate["failed_checks"],
            "correctness_parity_required": contract["correctness_parity_required"],
            "correctness_parity_passed": gate["all_variant_canonical_component_signatures_match"],
            "legacy_no_regression": gate["legacy_no_regression"],
            "component_signature_shortcut_blocked": gate["component_signature_shortcut_blocked"],
            "runner_vs_embree_hot_speedup": gate["runner_vs_embree_hot_speedup"],
            "runner_vs_embree_wall_speedup": gate["runner_vs_embree_wall_speedup"],
            "runner_vs_legacy_hot_speedup": gate["runner_vs_legacy_hot_speedup"],
            "runner_vs_legacy_wall_speedup": gate["runner_vs_legacy_wall_speedup"],
            "runner_vs_embree_hot_floor": gate["runner_vs_embree_hot_floor"],
            "runner_vs_embree_wall_floor": gate["runner_vs_embree_wall_floor"],
            "runner_vs_legacy_wall_floor": gate["runner_vs_legacy_wall_floor"],
            "representative_speedup_floor": contract["representative_speedup_floor"],
            "partner_parity_floor": contract["partner_parity_floor"],
            "host_materialization_in_hot_path": False,
        },
        "coverage_effect": decision["coverage_effect"],
        "evidence": V4_GOAL4635_EVIDENCE,
        "claim_boundaries": {
            "partner_migration_counts_as_v4_speed_win": False,
            "partner_parity_counts_as_v4_speed_win": False,
            "arbitrary_numba_callback_claim_authorized": False,
            "tier3_callback_claim_authorized": False,
            "raw_optix_callback_claim_authorized": False,
            "cupy_performance_claim_authorized": False,
            "release_claim_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "all_benchmark_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "c_abi_or_embedding_claim_authorized": False,
            "non_python_host_claim_authorized": False,
            "app_specific_native_kernel_authorized": False,
        },
    }


def validate_v4_goal4650_numba_fixed_certification() -> dict[str, Any]:
    """Validate the Goal4650 fixed-Numba certification record."""

    record = v4_goal4650_numba_fixed_certification()
    if record["status"] != V4_GOAL4650_NUMBA_FIXED_CERTIFICATION_STATUS:
        raise ValueError("Goal4650 status drift")
    if not record["candidate_allowed_by_goal4648_contract"]:
        raise ValueError("Goal4650 candidate is not allowed by the Goal4648 contract")
    if record["partner"] != "numba" or record["measured_partners"] != ("numba",):
        raise ValueError("Goal4650 is Numba-fixed only")
    if not record["fixed_operator_only"]:
        raise ValueError("Goal4650 requires fixed-operator-only certification")
    if record["arbitrary_callback_supported"]:
        raise ValueError("Goal4650 must not authorize arbitrary callbacks")
    if record["planner_status"] != "tier2_measured_ready" or not record["measured_partner"]:
        raise ValueError("Goal4650 planner route must be measured and ready for Numba")

    gates = record["certification_gates"]
    if gates["status"] != "pass" or gates["failed_checks"]:
        raise ValueError("Goal4650 requires a passing same-contract gate")
    if not gates["correctness_parity_passed"]:
        raise ValueError("Goal4650 requires correctness parity")
    if not gates["legacy_no_regression"]:
        raise ValueError("Goal4650 requires legacy no-regression")
    if not gates["component_signature_shortcut_blocked"]:
        raise ValueError("Goal4650 requires the component-signature shortcut to stay blocked")
    if gates["runner_vs_embree_hot_speedup"] < gates["runner_vs_embree_hot_floor"]:
        raise ValueError("Goal4650 hot speedup below Embree floor")
    if gates["runner_vs_embree_wall_speedup"] < gates["runner_vs_embree_wall_floor"]:
        raise ValueError("Goal4650 wall speedup below Embree floor")
    if gates["runner_vs_legacy_wall_speedup"] < gates["runner_vs_legacy_wall_floor"]:
        raise ValueError("Goal4650 wall speedup below legacy parity floor")
    if gates["host_materialization_in_hot_path"]:
        raise ValueError("Goal4650 must not have hot-path host materialization")

    for flag, value in record["claim_boundaries"].items():
        if value:
            raise ValueError(f"Goal4650 must not authorize {flag}")
    return record


__all__ = [
    "V4_GOAL4650_NUMBA_FIXED_CERTIFICATION_STATUS",
    "V4_GOAL4650_NUMBA_FIXED_CANDIDATE_ID",
    "v4_goal4650_numba_fixed_certification",
    "validate_v4_goal4650_numba_fixed_certification",
]
