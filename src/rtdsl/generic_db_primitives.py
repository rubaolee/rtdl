from __future__ import annotations

import time
from typing import Any


ACTIVE_V1_5_GENERIC_DB_BACKENDS = ("embree", "optix")
FROZEN_BEFORE_V2_1_DB_BACKENDS = ("vulkan", "hiprt", "apple_rt")
V1_5_DB_COMPACT_SUMMARY_RESULT_LAYOUTS = (
    "scalar_int64_hit_count",
    "grouped_int64_count_map",
    "grouped_int64_sum_map",
)


_DB_SUMMARY_CONTRACT_BY_OPERATION = {
    "conjunctive_scan_count": {
        "summary_primitive": "COUNT_HITS",
        "result_layout": "scalar_int64_hit_count",
        "dtype": "int64",
        "materialization_free": True,
    },
    "grouped_count_summary": {
        "summary_primitive": "REDUCE_INT(COUNT)",
        "result_layout": "grouped_int64_count_map",
        "dtype": "int64",
        "materialization_free": True,
    },
    "grouped_sum_summary": {
        "summary_primitive": "REDUCE_INT(SUM)",
        "result_layout": "grouped_int64_sum_map",
        "dtype": "int64",
        "materialization_free": True,
    },
}


def _validate_backend(backend: str) -> str:
    normalized = backend.lower().replace("-", "_")
    if normalized in FROZEN_BEFORE_V2_1_DB_BACKENDS:
        raise ValueError(f"{backend} DB generic primitive is frozen before v2.1")
    if normalized not in ACTIVE_V1_5_GENERIC_DB_BACKENDS:
        raise ValueError(f"unsupported v1.5 generic DB backend: {backend}")
    return normalized


def _validate_requests(requests: Any) -> tuple[dict[str, Any], ...]:
    normalized_requests = tuple(dict(request) for request in requests)
    if not normalized_requests:
        raise ValueError("generic DB compact summary requires at least one request")
    valid_operations = {
        "conjunctive_scan_count",
        "grouped_count_summary",
        "grouped_sum_summary",
    }
    seen_names: set[str] = set()
    for request in normalized_requests:
        name = str(request.get("name", "")).strip()
        operation = str(request.get("operation", "")).strip()
        if not name:
            raise ValueError("generic DB compact summary request name must be non-empty")
        if name in seen_names:
            raise ValueError(f"duplicate generic DB compact summary request name: {name}")
        seen_names.add(name)
        if operation not in valid_operations:
            raise ValueError(f"unsupported generic DB compact summary operation: {operation}")
        if operation == "conjunctive_scan_count" and "predicates" not in request:
            raise ValueError("conjunctive_scan_count requires predicates")
        if operation in {"grouped_count_summary", "grouped_sum_summary"} and "query" not in request:
            raise ValueError(f"{operation} requires query")
    return normalized_requests


def _summary_primitives(requests: tuple[dict[str, Any], ...]) -> tuple[str, ...]:
    primitives: list[str] = []
    for request in requests:
        operation = str(request["operation"])
        if operation == "conjunctive_scan_count":
            primitive = "COUNT_HITS"
        elif operation == "grouped_count_summary":
            primitive = "REDUCE_INT(COUNT)"
        else:
            primitive = "REDUCE_INT(SUM)"
        if primitive not in primitives:
            primitives.append(primitive)
    return tuple(primitives)


def _summary_contracts(requests: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], ...]:
    contracts = []
    for request in requests:
        operation = str(request["operation"])
        contract = _DB_SUMMARY_CONTRACT_BY_OPERATION[operation]
        contracts.append(
            {
                "name": str(request["name"]),
                "operation": operation,
                **contract,
            }
        )
    return tuple(contracts)


def run_generic_db_compact_summary_batch(
    *,
    prepared_dataset: Any,
    requests: Any,
    backend: str,
) -> dict[str, Any]:
    """Run app-name-free DB compact summaries without row materialization."""
    normalized_backend = _validate_backend(backend)
    normalized_requests = _validate_requests(requests)
    if not hasattr(prepared_dataset, "compact_summary_batch"):
        raise ValueError("prepared_dataset must expose compact_summary_batch")

    query_start = time.perf_counter()
    results = prepared_dataset.compact_summary_batch(normalized_requests)
    query_sec = time.perf_counter() - query_start
    native_phases = (
        prepared_dataset.last_compact_summary_batch_phase_timings()
        if hasattr(prepared_dataset, "last_compact_summary_batch_phase_timings")
        else {}
    )
    summary_primitives = _summary_primitives(normalized_requests)
    summary_contracts = _summary_contracts(normalized_requests)
    return {
        "primitive": "DB_COMPACT_SUMMARY",
        "summary_primitives": summary_primitives,
        "summary_contracts": summary_contracts,
        "backend": normalized_backend,
        "prepared": True,
        "materialization_free": True,
        "request_count": len(normalized_requests),
        "request_operations": tuple(str(request["operation"]) for request in normalized_requests),
        "result_layout": "aggregate_scan_count_and_grouped_integer_maps",
        "results": results,
        "native_db_phases": native_phases,
        "run_phases": {
            "query_generic_db_compact_summary_batch_sec": query_sec,
        },
        "claim_boundary": (
            "Generic v1.5 prepared DB compact-summary primitive only: scan count, grouped "
            "integer count, and grouped integer sum over an application-owned denormalized table; "
            "not SQL, DBMS behavior, joins, indexes, transactions, query planning, row output, "
            "or public speedup wording."
        ),
    }
