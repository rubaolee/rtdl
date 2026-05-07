from __future__ import annotations

import ctypes
import time
from typing import Any

from .v1_5_2_collect_buffers import complete_prepared_collect_k_result_buffer_descriptor
from .v1_5_2_collect_buffers import run_native_collect_k_bounded_rows_with_prepared_host_output_buffer
from .v1_5_2_collect_buffers import validate_collect_result_buffer_descriptor


V1_5_3_REDUCED_COPY_STATUS = "typed_host_input_buffer_path_and_copy_count_measurement_present"
V1_5_3_REDUCED_COPY_TRACK = "python_rtdl"
V1_5_3_REDUCED_COPY_SCOPE = (
    "typed_contiguous_host_buffers",
    "preallocated_result_buffers",
    "prepared_host_buffer_reuse",
    "prepared_device_or_staging_buffer_reuse",
)
V1_5_3_REDUCED_COPY_REQUIRED_EVIDENCE = (
    "python_materialized_rows_baseline",
    "typed_contiguous_host_buffer_path",
    "preallocated_result_buffer_reuse_path",
    "copy_count_or_transfer_count_measurement",
    "embree_optix_same_contract_parity_where_claimed",
    "external_ai_review_before_public_claims",
)
V1_5_3_REDUCED_COPY_SATISFIED_EVIDENCE = (
    "python_materialized_rows_baseline",
    "typed_contiguous_host_buffer_path",
    "preallocated_result_buffer_reuse_path",
    "copy_count_or_transfer_count_measurement",
)
V1_5_3_REDUCED_COPY_MISSING_EVIDENCE = tuple(
    item
    for item in V1_5_3_REDUCED_COPY_REQUIRED_EVIDENCE
    if item not in V1_5_3_REDUCED_COPY_SATISFIED_EVIDENCE
)
V1_5_3_REDUCED_COPY_BLOCKED_CLAIMS = (
    "true_zero_copy",
    "public_speedup",
    "whole_app_speedup",
    "stable_public_primitive",
    "release_action",
)
V1_5_3_REDUCED_COPY_ALLOWED_WORDING = (
    "reduced-copy candidate",
    "reduced-transfer candidate",
    "prepared host-buffer reuse",
    "typed contiguous host-buffer path",
)
V1_5_3_REDUCED_COPY_FORBIDDEN_WORDING = (
    "true zero-copy",
    "zero-copy speedup",
    "whole-app acceleration",
    "public speedup",
    "release-ready",
)


def v1_5_3_reduced_copy_contract() -> dict[str, Any]:
    """Return the v1.5.3 reduced-copy contract for Python+RTDL buffers."""
    return {
        "status": V1_5_3_REDUCED_COPY_STATUS,
        "track": V1_5_3_REDUCED_COPY_TRACK,
        "scope": V1_5_3_REDUCED_COPY_SCOPE,
        "required_evidence": V1_5_3_REDUCED_COPY_REQUIRED_EVIDENCE,
        "satisfied_evidence": V1_5_3_REDUCED_COPY_SATISFIED_EVIDENCE,
        "missing_evidence": V1_5_3_REDUCED_COPY_MISSING_EVIDENCE,
        "blocked_claims": V1_5_3_REDUCED_COPY_BLOCKED_CLAIMS,
        "allowed_wording": V1_5_3_REDUCED_COPY_ALLOWED_WORDING,
        "forbidden_wording": V1_5_3_REDUCED_COPY_FORBIDDEN_WORDING,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "next_implementation_lanes": (
            "add typed contiguous host input/output adapters for collect rows",
            "measure copy count against python materialized row baselines",
            "separate host reduced-copy wording from device zero-copy wording",
            "only add OptiX device/staging reuse claims after measured RTX evidence",
        ),
        "claim_boundary": (
            "v1.5.3 begins the reduced-copy lane for Python+RTDL buffer "
            "plumbing. It may describe reduced-copy or reduced-transfer "
            "candidates only after measured copy-count evidence. It does not "
            "authorize true zero-copy, public speedup wording, whole-app "
            "claims, stable primitive promotion, partner tensor handoff, or "
            "release action."
        ),
    }


