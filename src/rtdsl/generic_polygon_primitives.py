from __future__ import annotations

import time
from typing import Any

from .bounded_collection_contracts import v1_5_collect_k_bounded_contracts
from .float_reduction_contracts import V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL
from .float_reduction_contracts import V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL
from .float_reduction_contracts import V1_5_POLYGON_FLOAT_SUM_RESULT_LAYOUTS
from .v1_5_1_collect_k_bounded import collect_k_bounded_rows


ACTIVE_V1_5_GENERIC_POLYGON_BACKENDS = ("embree", "optix")
FROZEN_BEFORE_V2_1_POLYGON_BACKENDS = ("vulkan", "hiprt", "apple_rt")


def _polygon_float_sum_contract(*, result_layout: str, value_fields: tuple[str, ...]) -> dict[str, Any]:
    if result_layout not in V1_5_POLYGON_FLOAT_SUM_RESULT_LAYOUTS:
        raise ValueError(f"unsupported polygon REDUCE_FLOAT(SUM) result layout: {result_layout}")
    return {
        "summary_primitive": "REDUCE_FLOAT(SUM)",
        "result_layout": result_layout,
        "dtype": "float64",
        "value_fields": value_fields,
        "integer_parity_required": True,
        "scalar_helper_direct_use": False,
        "reason": (
            "polygon summaries preserve exact integer oracle parity before exposing "
            "float64 REDUCE_FLOAT(SUM) metadata"
        ),
    }


def _validate_backend(backend: str) -> str:
    normalized = backend.lower().replace("-", "_")
    if normalized in FROZEN_BEFORE_V2_1_POLYGON_BACKENDS:
        raise ValueError(f"{backend} polygon generic primitive is frozen before v2.1")
    if normalized not in ACTIVE_V1_5_GENERIC_POLYGON_BACKENDS:
        raise ValueError(f"unsupported v1.5 generic polygon backend: {backend}")
    return normalized


def run_generic_polygon_pair_exact_area_summary(
    *,
    left: Any,
    right: Any,
    candidate_pairs: Any,
    backend: str,
    exact_summary_fn,
) -> dict[str, Any]:
    """Run app-name-free polygon exact-area summary over candidate pairs."""
    normalized_backend = _validate_backend(backend)
    normalized_candidate_pairs = frozenset(
        (int(left_id), int(right_id)) for left_id, right_id in candidate_pairs
    )
    query_start = time.perf_counter()
    summary = exact_summary_fn(left, right, normalized_candidate_pairs)
    query_sec = time.perf_counter() - query_start
    total_intersection_area = int(summary["total_intersection_area"])
    total_union_area = int(summary["total_union_area"])
    summary_contract = _polygon_float_sum_contract(
        result_layout="summary_float64_sums",
        value_fields=("total_intersection_area", "total_union_area"),
    )
    return {
        "primitive": "POLYGON_PAIR_EXACT_AREA_SUMMARY",
        "summary_primitive": summary_contract["summary_primitive"],
        "summary_contract": summary_contract,
        "backend": normalized_backend,
        "candidate_pair_count": len(normalized_candidate_pairs),
        "overlap_pair_count": int(summary["overlap_pair_count"]),
        "result_layout": summary_contract["result_layout"],
        "dtype": summary_contract["dtype"],
        "total_intersection_area": float(total_intersection_area),
        "total_union_area": float(total_union_area),
        "integer_parity_values": {
            "total_intersection_area": total_intersection_area,
            "total_union_area": total_union_area,
            "overlap_pair_count": int(summary["overlap_pair_count"]),
        },
        "abs_tol": V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL,
        "rel_tol": V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL,
        "run_phases": {
            "query_polygon_exact_area_reduce_float_sum_sec": query_sec,
        },
        "claim_boundary": (
            "Generic v1.5 polygon-pair exact-area summary over already discovered candidate pairs; "
            "current integer-grid oracle requires exact integer parity before float tolerance applies; "
            "not generic polygon overlay, broad GIS, whole-app speedup, or public speedup wording."
        ),
    }


