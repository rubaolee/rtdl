from __future__ import annotations

import time
from typing import Any

from .bounded_collection_contracts import v1_5_collect_k_bounded_contracts
from .float_reduction_contracts import V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL
from .float_reduction_contracts import V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL


ACTIVE_V1_5_GENERIC_POLYGON_BACKENDS = ("embree", "optix")
FROZEN_BEFORE_V2_1_POLYGON_BACKENDS = ("vulkan", "hiprt", "apple_rt")


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
    return {
        "primitive": "POLYGON_PAIR_EXACT_AREA_SUMMARY",
        "summary_primitive": "REDUCE_FLOAT(SUM)",
        "backend": normalized_backend,
        "candidate_pair_count": len(normalized_candidate_pairs),
        "overlap_pair_count": int(summary["overlap_pair_count"]),
        "result_layout": "summary_float64_sums",
        "dtype": "float64",
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
    if k is not None and int(k) < 0:
        raise ValueError("COLLECT_K_BOUNDED capacity k must be non-negative")
    contract = v1_5_collect_k_bounded_contracts()[0]
    normalized_pairs = tuple(
        sorted({(int(left_id), int(right_id)) for left_id, right_id in candidate_pairs})
    )
    capacity = len(normalized_pairs) if k is None else int(k)
    emitted = len(normalized_pairs)
    overflowed = emitted > capacity
    metadata = {
        "primitive": contract["collection_primitive"],
        "status": contract["status"],
        "capacity": capacity,
        "emitted_count": emitted,
        "overflowed": overflowed,
        "overflow_policy": contract["overflow_policy"],
        "failure_mode": contract["failure_mode"],
        "truncation_allowed": contract["truncation_allowed"],
        "complete_candidate_coverage": not overflowed,
        "ordering_policy": contract["ordering_policy"],
        "public_wording_allowed": contract["public_wording_allowed"],
        "candidate_pairs": normalized_pairs if not overflowed else (),
    }
    if overflowed:
        raise RuntimeError(
            "COLLECT_K_BOUNDED overflowed capacity "
            f"{capacity}; emitted {emitted}; failure_mode={contract['failure_mode']}"
        )
    return metadata


def run_generic_polygon_set_jaccard_summary(
    *,
    left: Any,
    right: Any,
    candidate_pairs: Any,
    backend: str,
    exact_score_fn,
    collection_capacity: int | None = None,
) -> dict[str, Any]:
    """Run Jaccard scoring only after fail-closed bounded collection succeeds."""
    normalized_backend = _validate_backend(backend)
    collect_start = time.perf_counter()
    collection = collect_k_bounded_candidate_pairs(candidate_pairs, k=collection_capacity)
    collect_sec = time.perf_counter() - collect_start
    score_start = time.perf_counter()
    rows = tuple(exact_score_fn(left, right, frozenset(collection["candidate_pairs"])))
    if not rows and collection["candidate_pairs"]:
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
    return {
        "primitive": "POLYGON_SET_JACCARD_SUMMARY",
        "collection_primitive": collection["primitive"],
        "summary_primitive": "REDUCE_FLOAT(SUM)",
        "backend": normalized_backend,
        "result_layout": "single_jaccard_summary_row",
        "dtype": "float64",
        "candidate_pair_count": len(collection["candidate_pairs"]),
        "collection": {key: value for key, value in collection.items() if key != "candidate_pairs"},
        "summary": summary,
        "rows": rows,
        "abs_tol": V1_5_FLOAT_REDUCTION_DEFAULT_ABS_TOL,
        "rel_tol": V1_5_FLOAT_REDUCTION_DEFAULT_REL_TOL,
        "run_phases": {
            "query_polygon_collect_k_bounded_sec": collect_sec,
            "query_polygon_jaccard_reduce_float_sum_sec": score_sec,
        },
        "claim_boundary": (
            "Generic v1.5 diagnostic Jaccard scoring over fail-closed bounded candidate pairs; "
            "score reduction runs only after complete candidate coverage; not public speedup wording."
        ),
    }
