from __future__ import annotations

from typing import Any


V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL = 1e-9
V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL = 1e-9


def v1_5_float_sum_reduction_contracts() -> tuple[dict[str, Any], ...]:
    """Return v1.5 REDUCE_FLOAT(SUM) contracts for deferred polygon rows."""
    return (
        {
            "app": "polygon_pair_overlap_area_rows",
            "subpath": "exact_area_sum",
            "status": "design_required",
            "input_rows": "positive_polygon_pair_area_rows",
            "reduction_primitive": "REDUCE_FLOAT(SUM)",
            "group_key": "summary",
            "value_fields": ("intersection_area", "union_area"),
            "result_layout": "summary_float64_sums",
            "dtype": "float64",
            "abs_tol": V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL,
            "rel_tol": V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL,
            "determinism_policy": "backend must publish reduction order or validate within tolerance",
            "current_oracle_policy": "integer-grid unit-cell area still requires exact integer parity before float tolerance is applied",
            "claim_boundary": "exact area summary only; not generic polygon overlay, GIS, or public speedup wording; public speedup wording remains blocked",
        },
        {
            "app": "polygon_set_jaccard",
            "subpath": "exact_score_sum",
            "status": "pod_verified_generic_non_public",
            "input_rows": "bounded_candidate_pair_score_rows",
            "reduction_primitive": "REDUCE_FLOAT(SUM)",
            "group_key": "summary",
            "value_fields": ("intersection_area", "union_area"),
            "result_layout": "summary_float64_sums_plus_ratio",
            "dtype": "float64",
            "abs_tol": V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL,
            "rel_tol": V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL,
            "determinism_policy": "backend must publish collection order and reduction tolerance",
            "current_oracle_policy": "complete bounded collection required before backend-neutral native polygon-pair area summary and ratio computation",
            "claim_boundary": "diagnostic only because OptiX remains slower than Embree; public speedup wording remains blocked",
        },
    )


def validate_v1_5_float_sum_reduction_contracts() -> tuple[dict[str, Any], ...]:
    contracts = v1_5_float_sum_reduction_contracts()
    required_fields = (
        "app",
        "subpath",
        "status",
        "input_rows",
        "reduction_primitive",
        "group_key",
        "value_fields",
        "result_layout",
        "dtype",
        "abs_tol",
        "rel_tol",
        "determinism_policy",
        "current_oracle_policy",
        "claim_boundary",
    )
    valid_statuses = {"design_required", "blocked_by_collect_k_bounded", "pod_verified_generic_non_public"}
    for contract in contracts:
        for field in required_fields:
            if field not in contract:
                raise ValueError(f"missing float reduction contract field: {field}")
        if contract["status"] not in valid_statuses:
            raise ValueError(f"invalid float reduction contract status: {contract['status']}")
        if contract["reduction_primitive"] != "REDUCE_FLOAT(SUM)":
            raise ValueError("v1.5 float-sum contract must use REDUCE_FLOAT(SUM)")
        if contract["dtype"] != "float64":
            raise ValueError("v1.5 polygon float-sum contract must default to float64")
        if float(contract["abs_tol"]) < 0.0 or float(contract["rel_tol"]) < 0.0:
            raise ValueError("float reduction tolerances must be non-negative")
        value_fields = tuple(contract["value_fields"])
        if not value_fields:
            raise ValueError("float reduction value_fields must not be empty")
        if "public speedup" not in str(contract["claim_boundary"]):
            raise ValueError("float reduction claim boundary must block public speedup wording")
    return contracts
