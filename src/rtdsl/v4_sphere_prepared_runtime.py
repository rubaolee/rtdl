"""Prepared public owner for the Goal5833 built-in-sphere route."""

from __future__ import annotations

import ctypes
import ctypes.util
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import threading

from .physical_execution_provenance import (
    OptixTraversalAuditSession,
    _loaded_provider_sha256,
    _registered_loaded_provider_identity,
    validate_traversal_receipt,
)
from .v4_sphere_optix_compiler import consume_verified_sphere_executable
from .v4_sphere_physical_schema import (
    SPHERE_DISCRIMINANT_GUARD_UNIT_ROUNDOFFS,
    SPHERE_NONEXACT_TOI_ULP_BOUND,
    SPHERE_NUMERIC_POLICY,
    verify_builtin_sphere_physical_schema,
    verify_first_contact_expected_outputs,
    verify_motion_segments,
    verify_reference_sphere_contents,
)


# Exact values from the pinned OptiX 9 ``optix_types.h`` authority.  The
# descriptor reports the values copied from the concrete build input/options;
# comparing them here prevents symbolic receipt labels from blessing a
# different native primitive or flag set.
_EXPECTED_OPTIX9_SPHERE_FACTS = {
    "build_input_type": 0x2146,  # OPTIX_BUILD_INPUT_TYPE_SPHERES
    "primitive_type": 0x2506,  # OPTIX_PRIMITIVE_TYPE_SPHERE
    "primitive_type_flags": 1 << 6,  # OPTIX_PRIMITIVE_TYPE_FLAGS_SPHERE
    "builtin_is_build_flags": 1 << 2,  # OPTIX_BUILD_FLAG_PREFER_FAST_TRACE
    "build_flags": 1 << 2,  # OPTIX_BUILD_FLAG_PREFER_FAST_TRACE
    "geometry_flags": 1 << 1,  # REQUIRE_SINGLE_ANYHIT_CALL
    "traversable_graph_flags": 1 << 0,  # ALLOW_SINGLE_GAS
}


class _Status(ctypes.Structure):
    _fields_ = [
        ("first_error_claimed", ctypes.c_uint32),
        ("error_code", ctypes.c_uint32),
        ("stage", ctypes.c_uint32),
        ("role", ctypes.c_uint32),
        ("launch_index", ctypes.c_uint64),
        ("error_site", ctypes.c_uint32),
        ("effect_tag", ctypes.c_uint32),
        ("nonce_word", ctypes.c_uint32),
        ("invocation_mask", ctypes.c_uint32),
    ]


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _mapped_symbol_library_path(symbol) -> Path:
    """Resolve the OS-mapped object that owns one callable native symbol."""
    try:
        address = ctypes.cast(symbol, ctypes.c_void_p).value
    except (TypeError, ValueError) as exc:
        raise RuntimeError("native sphere ABI symbol has no mapped address") from exc
    if not address:
        raise RuntimeError("native sphere ABI symbol has a zero mapped address")
    if os.name == "nt":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        get_module = kernel32.GetModuleHandleExW
        get_module.argtypes = [ctypes.c_uint32, ctypes.c_void_p,
                               ctypes.POINTER(ctypes.c_void_p)]
        get_module.restype = ctypes.c_int
        module = ctypes.c_void_p()
        # FROM_ADDRESS | UNCHANGED_REFCOUNT: inspect without changing lifetime.
        if not get_module(0x00000004 | 0x00000002,
                          ctypes.c_void_p(address), ctypes.byref(module)):
            raise RuntimeError(
                f"cannot resolve native sphere ABI module: {ctypes.get_last_error()}")
        get_name = kernel32.GetModuleFileNameW
        get_name.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32]
        get_name.restype = ctypes.c_uint32
        capacity = 32768
        buffer = ctypes.create_unicode_buffer(capacity)
        length = int(get_name(module, buffer, capacity))
        if length == 0 or length >= capacity:
            raise RuntimeError(
                f"cannot read native sphere ABI module path: {ctypes.get_last_error()}")
        return Path(buffer.value).resolve(strict=True)

    class _DlInfo(ctypes.Structure):
        _fields_ = [
            ("dli_fname", ctypes.c_char_p), ("dli_fbase", ctypes.c_void_p),
            ("dli_sname", ctypes.c_char_p), ("dli_saddr", ctypes.c_void_p),
        ]

    library_name = ctypes.util.find_library("dl")
    loader = ctypes.CDLL(library_name) if library_name else ctypes.CDLL(None)
    dladdr = getattr(loader, "dladdr", None)
    if dladdr is None:
        raise RuntimeError("dladdr is unavailable for native sphere ABI binding")
    dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(_DlInfo)]
    dladdr.restype = ctypes.c_int
    info = _DlInfo()
    if int(dladdr(ctypes.c_void_p(address), ctypes.byref(info))) == 0 \
            or not info.dli_fname:
        raise RuntimeError("dladdr could not resolve native sphere ABI module")
    mapped = Path(os.fsdecode(info.dli_fname))
    if not mapped.is_absolute():
        # Main-executable symbols may be reported as a bare argv[0] (for
        # example ``python3``).  Resolve that OS-provided name through PATH;
        # ordinary RTDL DSO symbols loaded from an absolute authority path do
        # not take this branch.
        located = shutil.which(str(mapped))
        mapped = Path(located) if located else Path.cwd() / mapped
    return mapped.resolve(strict=True)


