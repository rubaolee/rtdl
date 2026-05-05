from __future__ import annotations

from copy import deepcopy
from typing import Any


ACTIVE_V1_4_POLYGON_BACKENDS = ("embree", "optix")


def _backend_contract_role(backend: str) -> str:
    if backend == "embree":
        return "cpu_rt_baseline_and_fallback"
    if backend == "optix":
        return "nvidia_rt_target"
    return "compatibility_or_inactive"


def polygon_pair_primitive_contract(
    *,
    backend: str,
    output_mode: str,
    candidate_row_count: int | None,
) -> dict[str, Any]:
    normalized_backend = backend.lower().replace("-", "_")
    native_candidate_discovery = normalized_backend in ACTIVE_V1_4_POLYGON_BACKENDS
    return {
        "app_row": "polygon_pair_overlap_area_rows",
        "primitive": "ANY_HIT" if native_candidate_discovery else "row_materialization",
        "candidate_primitive": "ANY_HIT" if native_candidate_discovery else "not_applicable",
        "future_area_primitive": "REDUCE_FLOAT(SUM)",
        "future_area_primitive_status": "deferred_until_generic_float_reduction_contract",
        "backend": normalized_backend,
        "backend_scope": ACTIVE_V1_4_POLYGON_BACKENDS,
        "active_v1_4_backend": normalized_backend in ACTIVE_V1_4_POLYGON_BACKENDS,
        "backend_contract_role": _backend_contract_role(normalized_backend),
        "same_contract_baseline_required": normalized_backend in ACTIVE_V1_4_POLYGON_BACKENDS,
        "mode": "native_candidate_plus_app_specific_exact_area" if native_candidate_discovery else "exact_rows",
        "build_layout": "polygon2d_build_buffer",
        "probe_layout": "polygon2d_probe_buffer",
        "result_layout": "positive_pair_rows_or_summary",
        "output_mode": output_mode,
        "candidate_row_count": candidate_row_count,
        "goal1270_diagnostic_split_preserved": True,
        "exact_area_continuation": "app_specific_native_cpp",
        "phase_counters": (
            "rt_candidate_discovery_sec",
            "native_exact_continuation_sec",
            "query_and_materialize_sec",
            "summary_postprocess_sec",
        ),
        "claim_boundary": (
            "polygon_pair_overlap_area_rows candidate discovery only: native "
            "RT traversal identifies positive polygon-pair candidates before an "
            "app-specific exact grid-cell area continuation. This is not a "
            "generic polygon overlay engine, not a generic area-reduction "
            "primitive, and not public whole-app speedup wording."
        ),
        "migration_status": "compatibility_wrapper_metadata_only",
    }


def attach_polygon_pair_primitive_contract(
    payload: dict[str, Any],
    *,
    backend: str,
    output_mode: str,
) -> dict[str, Any]:
    result = deepcopy(payload)
    candidate_row_count = result.get("candidate_row_count")
    result["primitive_contract"] = polygon_pair_primitive_contract(
        backend=backend,
        output_mode=output_mode,
        candidate_row_count=int(candidate_row_count) if candidate_row_count is not None else None,
    )
    return result
