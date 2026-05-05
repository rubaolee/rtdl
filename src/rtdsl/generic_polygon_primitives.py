from __future__ import annotations

import time
from typing import Any

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
