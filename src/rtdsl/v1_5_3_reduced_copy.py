from __future__ import annotations

import ctypes
from typing import Any


V1_5_3_REDUCED_COPY_STATUS = "typed_host_input_buffer_path_present_measurement_pending"
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
            "claims, stable primitive promotion, or release action."
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