def _loaded_native_identity(library, explicit, *, symbol=None) -> tuple[Path, str]:
    """Bind authority to the mapped DSO that owns the called sphere ABI."""
    authorized = (
        Path(explicit).expanduser().resolve() if explicit is not None else None)
    if symbol is None:
        symbol = getattr(
            library, "rtdl_optix_v4_prepare_builtin_sphere_callback_v1", None)
    if symbol is None:
        raise RuntimeError("native library lacks a mapped Goal5833 sphere symbol")
    mapped_path = _mapped_symbol_library_path(symbol)
    registered = _registered_loaded_provider_identity(library)
    if registered is not None:
        actual_path, actual_sha256 = registered
    else:
        raw = (
            getattr(library, "_rtdl_loaded_library_path", None)
            or getattr(library, "_rtdl_library_path", None)
            or getattr(library, "_name", None)
        )
        if not raw:
            raise RuntimeError("loaded native library path identity is unavailable")
        actual_path = Path(raw).expanduser().resolve()
        if not actual_path.is_file():
            raise RuntimeError(
                f"loaded native library path is not a file: {actual_path}")
        actual_sha256 = _loaded_provider_sha256(library, actual_path)
    actual_path = Path(actual_path).resolve()
    if actual_path != mapped_path:
        raise RuntimeError(
            "registered sphere provider differs from the OS-mapped ABI owner: "
            f"registered={actual_path}; mapped={mapped_path}")
    if authorized is not None and authorized != actual_path:
        raise RuntimeError(
            "authorized sphere native path differs from the loaded provider: "
            f"authorized={authorized}; loaded={actual_path}")
    if not actual_path.is_file():
        raise RuntimeError(f"loaded native library path is not a file: {actual_path}")
    if hashlib.sha256(actual_path.read_bytes()).hexdigest() != actual_sha256:
        raise RuntimeError("loaded sphere native bytes changed after provider registration")
    return actual_path, actual_sha256


def _f32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", float(value)))[0]


def _native_fingerprint(domain: str, columns: tuple[tuple[str, object], ...]) -> str:
    states = [
        14695981039346656037,
        1099511628211 ^ 0x9E3779B97F4A7C15,
        0x6A09E667F3BCC909,
        0xBB67AE8584CAA73B,
    ]
    primes = [1099511628211, 1099511627791, 1099511627689, 1099511627609]
    mask = (1 << 64) - 1

    def add_byte(value: int) -> None:
        for index in range(4):
            states[index] ^= value + index * 17
            states[index] = (states[index] * primes[index]) & mask

    def add_u32(value: int) -> None:
        for shift in range(0, 32, 8):
            add_byte((int(value) >> shift) & 0xFF)

    def add_u64(value: int) -> None:
        for shift in range(0, 64, 8):
            add_byte((int(value) >> shift) & 0xFF)

    encoded_domain = domain.encode("ascii")
    add_u64(len(encoded_domain))
    for value in encoded_domain:
        add_byte(value)
    for kind, value in columns:
        if kind == "u32":
            add_u32(int(value))
        elif kind == "u64":
            add_u64(int(value))
        elif kind == "f32":
            add_u32(_f32_bits(float(value)))
        else:
            raise RuntimeError(f"unknown native fingerprint column kind: {kind}")
    return "".join(f"{value:016x}" for value in states)


def _native_static_input_fingerprint(centers, radii, application_ids) -> str:
    columns: list[tuple[str, object]] = [("u64", len(centers))]
    for center, radius, application_id in zip(centers, radii, application_ids):
        columns.extend(("f32", value) for value in center)
        columns.append(("f32", radius))
        columns.append(("u32", application_id))
    return _native_fingerprint("rtdl.v4.native_sphere_static_input.v1", tuple(columns))


def _native_query_fingerprint(normalized) -> str:
    columns: list[tuple[str, object]] = [("u64", len(normalized))]
    for row in normalized:
        columns.extend(("f32", value) for value in row)
    return _native_fingerprint("rtdl.v4.native_sphere_query.v1", tuple(columns))


def _native_output_fingerprint(
    outputs, observed_primitive, observed_kind, observed_t,
) -> str:
    columns: list[tuple[str, object]] = [("u64", len(outputs))]
    for index, output in enumerate(outputs):
        columns.extend(("u32", value) for value in output)
        columns.append(("u32", observed_primitive[index]))
        columns.append(("u32", observed_kind[index]))
        columns.append(("f32", observed_t[index]))
    return _native_fingerprint("rtdl.v4.native_sphere_output.v1", tuple(columns))


def _native_status_fingerprint(statuses) -> str:
    columns: list[tuple[str, object]] = [("u64", len(statuses))]
    for status in statuses:
        for name, _ctype in _Status._fields_:
            columns.append(("u64" if name == "launch_index" else "u32", status[name]))
    return _native_fingerprint("rtdl.v4.native_sphere_status.v1", tuple(columns))


