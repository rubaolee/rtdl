from __future__ import annotations

from typing import Any

from .v1_5_1_collect_k_bounded import collect_k_bounded_rows
from .v1_5_1_collect_k_bounded import validate_collect_k_bounded_result


V1_5_2_COLLECT_BUFFER_STATUS = "python_rtdl_buffer_contract_foundation"
V1_5_2_COLLECT_BUFFER_KINDS = ("result", "prepared_result")
V1_5_2_COLLECT_BUFFER_DEVICES = ("cpu", "cuda")
V1_5_2_COLLECT_BUFFER_DTYPES = ("int64",)
V1_5_2_COLLECT_BUFFER_LAYOUT = "row_major_dense_candidate_id_rows"
V1_5_2_COLLECT_BUFFER_OWNERS = ("python", "rtdl", "native")
V1_5_2_COLLECT_BUFFER_MUTABILITY = ("immutable", "mutable")
V1_5_2_COLLECT_BUFFER_COPY_BOUNDARIES = (
    "python_materialized_rows",
    "native_row_buffer_metadata",
    "prepared_host_buffer_reuse",
    "prepared_device_buffer_reuse",
)
V1_5_2_COLLECT_BUFFER_FORBIDDEN_CLAIMS = (
    "true_zero_copy",
    "public_speedup",
    "whole_app_speedup",
    "stable_public_primitive",
    "release_action",
)


def v1_5_2_collect_buffer_contract() -> dict[str, Any]:
    """Return the v1.5.2 app-generic collect result-buffer contract."""
    return {
        "status": V1_5_2_COLLECT_BUFFER_STATUS,
        "track": "python_rtdl",
        "buffer_kinds": V1_5_2_COLLECT_BUFFER_KINDS,
        "dtype_scope": V1_5_2_COLLECT_BUFFER_DTYPES,
        "device_scope": V1_5_2_COLLECT_BUFFER_DEVICES,
        "layout": V1_5_2_COLLECT_BUFFER_LAYOUT,
        "owner_scope": V1_5_2_COLLECT_BUFFER_OWNERS,
        "mutability_scope": V1_5_2_COLLECT_BUFFER_MUTABILITY,
        "required_fields": (
            "primitive",
            "buffer_kind",
            "dtype",
            "layout",
            "shape",
            "capacity",
            "valid_count",
            "row_width",
            "device",
            "owner",
            "mutability",
            "copy_boundary",
            "overflowed",
            "fail_closed",
        ),
        "copy_boundaries": V1_5_2_COLLECT_BUFFER_COPY_BOUNDARIES,
        "forbidden_claims": V1_5_2_COLLECT_BUFFER_FORBIDDEN_CLAIMS,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "v1.5.2 collect buffer descriptors define app-generic metadata "
            "for Python+RTDL result buffers only. They do not authorize true "
            "zero-copy, public speedup wording, whole-app claims, stable "
            "public primitive wording, partner tensor handoff, or release action."
        ),
    }


def validate_v1_5_2_collect_buffer_contract() -> dict[str, Any]:
    contract = v1_5_2_collect_buffer_contract()
    if contract["status"] != V1_5_2_COLLECT_BUFFER_STATUS:
        raise ValueError("invalid v1.5.2 collect buffer contract status")
    if tuple(contract["buffer_kinds"]) != V1_5_2_COLLECT_BUFFER_KINDS:
        raise ValueError("collect buffer kind scope changed")
    if tuple(contract["dtype_scope"]) != V1_5_2_COLLECT_BUFFER_DTYPES:
        raise ValueError("collect buffer dtype scope changed")
    if tuple(contract["device_scope"]) != V1_5_2_COLLECT_BUFFER_DEVICES:
        raise ValueError("collect buffer device scope changed")
    if tuple(contract["owner_scope"]) != V1_5_2_COLLECT_BUFFER_OWNERS:
        raise ValueError("collect buffer owner scope changed")
    if tuple(contract["mutability_scope"]) != V1_5_2_COLLECT_BUFFER_MUTABILITY:
        raise ValueError("collect buffer mutability scope changed")
    false_flags = (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "release_action_authorized",
    )
    for flag in false_flags:
        if contract[flag] is not False:
            raise ValueError(f"v1.5.2 collect buffer contract must keep {flag}=False")
    for phrase in (
        "do not authorize true zero-copy",
        "public speedup wording",
        "whole-app claims",
        "release action",
    ):
        if phrase not in contract["claim_boundary"]:
            raise ValueError("collect buffer claim boundary is incomplete")
    return contract


