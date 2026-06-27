from __future__ import annotations

from typing import Any


V4_GOAL4636C_DECISION_STATUS = "goal4636c_aabb_index_pod_gate_passed_pending_frontdoor_catalog_not_release"
V4_GOAL4636C_DECISION = "accept_aabb_index_pod_gate_require_frontdoor_catalog_goal"
V4_GOAL4636C_EVIDENCE = (
    "tools/_archive/future/v4/evidence/v4_goal4636c_aabb_index_all_ops_pod_gate_2026-06-25/m30_all_ops.json",
    "tools/_archive/future/v4/reviews/goal4636c_aabb_index_target_protocol_review_record_2026-06-25.md",
)


def v4_goal4636_aabb_index_decision() -> dict[str, Any]:
    return {
        "status": V4_GOAL4636C_DECISION_STATUS,
        "decision": V4_GOAL4636C_DECISION,
        "operator": "aabb_index_query_2d_all_ops_count",
        "api_surface": "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
        "generic_primitive": "AABB_INDEX_QUERY_2D",
        "target_coverage_row": "librts_spatial_index",
        "continuation_class": "aabb_index_all_ops_count",
        "scope": "rtdl_native_prepared_runner",
        "same_contract_gate": {
            "status": "pass",
            "dataset": "uniform",
            "box_count": 1_000_000,
            "query_count": 1_000,
            "operation": "all",
            "embree_repeat": 240,
            "optix_repeat": 240,
            "all_counts_match_cross_backend": True,
            "all_same_contract_family": True,
            "accepted_contract_family": "generic_prepared_aabb_index_query_2d",
            "accepted_contracts": (
                "generic_prepared_aabb_index_query_2d",
                "generic_prepared_aabb_index_query_2d_count",
                "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
            ),
            "embree_over_optix_query_median": 264.8223871986397,
            "embree_over_optix_query_median_floor": 10.0,
            "embree_over_optix_query_total": 115.00724056766381,
            "embree_over_optix_query_total_floor": 10.0,
            "embree_query_median_sec": 0.5198514759540558,
            "optix_query_median_sec": 0.001963019371032715,
            "embree_query_total_sec": 130.3403503447771,
            "optix_query_total_sec": 1.1333229951560497,
            "cpu_reference_skipped_acknowledged": True,
            "correctness_oracle": "cross_backend_count_match_same_fixture",
        },
        "coverage_effect": {
            "row": "librts_spatial_index",
            "from": "deferred_or_uncovered_v4_0",
            "to": "pending_strong_measured_operator_coverage_after_frontdoor_catalog_goal",
            "reason": (
                "The large same-RT-hardware AABB all-ops gate passed materially, "
                "but the public front-door/catalog surface is intentionally a "
                "separate goal before the coverage table can be promoted."
            ),
        },
        "next_action": (
            "Start the front-door/catalog goal for "
            "v4_aabb_index_query_2d_all_ops_count_prepared_runner; then refresh "
            "coverage and release blockers from a measured public surface."
        ),
        "evidence": V4_GOAL4636C_EVIDENCE,
        "measured_catalog_promotion_authorized": False,
        "frontdoor_catalog_goal_required": True,
        "release_authorized": False,
        "release_candidate_authorized": False,
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


def validate_v4_goal4636_aabb_index_decision() -> dict[str, Any]:
    decision = v4_goal4636_aabb_index_decision()
    if decision["decision"] != V4_GOAL4636C_DECISION:
        raise ValueError("Goal4636C decision drift")
    gate = decision["same_contract_gate"]
    if gate["status"] != "pass":
        raise ValueError("Goal4636C AABB gate must remain passed")
    if not gate["all_counts_match_cross_backend"]:
        raise ValueError("Goal4636C must preserve count-parity evidence")
    if not gate["all_same_contract_family"]:
        raise ValueError("Goal4636C must preserve contract-family evidence")
    if gate["embree_repeat"] != gate["optix_repeat"]:
        raise ValueError("Goal4636C must preserve symmetric repeat evidence")
    if gate["embree_over_optix_query_median"] < gate["embree_over_optix_query_median_floor"]:
        raise ValueError("Goal4636C median gate no longer passes")
    if gate["embree_over_optix_query_total"] < gate["embree_over_optix_query_total_floor"]:
        raise ValueError("Goal4636C total gate no longer passes")
    if decision["measured_catalog_promotion_authorized"]:
        raise ValueError("Goal4636C gate alone must not authorize catalog promotion")
    if not decision["frontdoor_catalog_goal_required"]:
        raise ValueError("Goal4636C must require a separate front-door/catalog goal")
    for flag in (
        "release_authorized",
        "release_candidate_authorized",
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
            raise ValueError(f"Goal4636C must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4636C_DECISION_STATUS",
    "V4_GOAL4636C_DECISION",
    "V4_GOAL4636C_EVIDENCE",
    "v4_goal4636_aabb_index_decision",
    "validate_v4_goal4636_aabb_index_decision",
]