def validate_v1_5_3_reduced_copy_contract() -> dict[str, Any]:
    contract = v1_5_3_reduced_copy_contract()
    if contract["status"] != V1_5_3_REDUCED_COPY_STATUS:
        raise ValueError("invalid v1.5.3 reduced-copy status")
    if contract["track"] != V1_5_3_REDUCED_COPY_TRACK:
        raise ValueError("invalid v1.5.3 reduced-copy track")
    if tuple(contract["required_evidence"]) != V1_5_3_REDUCED_COPY_REQUIRED_EVIDENCE:
        raise ValueError("v1.5.3 reduced-copy required evidence changed")
    if tuple(contract["satisfied_evidence"]) != V1_5_3_REDUCED_COPY_SATISFIED_EVIDENCE:
        raise ValueError("v1.5.3 reduced-copy satisfied evidence changed")
    if tuple(contract["missing_evidence"]) != V1_5_3_REDUCED_COPY_MISSING_EVIDENCE:
        raise ValueError("v1.5.3 reduced-copy missing evidence changed")
    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "release_action_authorized",
    ):
        if contract[flag] is not False:
            raise ValueError(f"v1.5.3 reduced-copy contract must keep {flag}=False")
    for phrase in (
        "reduced-copy lane",
        "measured copy-count evidence",
        "does not authorize true zero-copy",
        "public speedup wording",
        "whole-app claims",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in contract["claim_boundary"]:
            raise ValueError("v1.5.3 reduced-copy claim boundary is incomplete")
    return contract


def prepare_collect_k_i64_host_input_buffer(
    candidate_rows: Any,
    *,
    row_width: int,
    owner: str = "python",
) -> dict[str, Any]:
    """Prepare row-major int64 input storage for COLLECT_K_BOUNDED.

    This is a typed contiguous host-buffer path, not a zero-copy path: Python
    still converts user rows into RTDL-owned ctypes storage.
    """
    row_width = int(row_width)
    if row_width <= 0:
        raise ValueError("typed collect input buffer row_width must be positive")
    flat_values: list[int] = []
    row_count = 0
    for row in candidate_rows:
        values = (row,) if isinstance(row, int) else tuple(row)
        if len(values) != row_width:
            raise ValueError(
                "typed collect input buffer row width mismatch: "
                f"expected {row_width}, got {len(values)}"
            )
        flat_values.extend(int(value) for value in values)
        row_count += 1
    array_type = ctypes.c_int64 * len(flat_values)
    buffer = array_type(*flat_values)
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "status": "typed_contiguous_host_input_buffer_prepared",
        "track": V1_5_3_REDUCED_COPY_TRACK,
        "buffer_kind": "candidate_input",
        "dtype": "int64",
        "layout": "row_major_dense_candidate_id_rows",
        "shape": (row_count, row_width),
        "row_count": row_count,
        "row_width": row_width,
        "flat_value_count": len(flat_values),
        "device": "cpu",
        "owner": str(owner),
        "copy_boundary": "typed_contiguous_host_buffer",
        "ctypes_buffer": buffer,
        "ctypes_pointer": ctypes.cast(buffer, ctypes.POINTER(ctypes.c_int64)),
        "buffer_address": ctypes.addressof(buffer) if flat_values else None,
        "materialized_nested_python_rows_present": False,
        "typed_contiguous_host_buffer_path": True,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Typed contiguous host input buffers make Python-to-native input "
            "storage explicit for measurement and reuse planning. This path "
            "still copies user rows into ctypes host storage and does not "
            "authorize true zero-copy, public speedup wording, whole-app "
            "claims, stable primitive promotion, partner tensor handoff, or "
            "release action."
        ),
    }


def validate_collect_k_i64_host_input_buffer(buffer_descriptor: dict[str, Any]) -> dict[str, Any]:
    descriptor = dict(buffer_descriptor)
    if descriptor.get("status") != "typed_contiguous_host_input_buffer_prepared":
        raise ValueError("invalid typed collect input buffer status")
    if descriptor.get("primitive") != "COLLECT_K_BOUNDED":
        raise ValueError("typed collect input buffer must target COLLECT_K_BOUNDED")
    if descriptor.get("dtype") != "int64":
        raise ValueError("typed collect input buffer must use int64 dtype")
    if descriptor.get("copy_boundary") != "typed_contiguous_host_buffer":
        raise ValueError("typed collect input buffer has invalid copy boundary")
    row_count = int(descriptor["row_count"])
    row_width = int(descriptor["row_width"])
    if row_count < 0 or row_width <= 0:
        raise ValueError("typed collect input buffer has invalid shape")
    if tuple(descriptor["shape"]) != (row_count, row_width):
        raise ValueError("typed collect input buffer shape mismatch")
    if int(descriptor["flat_value_count"]) != row_count * row_width:
        raise ValueError("typed collect input buffer flat value count mismatch")
    if descriptor.get("typed_contiguous_host_buffer_path") is not True:
        raise ValueError("typed collect input buffer path flag must be true")
    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "release_action_authorized",
    ):
        if descriptor[flag] is not False:
            raise ValueError(f"typed collect input buffer must keep {flag}=False")
    return descriptor