def collect_k_result_buffer_descriptor(
    result: dict[str, Any],
    *,
    row_width: int,
    backend: str | None = None,
    device: str = "cpu",
    owner: str = "python",
    mutability: str = "immutable",
    copy_boundary: str = "python_materialized_rows",
) -> dict[str, Any]:
    """Describe a completed collect-k result as an app-generic result buffer."""
    contract = validate_v1_5_2_collect_buffer_contract()
    if device not in V1_5_2_COLLECT_BUFFER_DEVICES:
        raise ValueError(f"unsupported collect buffer device: {device}")
    if copy_boundary not in V1_5_2_COLLECT_BUFFER_COPY_BOUNDARIES:
        raise ValueError(f"unsupported collect buffer copy_boundary: {copy_boundary}")
    validated = validate_collect_k_bounded_result(
        result,
        row_width=int(row_width),
        backend=backend,
    )
    capacity = int(validated["capacity"])
    valid_count = int(validated["valid_count"])
    descriptor = {
        "primitive": validated["primitive"],
        "status": contract["status"],
        "track": contract["track"],
        "buffer_kind": "result",
        "backend": validated.get("backend", backend),
        "dtype": "int64",
        "layout": contract["layout"],
        "shape": (capacity, int(row_width)),
        "valid_shape": (valid_count, int(row_width)),
        "capacity": capacity,
        "valid_count": valid_count,
        "row_width": int(row_width),
        "device": device,
        "owner": str(owner),
        "mutability": str(mutability),
        "copy_boundary": copy_boundary,
        "overflowed": False,
        "fail_closed": True,
        "materialized_python_rows_present": "candidate_id_rows" in validated,
        "candidate_id_rows_present": "candidate_id_rows" in validated,
        "source_result_layout": validated["result_layout"],
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": contract["claim_boundary"],
    }
    return validate_collect_result_buffer_descriptor(descriptor)


def prepare_collect_k_result_buffer_descriptor(
    *,
    capacity: int,
    row_width: int,
    backend: str | None = None,
    device: str = "cpu",
    owner: str = "rtdl",
    mutability: str = "mutable",
    copy_boundary: str = "prepared_host_buffer_reuse",
) -> dict[str, Any]:
    """Describe a caller-prepared collect-k output buffer before execution."""
    contract = validate_v1_5_2_collect_buffer_contract()
    capacity = int(capacity)
    row_width = int(row_width)
    descriptor = {
        "primitive": "COLLECT_K_BOUNDED",
        "status": contract["status"],
        "track": contract["track"],
        "buffer_kind": "prepared_result",
        "backend": backend,
        "dtype": "int64",
        "layout": contract["layout"],
        "shape": (capacity, row_width),
        "valid_shape": (0, row_width),
        "capacity": capacity,
        "valid_count": 0,
        "row_width": row_width,
        "device": device,
        "owner": str(owner),
        "mutability": str(mutability),
        "copy_boundary": copy_boundary,
        "overflowed": False,
        "fail_closed": True,
        "materialized_python_rows_present": False,
        "candidate_id_rows_present": False,
        "source_result_layout": None,
        "prepared_before_execution": True,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": contract["claim_boundary"],
    }
    return validate_collect_result_buffer_descriptor(descriptor)


def complete_prepared_collect_k_result_buffer_descriptor(
    prepared_descriptor: dict[str, Any],
    result: dict[str, Any],
    *,
    backend: str | None = None,
) -> dict[str, Any]:
    """Bind a validated collect-k result to a compatible prepared descriptor."""
    prepared = validate_collect_result_buffer_descriptor(prepared_descriptor)
    if prepared["buffer_kind"] != "prepared_result":
        raise ValueError("prepared collect buffer completion requires buffer_kind=prepared_result")
    if "row_width" in result and int(result["row_width"]) != prepared["row_width"]:
        raise ValueError("completed collect result row_width does not match prepared buffer")
    result_backend = backend if backend is not None else result.get("backend")
    result_descriptor = collect_k_result_buffer_descriptor(
        result,
        row_width=prepared["row_width"],
        backend=result_backend,
        device=prepared["device"],
        owner=prepared["owner"],
        mutability=prepared["mutability"],
        copy_boundary=prepared["copy_boundary"],
    )
    if result_descriptor["capacity"] > prepared["capacity"]:
        raise RuntimeError("completed collect result exceeds prepared buffer capacity")
    if result_descriptor["device"] != prepared["device"]:
        raise ValueError("completed collect result device does not match prepared buffer")
    prepared_backend = prepared.get("backend")
    completed_backend = result_descriptor.get("backend")
    if prepared_backend is not None and completed_backend is not None:
        if completed_backend != prepared_backend:
            raise ValueError("completed collect result backend mismatch")
    completed = {
        **result_descriptor,
        "buffer_kind": "result",
        "prepared_buffer_kind": prepared["buffer_kind"],
        "prepared_backend": prepared_backend,
        "prepared_before_execution": bool(prepared.get("prepared_before_execution", False)),
        "prepared_capacity": prepared["capacity"],
        "prepared_shape": prepared["shape"],
        "prepared_valid_shape": prepared["valid_shape"],
        "prepared_copy_boundary": prepared["copy_boundary"],
        "prepared_descriptor_compatible": True,
    }
    return validate_collect_result_buffer_descriptor(completed)