def collect_k_bounded_candidate_pairs(
    candidate_pairs: Any,
    *,
    k: int | None,
) -> dict[str, Any]:
    """Collect candidate pair IDs with v1.5 fail-closed overflow behavior."""
    contract = v1_5_collect_k_bounded_contracts()[0]
    capacity = None
    rows = tuple((int(left_id), int(right_id)) for left_id, right_id in candidate_pairs)
    if k is None:
        capacity = len(set(rows))
    else:
        capacity = int(k)
    row_buffer = collect_k_bounded_rows(rows, k=capacity, row_width=2)
    candidate_pair_rows = row_buffer["candidate_id_rows"]
    return {
        "primitive": contract["collection_primitive"],
        "status": contract["status"],
        "app_generic": row_buffer["app_generic"],
        "capacity": row_buffer["capacity"],
        "valid_count": row_buffer["valid_count"],
        "emitted_count": row_buffer["emitted_count"],
        "overflowed": row_buffer["overflowed"],
        "overflow_policy": contract["overflow_policy"],
        "failure_mode": contract["failure_mode"],
        "truncation_allowed": contract["truncation_allowed"],
        "partial_result_on_overflow_allowed": row_buffer[
            "partial_result_on_overflow_allowed"
        ],
        "score_or_reduction_after_overflow_allowed": row_buffer[
            "score_or_reduction_after_overflow_allowed"
        ],
        "complete_candidate_coverage": row_buffer["complete_candidate_coverage"],
        "ordering_policy": row_buffer["ordering_policy"],
        "duplicate_policy": row_buffer["duplicate_policy"],
        "row_width": row_buffer["row_width"],
        "candidate_id_rows": candidate_pair_rows,
        "generic_result_layout": row_buffer["result_layout"],
        "public_wording_allowed": contract["public_wording_allowed"],
        "claim_boundary": contract["claim_boundary"],
        "candidate_pairs": candidate_pair_rows,
    }


def _validate_complete_collection(collection: dict[str, Any], *, backend: str) -> tuple[tuple[int, int], ...]:
    if collection.get("primitive") != "COLLECT_K_BOUNDED":
        raise ValueError("native collection must use primitive COLLECT_K_BOUNDED")
    if collection.get("backend") != backend:
        raise ValueError("native collection backend does not match requested backend")
    if collection.get("overflowed"):
        raise RuntimeError(
            "COLLECT_K_BOUNDED native collection reported overflow; "
            f"failure_mode={collection.get('failure_mode', 'fail_closed_overflow')}"
        )
    if not collection.get("complete_candidate_coverage"):
        raise RuntimeError("COLLECT_K_BOUNDED native collection did not report complete candidate coverage")
    if "candidate_id_rows" in collection:
        row_buffer = collect_k_bounded_rows(
            collection["candidate_id_rows"],
            k=int(collection.get("capacity", collection.get("valid_count", 0))),
            row_width=2,
        )
        return tuple(
            (int(left_id), int(right_id))
            for left_id, right_id in row_buffer["candidate_id_rows"]
        )
    if "candidate_pairs" in collection:
        return tuple((int(left_id), int(right_id)) for left_id, right_id in collection["candidate_pairs"])
    raise ValueError("native collection must include candidate_id_rows or candidate_pairs")


