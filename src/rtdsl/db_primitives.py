from __future__ import annotations

from copy import deepcopy
from typing import Any


ACTIVE_V1_4_DB_BACKENDS = ("embree", "optix")


def _backend_contract_role(backend: str) -> str:
    if backend == "embree":
        return "cpu_rt_baseline_and_fallback"
    if backend == "optix":
        return "nvidia_rt_target"
    return "compatibility_or_inactive"


def sales_risk_primitive_contract(
    *,
    backend: str,
    output_mode: str,
    materialization_free: bool,
    chunked: bool = False,
) -> dict[str, Any]:
    normalized_backend = backend.lower().replace("-", "_")
    compact_summary = output_mode == "compact_summary"
    return {
        "app_row": "database_analytics.sales_risk",
        "primitive": "COUNT_HITS" if compact_summary else "row_materialization",
        "alternate_primitive": "REDUCE_INT(COUNT)" if compact_summary else "not_applicable",
        "secondary_primitive": "REDUCE_INT(SUM)" if compact_summary else "not_applicable",
        "backend": normalized_backend,
        "backend_scope": ACTIVE_V1_4_DB_BACKENDS,
        "active_v1_4_backend": normalized_backend in ACTIVE_V1_4_DB_BACKENDS,
        "backend_contract_role": _backend_contract_role(normalized_backend),
        "same_contract_baseline_required": normalized_backend in ACTIVE_V1_4_DB_BACKENDS,
        "mode": "prepared_compact_summary" if compact_summary else "one_shot_or_materializing",
        "build_layout": "columnar_denorm_table",
        "probe_layout": "predicate_bundle_and_grouped_query",
        "result_layout": (
            "aggregate_scan_count_and_grouped_integer_maps"
            if compact_summary
            else "materialized_scan_count_sum_rows"
        ),
        "prepared_state": (
            "prepared_columnar_dataset_reusable"
            if compact_summary and normalized_backend in ACTIVE_V1_4_DB_BACKENDS
            else "none_required_for_materializing_rows"
        ),
        "materialization_free": bool(materialization_free),
        "chunked_compact_summary": bool(chunked),
        "phase_counters": (
            "query_compact_summary_batch_sec",
            "query_conjunctive_scan_count_sec",
            "query_grouped_count_summary_sec",
            "query_grouped_sum_summary_sec",
            "query_conjunctive_scan_and_materialize_sec",
            "query_grouped_count_and_materialize_sec",
            "query_grouped_sum_and_materialize_sec",
            "python_summary_postprocess_sec",
        ),
        "claim_boundary": (
            "database_analytics.sales_risk compact-summary only: bounded predicate "
            "count, grouped integer count, and grouped integer sum over an "
            "application-owned denormalized table. This excludes SQL engines, "
            "DBMS behavior, query planning, joins, transactions, indexes as a "
            "database feature, and row-materializing output."
        ),
        "migration_status": "compatibility_wrapper_metadata_only",
    }


def attach_sales_risk_primitive_contract(
    payload: dict[str, Any],
    *,
    backend: str,
    output_mode: str,
) -> dict[str, Any]:
    result = deepcopy(payload)
    run_phases = result.get("run_phases", {})
    materialization_free = output_mode == "compact_summary" and not any(
        "materialize" in str(phase) for phase in run_phases
    )
    session = result.get("session", {})
    result["primitive_contract"] = sales_risk_primitive_contract(
        backend=backend,
        output_mode=output_mode,
        materialization_free=materialization_free,
        chunked=bool(isinstance(session, dict) and session.get("chunked_compact_summary")),
    )
    return result