def run_collect_k_bounded_rows_with_prepared_result_buffer(
    candidate_rows: Any,
    prepared_descriptor: dict[str, Any],
) -> dict[str, Any]:
    """Run the Python reference collector through a prepared descriptor envelope."""
    prepared = validate_collect_result_buffer_descriptor(prepared_descriptor)
    if prepared["buffer_kind"] != "prepared_result":
        raise ValueError("prepared collect buffer execution requires buffer_kind=prepared_result")
    result = collect_k_bounded_rows(
        candidate_rows,
        k=prepared["capacity"],
        row_width=prepared["row_width"],
    )
    completed_descriptor = complete_prepared_collect_k_result_buffer_descriptor(
        prepared,
        result,
    )
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "status": prepared["status"],
        "track": prepared["track"],
        "execution_mode": "python_reference_prepared_descriptor_envelope",
        "backend": prepared.get("backend"),
        "prepared_descriptor": prepared,
        "result": result,
        "result_buffer_descriptor": completed_descriptor,
        "prepared_descriptor_compatible": completed_descriptor["prepared_descriptor_compatible"],
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Python reference execution envelope over prepared collect-buffer "
            "metadata only; this does not allocate native memory, prove buffer "
            "reuse, authorize zero-copy wording, or authorize performance claims."
        ),
    }


def validate_collect_result_buffer_descriptor(descriptor: dict[str, Any]) -> dict[str, Any]:
    contract = validate_v1_5_2_collect_buffer_contract()
    missing = [field for field in contract["required_fields"] if field not in descriptor]
    if missing:
        raise ValueError(f"collect result buffer descriptor missing fields: {tuple(missing)}")
    if descriptor["buffer_kind"] not in V1_5_2_COLLECT_BUFFER_KINDS:
        raise ValueError("collect result buffer descriptor has invalid buffer_kind")
    if descriptor["dtype"] not in V1_5_2_COLLECT_BUFFER_DTYPES:
        raise ValueError("collect result buffer descriptor has invalid dtype")
    if descriptor["layout"] != V1_5_2_COLLECT_BUFFER_LAYOUT:
        raise ValueError("collect result buffer descriptor has invalid layout")
    if descriptor["device"] not in V1_5_2_COLLECT_BUFFER_DEVICES:
        raise ValueError("collect result buffer descriptor has invalid device")
    if descriptor["owner"] not in V1_5_2_COLLECT_BUFFER_OWNERS:
        raise ValueError("collect result buffer descriptor has invalid owner")
    if descriptor["mutability"] not in V1_5_2_COLLECT_BUFFER_MUTABILITY:
        raise ValueError("collect result buffer descriptor has invalid mutability")
    if descriptor["copy_boundary"] not in V1_5_2_COLLECT_BUFFER_COPY_BOUNDARIES:
        raise ValueError("collect result buffer descriptor has invalid copy_boundary")
    capacity = int(descriptor["capacity"])
    valid_count = int(descriptor["valid_count"])
    row_width = int(descriptor["row_width"])
    if capacity < 0 or valid_count < 0 or row_width <= 0:
        raise ValueError("collect result buffer descriptor has invalid dimensions")
    if valid_count > capacity:
        raise ValueError("collect result buffer descriptor valid_count exceeds capacity")
    if tuple(descriptor["shape"]) != (capacity, row_width):
        raise ValueError("collect result buffer descriptor shape mismatch")
    if tuple(descriptor.get("valid_shape", (valid_count, row_width))) != (valid_count, row_width):
        raise ValueError("collect result buffer descriptor valid_shape mismatch")
    if descriptor["overflowed"] is not False:
        raise RuntimeError("collect result buffer descriptor must fail closed on overflow")
    if descriptor["fail_closed"] is not True:
        raise RuntimeError("collect result buffer descriptor must declare fail_closed=True")
    false_flags = (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "release_action_authorized",
    )
    for flag in false_flags:
        if descriptor.get(flag) is not False:
            raise ValueError(f"collect result buffer descriptor must keep {flag}=False")
    return {
        **descriptor,
        "capacity": capacity,
        "valid_count": valid_count,
        "row_width": row_width,
        "shape": (capacity, row_width),
        "valid_shape": (valid_count, row_width),
    }