def run_generic_polygon_set_jaccard_score_reduction(
    *,
    left: Any,
    right: Any,
    collection: dict[str, Any],
    backend: str,
    exact_score_fn,
) -> dict[str, Any]:
    """Run generic Jaccard score reduction after complete bounded collection."""
    normalized_backend = _validate_backend(backend)
    candidate_pairs = _validate_complete_collection(collection, backend=normalized_backend)
    score_start = time.perf_counter()
    rows = tuple(exact_score_fn(left, right, frozenset(candidate_pairs)))
    if not rows and candidate_pairs:
        raise RuntimeError(
            "exact_score_fn returned no rows for non-empty candidate_pairs; "
            "cannot produce Jaccard summary"
        )
    score_sec = time.perf_counter() - score_start
    summary = (
        dict(rows[0])
        if rows
        else {
            "intersection_area": 0,
            "left_area": 0,
            "right_area": 0,
            "union_area": 0,
            "jaccard_similarity": 0.0,
        }
    )
    integer_parity_values = {
        "intersection_area": int(summary["intersection_area"]),
        "left_area": int(summary["left_area"]),
        "right_area": int(summary["right_area"]),
        "union_area": int(summary["union_area"]),
    }
    summary_contract = _polygon_float_sum_contract(
        result_layout="summary_float64_sums_plus_ratio",
        value_fields=("intersection_area", "left_area", "right_area", "union_area"),
    )
    return {
        "primitive": "POLYGON_SET_JACCARD_SCORE_REDUCTION",
        "summary_primitive": summary_contract["summary_primitive"],
        "summary_contract": summary_contract,
        "backend": normalized_backend,
        "candidate_pair_count": len(candidate_pairs),
        "result_layout": summary_contract["result_layout"],
        "dtype": summary_contract["dtype"],
        "summary": summary,
        "rows": rows,
        "integer_parity_values": integer_parity_values,
        "abs_tol": V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL,
        "rel_tol": V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL,
        "run_phases": {
            "query_polygon_jaccard_reduce_float_sum_sec": score_sec,
        },
        "claim_boundary": (
            "Generic v1.5 diagnostic polygon-set Jaccard score reduction after complete "
            "COLLECT_K_BOUNDED coverage; current app route uses a backend-neutral native "
            "polygon-pair area summary before computing the ratio, but this is not a fused "
            "GPU Jaccard kernel and not public speedup wording."
        ),
    }


def run_generic_polygon_set_jaccard_summary(
    *,
    left: Any,
    right: Any,
    candidate_pairs: Any = None,
    collection: dict[str, Any] | None = None,
    backend: str,
    exact_score_fn,
    collection_capacity: int | None = None,
) -> dict[str, Any]:
    """Run Jaccard scoring only after fail-closed bounded collection succeeds."""
    normalized_backend = _validate_backend(backend)
    collect_start = time.perf_counter()
    if collection is None:
        if candidate_pairs is None:
            raise ValueError("candidate_pairs or collection must be provided")
        collection = collect_k_bounded_candidate_pairs(candidate_pairs, k=collection_capacity)
        native_collection = False
    else:
        native_collection = bool(collection.get("native_collection", True))
        _validate_complete_collection(collection, backend=normalized_backend)
    collect_sec = time.perf_counter() - collect_start
    score_reduction = run_generic_polygon_set_jaccard_score_reduction(
        left=left,
        right=right,
        collection=collection | {"backend": normalized_backend},
        backend=normalized_backend,
        exact_score_fn=exact_score_fn,
    )
    return {
        "primitive": "POLYGON_SET_JACCARD_SUMMARY",
        "collection_primitive": collection["primitive"],
        "score_reduction_primitive": score_reduction["primitive"],
        "summary_primitive": score_reduction["summary_primitive"],
        "backend": normalized_backend,
        "result_layout": "single_jaccard_summary_row",
        "dtype": "float64",
        "candidate_pair_count": score_reduction["candidate_pair_count"],
        "collection": {
            key: value for key, value in collection.items() if key != "candidate_pairs"
        } | {"native_collection": native_collection},
        "score_reduction": {
            key: value for key, value in score_reduction.items() if key not in {"rows", "summary"}
        },
        "summary": score_reduction["summary"],
        "rows": score_reduction["rows"],
        "abs_tol": V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL,
        "rel_tol": V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL,
        "run_phases": {
            "query_polygon_collect_k_bounded_sec": collect_sec,
            **score_reduction["run_phases"],
        },
        "claim_boundary": (
            "Generic v1.5 diagnostic Jaccard scoring over fail-closed bounded candidate pairs; "
            "score reduction runs only after complete candidate coverage; not public speedup wording."
        ),
    }