def run_native_collect_k_bounded_with_typed_host_buffers(
    input_buffer_descriptor: dict[str, Any],
    prepared_output_descriptor: dict[str, Any],
    *,
    output_buffer: Any,
    library: Any,
    symbol_name: str,
    backend: str,
    candidate_source_symbol: str = "typed_contiguous_host_input_buffer",
) -> dict[str, Any]:
    """Run native collect-k using explicit typed host input and output buffers."""
    input_descriptor = validate_collect_k_i64_host_input_buffer(input_buffer_descriptor)
    prepared = validate_collect_result_buffer_descriptor(prepared_output_descriptor)
    if prepared["buffer_kind"] != "prepared_result":
        raise ValueError("typed host native collect requires prepared output descriptor")
    if prepared["device"] != "cpu":
        raise ValueError("typed host native collect requires CPU output descriptor")
    if prepared["copy_boundary"] != "prepared_host_buffer_reuse":
        raise ValueError("typed host native collect requires prepared_host_buffer_reuse output")
    if prepared["row_width"] != input_descriptor["row_width"]:
        raise ValueError("typed host native collect input/output row_width mismatch")
    if prepared.get("backend") is not None and prepared.get("backend") != backend:
        raise ValueError("typed host native collect backend mismatch")
    output_len = prepared["capacity"] * prepared["row_width"]
    if output_buffer is None and output_len != 0:
        raise ValueError("typed host native collect output_buffer is required when capacity is nonzero")
    if output_buffer is not None and len(output_buffer) < output_len:
        raise ValueError("typed host native collect output_buffer is smaller than capacity * row_width")

    symbol = getattr(library, symbol_name, None)
    if symbol is None:
        raise ValueError(f"loaded {backend} backend does not export {symbol_name}")
    symbol.argtypes = [
        ctypes.POINTER(ctypes.c_int64),
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int64),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    symbol.restype = ctypes.c_int

    output_pointer = (
        ctypes.cast(output_buffer, ctypes.POINTER(ctypes.c_int64)) if output_buffer is not None else None
    )
    emitted_count = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        input_descriptor["ctypes_pointer"],
        input_descriptor["row_count"],
        input_descriptor["row_width"],
        output_pointer,
        prepared["capacity"],
        ctypes.byref(emitted_count),
        ctypes.byref(overflowed),
        error,
        len(error),
    )
    error_text = error.value.decode("utf-8", errors="replace")
    if int(status) != 0:
        raise RuntimeError(error_text or f"{backend} collect-k symbol failed with status {status}")
    emitted = int(emitted_count.value)
    if int(overflowed.value):
        raise RuntimeError(
            "COLLECT_K_BOUNDED overflowed prepared output capacity "
            f"{prepared['capacity']}; emitted {emitted}; no partial result returned"
        )
    rows = tuple(
        tuple(
            int(output_buffer[row_index * prepared["row_width"] + column_index])
            for column_index in range(prepared["row_width"])
        )
        for row_index in range(emitted)
    )
    result = {
        "primitive": "COLLECT_K_BOUNDED",
        "status": "complete",
        "track": V1_5_3_REDUCED_COPY_TRACK,
        "backend": str(backend),
        "native_i64_adapter": True,
        "native_generic_symbol": str(symbol_name),
        "candidate_source_symbol": str(candidate_source_symbol),
        "binary_symbol_validation_present": True,
        "row_dtype": "int64",
        "row_width": prepared["row_width"],
        "capacity": prepared["capacity"],
        "valid_count": emitted,
        "emitted_count": emitted,
        "overflowed": False,
        "complete_candidate_coverage": True,
        "candidate_id_rows": rows,
        "result_layout": "dense_candidate_id_rows_with_valid_count",
        "fail_closed": True,
        "prepared_input_buffer_supplied": True,
        "prepared_output_buffer_supplied": True,
    }
    completed_descriptor = complete_prepared_collect_k_result_buffer_descriptor(
        prepared,
        result,
        backend=str(backend),
    )
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "status": "typed_host_input_prepared_host_output_native_envelope",
        "track": V1_5_3_REDUCED_COPY_TRACK,
        "backend": str(backend),
        "symbol_name": str(symbol_name),
        "candidate_source_symbol": str(candidate_source_symbol),
        "input_buffer_descriptor": input_descriptor,
        "prepared_output_descriptor": prepared,
        "result": result,
        "result_buffer_descriptor": completed_descriptor,
        "input_buffer_address": input_descriptor["buffer_address"],
        "output_buffer_address": ctypes.addressof(output_buffer) if output_buffer is not None else None,
        "typed_contiguous_host_buffer_path": True,
        "prepared_output_buffer_reused_by_python_wrapper": True,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This native envelope uses an explicit typed ctypes host input "
            "buffer and caller-owned ctypes host output buffer. It avoids "
            "wrapper-internal row reflattening for this path, but still uses "
            "host ctypes storage and does not authorize true zero-copy, public "
            "speedup wording, whole-app claims, stable primitive promotion, or "
            "partner tensor handoff, or release action."
        ),
    }


