from __future__ import annotations

from typing import Any

import numpy as np


ACTIVE_QUERY_STATUS_MACHINE_CONTRACT = "generic_active_query_status_machine_reference_v1"

ACTIVE_QUERY_STATUS_KIND_CODES = {
    "completed": 1,
    "offload": 2,
    "miss": 3,
    "aborted": 4,
}

ACTIVE_QUERY_ABORT_REASON_CODES = {
    "upper_bound_not_exceeding_global_bound": 1,
}

ACTIVE_QUERY_OFFLOAD_ROW_SCHEMA = (
    "active_queue_index",
    "query_row_id",
    "source_id",
    "cell_id",
    "work_count",
    "lower_bound_sq",
    "upper_bound_sq",
    "current_best_sq",
)

ACTIVE_QUERY_TERMINAL_ROW_SCHEMA = (
    "active_queue_index",
    "query_row_id",
    "source_id",
    "status_code",
    "nearest_item_id",
    "nearest_distance_sq",
)

ACTIVE_QUERY_FRONTIER_BRIDGE_CONTRACT = "generic_active_query_status_from_frontier_rows_v1"
ACTIVE_QUERY_MULTIROUND_STATUS_CONTRACT = "generic_active_query_multiround_status_reference_v1"
ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT = "generic_active_query_status_trace_summary_v1"
ACTIVE_QUERY_STATUS_STREAM_NATIVE_ABI_CONTRACT = "generic_active_query_status_stream_native_abi_v1"
ACTIVE_QUERY_STATUS_STATE_MACHINE_NATIVE_SPIKE_CONTRACT = (
    "generic_active_query_status_state_machine_native_spike_v1"
)
ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT = (
    "generic_native_payload_transition_trace_stream_contract_v1"
)
ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT = (
    "generic_native_payload_transition_trace_summary_v1"
)
_ACTIVE_QUERY_TRACE_FNV64_OFFSET = 1469598103934665603
_ACTIVE_QUERY_TRACE_FNV64_PRIME = 1099511628211
_ACTIVE_QUERY_TRACE_U64_MASK = (1 << 64) - 1

ACTIVE_QUERY_STATUS_STREAM_NATIVE_ROW_SCHEMA = (
    "active_queue_index",
    "query_row_id",
    "source_id",
    "cell_id",
    "status_code",
    "transition_phase_code",
    "current_best_before_sq",
    "current_best_after_sq",
)

ACTIVE_QUERY_STATUS_STREAM_NATIVE_TELEMETRY_SCHEMA = (
    "raw_offload_rows_before_sort_reduce",
    "raw_offload_row_hash_or_sample_rows",
    "status_count_offloading",
    "feedback_update_count_or_not_applicable",
    "miss_count",
    "completed_count",
    "aborted_count",
)

ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_ROW_SCHEMA = (
    "active_queue_index",
    "query_row_id",
    "source_id",
    "primitive_or_cell_id",
    "cell_namespace_code",
    "status_code",
    "transition_phase_code",
    "current_best_before_sq",
    "current_best_after_sq",
    "lower_bound_sq",
    "upper_bound_sq",
    "work_count",
    "payload_event_ordinal",
)

ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_TELEMETRY_SCHEMA = (
    "active_query_count",
    "raw_transition_row_count",
    "raw_transition_row_hash_or_deterministic_samples",
    "status_count_offloading",
    "status_count_completed",
    "status_count_miss",
    "status_count_aborted",
    "feedback_update_count_or_not_applicable",
    "row_capacity",
    "overflowed",
)

_ACTIVE_QUERY_STATUS_STREAM_NATIVE_FORBIDDEN_TOKENS = (
    "x" + "hd",
    "x-" + "hd",
    "haus" + "dorff",
    "pa" + "per",
    "hd_" + "exec",
    "fig" + "ure",
)