def _native_counter_fingerprint(counters) -> str:
    return _native_fingerprint(
        "rtdl.v4.native_sphere_counters.v1",
        (("u64", len(counters)), *(('u64', value) for value in counters)),
    )


def _field_mapping_commitment(authority) -> str:
    schema = authority.schema
    return _digest({
        "schema": "rtdl.v4.sphere_field_mapping_commitment.v1",
        "centers": schema.center_field_id,
        "radii": schema.radius_field_id,
        "application_ids": schema.application_id_field_id,
        "queries": schema.query_field_id,
        "outputs": schema.output_field_id,
        "status": schema.status_field_id,
    })


def _static_input_commitment(centers, radii, application_ids) -> str:
    return _digest({
        "schema": "rtdl.v4.sphere_static_host_ffi_projection.v1",
        "centers_f32_bits": [
            [_f32_bits(value) for value in row] for row in centers],
        "radii_f32_bits": [_f32_bits(value) for value in radii],
        "application_ids_u32": [int(value) for value in application_ids],
    })


def _query_commitment(normalized) -> str:
    return _digest({
        "schema": "rtdl.v4.sphere_query_host_ffi_projection.v1",
        "segments_f32_bits": [
            [_f32_bits(value) for value in row] for row in normalized],
    })


def _require_traversal_provider_binding(
    receipt: dict[str, object], *, native_path: Path, native_sha256: str,
) -> None:
    raw_path = receipt.get("provider_library_path")
    if not isinstance(raw_path, str) or not raw_path:
        raise RuntimeError("sphere traversal receipt lacks loaded-provider path")
    if Path(raw_path).expanduser().resolve() != native_path.resolve() \
            or receipt.get("provider_library_sha256") != native_sha256:
        raise RuntimeError(
            "sphere traversal receipt provider differs from authorized native")


def _fresh(authority, plan, abi):
    fresh = verify_builtin_sphere_physical_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority or plan != fresh.canonical_plan:
        raise RuntimeError("sphere authority/plan does not rederive exactly")
    from .v4_sphere_callback_abi import verify_sphere_callback_abi
    verify_sphere_callback_abi(abi, fresh)
    return fresh