def measure_collect_k_typed_host_input_reuse(
    candidate_rows: Any,
    prepared_output_descriptor: dict[str, Any],
    *,
    output_buffer: Any,
    library: Any,
    symbol_name: str,
    backend: str,
    row_width: int,
    iterations: int = 3,
) -> dict[str, Any]:
    """Compare wrapper-internal input materialization with typed input reuse."""
    iteration_count = int(iterations)
    if iteration_count <= 0:
        raise ValueError("typed host input reuse measurement requires iterations > 0")
    prepared = validate_collect_result_buffer_descriptor(prepared_output_descriptor)
    typed_input = prepare_collect_k_i64_host_input_buffer(candidate_rows, row_width=row_width)
    baseline_runs = []
    typed_runs = []
    baseline_elapsed_total_s = 0.0
    typed_elapsed_total_s = 0.0
    for iteration in range(iteration_count):
        start = time.perf_counter()
        baseline = run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
            candidate_rows,
            prepared,
            output_buffer=output_buffer,
            library=library,
            symbol_name=symbol_name,
            candidate_source_symbol="python_materialized_rows_each_call",
            backend=backend,
        )
        baseline_elapsed_s = time.perf_counter() - start
        baseline_elapsed_total_s += baseline_elapsed_s
        baseline_runs.append(
            {
                "iteration": iteration,
                "elapsed_s": baseline_elapsed_s,
                "valid_shape": baseline["result_buffer_descriptor"]["valid_shape"],
                "input_materialization_count": 1,
                "output_buffer_reused": baseline["prepared_output_buffer_reused_by_python_wrapper"],
            }
        )
        start = time.perf_counter()
        typed = run_native_collect_k_bounded_with_typed_host_buffers(
            typed_input,
            prepared,
            output_buffer=output_buffer,
            library=library,
            symbol_name=symbol_name,
            backend=backend,
        )
        typed_elapsed_s = time.perf_counter() - start
        typed_elapsed_total_s += typed_elapsed_s
        typed_runs.append(
            {
                "iteration": iteration,
                "elapsed_s": typed_elapsed_s,
                "valid_shape": typed["result_buffer_descriptor"]["valid_shape"],
                "input_materialization_count": 0,
                "input_buffer_address": typed["input_buffer_address"],
                "output_buffer_reused": typed["prepared_output_buffer_reused_by_python_wrapper"],
            }
        )
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "status": "typed_host_input_copy_count_measurement_complete",
        "track": V1_5_3_REDUCED_COPY_TRACK,
        "backend": str(backend),
        "iterations": iteration_count,
        "baseline_path": "python_wrapper_materializes_ctypes_input_each_call",
        "typed_path": "typed_contiguous_host_input_buffer_reused_across_calls",
        "baseline_input_materialization_count": iteration_count,
        "typed_input_materialization_count": 1,
        "input_materialization_count_delta": iteration_count - 1,
        "baseline_runs": tuple(baseline_runs),
        "typed_runs": tuple(typed_runs),
        "baseline_elapsed_total_s": baseline_elapsed_total_s,
        "typed_elapsed_total_s": typed_elapsed_total_s,
        "timing_recorded_for_diagnostics_only": True,
        "copy_count_or_transfer_count_measurement": True,
        "typed_input_buffer_address": typed_input["buffer_address"],
        "prepared_output_buffer_address": ctypes.addressof(output_buffer) if output_buffer is not None else None,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This measurement compares wrapper-level input materialization "
            "counts for a Python materialized baseline and a typed contiguous "
            "host input buffer. Timing is diagnostic only. It does not "
            "authorize true zero-copy, public speedup wording, whole-app "
            "claims, stable primitive promotion, partner tensor handoff, or "
            "release action."
        ),
    }
