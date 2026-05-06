from __future__ import annotations

from typing import Any, Iterable


V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE = "COLLECT_K_BOUNDED"
V1_5_1_COLLECT_K_BOUNDED_STATUS = "promotion_candidate_python_rtdl_track"
V1_5_1_COLLECT_K_BOUNDED_RESULT_LAYOUT = "dense_candidate_id_rows_with_valid_count"
V1_5_1_COLLECT_K_BOUNDED_OVERFLOW_POLICY = "fail_closed_before_result_materialization"
V1_5_1_COLLECT_K_BOUNDED_ORDERING_POLICY = "stable_lexicographic_by_candidate_id_row"
V1_5_1_COLLECT_K_BOUNDED_DUPLICATE_POLICY = "deduplicate_before_capacity_check"
V1_5_1_COLLECT_K_BOUNDED_BACKENDS = ("embree", "optix")


def v1_5_1_collect_k_bounded_contract() -> dict[str, Any]:
    """Return the app-generic v1.5.1 bounded collection promotion contract."""
    return {
        "primitive": V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE,
        "status": V1_5_1_COLLECT_K_BOUNDED_STATUS,
        "track": "python_rtdl",
        "app_generic": True,
        "stable_promotion_authorized": False,
        "active_backend_scope": V1_5_1_COLLECT_K_BOUNDED_BACKENDS,
        "result_layout": V1_5_1_COLLECT_K_BOUNDED_RESULT_LAYOUT,
        "row_dtype": "int64",
        "capacity_parameter": "k",
        "capacity_unit": "candidate_id_rows",
        "valid_count_field": "valid_count",
        "overflow_field": "overflowed",
        "ordering_policy": V1_5_1_COLLECT_K_BOUNDED_ORDERING_POLICY,
        "duplicate_policy": V1_5_1_COLLECT_K_BOUNDED_DUPLICATE_POLICY,
        "overflow_policy": V1_5_1_COLLECT_K_BOUNDED_OVERFLOW_POLICY,
        "failure_mode": "fail_closed_overflow",
        "truncation_allowed": False,
        "partial_result_on_overflow_allowed": False,
        "score_or_reduction_after_overflow_allowed": False,
        "complete_candidate_coverage_required": True,
        "bounds_tests_required": (
            "k_zero_with_zero_results",
            "k_zero_overflow_with_positive_results",
            "exact_k_full_buffer",
            "k_plus_one_overflow",
            "deterministic_ordering",
            "duplicate_rows_deduplicated_before_capacity_check",
            "row_width_mismatch_rejected",
            "negative_k_rejected",
        ),
        "claim_boundary": (
            "v1.5.1 app-generic COLLECT_K_BOUNDED promotion candidate contract only; "
            "not yet public promotion, not a Jaccard-specific or polygon-specific engine path, "
            "and not a performance or zero-copy claim."
        ),
    }


def validate_v1_5_1_collect_k_bounded_contract() -> dict[str, Any]:
    contract = v1_5_1_collect_k_bounded_contract()
    required = (
        "primitive",
        "status",
        "track",
        "app_generic",
        "stable_promotion_authorized",
        "active_backend_scope",
        "result_layout",
        "row_dtype",
        "capacity_parameter",
        "capacity_unit",
        "valid_count_field",
        "overflow_field",
        "ordering_policy",
        "duplicate_policy",
        "overflow_policy",
        "failure_mode",
        "truncation_allowed",
        "partial_result_on_overflow_allowed",
        "score_or_reduction_after_overflow_allowed",
        "complete_candidate_coverage_required",
        "bounds_tests_required",
        "claim_boundary",
    )
    for field in required:
        if field not in contract:
            raise ValueError(f"missing v1.5.1 collect-k contract field: {field}")
        if field not in {
            "stable_promotion_authorized",
            "truncation_allowed",
            "partial_result_on_overflow_allowed",
            "score_or_reduction_after_overflow_allowed",
        } and not contract[field]:
            raise ValueError(f"empty v1.5.1 collect-k contract field: {field}")
    if contract["primitive"] != V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE:
        raise ValueError("v1.5.1 collect-k contract must target COLLECT_K_BOUNDED")
    if contract["app_generic"] is not True:
        raise ValueError("v1.5.1 collect-k contract must be app-generic")
    if contract["stable_promotion_authorized"] is not False:
        raise ValueError("v1.5.1 collect-k contract is a candidate, not final promotion")
    if tuple(contract["active_backend_scope"]) != V1_5_1_COLLECT_K_BOUNDED_BACKENDS:
        raise ValueError("v1.5.1 collect-k backend scope must remain Embree+OptiX")
    for false_flag in (
        "truncation_allowed",
        "partial_result_on_overflow_allowed",
        "score_or_reduction_after_overflow_allowed",
    ):
        if contract[false_flag] is not False:
            raise ValueError(f"v1.5.1 collect-k must keep {false_flag}=False")
    if contract["complete_candidate_coverage_required"] is not True:
        raise ValueError("v1.5.1 collect-k must require complete candidate coverage")
    required_bounds = {
        "k_zero_with_zero_results",
        "k_zero_overflow_with_positive_results",
        "exact_k_full_buffer",
        "k_plus_one_overflow",
        "deterministic_ordering",
        "duplicate_rows_deduplicated_before_capacity_check",
        "row_width_mismatch_rejected",
        "negative_k_rejected",
    }
    if set(contract["bounds_tests_required"]) != required_bounds:
        raise ValueError("v1.5.1 collect-k bounds test set mismatch")
    boundary = str(contract["claim_boundary"])
    for phrase in (
        "app-generic",
        "not yet public promotion",
        "not a Jaccard-specific",
        "not a performance or zero-copy claim",
    ):
        if phrase not in boundary:
            raise ValueError("v1.5.1 collect-k claim boundary is too broad")
    return contract