def _configure(library):
    prepare = getattr(library, "rtdl_optix_v4_prepare_builtin_sphere_callback_v1", None)
    execute = getattr(library, "rtdl_optix_v4_execute_prepared_builtin_sphere_callback_v1", None)
    describe = getattr(
        library, "rtdl_optix_v4_describe_prepared_builtin_sphere_callback_v1", None)
    destroy = getattr(library, "rtdl_optix_v4_destroy_prepared_builtin_sphere_callback_v1", None)
    if prepare is None or execute is None or describe is None or destroy is None:
        raise RuntimeError("native library lacks Goal5833 built-in sphere ABI")
    prepare.argtypes = [
        ctypes.c_char_p, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    execute.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(_Status), ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    describe.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    destroy.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    for symbol in (prepare, execute, describe, destroy):
        symbol.restype = ctypes.c_int
    return prepare, execute, describe, destroy


def _raise(status: int, error, label: str) -> None:
    if status:
        raise RuntimeError(
            error.value.decode("utf-8", errors="replace")
            or f"{label} failed with status {status}")


def _is_native_fingerprint(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value)


def _is_nonzero_native_fingerprint(value: object) -> bool:
    return _is_native_fingerprint(value) and value != "0" * 64


def _read_native_descriptor(describe, token: int) -> dict[str, object]:
    size = ctypes.c_size_t()
    error = ctypes.create_string_buffer(16384)
    _raise(int(describe(
        token, None, 0, ctypes.byref(size), error, len(error))),
        error, "prepared built-in sphere descriptor size")
    if size.value == 0 or size.value > 1 << 20:
        raise RuntimeError("prepared built-in sphere descriptor size is invalid")
    output = ctypes.create_string_buffer(size.value + 1)
    error = ctypes.create_string_buffer(16384)
    _raise(int(describe(
        token, output, len(output), ctypes.byref(size), error, len(error))),
        error, "prepared built-in sphere descriptor")
    try:
        descriptor = json.loads(output.raw[:size.value].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("prepared built-in sphere descriptor is invalid JSON") from exc
    expected_keys = {
        "schema", "build_input_type", "primitive_type",
        "primitive_type_flags", "builtin_is_build_flags",
        "builtin_is_module",
        "user_intersection_program", "uses_motion_blur", "build_flags",
        "geometry_flags", "center_stride_bytes", "radius_stride_bytes",
        "single_radius", "primitive_index_offset", "sbt_record_count",
        "gas_count", "primitive_count", "motion_key_count",
        "traversable_graph_flags", "max_payload_values",
        "max_attribute_values", "max_trace_depth", "program_group_count",
        "compiled_optix_version",
        "compiled_optix_major", "compiled_optix_minor",
        "compiled_optix_patch", "cuda_device_ordinal",
        "cuda_compute_capability_major", "cuda_compute_capability_minor",
        "cuda_driver_version", "static_input_fingerprint",
        "device_static_input_fingerprint",
        "center_device_pointer", "radius_device_pointer",
        "application_id_device_pointer", "traversable_identity",
        "last_execution_present", "last_status_failed", "last_query_count",
        "last_status_d2h_call_count",
        "last_application_output_d2h_call_count",
        "last_output_after_status_failure_count",
        "last_query_device_pointer_nonzero_count",
        "last_output_device_pointer_nonzero_count",
        "last_query_fingerprint", "last_device_query_fingerprint",
        "last_output_fingerprint",
        "last_status_fingerprint", "last_counter_fingerprint",
        "last_query_device_pointer_fingerprint",
        "last_output_device_pointer_fingerprint",
    }
    if not isinstance(descriptor, dict) or set(descriptor) != expected_keys:
        raise RuntimeError("prepared built-in sphere descriptor fields differ")
    if descriptor["schema"] != "rtdl.v4.native_builtin_sphere_descriptor.v2" \
            or descriptor["builtin_is_module"] is not True \
            or descriptor["user_intersection_program"] is not False \
            or descriptor["uses_motion_blur"] is not False \
            or descriptor["center_stride_bytes"] != 12 \
            or descriptor["radius_stride_bytes"] != 4 \
            or descriptor["single_radius"] is not False \
            or descriptor["primitive_index_offset"] != 0 \
            or descriptor["sbt_record_count"] != 1 \
            or descriptor["gas_count"] != 1 \
            or descriptor["motion_key_count"] != 0 \
            or any(descriptor[key] != value for key, value in
                   _EXPECTED_OPTIX9_SPHERE_FACTS.items()) \
            or descriptor["max_payload_values"] != 8 \
            or descriptor["max_attribute_values"] != 0 \
            or descriptor["max_trace_depth"] != 1 \
            or descriptor["program_group_count"] != 3 \
            or descriptor["traversable_graph_flags"] == 0:
        raise RuntimeError("prepared built-in sphere descriptor contract differs")
    for key in (
        "build_input_type", "primitive_type", "primitive_type_flags",
        "builtin_is_build_flags",
        "build_flags", "geometry_flags", "primitive_count",
        "motion_key_count",
        "traversable_graph_flags", "max_payload_values",
        "max_attribute_values", "max_trace_depth", "program_group_count",
        "compiled_optix_version", "compiled_optix_major",
        "compiled_optix_minor", "compiled_optix_patch",
        "cuda_device_ordinal", "cuda_compute_capability_major",
        "cuda_compute_capability_minor", "cuda_driver_version",
        "center_device_pointer", "radius_device_pointer",
        "application_id_device_pointer", "traversable_identity",
        "last_query_count", "last_status_d2h_call_count",
        "last_application_output_d2h_call_count",
        "last_output_after_status_failure_count",
        "last_query_device_pointer_nonzero_count",
        "last_output_device_pointer_nonzero_count",
    ):
        if not isinstance(descriptor[key], int) or isinstance(descriptor[key], bool) \
                or descriptor[key] < 0:
            raise RuntimeError(f"prepared built-in sphere descriptor {key} is invalid")
    encoded_version = (
        descriptor["compiled_optix_major"] * 10000
        + descriptor["compiled_optix_minor"] * 100
        + descriptor["compiled_optix_patch"]
    )
    if descriptor["compiled_optix_version"] != encoded_version \
            or descriptor["compiled_optix_major"] == 0 \
            or descriptor["compiled_optix_minor"] >= 100 \
            or descriptor["compiled_optix_patch"] >= 100 \
            or descriptor["cuda_compute_capability_major"] == 0 \
            or descriptor["cuda_compute_capability_minor"] >= 100 \
            or descriptor["cuda_driver_version"] == 0:
        raise RuntimeError("prepared built-in sphere runtime identity is invalid")
    if any(descriptor[key] == 0 for key in (
            "center_device_pointer", "radius_device_pointer",
            "application_id_device_pointer", "traversable_identity")):
        raise RuntimeError("prepared built-in sphere static device identity is zero")
    if not _is_native_fingerprint(descriptor["static_input_fingerprint"]) \
            or descriptor["device_static_input_fingerprint"] \
                != descriptor["static_input_fingerprint"]:
        raise RuntimeError("prepared built-in sphere static fingerprint is malformed")
    if type(descriptor["last_execution_present"]) is not bool \
            or type(descriptor["last_status_failed"]) is not bool:
        raise RuntimeError("prepared built-in sphere execution state is malformed")
    if descriptor["last_execution_present"]:
        for key in (
            "last_query_fingerprint", "last_device_query_fingerprint",
            "last_status_fingerprint",
            "last_counter_fingerprint", "last_query_device_pointer_fingerprint",
            "last_output_device_pointer_fingerprint",
        ):
            if not _is_native_fingerprint(descriptor[key]):
                raise RuntimeError(
                    f"prepared built-in sphere {key} is malformed")
        if descriptor["last_device_query_fingerprint"] \
                != descriptor["last_query_fingerprint"]:
            raise RuntimeError(
                "prepared built-in sphere device query content differs")
        if any(not _is_nonzero_native_fingerprint(descriptor[key]) for key in (
                "last_query_device_pointer_fingerprint",
                "last_output_device_pointer_fingerprint")):
            raise RuntimeError(
                "prepared built-in sphere device pointer fingerprint is zero")
        if descriptor["last_query_count"] == 0 \
                or descriptor["last_status_d2h_call_count"] != 1 \
                or descriptor["last_query_device_pointer_nonzero_count"] != 6 \
                or descriptor["last_output_device_pointer_nonzero_count"] != 8:
            raise RuntimeError(
                "prepared built-in sphere execution device identity differs")
        if descriptor["last_status_failed"]:
            if descriptor["last_output_fingerprint"] != "" \
                    or descriptor["last_application_output_d2h_call_count"] != 0 \
                    or descriptor["last_output_after_status_failure_count"] != 0:
                raise RuntimeError(
                    "prepared built-in sphere copied output after device failure")
        elif not _is_native_fingerprint(descriptor["last_output_fingerprint"]) \
                or descriptor["last_application_output_d2h_call_count"] != 6 \
                or descriptor["last_output_after_status_failure_count"] != 0:
            raise RuntimeError(
                "prepared built-in sphere successful output identity differs")
    elif any(descriptor[key] not in (0, "", False) for key in (
            "last_status_failed", "last_query_count",
            "last_status_d2h_call_count",
            "last_application_output_d2h_call_count",
            "last_output_after_status_failure_count",
            "last_query_device_pointer_nonzero_count",
            "last_output_device_pointer_nonzero_count",
            "last_query_fingerprint", "last_device_query_fingerprint",
            "last_output_fingerprint",
            "last_status_fingerprint", "last_counter_fingerprint",
            "last_query_device_pointer_fingerprint",
            "last_output_device_pointer_fingerprint")):
        raise RuntimeError("prepared built-in sphere pre-execution state differs")
    return descriptor


def _strict_version_components(value: str, count: int, label: str) -> tuple[int, ...]:
    parts = value.split(".") if isinstance(value, str) else []
    if len(parts) != count or any(
            not item or (len(item) > 1 and item.startswith("0"))
            or not item.isascii() or not item.isdecimal()
            for item in parts):
        raise RuntimeError(f"sphere target {label} is not a strict version")
    result = tuple(int(item) for item in parts)
    if result[0] == 0 or any(item >= 100 for item in result[1:]):
        raise RuntimeError(f"sphere target {label} is outside supported version form")
    return result


def _require_native_target_binding(descriptor, target) -> None:
    expected_optix = _strict_version_components(
        target.optix_sdk, 3, "OptiX SDK")
    expected_compute = _strict_version_components(
        target.compute_capability, 2, "compute capability")
    observed_optix = tuple(descriptor[key] for key in (
        "compiled_optix_major", "compiled_optix_minor", "compiled_optix_patch"))
    observed_compute = tuple(descriptor[key] for key in (
        "cuda_compute_capability_major", "cuda_compute_capability_minor"))
    if observed_optix != expected_optix:
        raise RuntimeError(
            "loaded sphere native OptiX SDK differs from target authority: "
            f"expected={expected_optix}; observed={observed_optix}")
    if observed_compute != expected_compute:
        raise RuntimeError(
            "live sphere CUDA compute capability differs from target authority: "
            f"expected={expected_compute}; observed={observed_compute}")


def _require_native_descriptor_transition(before, after) -> None:
    stable_keys = {key for key in before if not key.startswith("last_")}
    if set(before) != set(after) or any(
            before[key] != after[key] for key in stable_keys):
        raise RuntimeError(
            "prepared built-in sphere native descriptor changed static identity")


def _require_native_execution_fingerprints(
    descriptor, *, normalized, outputs, observed_primitive, observed_kind,
    observed_t, statuses, counters,
) -> None:
    expected = {
        "last_query_fingerprint": _native_query_fingerprint(normalized),
        "last_device_query_fingerprint": _native_query_fingerprint(normalized),
        "last_output_fingerprint": _native_output_fingerprint(
            outputs, observed_primitive, observed_kind, observed_t),
        "last_status_fingerprint": _native_status_fingerprint(statuses),
        "last_counter_fingerprint": _native_counter_fingerprint(counters),
    }
    if descriptor["last_execution_present"] is not True \
            or descriptor["last_status_failed"] is not False \
            or descriptor["last_query_count"] != len(normalized) \
            or any(not _is_nonzero_native_fingerprint(descriptor[key]) for key in (
                "last_query_device_pointer_fingerprint",
                "last_output_device_pointer_fingerprint")) \
            or any(descriptor[key] != value for key, value in expected.items()):
        raise RuntimeError(
            "prepared built-in sphere native content fingerprint differs")


def _require_native_failure_fingerprints(
    descriptor, *, normalized, statuses, counters,
) -> None:
    if descriptor["last_execution_present"] is not True \
            or descriptor["last_status_failed"] is not True \
            or descriptor["last_query_count"] != len(normalized) \
            or descriptor["last_query_fingerprint"] \
                != _native_query_fingerprint(normalized) \
            or descriptor["last_device_query_fingerprint"] \
                != _native_query_fingerprint(normalized) \
            or any(not _is_nonzero_native_fingerprint(descriptor[key]) for key in (
                "last_query_device_pointer_fingerprint",
                "last_output_device_pointer_fingerprint")) \
            or descriptor["last_status_fingerprint"] \
                != _native_status_fingerprint(statuses) \
            or descriptor["last_counter_fingerprint"] \
                != _native_counter_fingerprint(counters) \
            or descriptor["last_output_fingerprint"] != "" \
            or descriptor["last_application_output_d2h_call_count"] != 0 \
            or descriptor["last_output_after_status_failure_count"] != 0:
        raise RuntimeError(
            "prepared built-in sphere native failure fingerprint differs")


@dataclass(frozen=True)
class V4SphereCallbackResult:
    outputs: tuple[tuple[int, int, int], ...]
    hit_rows: tuple[dict[str, object], ...]
    observed_primitive_indices: tuple[int, ...]
    observed_hit_kinds: tuple[int, ...]
    observed_t_values: tuple[float, ...]
    counters: tuple[int, ...]
    statuses: tuple[dict[str, int], ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    composed_ptx_sha256: str
    native_library_sha256: str
    physical_receipt: dict[str, object]
    expected_comparison_policies: tuple[str, ...]


class PreparedBuiltinSphereOwner:
    def __init__(
        self, *, authority, plan, abi, executable,
        centers, radii, application_ids,
        library=None, native_library_path=None,
    ):
        fresh = _fresh(authority, plan, abi)
        normalized = verify_reference_sphere_contents(
            centers, radii, application_ids)
        self._centers, self._radii, self._application_ids = normalized
        composed_ptx = consume_verified_sphere_executable(
            executable, fresh, plan, abi)
        if library is None:
            from . import optix_runtime
            library = optix_runtime._load_optix_library()
        prepare, execute, describe, destroy = _configure(library)
        native_path, native_sha = _loaded_native_identity(
            library, native_library_path, symbol=prepare)
        if native_sha != fresh.target.native_sha256:
            raise RuntimeError("executed native bytes do not match sphere target authority")
        center_flat = [item for row in self._centers for item in row]
        center_native = (ctypes.c_float * len(center_flat))(*center_flat)
        radius_native = (ctypes.c_float * len(self._radii))(*self._radii)
        id_native = (ctypes.c_uint32 * len(self._application_ids))(*self._application_ids)
        token = ctypes.c_uint64()
        error = ctypes.create_string_buffer(16384)
        _raise(int(prepare(
            composed_ptx.encode("utf-8"), center_native, radius_native,
            id_native, len(self._centers), ctypes.byref(token), error, len(error))),
            error, "prepared built-in sphere prepare")
        if not token.value:
            raise RuntimeError("prepared built-in sphere returned zero token")
        try:
            native_descriptor = _read_native_descriptor(describe, int(token.value))
            if native_descriptor["primitive_count"] != len(self._centers):
                raise RuntimeError("prepared built-in sphere primitive count differs")
            _require_native_target_binding(native_descriptor, fresh.target)
            if native_descriptor["static_input_fingerprint"] \
                    != _native_static_input_fingerprint(
                        self._centers, self._radii, self._application_ids):
                raise RuntimeError(
                    "prepared built-in sphere native static content differs")
        except Exception as exc:
            cleanup_error = ctypes.create_string_buffer(16384)
            cleanup_status = int(destroy(
                int(token.value), cleanup_error, len(cleanup_error)))
            if cleanup_status:
                detail = cleanup_error.value.decode("utf-8", errors="replace")
                raise RuntimeError(
                    "prepared sphere descriptor failed and token cleanup also "
                    f"failed: {detail or cleanup_status}") from exc
            raise
        self._token = int(token.value)
        self._fresh = fresh
        self._plan = plan
        self._abi = abi
        self._library = library
        self._execute = execute
        self._describe = describe
        self._destroy = destroy
        self._native_sha = native_sha
        self._native_path = native_path
        self._ptx_sha = hashlib.sha256(composed_ptx.encode("utf-8")).hexdigest()
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._closed = False
        self._execution_count = 0
        self._native_descriptor = native_descriptor
        self._last_failure_receipt = None
        self._physical_receipt = {
            "schema": "rtdl.v4.builtin_sphere_physical_receipt.v1",
            "native_descriptor": native_descriptor,
            "build_input_type_name": "OPTIX_BUILD_INPUT_TYPE_SPHERES",
            "primitive_type_name": "OPTIX_PRIMITIVE_TYPE_SPHERE",
            "primitive_type_flags_name": "OPTIX_PRIMITIVE_TYPE_FLAGS_SPHERE",
            "builtin_is_api_name": "optixBuiltinISModuleGet",
            "build_flags_name": "OPTIX_BUILD_FLAG_PREFER_FAST_TRACE",
            "geometry_flags_name": "OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL",
            "native_library_sha256": native_sha,
            "authorized_native_library_path": str(native_path),
            "loaded_native_library_path": str(native_path),
            "loaded_native_library_sha256": native_sha,
            "composed_ptx_sha256": self._ptx_sha,
            "authority_nonce": fresh.authority_nonce,
            "field_mapping_commitment_sha256": _field_mapping_commitment(fresh),
            "static_input_commitment_sha256": _static_input_commitment(
                self._centers, self._radii, self._application_ids),
            "commitment_scope": (
                "canonical_host_ffi_projection_plus_native_content_and_device_identity"),
            "status_before_output": True,
            "numeric_policy": SPHERE_NUMERIC_POLICY,
            "discriminant_guard_binary32_unit_roundoffs":
                SPHERE_DISCRIMINANT_GUARD_UNIT_ROUNDOFFS,
            "nonexact_toi_ulp_bound": SPHERE_NONEXACT_TOI_ULP_BOUND,
            "exact_root_requires_bit_equality": True,
        }

    def _check(self):
        if self._closed:
            raise RuntimeError("prepared built-in sphere owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError("prepared built-in sphere owner crossed process boundary")
        if threading.get_ident() != self._thread:
            raise RuntimeError("prepared built-in sphere owner crossed thread boundary")

    @property
    def lifecycle_receipt(self):
        self._check()
        return {
            "schema": "rtdl.v4.prepared_builtin_sphere_owner.v1",
            "process_bound": True, "thread_bound": True,
            "nonserializable": True, "nonreentrant": True,
            "execution_count": self._execution_count,
            "native_library_sha256": self._native_sha,
            "composed_ptx_sha256": self._ptx_sha,
            "physical_receipt_sha256": _digest(self._physical_receipt),
        }

    @property
    def last_failure_receipt(self):
        self._check()
        if self._last_failure_receipt is None:
            return None
        return json.loads(json.dumps(
            self._last_failure_receipt, sort_keys=True, allow_nan=False))

    def __getstate__(self):
        raise RuntimeError("prepared built-in sphere owner cannot be serialized")

    def execute(self, queries, *, expected_output=None):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared built-in sphere owner is already executing")
        try:
            starts, ends = [], []
            for index, query in enumerate(queries):
                if len(query) != 2:
                    raise ValueError(f"query {index} must be (start,end)")
                starts.append(tuple(query[0])); ends.append(tuple(query[1]))
            normalized = verify_motion_segments(
                starts, ends, centers=self._centers, radii=self._radii)
            start_flat = [value for row in normalized for value in row[:3]]
            end_flat = [value for row in normalized for value in row[3:]]
            count = len(normalized)
            starts_native = (ctypes.c_float * len(start_flat))(*start_flat)
            ends_native = (ctypes.c_float * len(end_flat))(*end_flat)
            output_0 = (ctypes.c_uint32 * count)()
            output_1 = (ctypes.c_uint32 * count)()
            output_2 = (ctypes.c_uint32 * count)()
            observed_primitive = (ctypes.c_uint32 * count)()
            observed_kind = (ctypes.c_uint32 * count)()
            observed_t = (ctypes.c_float * count)()
            statuses = (_Status * count)()
            counters = (ctypes.c_uint64 * 7)()
            error = ctypes.create_string_buffer(16384)
            audit = OptixTraversalAuditSession.open(library=self._library)
            try:
                native_status = int(self._execute(
                    self._token, starts_native, ends_native, count,
                    output_0, output_1, output_2, observed_primitive,
                    observed_kind, observed_t, statuses, counters,
                    error, len(error)))
                status_rows = tuple({
                    name: int(getattr(item, name)) for name, _ in _Status._fields_}
                    for item in statuses)
                counter_values = tuple(int(item) for item in counters)
                execution_descriptor = _read_native_descriptor(
                    self._describe, self._token)
                _require_native_descriptor_transition(
                    self._native_descriptor, execution_descriptor)
                _require_native_target_binding(
                    execution_descriptor, self._fresh.target)
                if native_status:
                    _require_native_failure_fingerprints(
                        execution_descriptor, normalized=normalized,
                        statuses=status_rows, counters=counter_values)
                    failure_physical_receipt = dict(self._physical_receipt)
                    failure_physical_receipt.update({
                        "native_descriptor": execution_descriptor,
                        "query_commitment_sha256": _query_commitment(normalized),
                        "status_commitment_sha256": _digest({
                            "schema": "rtdl.v4.sphere_status_host_projection.v1",
                            "rows": status_rows,
                        }),
                        "counter_commitment_sha256": _digest({
                            "schema": "rtdl.v4.sphere_counter_host_projection.v1",
                            "values": list(counter_values),
                        }),
                        "device_status_rows": status_rows,
                        "role_counters": list(counter_values),
                        "application_output_d2h_after_status_failure": 0,
                        "device_failure_observed": True,
                    })
                    failure_digest = _digest({
                        "schema": "rtdl.v4.sphere_device_failure.v1",
                        "status": status_rows,
                        "counters": counter_values,
                    })
                    failure_traversal = audit.finish(
                        semantic_digest=_digest({
                            "authority": self._fresh.authority_nonce,
                            "plan": self._plan.plan_sha256,
                            "abi": self._abi.abi_sha256,
                            "ptx": self._ptx_sha,
                            "native": self._native_sha,
                            "physical": failure_physical_receipt,
                        }),
                        output_digest=failure_digest,
                        route_identity=(
                            "v4_builtin_sphere_callback_ir:four_role_composed_v1"),
                        expected_program_bundles=(
                            "v4_builtin_sphere_callback_ir_four_role_composed",),
                    )
                    _require_traversal_provider_binding(
                        failure_traversal, native_path=self._native_path,
                        native_sha256=self._native_sha)
                    validate_traversal_receipt(
                        failure_traversal,
                        provider_library_sha256=self._native_sha,
                        route_identity=(
                            "v4_builtin_sphere_callback_ir:four_role_composed_v1"),
                        output_digest=failure_digest,
                        expected_program_bundles=(
                            "v4_builtin_sphere_callback_ir_four_role_composed",),
                        expected_successful_launch_count=1,
                        expected_raygen_invocation_count=count,
                    )
                    self._last_failure_receipt = {
                        "schema": "rtdl.v4.builtin_sphere_failure_receipt.v1",
                        "physical_receipt": failure_physical_receipt,
                        "traversal_receipt": failure_traversal,
                        "failure_digest": failure_digest,
                    }
                    _raise(native_status, error,
                           "prepared built-in sphere execute")
                if any(row["first_error_claimed"] or row["error_code"] for row in status_rows):
                    raise RuntimeError("prepared built-in sphere returned device error")
                outputs = tuple((
                    int(output_0[index]), int(output_1[index]), int(output_2[index]))
                    for index in range(count))
                observed_primitive_values = tuple(
                    int(item) for item in observed_primitive)
                observed_kind_values = tuple(int(item) for item in observed_kind)
                observed_t_values = tuple(float(item) for item in observed_t)
                _require_native_execution_fingerprints(
                    execution_descriptor, normalized=normalized, outputs=outputs,
                    observed_primitive=observed_primitive_values,
                    observed_kind=observed_kind_values,
                    observed_t=observed_t_values, statuses=status_rows,
                    counters=counter_values)
                comparison_policies: tuple[str, ...] = ()
                if expected_output is not None:
                    comparison_policies = verify_first_contact_expected_outputs(
                        outputs, expected_output, normalized,
                        centers=self._centers, radii=self._radii,
                        application_ids=self._application_ids,
                    )
                output_sha = _digest(outputs)
                status_sha = _digest({
                    "schema": "rtdl.v4.sphere_status_host_projection.v1",
                    "rows": status_rows,
                })
                counter_sha = _digest({
                    "schema": "rtdl.v4.sphere_counter_host_projection.v1",
                    "values": [int(item) for item in counters],
                })
                execution_physical_receipt = dict(self._physical_receipt)
                execution_physical_receipt.update({
                    "native_descriptor": execution_descriptor,
                    "query_commitment_sha256": _query_commitment(normalized),
                    "output_commitment_sha256": output_sha,
                    "status_commitment_sha256": status_sha,
                    "counter_commitment_sha256": counter_sha,
                })
                receipt = audit.finish(
                    semantic_digest=_digest({
                        "authority": self._fresh.authority_nonce,
                        "plan": self._plan.plan_sha256,
                        "abi": self._abi.abi_sha256,
                        "ptx": self._ptx_sha,
                        "native": self._native_sha,
                        "physical": execution_physical_receipt,
                    }),
                    output_digest=output_sha,
                    route_identity="v4_builtin_sphere_callback_ir:four_role_composed_v1",
                    expected_program_bundles=(
                        "v4_builtin_sphere_callback_ir_four_role_composed",),
                )
            except Exception:
                audit.abort()
                raise
            if receipt["physical_executor_classification"] != "optix_traversal_observed":
                raise RuntimeError("prepared built-in sphere lacked bound traversal")
            _require_traversal_provider_binding(
                receipt, native_path=self._native_path,
                native_sha256=self._native_sha)
            validate_traversal_receipt(
                receipt,
                provider_library_sha256=self._native_sha,
                route_identity="v4_builtin_sphere_callback_ir:four_role_composed_v1",
                output_digest=output_sha,
                expected_program_bundles=(
                    "v4_builtin_sphere_callback_ir_four_role_composed",),
                expected_successful_launch_count=1,
                expected_raygen_invocation_count=count,
            )
            hit_rows = tuple({
                "primitive_index": (
                    None if int(observed_primitive[index]) == 0xFFFFFFFF
                    else int(observed_primitive[index])),
                "hit_kind": (
                    None if int(observed_kind[index]) == 0xFFFFFFFF
                    else int(observed_kind[index])),
                "t": (
                    None if int(observed_primitive[index]) == 0xFFFFFFFF
                    else float(observed_t[index])),
            } for index in range(count))
            self._execution_count += 1
            return V4SphereCallbackResult(
                outputs, hit_rows, observed_primitive_values,
                observed_kind_values, observed_t_values,
                tuple(int(item) for item in counters),
                status_rows, receipt, output_sha, self._ptx_sha,
                self._native_sha, execution_physical_receipt,
                comparison_policies)
        finally:
            self._active.release()

    def close(self):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close built-in sphere during execution")
        try:
            error = ctypes.create_string_buffer(16384)
            _raise(int(self._destroy(self._token, error, len(error))), error,
                   "prepared built-in sphere destroy")
            self._token = 0
            self._closed = True
        finally:
            self._active.release()

    def __enter__(self):
        self._check(); return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def prepare_builtin_sphere_callback(**kwargs):
    return PreparedBuiltinSphereOwner(**kwargs)


__all__ = [
    "PreparedBuiltinSphereOwner", "V4SphereCallbackResult",
    "prepare_builtin_sphere_callback",
]