def _i64(values: Any, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.int64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional array")
    return array


def _f64(values: Any, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional array")
    return array


def _empty_offload_columns() -> dict[str, np.ndarray]:
    return {
        "active_queue_indices": np.asarray([], dtype=np.int64),
        "query_row_ids": np.asarray([], dtype=np.int64),
        "source_ids": np.asarray([], dtype=np.int64),
        "cell_ids": np.asarray([], dtype=np.int64),
        "work_counts": np.asarray([], dtype=np.int64),
        "lower_bounds_sq": np.asarray([], dtype=np.float64),
        "upper_bounds_sq": np.asarray([], dtype=np.float64),
        "current_best_sq": np.asarray([], dtype=np.float64),
    }


def _empty_terminal_columns() -> dict[str, np.ndarray]:
    return {
        "active_queue_indices": np.asarray([], dtype=np.int64),
        "query_row_ids": np.asarray([], dtype=np.int64),
        "source_ids": np.asarray([], dtype=np.int64),
        "status_codes": np.asarray([], dtype=np.int64),
        "nearest_item_ids": np.asarray([], dtype=np.int64),
        "nearest_distance_sq": np.asarray([], dtype=np.float64),
    }


def _column_mapping(table: Any, name: str) -> dict[str, Any]:
    if not isinstance(table, dict):
        raise ValueError(f"{name} must be a mapping")
    columns = table.get("columns", table)
    if not isinstance(columns, dict):
        raise ValueError(f"{name} columns must be a mapping")
    return columns


def _default_sample_indices(row_count: int) -> np.ndarray:
    if row_count <= 0:
        return np.asarray([], dtype=np.int64)
    if row_count == 1:
        return np.asarray([0], dtype=np.int64)
    middle = row_count // 2
    return np.asarray(sorted({0, middle, row_count - 1}), dtype=np.int64)


def _fnv1a_u64_from_i64_columns(columns: dict[str, np.ndarray], names: tuple[str, ...]) -> int:
    value = _ACTIVE_QUERY_TRACE_FNV64_OFFSET
    if not names:
        raise ValueError("hash column list must not be empty")
    row_count = next(iter(columns.values())).size if columns else 0
    for row_index in range(row_count):
        for name in names:
            cell = int(columns[name][row_index]) & _ACTIVE_QUERY_TRACE_U64_MASK
            value ^= cell
            value = (value * _ACTIVE_QUERY_TRACE_FNV64_PRIME) & _ACTIVE_QUERY_TRACE_U64_MASK
    return int(value)


def active_query_status_trace_summary_numpy_columns(
    offload_rows,
    *,
    active_queue_indices=None,
    hash_columns=("source_ids", "cell_ids"),
    sample_columns=("source_ids", "cell_ids"),
    sample_indices=None,
    return_metadata: bool = False,
):
    """Summarize generic active-query offload rows for status-stream auditing.

    The summary is app-neutral: it reports row counts, a deterministic integer
    hash over selected integer columns, and a small deterministic sample.
    Applications may compare this shape to their own oracle, but this function
    does not encode app option names or external implementation semantics.
    """

    columns = _column_mapping(offload_rows, "offload_rows")
    hash_columns = tuple(str(name) for name in hash_columns)
    sample_columns = tuple(str(name) for name in sample_columns)
    required = tuple(dict.fromkeys(hash_columns + sample_columns))
    missing = [name for name in required if name not in columns]
    if missing:
        raise ValueError(f"offload row table missing required columns: {', '.join(missing)}")

    arrays: dict[str, np.ndarray] = {}
    row_count: int | None = None
    for name in required:
        arrays[name] = _i64(columns[name], name)
        if row_count is None:
            row_count = int(arrays[name].size)
        elif arrays[name].size != row_count:
            raise ValueError("all summarized offload row columns must have the same shape")
    if row_count is None:
        row_count = 0

    if active_queue_indices is None:
        active_count = None
    else:
        active_count = int(_i64(active_queue_indices, "active queue indices").size)

    if sample_indices is None:
        sample_idx = _default_sample_indices(row_count)
    else:
        sample_idx = _i64(sample_indices, "sample indices")
        if np.any(sample_idx < 0) or np.any(sample_idx >= row_count):
            raise ValueError("sample indices must be within the offload row table")
    sample_payload = {
        name: arrays[name][sample_idx].astype(np.int64).tolist()
        for name in sample_columns
    }

    summary = {
        "schema": "rtdl.generic.active_query_status_trace_summary.v1",
        "contract": ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT,
        "app_semantics": "none",
        "row_count": int(row_count),
        "status_count_offloading": int(row_count),
        "active_query_count": active_count,
        "raw_offload_row_hash": _fnv1a_u64_from_i64_columns(arrays, hash_columns),
        "hash_columns": list(hash_columns),
        "sample_indices": sample_idx.astype(np.int64).tolist(),
        "sample_columns": list(sample_columns),
        "samples": sample_payload,
    }
    if return_metadata:
        summary["metadata"] = {
            "adapter": "active_query_status_trace_summary_numpy_columns",
            "partner": "numpy",
            "contract": ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT,
            "hash_contract": "fnv1a_u64_over_selected_int64_columns",
            "default_hash_offset": _ACTIVE_QUERY_TRACE_FNV64_OFFSET,
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_cpu_reference_only",
            "explicit_app_option_support_claimed": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return summary


def active_query_status_stream_native_abi_contract() -> dict[str, Any]:
    """Describe the generic native active-query status-stream ABI target.

    This is a contract description, not an executable backend.  Native engines
    that implement it must expose row-level transition state and telemetry
    sufficient for comparison against an external status oracle.  The contract
    is deliberately app-neutral and carries no benchmark-specific option names.
    """

    return {
        "contract": ACTIVE_QUERY_STATUS_STREAM_NATIVE_ABI_CONTRACT,
        "status": "specified_native_abi_no_backend_implementation",
        "executable": False,
        "app_generic": True,
        "reference_contract": ACTIVE_QUERY_MULTIROUND_STATUS_CONTRACT,
        "single_round_reference_contract": ACTIVE_QUERY_STATUS_MACHINE_CONTRACT,
        "trace_summary_contract": ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT,
        "input_state_schema": (
            "active_queue_index",
            "query_row_id",
            "source_id",
            "current_best_sq",
            "current_best_item_id",
        ),
        "output_row_schema": ACTIVE_QUERY_STATUS_STREAM_NATIVE_ROW_SCHEMA,
        "telemetry_schema": ACTIVE_QUERY_STATUS_STREAM_NATIVE_TELEMETRY_SCHEMA,
        "status_kind_codes": dict(ACTIVE_QUERY_STATUS_KIND_CODES),
        "transition_phase_code_semantics": (
            "engine-defined generic phase code; applications may map it to an "
            "external oracle only outside RTDL core"
        ),
        "required_comparison_fields": (
            "row_count",
            "row_hash_or_deterministic_samples",
            "status_count_offloading",
            "feedback_update_count_or_not_applicable",
            "miss_count",
            "completed_count",
            "aborted_count",
        ),
        "state_requirements": (
            "current-best state is keyed by active_queue_index",
            "feedback updates must be explicit or explicitly not applicable",
            "terminal status rows must distinguish miss, completed, and aborted",
            "overflow must fail closed without partial success claims",
        ),
        "forbidden_backend_behavior": (
            "hard-coded per-workload row fanout",
            "benchmark option names in native or core symbols",
            "claiming parity without row count plus hash or sample evidence",
        ),
        "overflow_policy": "fail_closed_no_partial_rows",
        "native_engine_app_specific": False,
        "explicit_app_option_support_claimed": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }


def validate_active_query_status_stream_native_abi_contract(
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the generic native active-query status-stream ABI contract."""

    contract = active_query_status_stream_native_abi_contract() if contract is None else dict(contract)
    required_fields = {
        "contract",
        "status",
        "executable",
        "app_generic",
        "reference_contract",
        "output_row_schema",
        "telemetry_schema",
        "overflow_policy",
    }
    missing = sorted(required_fields.difference(contract))
    if missing:
        return {
            "status": "reject",
            "reason": f"missing required fields: {', '.join(missing)}",
            "contract": contract,
        }
    if contract["contract"] != ACTIVE_QUERY_STATUS_STREAM_NATIVE_ABI_CONTRACT:
        return {
            "status": "reject",
            "reason": "unexpected contract identifier",
            "contract": contract,
        }
    if tuple(contract["output_row_schema"]) != ACTIVE_QUERY_STATUS_STREAM_NATIVE_ROW_SCHEMA:
        return {
            "status": "reject",
            "reason": "unexpected output row schema",
            "contract": contract,
        }
    if tuple(contract["telemetry_schema"]) != ACTIVE_QUERY_STATUS_STREAM_NATIVE_TELEMETRY_SCHEMA:
        return {
            "status": "reject",
            "reason": "unexpected telemetry schema",
            "contract": contract,
        }
    if contract["executable"] is not False:
        return {
            "status": "reject",
            "reason": "contract description must not claim backend execution",
            "contract": contract,
        }
    if contract["app_generic"] is not True:
        return {
            "status": "reject",
            "reason": "contract must be app generic",
            "contract": contract,
        }
    lowered = str(contract).lower()
    leaked = [token for token in _ACTIVE_QUERY_STATUS_STREAM_NATIVE_FORBIDDEN_TOKENS if token in lowered]
    if leaked:
        return {
            "status": "reject",
            "reason": f"app identity token leaked into contract: {', '.join(leaked)}",
            "contract": contract,
        }
    return {
        "status": "accept",
        "contract": contract,
        "checked_fields": tuple(sorted(required_fields)),
    }


def active_query_status_state_machine_native_spike_contract() -> dict[str, Any]:
    """Describe the next generic native active-query state-machine spike.

    The contract is intentionally design-only. It defines the semantic surface
    a native engine must expose before an app may compare against an external
    traversal-state oracle. It is not an executable backend and it does not
    authorize app-specific option support.
    """

    return {
        "contract": ACTIVE_QUERY_STATUS_STATE_MACHINE_NATIVE_SPIKE_CONTRACT,
        "status": "specified_design_only_no_backend_implementation",
        "executable": False,
        "app_generic": True,
        "builds_on_contract": ACTIVE_QUERY_STATUS_STREAM_NATIVE_ABI_CONTRACT,
        "reference_contracts": (
            ACTIVE_QUERY_STATUS_MACHINE_CONTRACT,
            ACTIVE_QUERY_MULTIROUND_STATUS_CONTRACT,
            ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT,
        ),
        "required_emission_points": (
            {
                "name": "raw_offload_before_continuation_reduce",
                "must_happen_before": (
                    "row collapse",
                    "sort or unique",
                    "continuation feedback",
                    "light-row exact continuation",
                ),
                "required_columns": (
                    "active_queue_index",
                    "query_row_id",
                    "source_id",
                    "cell_id",
                    "status_code",
                    "transition_phase_code",
                    "current_best_before_sq",
                    "current_best_after_sq",
                ),
                "purpose": "preserve raw offload denominator before downstream state changes",
            },
            {
                "name": "post_continuation_feedback",
                "must_happen_after": ("continuation feedback",),
                "required_columns": (
                    "active_queue_index",
                    "current_best_before_sq",
                    "current_best_after_sq",
                    "feedback_applied",
                ),
                "purpose": "make state feedback explicit rather than inferred from final scalar output",
            },
        ),
        "required_telemetry": (
            "active_query_count",
            "raw_offload_row_count",
            "raw_offload_row_hash_or_deterministic_samples",
            "status_count_offloading",
            "status_count_aborted",
            "status_count_miss",
            "status_count_completed",
            "feedback_update_count",
            "row_capacity",
            "overflowed",
        ),
        "success_gates": (
            "synthetic_non_app_raw_offload_rows",
            "bounded_app_oracle_row_count_and_hash",
            "full_external_oracle_row_count_hash_status_and_feedback",
        ),
        "required_fail_closed_rules": (
            "overflow_returns_no_partial_success_claim",
            "row_count_mismatch_keeps_external_option_unsupported",
            "hash_or_sample_mismatch_keeps_external_option_unsupported",
            "feedback_mismatch_keeps_external_option_unsupported",
        ),
        "forbidden_backend_behavior": (
            "hard_coded_row_fanout_per_active_query",
            "app_option_names_in_native_symbols",
            "app_dataset_names_in_core_or_native",
            "external_result_claim_without_row_hash_feedback_gate",
        ),
        "native_engine_app_specific": False,
        "explicit_app_option_support_claimed": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }


def validate_active_query_status_state_machine_native_spike_contract(
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the generic native active-query state-machine spike contract."""

    contract = (
        active_query_status_state_machine_native_spike_contract()
        if contract is None
        else dict(contract)
    )
    required_fields = {
        "contract",
        "status",
        "executable",
        "app_generic",
        "required_emission_points",
        "required_telemetry",
        "success_gates",
        "required_fail_closed_rules",
        "forbidden_backend_behavior",
    }
    missing = sorted(required_fields.difference(contract))
    if missing:
        return {
            "status": "reject",
            "reason": f"missing required fields: {', '.join(missing)}",
            "contract": contract,
        }
    if contract["contract"] != ACTIVE_QUERY_STATUS_STATE_MACHINE_NATIVE_SPIKE_CONTRACT:
        return {
            "status": "reject",
            "reason": "unexpected contract identifier",
            "contract": contract,
        }
    if contract["executable"] is not False:
        return {
            "status": "reject",
            "reason": "state-machine spike contract must not claim backend execution",
            "contract": contract,
        }
    if contract["app_generic"] is not True:
        return {
            "status": "reject",
            "reason": "state-machine spike contract must be app generic",
            "contract": contract,
        }

    emission_points = contract["required_emission_points"]
    if not isinstance(emission_points, tuple) or not emission_points:
        return {
            "status": "reject",
            "reason": "required emission points must be a non-empty tuple",
            "contract": contract,
        }
    emission_names = {
        str(point.get("name", ""))
        for point in emission_points
        if isinstance(point, dict)
    }
    if "raw_offload_before_continuation_reduce" not in emission_names:
        return {
            "status": "reject",
            "reason": "missing raw offload emission point before continuation/reduce",
            "contract": contract,
        }
    if "post_continuation_feedback" not in emission_names:
        return {
            "status": "reject",
            "reason": "missing post-continuation feedback emission point",
            "contract": contract,
        }

    telemetry = tuple(contract["required_telemetry"])
    for required_name in (
        "raw_offload_row_count",
        "raw_offload_row_hash_or_deterministic_samples",
        "feedback_update_count",
        "overflowed",
    ):
        if required_name not in telemetry:
            return {
                "status": "reject",
                "reason": f"missing required telemetry: {required_name}",
                "contract": contract,
            }

    gates = tuple(contract["success_gates"])
    if "synthetic_non_app_raw_offload_rows" not in gates:
        return {
            "status": "reject",
            "reason": "missing synthetic non-app gate",
            "contract": contract,
        }
    if "full_external_oracle_row_count_hash_status_and_feedback" not in gates:
        return {
            "status": "reject",
            "reason": "missing full external oracle gate",
            "contract": contract,
        }

    lowered = str(contract).lower()
    leaked = [token for token in _ACTIVE_QUERY_STATUS_STREAM_NATIVE_FORBIDDEN_TOKENS if token in lowered]
    if leaked:
        return {
            "status": "reject",
            "reason": f"app identity token leaked into contract: {', '.join(leaked)}",
            "contract": contract,
        }

    return {
        "status": "accept",
        "contract": contract,
        "checked_fields": tuple(sorted(required_fields)),
        "emission_points": tuple(sorted(emission_names)),
    }


def native_payload_transition_trace_stream_contract() -> dict[str, Any]:
    """Describe a generic native payload-transition trace contract.

    This is a design/schema contract, not a backend implementation.  It narrows
    the older active-query status-stream target to rows emitted at native
    traversal or payload transition time, before downstream frontier lowering,
    row collapse, or continuation feedback can change the raw transition
    denominator.
    """

    return {
        "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT,
        "status": "specified_design_only_no_backend_implementation",
        "executable": False,
        "app_generic": True,
        "builds_on_contract": ACTIVE_QUERY_STATUS_STATE_MACHINE_NATIVE_SPIKE_CONTRACT,
        "row_schema": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_ROW_SCHEMA,
        "telemetry_schema": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_TELEMETRY_SCHEMA,
        "status_kind_codes": dict(ACTIVE_QUERY_STATUS_KIND_CODES),
        "required_emission_stage": (
            "native traversal or payload transition before frontier lowering, "
            "row collapse, sort/unique, grouped reduction, or continuation feedback"
        ),
        "cell_namespace_policy": (
            "producer must state whether primitive_or_cell_id is compact, original, "
            "backend-native, or application-mapped outside RTDL core"
        ),
        "row_order_policy": (
            "deterministic row order is preferred; otherwise the backend must provide "
            "a deterministic hash/sample policy over app-neutral integer columns"
        ),
        "success_gates": (
            "synthetic_non_app_payload_transition_trace_behavior",
            "bounded_external_oracle_sample_row_recovery",
            "full_external_oracle_row_count_hash_status_feedback",
        ),
        "required_fail_closed_rules": (
            "overflow_returns_no_partial_success_claim",
            "missing_cell_namespace_rejects_contract",
            "row_count_mismatch_keeps_external_option_unsupported",
            "hash_or_sample_mismatch_keeps_external_option_unsupported",
            "feedback_mismatch_keeps_external_option_unsupported",
        ),
        "forbidden_backend_behavior": (
            "hard_coded_row_fanout_per_active_query",
            "hard_coded_oracle_sample_rows",
            "external_option_names_in_native_symbols",
            "dataset_names_in_core_or_native",
            "external_result_claim_without_bounded_sample_recovery",
        ),
        "native_engine_app_specific": False,
        "external_option_support_claimed": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }


def validate_native_payload_transition_trace_stream_contract(
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the generic native payload-transition trace contract."""

    contract = (
        native_payload_transition_trace_stream_contract()
        if contract is None
        else dict(contract)
    )
    required_fields = {
        "contract",
        "status",
        "executable",
        "app_generic",
        "row_schema",
        "telemetry_schema",
        "required_emission_stage",
        "cell_namespace_policy",
        "success_gates",
        "required_fail_closed_rules",
        "forbidden_backend_behavior",
    }
    missing = sorted(required_fields.difference(contract))
    if missing:
        return {
            "status": "reject",
            "reason": f"missing required fields: {', '.join(missing)}",
            "contract": contract,
        }
    if contract["contract"] != ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT:
        return {
            "status": "reject",
            "reason": "unexpected contract identifier",
            "contract": contract,
        }
    if contract["executable"] is not False:
        return {
            "status": "reject",
            "reason": "payload-transition trace contract must not claim backend execution",
            "contract": contract,
        }
    if contract["app_generic"] is not True:
        return {
            "status": "reject",
            "reason": "payload-transition trace contract must be app generic",
            "contract": contract,
        }
    if tuple(contract["row_schema"]) != ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_ROW_SCHEMA:
        return {
            "status": "reject",
            "reason": "unexpected payload-transition row schema",
            "contract": contract,
        }
    if tuple(contract["telemetry_schema"]) != ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_TELEMETRY_SCHEMA:
        return {
            "status": "reject",
            "reason": "unexpected payload-transition telemetry schema",
            "contract": contract,
        }

    row_schema = tuple(contract["row_schema"])
    for required_name in (
        "primitive_or_cell_id",
        "cell_namespace_code",
        "payload_event_ordinal",
        "current_best_before_sq",
        "current_best_after_sq",
    ):
        if required_name not in row_schema:
            return {
                "status": "reject",
                "reason": f"missing required row field: {required_name}",
                "contract": contract,
            }

    telemetry = tuple(contract["telemetry_schema"])
    for required_name in (
        "raw_transition_row_count",
        "raw_transition_row_hash_or_deterministic_samples",
        "feedback_update_count_or_not_applicable",
        "overflowed",
    ):
        if required_name not in telemetry:
            return {
                "status": "reject",
                "reason": f"missing required telemetry: {required_name}",
                "contract": contract,
            }

    gates = tuple(contract["success_gates"])
    if "synthetic_non_app_payload_transition_trace_behavior" not in gates:
        return {
            "status": "reject",
            "reason": "missing synthetic non-app behavior gate",
            "contract": contract,
        }
    if "bounded_external_oracle_sample_row_recovery" not in gates:
        return {
            "status": "reject",
            "reason": "missing bounded sample-row recovery gate",
            "contract": contract,
        }
    if "full_external_oracle_row_count_hash_status_feedback" not in gates:
        return {
            "status": "reject",
            "reason": "missing full external oracle gate",
            "contract": contract,
        }

    lowered = str(contract).lower()
    leaked = [token for token in _ACTIVE_QUERY_STATUS_STREAM_NATIVE_FORBIDDEN_TOKENS if token in lowered]
    if leaked:
        return {
            "status": "reject",
            "reason": f"app identity token leaked into contract: {', '.join(leaked)}",
            "contract": contract,
        }

    return {
        "status": "accept",
        "contract": contract,
        "checked_fields": tuple(sorted(required_fields)),
    }


def payload_transition_trace_summary_numpy_columns(
    trace_rows,
    *,
    active_queue_indices=None,
    row_capacity: int | None = None,
    overflowed: bool = False,
    hash_columns=(
        "active_queue_indices",
        "primitive_or_cell_ids",
        "status_codes",
        "payload_event_ordinals",
    ),
    sample_columns=(
        "active_queue_indices",
        "source_ids",
        "primitive_or_cell_ids",
        "status_codes",
        "payload_event_ordinals",
    ),
    sample_indices=None,
    return_metadata: bool = False,
):
    """Summarize generic native payload-transition trace rows.

    This reference helper is intentionally app-neutral.  It validates the
    column shape needed by ``native_payload_transition_trace_stream_contract``
    and returns counts, a deterministic hash, and deterministic samples.  It
    does not execute a native backend and it does not claim support for any
    external application option.
    """

    columns = _column_mapping(trace_rows, "trace_rows")
    aliases = {
        "active_queue_index": "active_queue_indices",
        "query_row_id": "query_row_ids",
        "source_id": "source_ids",
        "primitive_or_cell_id": "primitive_or_cell_ids",
        "cell_namespace_code": "cell_namespace_codes",
        "status_code": "status_codes",
        "transition_phase_code": "transition_phase_codes",
        "current_best_before_sq": "current_best_before_sq",
        "current_best_after_sq": "current_best_after_sq",
        "lower_bound_sq": "lower_bounds_sq",
        "upper_bound_sq": "upper_bounds_sq",
        "work_count": "work_counts",
        "payload_event_ordinal": "payload_event_ordinals",
    }
    required_column_names = tuple(aliases.values())
    missing = [name for name in required_column_names if name not in columns]
    if missing:
        return {
            "status": "reject",
            "reason": f"payload transition trace missing required columns: {', '.join(missing)}",
            "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
        }

    int_columns = {
        "active_queue_indices",
        "query_row_ids",
        "source_ids",
        "primitive_or_cell_ids",
        "cell_namespace_codes",
        "status_codes",
        "transition_phase_codes",
        "work_counts",
        "payload_event_ordinals",
    }
    float_columns = {
        "current_best_before_sq",
        "current_best_after_sq",
        "lower_bounds_sq",
        "upper_bounds_sq",
    }
    arrays: dict[str, np.ndarray] = {}
    row_count: int | None = None
    for name in required_column_names:
        if name in int_columns:
            arrays[name] = _i64(columns[name], name)
        elif name in float_columns:
            arrays[name] = _f64(columns[name], name)
        else:  # pragma: no cover - defensive for future schema edits.
            raise AssertionError(f"unclassified payload transition column: {name}")
        if row_count is None:
            row_count = int(arrays[name].size)
        elif arrays[name].size != row_count:
            return {
                "status": "reject",
                "reason": "all payload transition trace columns must have the same shape",
                "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
            }
    row_count = 0 if row_count is None else row_count

    if row_capacity is not None and row_capacity < row_count:
        return {
            "status": "reject",
            "reason": "row_capacity is smaller than emitted payload transition rows",
            "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
            "row_count": int(row_count),
            "row_capacity": int(row_capacity),
        }
    if overflowed:
        return {
            "status": "reject",
            "reason": "overflowed payload transition trace cannot be summarized as success",
            "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
            "row_count": int(row_count),
            "row_capacity": None if row_capacity is None else int(row_capacity),
            "overflowed": True,
        }

    valid_status_codes = set(ACTIVE_QUERY_STATUS_KIND_CODES.values())
    observed_status_codes = {int(code) for code in arrays["status_codes"].tolist()}
    unknown_status_codes = sorted(observed_status_codes.difference(valid_status_codes))
    if unknown_status_codes:
        return {
            "status": "reject",
            "reason": f"unknown payload transition status codes: {unknown_status_codes}",
            "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
        }
    if np.any(arrays["cell_namespace_codes"] < 0):
        return {
            "status": "reject",
            "reason": "cell namespace codes must be non-negative",
            "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
        }
    if np.any(arrays["payload_event_ordinals"] < 0):
        return {
            "status": "reject",
            "reason": "payload event ordinals must be non-negative",
            "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
        }

    hash_columns = tuple(str(name) for name in hash_columns)
    sample_columns = tuple(str(name) for name in sample_columns)
    missing_hash_or_sample = [
        name for name in tuple(dict.fromkeys(hash_columns + sample_columns))
        if name not in arrays
    ]
    if missing_hash_or_sample:
        return {
            "status": "reject",
            "reason": f"unknown hash/sample columns: {', '.join(missing_hash_or_sample)}",
            "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
        }

    if active_queue_indices is None:
        active_count = None
    else:
        active_count = int(_i64(active_queue_indices, "active queue indices").size)

    if sample_indices is None:
        sample_idx = _default_sample_indices(row_count)
    else:
        sample_idx = _i64(sample_indices, "sample indices")
        if np.any(sample_idx < 0) or np.any(sample_idx >= row_count):
            return {
                "status": "reject",
                "reason": "sample indices must be within the payload transition row table",
                "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
            }
    sample_payload = {
        name: arrays[name][sample_idx].astype(np.int64).tolist()
        for name in sample_columns
    }

    kind_codes = ACTIVE_QUERY_STATUS_KIND_CODES
    status_counts = {
        "status_count_offloading": int(np.count_nonzero(arrays["status_codes"] == kind_codes["offload"])),
        "status_count_completed": int(np.count_nonzero(arrays["status_codes"] == kind_codes["completed"])),
        "status_count_miss": int(np.count_nonzero(arrays["status_codes"] == kind_codes["miss"])),
        "status_count_aborted": int(np.count_nonzero(arrays["status_codes"] == kind_codes["aborted"])),
    }
    summary = {
        "status": "accept",
        "schema": "rtdl.generic.payload_transition_trace_summary.v1",
        "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
        "trace_contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT,
        "app_semantics": "none",
        "row_count": int(row_count),
        "active_query_count": active_count,
        "raw_transition_row_count": int(row_count),
        "raw_transition_row_hash": _fnv1a_u64_from_i64_columns(arrays, hash_columns),
        "hash_columns": list(hash_columns),
        "sample_indices": sample_idx.astype(np.int64).tolist(),
        "sample_columns": list(sample_columns),
        "samples": sample_payload,
        "row_capacity": None if row_capacity is None else int(row_capacity),
        "overflowed": False,
        **status_counts,
    }
    if return_metadata:
        summary["metadata"] = {
            "adapter": "payload_transition_trace_summary_numpy_columns",
            "partner": "numpy",
            "contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
            "trace_contract": ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT,
            "hash_contract": "fnv1a_u64_over_selected_int64_columns",
            "default_hash_offset": _ACTIVE_QUERY_TRACE_FNV64_OFFSET,
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_cpu_reference_only",
            "external_option_support_claimed": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return summary


def apply_active_query_feedback_numpy_columns(
    active_queue_indices,
    current_best_sq,
    current_best_item_ids,
    feedback_active_queue_indices,
    feedback_best_sq,
    feedback_item_ids,
    *,
    return_metadata: bool = False,
):
    """Apply generic continuation feedback to active-query state.

    Feedback rows are keyed by ``active_queue_index``.  Lower distances win, and
    lower item ids break equal-distance ties.  Unknown feedback queue ids fail
    closed instead of being ignored because silent state drift would make later
    traversal comparisons meaningless.
    """

    active_queue_indices = _i64(active_queue_indices, "active queue indices")
    current_best_sq = _f64(current_best_sq, "current best sq")
    current_best_item_ids = _i64(current_best_item_ids, "current best item ids")
    if current_best_sq.shape != active_queue_indices.shape:
        raise ValueError("current best sq must have the same shape as active queue indices")
    if current_best_item_ids.shape != active_queue_indices.shape:
        raise ValueError("current best item ids must have the same shape as active queue indices")
    if np.unique(active_queue_indices).size != active_queue_indices.size:
        raise ValueError("active queue indices must be unique")

    feedback_active_queue_indices = _i64(feedback_active_queue_indices, "feedback active queue indices")
    feedback_best_sq = _f64(feedback_best_sq, "feedback best sq")
    feedback_item_ids = _i64(feedback_item_ids, "feedback item ids")
    if feedback_best_sq.shape != feedback_active_queue_indices.shape:
        raise ValueError("feedback best sq must have the same shape as feedback active queue indices")
    if feedback_item_ids.shape != feedback_active_queue_indices.shape:
        raise ValueError("feedback item ids must have the same shape as feedback active queue indices")

    index_by_queue = {int(queue_index): offset for offset, queue_index in enumerate(active_queue_indices)}
    updated_best = current_best_sq.copy()
    updated_items = current_best_item_ids.copy()
    applied = 0
    for queue_index, distance_sq, item_id in zip(
        feedback_active_queue_indices,
        feedback_best_sq,
        feedback_item_ids,
    ):
        queue_index_int = int(queue_index)
        if queue_index_int not in index_by_queue:
            raise ValueError("feedback active queue index is not present in active state")
        offset = index_by_queue[queue_index_int]
        candidate_distance = float(distance_sq)
        candidate_item = int(item_id)
        previous_distance = float(updated_best[offset])
        previous_item = int(updated_items[offset])
        if (
            candidate_distance < previous_distance
            or (
                candidate_distance == previous_distance
                and (previous_item < 0 or (candidate_item >= 0 and candidate_item < previous_item))
            )
        ):
            updated_best[offset] = candidate_distance
            updated_items[offset] = candidate_item
            applied += 1

    result = {
        "columns": {
            "active_queue_indices": active_queue_indices.copy(),
            "current_best_sq": updated_best,
            "current_best_item_ids": updated_items,
        }
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "apply_active_query_feedback_numpy_columns",
            "contract": ACTIVE_QUERY_STATUS_MACHINE_CONTRACT,
            "app_semantics": "none",
            "feedback_rows": int(feedback_active_queue_indices.size),
            "feedback_updates_applied": int(applied),
        }
    return result


def active_query_status_machine_reference_numpy_columns(
    query_row_ids,
    active_queue_indices,
    source_ids,
    current_best_sq,
    current_best_item_ids,
    candidate_query_row_ids,
    candidate_cell_ids,
    candidate_min_sq,
    candidate_max_sq,
    candidate_work_counts,
    *,
    candidate_exact_best_sq=None,
    candidate_exact_item_ids=None,
    heavy_threshold: int,
    radius_sq: float = float("inf"),
    global_bound_sq: float | None = None,
    row_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Run a CPU reference active-query status machine over candidate rows.

    The contract is intentionally app-neutral.  It models a common traversal
    shape: active query rows carry current-best state, light candidates can
    complete nearest updates, heavy candidates are emitted as offload rows,
    empty unresolved queries become miss rows, and optional global-bound aborts
    are explicit terminal rows.
    """

    query_row_ids = _i64(query_row_ids, "query row ids")
    active_queue_indices = _i64(active_queue_indices, "active queue indices")
    source_ids = _i64(source_ids, "source ids")
    current_best_sq = _f64(current_best_sq, "current best sq")
    current_best_item_ids = _i64(current_best_item_ids, "current best item ids")
    expected_shape = query_row_ids.shape
    for name, array in (
        ("active queue indices", active_queue_indices),
        ("source ids", source_ids),
        ("current best sq", current_best_sq),
        ("current best item ids", current_best_item_ids),
    ):
        if array.shape != expected_shape:
            raise ValueError(f"{name} must have the same shape as query row ids")
    if np.unique(query_row_ids).size != query_row_ids.size:
        raise ValueError("query row ids must be unique")
    if np.unique(active_queue_indices).size != active_queue_indices.size:
        raise ValueError("active queue indices must be unique")

    candidate_query_row_ids = _i64(candidate_query_row_ids, "candidate query row ids")
    candidate_cell_ids = _i64(candidate_cell_ids, "candidate cell ids")
    candidate_min_sq = _f64(candidate_min_sq, "candidate min sq")
    candidate_max_sq = _f64(candidate_max_sq, "candidate max sq")
    candidate_work_counts = _i64(candidate_work_counts, "candidate work counts")
    candidate_shape = candidate_query_row_ids.shape
    for name, array in (
        ("candidate cell ids", candidate_cell_ids),
        ("candidate min sq", candidate_min_sq),
        ("candidate max sq", candidate_max_sq),
        ("candidate work counts", candidate_work_counts),
    ):
        if array.shape != candidate_shape:
            raise ValueError(f"{name} must have the same shape as candidate query row ids")
    if np.any(candidate_work_counts < 0):
        raise ValueError("candidate work counts must be non-negative")
    heavy_threshold = int(heavy_threshold)
    if heavy_threshold < 0:
        raise ValueError("heavy_threshold must be non-negative")
    if row_capacity is not None:
        row_capacity = int(row_capacity)
        if row_capacity < 0:
            raise ValueError("row_capacity must be non-negative")

    if candidate_exact_best_sq is None:
        candidate_exact_best_sq = np.full(candidate_shape, np.inf, dtype=np.float64)
    else:
        candidate_exact_best_sq = _f64(candidate_exact_best_sq, "candidate exact best sq")
        if candidate_exact_best_sq.shape != candidate_shape:
            raise ValueError("candidate exact best sq must have the same shape as candidate query row ids")
    if candidate_exact_item_ids is None:
        candidate_exact_item_ids = np.full(candidate_shape, -1, dtype=np.int64)
    else:
        candidate_exact_item_ids = _i64(candidate_exact_item_ids, "candidate exact item ids")
        if candidate_exact_item_ids.shape != candidate_shape:
            raise ValueError("candidate exact item ids must have the same shape as candidate query row ids")

    radius_sq = float(radius_sq)
    global_bound_enabled = global_bound_sq is not None
    global_bound_value = float(global_bound_sq) if global_bound_sq is not None else -np.inf
    index_by_query = {int(query_id): offset for offset, query_id in enumerate(query_row_ids)}

    best_sq = current_best_sq.copy()
    best_items = current_best_item_ids.copy()
    status = np.zeros(query_row_ids.size, dtype=np.int64)
    seen_candidate = np.zeros(query_row_ids.size, dtype=bool)
    has_offload = np.zeros(query_row_ids.size, dtype=bool)
    pruned_by_radius_or_best = 0

    offload_rows: list[tuple[int, int, int, int, int, float, float, float]] = []
    aborted_rows: list[tuple[int, int, int, int, int, float]] = []

    for row_index, query_id in enumerate(candidate_query_row_ids):
        query_key = int(query_id)
        if query_key not in index_by_query:
            raise ValueError("candidate query row id is not present in active queries")
        query_offset = index_by_query[query_key]
        if status[query_offset] != 0:
            continue
        seen_candidate[query_offset] = True
        lower = float(candidate_min_sq[row_index])
        upper = float(candidate_max_sq[row_index])
        current = float(best_sq[query_offset])
        if lower > radius_sq or lower >= current:
            pruned_by_radius_or_best += 1
            continue
        if global_bound_enabled and upper <= global_bound_value:
            status[query_offset] = ACTIVE_QUERY_STATUS_KIND_CODES["aborted"]
            aborted_rows.append(
                (
                    int(active_queue_indices[query_offset]),
                    int(query_row_ids[query_offset]),
                    int(source_ids[query_offset]),
                    ACTIVE_QUERY_STATUS_KIND_CODES["aborted"],
                    int(best_items[query_offset]),
                    float(best_sq[query_offset]),
                )
            )
            continue
        if int(candidate_work_counts[row_index]) > heavy_threshold:
            has_offload[query_offset] = True
            offload_rows.append(
                (
                    int(active_queue_indices[query_offset]),
                    int(query_row_ids[query_offset]),
                    int(source_ids[query_offset]),
                    int(candidate_cell_ids[row_index]),
                    int(candidate_work_counts[row_index]),
                    lower,
                    upper,
                    current,
                )
            )
            continue
        exact_distance = float(candidate_exact_best_sq[row_index])
        exact_item = int(candidate_exact_item_ids[row_index])
        previous_item = int(best_items[query_offset])
        if (
            exact_distance < float(best_sq[query_offset])
            or (
                exact_distance == float(best_sq[query_offset])
                and (previous_item < 0 or (exact_item >= 0 and exact_item < previous_item))
            )
        ):
            best_sq[query_offset] = exact_distance
            best_items[query_offset] = exact_item

    completed_rows: list[tuple[int, int, int, int, int, float]] = []
    miss_rows: list[tuple[int, int, int, int, int, float]] = []
    for offset in range(query_row_ids.size):
        if status[offset] != 0:
            continue
        if has_offload[offset]:
            status[offset] = ACTIVE_QUERY_STATUS_KIND_CODES["offload"]
            continue
        if np.isfinite(best_sq[offset]):
            status[offset] = ACTIVE_QUERY_STATUS_KIND_CODES["completed"]
            completed_rows.append(
                (
                    int(active_queue_indices[offset]),
                    int(query_row_ids[offset]),
                    int(source_ids[offset]),
                    ACTIVE_QUERY_STATUS_KIND_CODES["completed"],
                    int(best_items[offset]),
                    float(best_sq[offset]),
                )
            )
        else:
            status[offset] = ACTIVE_QUERY_STATUS_KIND_CODES["miss"]
            miss_rows.append(
                (
                    int(active_queue_indices[offset]),
                    int(query_row_ids[offset]),
                    int(source_ids[offset]),
                    ACTIVE_QUERY_STATUS_KIND_CODES["miss"],
                    -1,
                    float("inf"),
                )
            )

    attempted_rows = len(offload_rows) + len(completed_rows) + len(miss_rows) + len(aborted_rows)
    overflowed = row_capacity is not None and attempted_rows > row_capacity

    if overflowed:
        offload_columns = _empty_offload_columns()
        completed_columns = _empty_terminal_columns()
        miss_columns = _empty_terminal_columns()
        aborted_columns = _empty_terminal_columns()
        emitted_rows = 0
    else:
        offload_columns = _offload_rows_to_columns(offload_rows)
        completed_columns = _terminal_rows_to_columns(completed_rows)
        miss_columns = _terminal_rows_to_columns(miss_rows)
        aborted_columns = _terminal_rows_to_columns(aborted_rows)
        emitted_rows = attempted_rows

    result = {
        "offload_rows": offload_columns,
        "completed_rows": completed_columns,
        "miss_rows": miss_columns,
        "aborted_rows": aborted_columns,
        "updated_state": {
            "active_queue_indices": active_queue_indices.copy(),
            "query_row_ids": query_row_ids.copy(),
            "source_ids": source_ids.copy(),
            "current_best_sq": best_sq,
            "current_best_item_ids": best_items,
            "status_codes": status,
        },
        "telemetry": {
            "schema": "rtdl.generic.active_query_status_machine.telemetry.v1",
            "active_query_count": int(query_row_ids.size),
            "candidate_row_count": int(candidate_query_row_ids.size),
            "offload_row_count": 0 if overflowed else len(offload_rows),
            "completed_row_count": 0 if overflowed else len(completed_rows),
            "miss_row_count": 0 if overflowed else len(miss_rows),
            "aborted_row_count": 0 if overflowed else len(aborted_rows),
            "attempted_output_row_count": int(attempted_rows),
            "emitted_output_row_count": int(emitted_rows),
            "pruned_by_radius_or_current_best_count": int(pruned_by_radius_or_best),
            "queries_with_candidates": int(np.count_nonzero(seen_candidate)),
            "overflowed": bool(overflowed),
        },
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "active_query_status_machine_reference_numpy_columns",
            "partner": "numpy",
            "contract": ACTIVE_QUERY_STATUS_MACHINE_CONTRACT,
            "offload_row_schema": ACTIVE_QUERY_OFFLOAD_ROW_SCHEMA,
            "terminal_row_schema": ACTIVE_QUERY_TERMINAL_ROW_SCHEMA,
            "status_kind_codes": dict(ACTIVE_QUERY_STATUS_KIND_CODES),
            "abort_reason_codes": dict(ACTIVE_QUERY_ABORT_REASON_CODES),
            "heavy_threshold": heavy_threshold,
            "radius_sq": radius_sq,
            "global_bound_sq": None if global_bound_sq is None else global_bound_value,
            "row_capacity": None if row_capacity is None else int(row_capacity),
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_cpu_reference_only",
            "explicit_app_option_support_claimed": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def active_query_status_from_frontier_row_table_numpy_columns(
    query_row_ids,
    active_queue_indices,
    source_ids,
    current_best_sq,
    current_best_item_ids,
    frontier_row_table,
    *,
    candidate_exact_best_sq=None,
    candidate_exact_item_ids=None,
    heavy_threshold: int,
    radius_sq: float = float("inf"),
    global_bound_sq: float | None = None,
    row_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Lower generic cell-MBR frontier rows into active-query status rows.

    This is the bridge between a native frontier row producer and the generic
    active-query state-machine reference.  It intentionally treats the frontier
    table as an app-neutral candidate stream: point counts become work counts,
    min/max distances become squared lower/upper bounds, and optional exact
    per-row nearest results can update current-best state for light rows.
    """

    if not isinstance(frontier_row_table, dict):
        raise ValueError("frontier_row_table must be a mapping")
    table_columns = frontier_row_table.get("columns", frontier_row_table)
    if not isinstance(table_columns, dict):
        raise ValueError("frontier_row_table columns must be a mapping")
    required = (
        "query_row_ids",
        "cell_ids",
        "point_counts",
        "min_distances",
        "max_distances",
    )
    missing = [name for name in required if name not in table_columns]
    if missing:
        raise ValueError(f"frontier row table missing required columns: {', '.join(missing)}")

    candidate_query_row_ids = _i64(table_columns["query_row_ids"], "frontier query row ids")
    candidate_cell_ids = _i64(table_columns["cell_ids"], "frontier cell ids")
    candidate_work_counts = _i64(table_columns["point_counts"], "frontier point counts")
    candidate_min_distances = _f64(table_columns["min_distances"], "frontier min distances")
    candidate_max_distances = _f64(table_columns["max_distances"], "frontier max distances")
    candidate_shape = candidate_query_row_ids.shape
    for name, array in (
        ("frontier cell ids", candidate_cell_ids),
        ("frontier point counts", candidate_work_counts),
        ("frontier min distances", candidate_min_distances),
        ("frontier max distances", candidate_max_distances),
    ):
        if array.shape != candidate_shape:
            raise ValueError(f"{name} must have the same shape as frontier query row ids")
    if np.any(candidate_work_counts < 0):
        raise ValueError("frontier point counts must be non-negative")
    if np.any(candidate_min_distances < 0.0) or np.any(candidate_max_distances < 0.0):
        raise ValueError("frontier distances must be non-negative")
    if np.any(candidate_max_distances < candidate_min_distances):
        raise ValueError("frontier max distances must be greater than or equal to min distances")

    result = active_query_status_machine_reference_numpy_columns(
        query_row_ids,
        active_queue_indices,
        source_ids,
        current_best_sq,
        current_best_item_ids,
        candidate_query_row_ids,
        candidate_cell_ids,
        candidate_min_distances * candidate_min_distances,
        candidate_max_distances * candidate_max_distances,
        candidate_work_counts,
        candidate_exact_best_sq=candidate_exact_best_sq,
        candidate_exact_item_ids=candidate_exact_item_ids,
        heavy_threshold=heavy_threshold,
        radius_sq=radius_sq,
        global_bound_sq=global_bound_sq,
        row_capacity=row_capacity,
        return_metadata=return_metadata,
    )
    if return_metadata:
        metadata = dict(result.get("metadata", {}))
        metadata.update(
            {
                "adapter": "active_query_status_from_frontier_row_table_numpy_columns",
                "contract": ACTIVE_QUERY_FRONTIER_BRIDGE_CONTRACT,
                "reference_contract": ACTIVE_QUERY_STATUS_MACHINE_CONTRACT,
                "frontier_row_count": int(candidate_query_row_ids.size),
                "frontier_row_contract": "generic_cell_mbr_nearest_frontier_row_table",
                "frontier_kind_codes_observed": (
                    tuple(int(value) for value in np.unique(_i64(table_columns["frontier_kind_codes"], "frontier kind codes")))
                    if "frontier_kind_codes" in table_columns
                    else None
                ),
                "app_semantics": "none",
                "native_engine_row_contract": "native_frontier_rows_lowered_to_cpu_reference",
                "explicit_app_option_support_claimed": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            }
        )
        result["metadata"] = metadata
    return result


def active_query_status_multiround_reference_numpy_columns(
    query_row_ids,
    active_queue_indices,
    source_ids,
    current_best_sq,
    current_best_item_ids,
    round_candidate_tables,
    *,
    heavy_threshold: int,
    radius_sq: float = float("inf"),
    global_bound_sq: float | None = None,
    continue_status_kinds=("offload",),
    return_metadata: bool = False,
):
    """Run a generic multi-round active-query status reference.

    Each round consumes candidate rows for the currently active queries, emits
    raw offload/completed/miss/aborted rows, optionally applies continuation
    feedback keyed by ``active_queue_index``, and carries selected status kinds
    into the next round.  The function is deliberately app-neutral: it models a
    reusable iterative traversal shape, not an app-specific option kernel.
    """

    query_row_ids = _i64(query_row_ids, "query row ids")
    active_queue_indices = _i64(active_queue_indices, "active queue indices")
    source_ids = _i64(source_ids, "source ids")
    current_best_sq = _f64(current_best_sq, "current best sq")
    current_best_item_ids = _i64(current_best_item_ids, "current best item ids")
    expected_shape = query_row_ids.shape
    for name, array in (
        ("active queue indices", active_queue_indices),
        ("source ids", source_ids),
        ("current best sq", current_best_sq),
        ("current best item ids", current_best_item_ids),
    ):
        if array.shape != expected_shape:
            raise ValueError(f"{name} must have the same shape as query row ids")
    if np.unique(query_row_ids).size != query_row_ids.size:
        raise ValueError("query row ids must be unique")
    if np.unique(active_queue_indices).size != active_queue_indices.size:
        raise ValueError("active queue indices must be unique")

    if isinstance(round_candidate_tables, dict):
        raise ValueError("round_candidate_tables must be a sequence of mappings")
    rounds = list(round_candidate_tables)
    if not rounds:
        raise ValueError("round_candidate_tables must contain at least one round")

    continue_codes: set[int] = set()
    for kind in continue_status_kinds:
        if kind not in ACTIVE_QUERY_STATUS_KIND_CODES:
            raise ValueError(f"unknown continue status kind: {kind}")
        continue_codes.add(ACTIVE_QUERY_STATUS_KIND_CODES[kind])

    active = {
        "query_row_ids": query_row_ids.copy(),
        "active_queue_indices": active_queue_indices.copy(),
        "source_ids": source_ids.copy(),
        "current_best_sq": current_best_sq.copy(),
        "current_best_item_ids": current_best_item_ids.copy(),
    }

    round_summaries: list[dict[str, Any]] = []
    round_results: list[dict[str, Any]] = []
    offload_sections: list[dict[str, np.ndarray]] = []
    completed_sections: list[dict[str, np.ndarray]] = []
    miss_sections: list[dict[str, np.ndarray]] = []
    aborted_sections: list[dict[str, np.ndarray]] = []
    total_feedback_rows = 0
    total_feedback_updates = 0

    for round_index, round_table in enumerate(rounds):
        if not isinstance(round_table, dict):
            raise ValueError("each round candidate table must be a mapping")
        columns = round_table.get("columns", round_table)
        if not isinstance(columns, dict):
            raise ValueError("round candidate table columns must be a mapping")
        required = (
            "candidate_query_row_ids",
            "candidate_cell_ids",
            "candidate_min_sq",
            "candidate_max_sq",
            "candidate_work_counts",
        )
        missing = [name for name in required if name not in columns]
        if missing:
            raise ValueError(f"round candidate table missing required columns: {', '.join(missing)}")

        round_result = active_query_status_machine_reference_numpy_columns(
            active["query_row_ids"],
            active["active_queue_indices"],
            active["source_ids"],
            active["current_best_sq"],
            active["current_best_item_ids"],
            columns["candidate_query_row_ids"],
            columns["candidate_cell_ids"],
            columns["candidate_min_sq"],
            columns["candidate_max_sq"],
            columns["candidate_work_counts"],
            candidate_exact_best_sq=columns.get("candidate_exact_best_sq"),
            candidate_exact_item_ids=columns.get("candidate_exact_item_ids"),
            heavy_threshold=heavy_threshold,
            radius_sq=radius_sq,
            global_bound_sq=global_bound_sq,
            row_capacity=round_table.get("row_capacity"),
            return_metadata=True,
        )
        if round_result["telemetry"]["overflowed"]:
            raise ValueError("round status reference overflowed")

        state = round_result["updated_state"]
        feedback_rows = 0
        feedback_updates = 0
        feedback_queue_indices = columns.get("feedback_active_queue_indices")
        if feedback_queue_indices is not None:
            for required_feedback in ("feedback_best_sq", "feedback_item_ids"):
                if required_feedback not in columns:
                    raise ValueError("feedback rows require feedback_best_sq and feedback_item_ids")
            feedback = apply_active_query_feedback_numpy_columns(
                state["active_queue_indices"],
                state["current_best_sq"],
                state["current_best_item_ids"],
                feedback_queue_indices,
                columns["feedback_best_sq"],
                columns["feedback_item_ids"],
                return_metadata=True,
            )
            state = dict(state)
            state["current_best_sq"] = feedback["columns"]["current_best_sq"]
            state["current_best_item_ids"] = feedback["columns"]["current_best_item_ids"]
            feedback_rows = int(feedback["metadata"]["feedback_rows"])
            feedback_updates = int(feedback["metadata"]["feedback_updates_applied"])
            total_feedback_rows += feedback_rows
            total_feedback_updates += feedback_updates

        status_codes = _i64(state["status_codes"], "round status codes")
        continue_mask = np.asarray([int(value) in continue_codes for value in status_codes], dtype=bool)
        active_next = {
            "query_row_ids": _i64(state["query_row_ids"], "round query row ids")[continue_mask],
            "active_queue_indices": _i64(state["active_queue_indices"], "round active queue indices")[continue_mask],
            "source_ids": _i64(state["source_ids"], "round source ids")[continue_mask],
            "current_best_sq": _f64(state["current_best_sq"], "round current best sq")[continue_mask],
            "current_best_item_ids": _i64(state["current_best_item_ids"], "round current best item ids")[continue_mask],
        }

        offload_sections.append(round_result["offload_rows"])
        completed_sections.append(round_result["completed_rows"])
        miss_sections.append(round_result["miss_rows"])
        aborted_sections.append(round_result["aborted_rows"])
        round_summaries.append(
            {
                "round_index": int(round_index),
                "active_query_count": int(round_result["telemetry"]["active_query_count"]),
                "candidate_row_count": int(round_result["telemetry"]["candidate_row_count"]),
                "offload_row_count": int(round_result["telemetry"]["offload_row_count"]),
                "completed_row_count": int(round_result["telemetry"]["completed_row_count"]),
                "miss_row_count": int(round_result["telemetry"]["miss_row_count"]),
                "aborted_row_count": int(round_result["telemetry"]["aborted_row_count"]),
                "feedback_row_count": feedback_rows,
                "feedback_updates_applied": feedback_updates,
                "next_active_query_count": int(active_next["query_row_ids"].size),
            }
        )
        round_results.append(round_result)
        active = active_next
        if active["query_row_ids"].size == 0:
            break

    result = {
        "round_results": round_results,
        "offload_rows": _concat_offload_columns(offload_sections),
        "completed_rows": _concat_terminal_columns(completed_sections),
        "miss_rows": _concat_terminal_columns(miss_sections),
        "aborted_rows": _concat_terminal_columns(aborted_sections),
        "final_active_state": active,
        "telemetry": {
            "schema": "rtdl.generic.active_query_multiround_status.telemetry.v1",
            "round_count": int(len(round_summaries)),
            "initial_active_query_count": int(query_row_ids.size),
            "final_active_query_count": int(active["query_row_ids"].size),
            "raw_offload_rows_before_sort_reduce": int(sum(row["offload_row_count"] for row in round_summaries)),
            "completed_row_count": int(sum(row["completed_row_count"] for row in round_summaries)),
            "miss_queue_count": int(sum(row["miss_row_count"] for row in round_summaries)),
            "aborted_row_count": int(sum(row["aborted_row_count"] for row in round_summaries)),
            "feedback_row_count": int(total_feedback_rows),
            "feedback_updates_applied": int(total_feedback_updates),
            "rounds": round_summaries,
        },
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "active_query_status_multiround_reference_numpy_columns",
            "partner": "numpy",
            "contract": ACTIVE_QUERY_MULTIROUND_STATUS_CONTRACT,
            "single_round_contract": ACTIVE_QUERY_STATUS_MACHINE_CONTRACT,
            "offload_row_schema": ACTIVE_QUERY_OFFLOAD_ROW_SCHEMA,
            "terminal_row_schema": ACTIVE_QUERY_TERMINAL_ROW_SCHEMA,
            "status_kind_codes": dict(ACTIVE_QUERY_STATUS_KIND_CODES),
            "continue_status_kinds": tuple(continue_status_kinds),
            "heavy_threshold": int(heavy_threshold),
            "radius_sq": float(radius_sq),
            "global_bound_sq": None if global_bound_sq is None else float(global_bound_sq),
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_cpu_reference_only",
            "explicit_app_option_support_claimed": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def _offload_rows_to_columns(rows: list[tuple[int, int, int, int, int, float, float, float]]) -> dict[str, np.ndarray]:
    if not rows:
        return _empty_offload_columns()
    array = np.asarray(rows, dtype=np.float64)
    return {
        "active_queue_indices": array[:, 0].astype(np.int64),
        "query_row_ids": array[:, 1].astype(np.int64),
        "source_ids": array[:, 2].astype(np.int64),
        "cell_ids": array[:, 3].astype(np.int64),
        "work_counts": array[:, 4].astype(np.int64),
        "lower_bounds_sq": array[:, 5].astype(np.float64),
        "upper_bounds_sq": array[:, 6].astype(np.float64),
        "current_best_sq": array[:, 7].astype(np.float64),
    }


def _terminal_rows_to_columns(rows: list[tuple[int, int, int, int, int, float]]) -> dict[str, np.ndarray]:
    if not rows:
        return _empty_terminal_columns()
    array = np.asarray(rows, dtype=np.float64)
    return {
        "active_queue_indices": array[:, 0].astype(np.int64),
        "query_row_ids": array[:, 1].astype(np.int64),
        "source_ids": array[:, 2].astype(np.int64),
        "status_codes": array[:, 3].astype(np.int64),
        "nearest_item_ids": array[:, 4].astype(np.int64),
        "nearest_distance_sq": array[:, 5].astype(np.float64),
    }


def _concat_offload_columns(sections: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    if not sections:
        return _empty_offload_columns()
    keys = tuple(_empty_offload_columns().keys())
    return {key: np.concatenate([section[key] for section in sections]) for key in keys}


def _concat_terminal_columns(sections: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    if not sections:
        return _empty_terminal_columns()
    keys = tuple(_empty_terminal_columns().keys())
    return {key: np.concatenate([section[key] for section in sections]) for key in keys}
