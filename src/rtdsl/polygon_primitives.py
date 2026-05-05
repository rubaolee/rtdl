from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bounded_collection_contracts import v1_5_collect_k_bounded_contracts


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
    contract = polygon_pair_primitive_contract(
        backend=backend,
        output_mode=output_mode,
        candidate_row_count=int(candidate_row_count) if candidate_row_count is not None else None,
    )
    from .primitive_contract_schema import validate_primitive_contract

    validate_primitive_contract(contract)
    result["primitive_contract"] = contract
    return result


def polygon_jaccard_diagnostic_contract(
    *,
    backend: str,
    output_mode: str,
    candidate_row_count: int | None,
) -> dict[str, Any]:
    normalized_backend = backend.lower().replace("-", "_")
    native_candidate_discovery = normalized_backend in ACTIVE_V1_4_POLYGON_BACKENDS
    collect_k_contract = v1_5_collect_k_bounded_contracts()[0]
    return {
        "app_row": "polygon_set_jaccard",
        "status": "optix_still_slower_with_reason",
        "primitive": "ANY_HIT" if native_candidate_discovery else "row_materialization",
        "candidate_primitive": "ANY_HIT" if native_candidate_discovery else "not_applicable",
        "experimental_collection_primitive": "COLLECT_K_BOUNDED",
        "future_score_primitive": "REDUCE_FLOAT(SUM)",
        "future_score_primitive_status": "blocked_by_native_score_reduction",
        "backend": normalized_backend,
        "backend_scope": ACTIVE_V1_4_POLYGON_BACKENDS,
        "active_v1_4_backend": normalized_backend in ACTIVE_V1_4_POLYGON_BACKENDS,
        "backend_contract_role": _backend_contract_role(normalized_backend),
        "same_contract_baseline_required": normalized_backend in ACTIVE_V1_4_POLYGON_BACKENDS,
        "mode": "diagnostic_native_candidate_plus_app_specific_exact_score" if native_candidate_discovery else "exact_rows",
        "build_layout": "polygon2d_build_buffer",
        "probe_layout": "polygon2d_probe_buffer",
        "result_layout": "single_jaccard_summary_row",
        "output_mode": output_mode,
        "candidate_row_count": candidate_row_count,
        "chunk_policy_required_for_public_evidence": True,
        "bounded_collection_policy": {
            "collection_primitive": collect_k_contract["collection_primitive"],
            "status": collect_k_contract["status"],
            "overflow_policy": collect_k_contract["overflow_policy"],
            "failure_mode": collect_k_contract["failure_mode"],
            "truncation_allowed": collect_k_contract["truncation_allowed"],
            "complete_candidate_coverage_required": collect_k_contract[
                "complete_candidate_coverage_required"
            ],
            "score_reduction_allowed_on_overflow": collect_k_contract[
                "score_reduction_allowed_on_overflow"
            ],
        },
        "public_wording_allowed": False,
        "exact_score_continuation": "app_specific_native_cpp",
        "phase_counters": (
            "rt_candidate_discovery_sec",
            "native_exact_continuation_sec",
            "query_and_materialize_sec",
            "summary_postprocess_sec",
        ),
        "claim_boundary": (
            "polygon_set_jaccard remains diagnostic: native RT traversal can "
            "identify candidate polygon pairs and native bounded collection is "
            "routed for Embree/OptiX summary mode, but exact set-area scoring "
            "still uses native continuation outside a stable generic score "
            "reduction primitive. Public wording remains blocked while OptiX "
            "is slower than Embree."
        ),
        "migration_status": "diagnostic_metadata_only",
    }


def attach_polygon_jaccard_diagnostic_contract(
    payload: dict[str, Any],
    *,
    backend: str,
    output_mode: str,
) -> dict[str, Any]:
    result = deepcopy(payload)
    candidate_row_count = result.get("candidate_row_count")
    contract = polygon_jaccard_diagnostic_contract(
        backend=backend,
        output_mode=output_mode,
        candidate_row_count=int(candidate_row_count) if candidate_row_count is not None else None,
    )
    from .primitive_contract_schema import validate_primitive_contract

    validate_primitive_contract(contract)
    result["primitive_contract"] = contract
    return result