def _normalize_candidate_rows(
    candidate_rows: Iterable[Any],
    *,
    row_width: int,
) -> tuple[tuple[int, ...], ...]:
    if row_width <= 0:
        raise ValueError("COLLECT_K_BOUNDED row_width must be positive")
    normalized: set[tuple[int, ...]] = set()
    for row in candidate_rows:
        if isinstance(row, int):
            values = (row,)
        else:
            values = tuple(row)
        if len(values) != row_width:
            raise ValueError(
                "COLLECT_K_BOUNDED candidate row width mismatch: "
                f"expected {row_width}, got {len(values)}"
            )
        normalized.add(tuple(int(value) for value in values))
    return tuple(sorted(normalized))


def collect_k_bounded_rows(
    candidate_rows: Iterable[Any],
    *,
    k: int,
    row_width: int = 1,
) -> dict[str, Any]:
    """Materialize an app-generic bounded candidate-id row buffer.

    Overflow fails before returning partial rows. This function is the Python
    reference shape that v1.5.1 native Embree/OptiX collection paths must match.
    """
    capacity = int(k)
    if capacity < 0:
        raise ValueError("COLLECT_K_BOUNDED capacity k must be non-negative")
    contract = validate_v1_5_1_collect_k_bounded_contract()
    rows = _normalize_candidate_rows(candidate_rows, row_width=int(row_width))
    emitted_count = len(rows)
    if emitted_count > capacity:
        raise RuntimeError(
            "COLLECT_K_BOUNDED overflowed capacity "
            f"{capacity}; emitted {emitted_count}; "
            f"failure_mode={contract['failure_mode']}; partial_result_returned=False"
        )
    return {
        "primitive": contract["primitive"],
        "status": contract["status"],
        "app_generic": True,
        "result_layout": contract["result_layout"],
        "row_dtype": contract["row_dtype"],
        "row_width": int(row_width),
        "capacity": capacity,
        "valid_count": emitted_count,
        "emitted_count": emitted_count,
        "overflowed": False,
        "complete_candidate_coverage": True,
        "ordering_policy": contract["ordering_policy"],
        "duplicate_policy": contract["duplicate_policy"],
        "overflow_policy": contract["overflow_policy"],
        "failure_mode": contract["failure_mode"],
        "truncation_allowed": contract["truncation_allowed"],
        "partial_result_on_overflow_allowed": contract[
            "partial_result_on_overflow_allowed"
        ],
        "score_or_reduction_after_overflow_allowed": contract[
            "score_or_reduction_after_overflow_allowed"
        ],
        "candidate_id_rows": rows,
        "claim_boundary": contract["claim_boundary"],
    }


def validate_collect_k_bounded_result(
    result: dict[str, Any],
    *,
    row_width: int,
    backend: str | None = None,
) -> dict[str, Any]:
    """Validate and normalize a completed app-generic bounded collection result."""
    if result.get("primitive") != V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE:
        raise ValueError("bounded collection result must use primitive COLLECT_K_BOUNDED")
    if backend is not None and result.get("backend") != backend:
        raise ValueError("bounded collection backend does not match requested backend")
    if result.get("overflowed"):
        raise RuntimeError(
            "COLLECT_K_BOUNDED result reported overflow; "
            f"failure_mode={result.get('failure_mode', 'fail_closed_overflow')}"
        )
    if result.get("complete_candidate_coverage") is not True:
        raise RuntimeError("COLLECT_K_BOUNDED result must report complete candidate coverage")
    if "candidate_id_rows" not in result:
        raise ValueError("bounded collection result must include candidate_id_rows")
    capacity = int(result.get("capacity", result.get("valid_count", 0)))
    normalized = collect_k_bounded_rows(
        result["candidate_id_rows"],
        k=capacity,
        row_width=int(row_width),
    )
    if int(result.get("row_width", row_width)) != int(row_width):
        raise ValueError("COLLECT_K_BOUNDED row_width metadata mismatch")
    if int(result.get("valid_count", normalized["valid_count"])) != normalized["valid_count"]:
        raise ValueError("COLLECT_K_BOUNDED valid_count metadata mismatch")
    if int(result.get("emitted_count", normalized["emitted_count"])) != normalized["emitted_count"]:
        raise ValueError("COLLECT_K_BOUNDED emitted_count metadata mismatch")
    if tuple(result.get("candidate_id_rows", ())) != normalized["candidate_id_rows"]:
        raise ValueError("COLLECT_K_BOUNDED candidate_id_rows must be canonicalized")
    return {
        **result,
        "app_generic": True,
        "result_layout": result.get("result_layout", normalized["result_layout"]),
        "generic_result_layout": result.get(
            "generic_result_layout",
            normalized["result_layout"],
        ),
        "row_dtype": result.get("row_dtype", normalized["row_dtype"]),
        "row_width": int(row_width),
        "capacity": capacity,
        "valid_count": normalized["valid_count"],
        "emitted_count": normalized["emitted_count"],
        "overflowed": False,
        "complete_candidate_coverage": True,
        "ordering_policy": normalized["ordering_policy"],
        "duplicate_policy": normalized["duplicate_policy"],
        "candidate_id_rows": normalized["candidate_id_rows"],
    }
