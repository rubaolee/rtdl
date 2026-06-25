from __future__ import annotations

from typing import Any

from .v4_coverage_audit import V4_COVERAGE_STRONG_MEASURED
from .v4_coverage_audit import v4_goal4627_coverage_rows
from .v4_operator_catalog import V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT
from .v4_operator_catalog import measured_v4_tier2_operator_catalog
from .v4_operator_catalog import plan_v4_operator_request


V4_GOAL4637_DECISION_STATUS = "goal4637_aabb_frontdoor_catalog_promoted_not_release"
V4_GOAL4637_DECISION = "promote_aabb_index_to_measured_v4_frontdoor_catalog_not_release"
V4_GOAL4637_EVIDENCE = (
    "future/v4/evidence/v4_goal4636c_aabb_index_all_ops_pod_gate_2026-06-25/m30_all_ops.json",
    "future/v4/v4_goal4636c_aabb_index_pod_gate_decision_2026-06-25.md",
)


def v4_goal4637_aabb_frontdoor_catalog_decision() -> dict[str, Any]:
    return {
        "status": V4_GOAL4637_DECISION_STATUS,
        "decision": V4_GOAL4637_DECISION,
        "operator": V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT,
        "api_surface": "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
        "generic_primitive": "AABB_INDEX_QUERY_2D",
        "target_coverage_row": "librts_spatial_index",
        "measured_partner": "rtdl_native",
        "validated_backends": ("optix", "embree"),
        "frontdoor_catalog_surface_added": True,
        "coverage_promoted_to_strong": True,
        "same_contract_gate": {
            "embree_over_optix_query_median": 264.8223871986397,
            "embree_over_optix_query_total": 115.00724056766381,
            "floor": 10.0,
            "counts_match": True,
            "contract_family_match": True,
        },
        "evidence": V4_GOAL4637_EVIDENCE,
        "release_authorized": False,
        "release_candidate_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "librts_paper_reproduction_claim_authorized": False,
        "authors_code_comparison_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "non_python_host_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4637_aabb_frontdoor_catalog_decision() -> dict[str, Any]:
    decision = v4_goal4637_aabb_frontdoor_catalog_decision()
    if decision["decision"] != V4_GOAL4637_DECISION:
        raise ValueError("Goal4637 decision drift")
    rows = {row["operator"]: row for row in measured_v4_tier2_operator_catalog()}
    if V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT not in rows:
        raise ValueError("Goal4637 AABB operator must be in the measured catalog")
    aabb = rows[V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT]
    if aabb["api_surface"] != decision["api_surface"]:
        raise ValueError("Goal4637 AABB catalog surface drift")
    if aabb["measured_partners"] != ("rtdl_native",):
        raise ValueError("Goal4637 AABB measured partner must stay rtdl_native")
    plan = plan_v4_operator_request("aabb_index_query", partner="rtdl_native")
    if plan.status != "tier2_measured_ready":
        raise ValueError("Goal4637 planner must route AABB as measured")
    coverage = {row.app: row for row in v4_goal4627_coverage_rows()}
    if coverage["librts_spatial_index"].coverage_status != V4_COVERAGE_STRONG_MEASURED:
        raise ValueError("Goal4637 must promote librts_spatial_index to strong operator coverage")
    gate = decision["same_contract_gate"]
    if gate["embree_over_optix_query_median"] < gate["floor"]:
        raise ValueError("Goal4637 median evidence no longer passes")
    if gate["embree_over_optix_query_total"] < gate["floor"]:
        raise ValueError("Goal4637 total evidence no longer passes")
    for flag in (
        "release_authorized",
        "release_candidate_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "all_benchmark_speedup_claim_authorized",
        "librts_paper_reproduction_claim_authorized",
        "authors_code_comparison_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "raw_optix_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "non_python_host_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4637 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4637_DECISION_STATUS",
    "V4_GOAL4637_DECISION",
    "V4_GOAL4637_EVIDENCE",
    "v4_goal4637_aabb_frontdoor_catalog_decision",
    "validate_v4_goal4637_aabb_frontdoor_catalog_decision",
]
