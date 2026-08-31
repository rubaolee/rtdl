"""Prepared public owner for the Goal5834 built-in round-linear curve route."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import threading

from .physical_execution_provenance import (
    OptixTraversalAuditSession,
    validate_traversal_receipt,
)
from .v4_curve_callback_abi import verify_curve_callback_abi
from .v4_curve_optix_compiler import consume_verified_curve_executable
from .v4_curve_physical_schema import (
    CURVE_BOOLEAN_NUMERIC_POLICY,
    CURVE_NUMERIC_POLICY,
    BuiltinCurveBooleanPhysicalSchema,
    verify_builtin_curve_physical_schema,
    verify_curve_boolean_motion_segments,
    verify_curve_first_contact_expected_outputs,
    verify_curve_motion_segments,
    verify_reference_curve_contents,
)
from .v4_sphere_prepared_runtime import (
    _Status,
    _digest,
    _f32_bits,
    _is_native_fingerprint,
    _is_nonzero_native_fingerprint,
    _loaded_native_identity,
    _native_fingerprint,
    _raise,
    _strict_version_components,
)


_EXPECTED_OPTIX9_CURVE_FACTS = {
    "build_input_type": 0x2145,  # OPTIX_BUILD_INPUT_TYPE_CURVES
    "primitive_type": 0x2503,  # OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR
    "primitive_type_flags": 1 << 3,
    "builtin_is_build_flags": 1 << 2,
    "builtin_is_curve_endcap_flags": 0,  # DEFAULT is round for linear curves
    "build_flags": 1 << 2,
    "geometry_flags": 1 << 1,
    "traversable_graph_flags": 1 << 0,
    "endcap_flags": 0,
}


def _native_static_input_fingerprint(
    control_points, widths, segment_indices, application_ids,
) -> str:
    columns: list[tuple[str, object]] = [("u64", len(control_points))]
    for point, width in zip(control_points, widths):
        columns.extend(("f32", value) for value in point)
        columns.append(("f32", width))
    columns.append(("u64", len(segment_indices)))
    for segment_index, application_id in zip(segment_indices, application_ids):
        columns.append(("u32", segment_index))
        columns.append(("u32", application_id))
    return _native_fingerprint(
        "rtdl.v4.native_curve_static_input.v1", tuple(columns))


def _native_query_fingerprint(normalized) -> str:
    columns: list[tuple[str, object]] = [("u64", len(normalized))]
    for row in normalized:
        columns.extend(("f32", value) for value in row)
    return _native_fingerprint("rtdl.v4.native_curve_query.v1", tuple(columns))


def _native_output_fingerprint(outputs, primitives, kinds, hit_t) -> str:
    columns: list[tuple[str, object]] = [("u64", len(outputs))]
    for index, output in enumerate(outputs):
        columns.extend(("u32", value) for value in output)
        columns.append(("u32", primitives[index]))
        columns.append(("u32", kinds[index]))
        columns.append(("f32", hit_t[index]))
    return _native_fingerprint("rtdl.v4.native_curve_output.v1", tuple(columns))


def _native_status_fingerprint(statuses) -> str:
    columns: list[tuple[str, object]] = [("u64", len(statuses))]
    for status in statuses:
        for name, _ctype in _Status._fields_:
            columns.append((
                "u64" if name == "launch_index" else "u32", status[name]))
    return _native_fingerprint("rtdl.v4.native_curve_status.v1", tuple(columns))


def _native_counter_fingerprint(counters) -> str:
    return _native_fingerprint(
        "rtdl.v4.native_curve_counters.v1",
        (("u64", len(counters)), *(("u64", value) for value in counters)),
    )


def _native_pointer_fingerprint(domain: str, values) -> str:
    return _native_fingerprint(
        domain, (("u64", len(values)), *(("u64", value) for value in values)))


def _field_mapping_commitment(authority) -> str:
    schema = authority.schema
    return _digest({
        "schema": "rtdl.v4.curve_field_mapping_commitment.v1",
        "control_points": schema.control_point_field_id,
        "widths": schema.width_field_id,
        "segment_indices": schema.segment_index_field_id,
        "application_ids": schema.application_id_field_id,
        "queries": schema.query_field_id,
        "outputs": schema.output_field_id,
        "status": schema.status_field_id,
    })


def curve_static_input_commitment_sha256(
    control_points, widths, segment_indices, application_ids,
) -> str:
    return _digest({
        "schema": "rtdl.v4.curve_static_host_ffi_projection.v1",
        "control_points_f32_bits": [
            [_f32_bits(value) for value in row] for row in control_points],
        "widths_f32_bits": [_f32_bits(value) for value in widths],
        "segment_indices_u32": [int(value) for value in segment_indices],
        "application_ids_u32": [int(value) for value in application_ids],
    })


def curve_query_commitment_sha256(normalized) -> str:
    return _digest({
        "schema": "rtdl.v4.curve_query_host_ffi_projection.v1",
        "segments_f32_bits": [
            [_f32_bits(value) for value in row] for row in normalized],
    })


# Historical private names remain aliases so old callers and frozen tests keep
# the exact commitment framing.
_static_input_commitment = curve_static_input_commitment_sha256
_query_commitment = curve_query_commitment_sha256


def _fresh(authority, plan, abi):
    fresh = verify_builtin_curve_physical_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority or plan != fresh.canonical_plan:
        raise RuntimeError("curve authority/plan does not rederive")
    verify_curve_callback_abi(abi, fresh)
    return fresh


def _configure(library):
    prepare = getattr(
        library, "rtdl_optix_v4_prepare_builtin_curve_callback_v1", None)
    execute = getattr(
        library, "rtdl_optix_v4_execute_prepared_builtin_curve_callback_v1", None)
    describe = getattr(
        library, "rtdl_optix_v4_describe_prepared_builtin_curve_callback_v1", None)
    destroy = getattr(
        library, "rtdl_optix_v4_destroy_prepared_builtin_curve_callback_v1", None)
    if prepare is None or execute is None or describe is None or destroy is None:
        raise RuntimeError("native library lacks Goal5834 built-in curve ABI")
    prepare.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t, ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    execute.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
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
    destroy.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    for symbol in (prepare, execute, describe, destroy):
        symbol.restype = ctypes.c_int
    return prepare, execute, describe, destroy


def _read_native_descriptor(describe, token: int) -> dict[str, object]:
    size = ctypes.c_size_t()
    error = ctypes.create_string_buffer(16384)
    _raise(int(describe(
        token, None, 0, ctypes.byref(size), error, len(error))),
        error, "prepared built-in curve descriptor size")
    if size.value == 0 or size.value > 1 << 20:
        raise RuntimeError("prepared built-in curve descriptor size is invalid")
    output = ctypes.create_string_buffer(size.value + 1)
    error = ctypes.create_string_buffer(16384)
    _raise(int(describe(
        token, output, len(output), ctypes.byref(size), error, len(error))),
        error, "prepared built-in curve descriptor")
    descriptor = json.loads(output.raw[:size.value].decode("utf-8"))
    expected_keys = {
        "schema", "build_input_type", "primitive_type",
        "primitive_type_flags", "builtin_is_build_flags",
        "builtin_is_curve_endcap_flags", "builtin_is_module",
        "user_intersection_program", "uses_motion_blur", "build_flags",
        "geometry_flags", "vertex_stride_bytes", "width_stride_bytes",
        "index_stride_bytes", "normal_buffers_present",
        "primitive_index_offset", "sbt_record_count", "gas_count",
        "primitive_count", "vertex_count", "motion_key_count", "endcap_flags",
        "traversable_graph_flags", "max_payload_values",
        "max_attribute_values", "max_trace_depth", "program_group_count",
        "compiled_optix_version", "compiled_optix_major",
        "compiled_optix_minor", "compiled_optix_patch", "cuda_device_ordinal",
        "cuda_compute_capability_major", "cuda_compute_capability_minor",
        "cuda_driver_version", "static_input_fingerprint",
        "device_static_input_fingerprint", "vertex_device_pointer",
        "width_device_pointer", "index_device_pointer",
        "application_id_device_pointer", "traversable_identity",
        "last_execution_present", "last_status_failed", "last_query_count",
        "last_status_d2h_call_count", "last_application_output_d2h_call_count",
        "last_output_after_status_failure_count",
        "last_query_device_pointer_nonzero_count",
        "last_output_device_pointer_nonzero_count", "last_query_fingerprint",
        "last_device_query_fingerprint", "last_output_fingerprint",
        "last_status_fingerprint", "last_counter_fingerprint",
        "last_query_device_pointer_fingerprint",
        "last_output_device_pointer_fingerprint",
    }
    if not isinstance(descriptor, dict) or set(descriptor) != expected_keys:
        raise RuntimeError("prepared built-in curve descriptor fields differ")
    if descriptor["schema"] != "rtdl.v4.native_builtin_curve_descriptor.v1" \
            or descriptor["builtin_is_module"] is not True \
            or descriptor["user_intersection_program"] is not False \
            or descriptor["uses_motion_blur"] is not False \
            or descriptor["vertex_stride_bytes"] != 12 \
            or descriptor["width_stride_bytes"] != 4 \
            or descriptor["index_stride_bytes"] != 4 \
            or descriptor["normal_buffers_present"] is not False \
            or descriptor["primitive_index_offset"] != 0 \
            or descriptor["sbt_record_count"] != 1 \
            or descriptor["gas_count"] != 1 \
            or descriptor["motion_key_count"] != 0 \
            or any(descriptor[key] != value for key, value in
                   _EXPECTED_OPTIX9_CURVE_FACTS.items()) \
            or descriptor["max_payload_values"] != 8 \
            or descriptor["max_attribute_values"] != 0 \
            or descriptor["max_trace_depth"] != 1 \
            or descriptor["program_group_count"] != 3 \
            or descriptor["traversable_graph_flags"] == 0:
        raise RuntimeError("prepared built-in curve descriptor contract differs")
    integer_keys = expected_keys - {
        "schema", "builtin_is_module", "user_intersection_program",
        "uses_motion_blur", "normal_buffers_present", "last_execution_present",
        "last_status_failed", "static_input_fingerprint",
        "device_static_input_fingerprint", "last_query_fingerprint",
        "last_device_query_fingerprint", "last_output_fingerprint",
        "last_status_fingerprint", "last_counter_fingerprint",
        "last_query_device_pointer_fingerprint",
        "last_output_device_pointer_fingerprint",
    }
    if any(not isinstance(descriptor[key], int)
           or isinstance(descriptor[key], bool) or descriptor[key] < 0
           for key in integer_keys):
        raise RuntimeError("prepared built-in curve integer descriptor is invalid")
    if descriptor["primitive_count"] == 0 or descriptor["vertex_count"] < 2:
        raise RuntimeError("prepared built-in curve cardinality is invalid")
    if any(descriptor[key] == 0 for key in (
            "vertex_device_pointer", "width_device_pointer",
            "index_device_pointer", "application_id_device_pointer",
            "traversable_identity")):
        raise RuntimeError("prepared built-in curve static device identity is zero")
    if not _is_native_fingerprint(descriptor["static_input_fingerprint"]) \
            or descriptor["device_static_input_fingerprint"] \
                != descriptor["static_input_fingerprint"]:
        raise RuntimeError("prepared built-in curve static fingerprint differs")
    if type(descriptor["last_execution_present"]) is not bool \
            or type(descriptor["last_status_failed"]) is not bool:
        raise RuntimeError("prepared built-in curve execution state is malformed")
    if descriptor["last_execution_present"]:
        for key in (
                "last_query_fingerprint", "last_device_query_fingerprint",
                "last_status_fingerprint", "last_counter_fingerprint",
                "last_query_device_pointer_fingerprint",
                "last_output_device_pointer_fingerprint"):
            if not _is_native_fingerprint(descriptor[key]):
                raise RuntimeError(f"prepared built-in curve {key} is malformed")
        if descriptor["last_query_fingerprint"] \
                != descriptor["last_device_query_fingerprint"] \
                or descriptor["last_status_d2h_call_count"] != 1 \
                or descriptor["last_query_device_pointer_nonzero_count"] != 6 \
                or descriptor["last_output_device_pointer_nonzero_count"] != 8:
            raise RuntimeError("prepared built-in curve execution identity differs")
        if descriptor["last_status_failed"]:
            if descriptor["last_output_fingerprint"] != "" \
                    or descriptor["last_application_output_d2h_call_count"] != 0 \
                    or descriptor["last_output_after_status_failure_count"] != 0:
                raise RuntimeError("curve output copied after device failure")
        elif not _is_native_fingerprint(descriptor["last_output_fingerprint"]) \
                or descriptor["last_application_output_d2h_call_count"] != 6 \
                or descriptor["last_output_after_status_failure_count"] != 0:
            raise RuntimeError("curve successful output identity differs")
    return descriptor


def _require_native_target_binding(descriptor, target) -> None:
    expected_optix = _strict_version_components(target.optix_sdk, 3, "OptiX SDK")
    expected_compute = _strict_version_components(
        target.compute_capability, 2, "compute capability")
    observed_optix = tuple(descriptor[key] for key in (
        "compiled_optix_major", "compiled_optix_minor", "compiled_optix_patch"))
    observed_compute = tuple(descriptor[key] for key in (
        "cuda_compute_capability_major", "cuda_compute_capability_minor"))
    if observed_optix != expected_optix or observed_compute != expected_compute:
        raise RuntimeError("loaded curve native target differs from authority")


def _require_descriptor_transition(before, after) -> None:
    stable = {key for key in before if not key.startswith("last_")}
    if set(before) != set(after) or any(
            before[key] != after[key] for key in stable):
        raise RuntimeError("curve native descriptor changed static identity")


def _require_execution_fingerprints(
    descriptor, *, normalized, outputs, primitives, kinds, hit_t,
    statuses, counters,
) -> None:
    expected = {
        "last_query_fingerprint": _native_query_fingerprint(normalized),
        "last_device_query_fingerprint": _native_query_fingerprint(normalized),
        "last_output_fingerprint": _native_output_fingerprint(
            outputs, primitives, kinds, hit_t),
        "last_status_fingerprint": _native_status_fingerprint(statuses),
        "last_counter_fingerprint": _native_counter_fingerprint(counters),
    }
    if descriptor["last_execution_present"] is not True \
            or descriptor["last_status_failed"] is not False \
            or descriptor["last_query_count"] != len(normalized) \
            or any(descriptor[key] != value for key, value in expected.items()):
        raise RuntimeError("curve native content fingerprint differs")


@dataclass(frozen=True)
class V4CurveCallbackResult:
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


@dataclass(frozen=True)
class V4CurveBooleanResult:
    per_query_hit: tuple[int, ...]
    any_hit: int
    counters: tuple[int, ...]
    statuses: tuple[dict[str, int], ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    physical_output_sha256: str
    composed_ptx_sha256: str
    native_library_sha256: str
    physical_receipt: dict[str, object]


class PreparedBuiltinCurveOwner:
    def __init__(
        self, *, authority, plan, abi, executable, control_points, widths,
        segment_indices, application_ids, library=None,
        native_library_path=None,
    ):
        fresh = _fresh(authority, plan, abi)
        self._boolean_mode = type(fresh.schema) is BuiltinCurveBooleanPhysicalSchema
        normalized = verify_reference_curve_contents(
            control_points, widths, segment_indices, application_ids)
        self._control_points, self._widths = normalized[:2]
        self._segment_indices, self._application_ids = normalized[2:]
        composed_ptx = consume_verified_curve_executable(
            executable, fresh, plan, abi)
        if library is None:
            from . import optix_runtime
            library = optix_runtime._load_optix_library()
        prepare, execute, describe, destroy = _configure(library)
        native_path, native_sha = _loaded_native_identity(
            library, native_library_path, symbol=prepare)
        if native_sha != fresh.target.native_sha256:
            raise RuntimeError("executed native bytes do not match curve authority")
        point_flat = [value for row in self._control_points for value in row]
        point_native = (ctypes.c_float * len(point_flat))(*point_flat)
        width_native = (ctypes.c_float * len(self._widths))(*self._widths)
        index_native = (ctypes.c_uint32 * len(self._segment_indices))(
            *self._segment_indices)
        id_native = (ctypes.c_uint32 * len(self._application_ids))(
            *self._application_ids)
        token = ctypes.c_uint64()
        error = ctypes.create_string_buffer(16384)
        _raise(int(prepare(
            composed_ptx.encode("utf-8"), point_native, width_native,
            index_native, id_native, len(self._control_points),
            len(self._segment_indices), ctypes.byref(token), error, len(error))),
            error, "prepared built-in curve prepare")
        if not token.value:
            raise RuntimeError("prepared built-in curve returned zero token")
        try:
            descriptor = _read_native_descriptor(describe, int(token.value))
            if descriptor["primitive_count"] != len(self._segment_indices) \
                    or descriptor["vertex_count"] != len(self._control_points):
                raise RuntimeError("prepared built-in curve cardinality differs")
            _require_native_target_binding(descriptor, fresh.target)
            if descriptor["static_input_fingerprint"] != \
                    _native_static_input_fingerprint(
                        self._control_points, self._widths,
                        self._segment_indices, self._application_ids):
                raise RuntimeError("prepared built-in curve static content differs")
        except Exception as exc:
            cleanup_error = ctypes.create_string_buffer(16384)
            cleanup_status = int(destroy(
                int(token.value), cleanup_error, len(cleanup_error)))
            if cleanup_status:
                raise RuntimeError("curve descriptor and cleanup both failed") from exc
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
        self._descriptor = descriptor
        self._last_failure_receipt = None
        self._physical_receipt = {
            "schema": "rtdl.v4.builtin_curve_physical_receipt.v1",
            "native_descriptor": descriptor,
            "build_input_type_name": "OPTIX_BUILD_INPUT_TYPE_CURVES",
            "primitive_type_name": "OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR",
            "primitive_type_flags_name":
                "OPTIX_PRIMITIVE_TYPE_FLAGS_ROUND_LINEAR",
            "curve_endcap_name":
                "OPTIX_CURVE_ENDCAP_DEFAULT__ROUND_FOR_LINEAR",
            "builtin_is_api_name": "optixBuiltinISModuleGet",
            "build_flags_name": "OPTIX_BUILD_FLAG_PREFER_FAST_TRACE",
            "geometry_flags_name":
                "OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL",
            "native_library_sha256": native_sha,
            "authorized_native_library_path": str(native_path),
            "loaded_native_library_path": str(native_path),
            "loaded_native_library_sha256": native_sha,
            "composed_ptx_sha256": self._ptx_sha,
            "authority_nonce": fresh.authority_nonce,
            "field_mapping_commitment_sha256": _field_mapping_commitment(fresh),
            "static_input_commitment_sha256": _static_input_commitment(
                self._control_points, self._widths,
                self._segment_indices, self._application_ids),
            "status_before_output": True,
            "numeric_policy": (
                CURVE_BOOLEAN_NUMERIC_POLICY
                if self._boolean_mode else CURVE_NUMERIC_POLICY),
            "numeric_admission": fresh.schema.numeric_admission_dict(),
        }

    def _check(self):
        if self._closed:
            raise RuntimeError("prepared built-in curve owner is closed")
        if os.getpid() != self._pid or threading.get_ident() != self._thread:
            raise RuntimeError("prepared built-in curve owner crossed ownership boundary")

    @property
    def lifecycle_receipt(self):
        self._check()
        return {
            "schema": "rtdl.v4.prepared_builtin_curve_owner.v1",
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "nonreentrant": True,
            "execution_count": self._execution_count,
            "native_library_sha256": self._native_sha,
            "composed_ptx_sha256": self._ptx_sha,
            "physical_receipt_sha256": _digest(self._physical_receipt),
        }

    @property
    def last_failure_receipt(self):
        self._check()
        return None if self._last_failure_receipt is None else json.loads(
            json.dumps(self._last_failure_receipt, sort_keys=True, allow_nan=False))

    def __getstate__(self):
        raise RuntimeError("prepared built-in curve owner cannot be serialized")

    def execute(self, queries, *, expected_output=None):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared built-in curve owner is already executing")
        try:
            starts, ends = [], []
            for index, query in enumerate(queries):
                if len(query) != 2:
                    raise ValueError(f"query {index} must be (start,end)")
                starts.append(tuple(query[0]))
                ends.append(tuple(query[1]))
            if self._boolean_mode:
                if expected_output is not None:
                    raise RuntimeError(
                        "Boolean oracle comparison is forbidden in the worker")
                normalized = verify_curve_boolean_motion_segments(starts, ends)
            else:
                normalized = verify_curve_motion_segments(
                    starts, ends,
                    control_points=self._control_points,
                    widths=self._widths,
                    segment_indices=self._segment_indices,
                )
            route_identity = (
                "v4_builtin_curve_callback_ir:"
                "four_role_provider_any_contact_boolean_v1"
                if self._boolean_mode else
                "v4_builtin_curve_callback_ir:four_role_composed_v1")
            start_flat = [value for row in normalized for value in row[:3]]
            end_flat = [value for row in normalized for value in row[3:]]
            count = len(normalized)
            starts_native = (ctypes.c_float * len(start_flat))(*start_flat)
            ends_native = (ctypes.c_float * len(end_flat))(*end_flat)
            output_0 = (ctypes.c_uint32 * count)()
            output_1 = (ctypes.c_uint32 * count)()
            output_2 = (ctypes.c_uint32 * count)()
            primitives = (ctypes.c_uint32 * count)()
            kinds = (ctypes.c_uint32 * count)()
            hit_t = (ctypes.c_float * count)()
            statuses = (_Status * count)()
            counters = (ctypes.c_uint64 * 7)()
            error = ctypes.create_string_buffer(16384)
            audit = OptixTraversalAuditSession.open(library=self._library)
            try:
                native_status = int(self._execute(
                    self._token, starts_native, ends_native, count,
                    output_0, output_1, output_2, primitives, kinds, hit_t,
                    statuses, counters, error, len(error)))
                status_rows = tuple({
                    name: int(getattr(item, name))
                    for name, _ in _Status._fields_} for item in statuses)
                counter_values = tuple(int(item) for item in counters)
                descriptor = _read_native_descriptor(
                    self._describe, self._token)
                _require_descriptor_transition(self._descriptor, descriptor)
                _require_native_target_binding(descriptor, self._fresh.target)
                if native_status:
                    failure_physical = dict(self._physical_receipt)
                    failure_physical.update({
                        "native_descriptor": descriptor,
                        "query_commitment_sha256": _query_commitment(normalized),
                        "device_status_rows": status_rows,
                        "role_counters": list(counter_values),
                        "application_output_d2h_after_status_failure": 0,
                        "device_failure_observed": True,
                    })
                    failure_digest = _digest({
                        "schema": "rtdl.v4.curve_device_failure.v1",
                        "status": status_rows,
                        "counters": counter_values,
                    })
                    traversal = audit.finish(
                        semantic_digest=_digest({
                            "authority": self._fresh.authority_nonce,
                            "plan": self._plan.plan_sha256,
                            "abi": self._abi.abi_sha256,
                            "ptx": self._ptx_sha,
                            "native": self._native_sha,
                            "physical": failure_physical,
                        }),
                        output_digest=failure_digest,
                        route_identity=route_identity,
                        expected_program_bundles=(
                            "v4_builtin_curve_callback_ir_four_role_composed",),
                    )
                    self._last_failure_receipt = {
                        "schema": "rtdl.v4.builtin_curve_failure_receipt.v1",
                        "physical_receipt": failure_physical,
                        "traversal_receipt": traversal,
                        "failure_digest": failure_digest,
                    }
                    _raise(native_status, error, "prepared built-in curve execute")
                outputs = tuple((
                    int(output_0[index]), int(output_1[index]), int(output_2[index]))
                    for index in range(count))
                primitive_values = tuple(int(value) for value in primitives)
                kind_values = tuple(int(value) for value in kinds)
                hit_values = tuple(float(value) for value in hit_t)
                _require_execution_fingerprints(
                    descriptor, normalized=normalized, outputs=outputs,
                    primitives=primitive_values, kinds=kind_values,
                    hit_t=hit_values, statuses=status_rows,
                    counters=counter_values)
                comparison_policies = ()
                physical_output_sha = _digest(outputs)
                per_query_hit = ()
                if self._boolean_mode:
                    if any(row[0] not in (0, 1) or row[1:] != (0, 0)
                           for row in outputs):
                        raise RuntimeError(
                            "curve Boolean native carrier is not hit+zero+zero")
                    per_query_hit = tuple(row[0] for row in outputs)
                    output_sha = _digest({
                        "schema": "rtdl.v4.curve_provider_any_contact_bits.v1",
                        "per_query_hit": list(per_query_hit),
                    })
                elif expected_output is not None:
                    comparison_policies = verify_curve_first_contact_expected_outputs(
                        outputs, expected_output, normalized,
                        control_points=self._control_points,
                        widths=self._widths,
                        segment_indices=self._segment_indices,
                        application_ids=self._application_ids,
                    )
                if not self._boolean_mode:
                    output_sha = physical_output_sha
                physical = dict(self._physical_receipt)
                physical.update({
                    "native_descriptor": descriptor,
                    "query_commitment_sha256": _query_commitment(normalized),
                    "output_commitment_sha256": output_sha,
                    "physical_output_commitment_sha256": physical_output_sha,
                })
                if self._boolean_mode:
                    physical.update({
                        "semantic_output_kind":
                            "provider_any_contact_bit_per_query",
                        "raw_gpu_bit_vector_commitment_sha256": output_sha,
                        "host_aggregation": "OR_after_raw_receipt_seal",
                    })
                receipt = audit.finish(
                    semantic_digest=_digest({
                        "authority": self._fresh.authority_nonce,
                        "plan": self._plan.plan_sha256,
                        "abi": self._abi.abi_sha256,
                        "ptx": self._ptx_sha,
                        "native": self._native_sha,
                        "physical": physical,
                    }),
                    output_digest=output_sha,
                    route_identity=route_identity,
                    expected_program_bundles=(
                        "v4_builtin_curve_callback_ir_four_role_composed",),
                )
            except Exception:
                audit.abort()
                raise
            if receipt["physical_executor_classification"] \
                    != "optix_traversal_observed":
                raise RuntimeError("prepared built-in curve lacked bound traversal")
            validate_traversal_receipt(
                receipt,
                provider_library_sha256=self._native_sha,
                route_identity=route_identity,
                output_digest=output_sha,
                expected_program_bundles=(
                    "v4_builtin_curve_callback_ir_four_role_composed",),
                expected_successful_launch_count=1,
                expected_raygen_invocation_count=count,
            )
            if self._boolean_mode:
                # The raw GPU vector is already sealed by the traversal receipt
                # above.  Only now perform the transparent host-side OR.
                any_hit = int(any(per_query_hit))
                self._execution_count += 1
                return V4CurveBooleanResult(
                    per_query_hit, any_hit, counter_values, status_rows,
                    receipt, output_sha, physical_output_sha, self._ptx_sha,
                    self._native_sha, physical)
            hit_rows = tuple({
                "primitive_index": None if primitive_values[index] == 0xFFFFFFFF
                    else primitive_values[index],
                "hit_kind": None if kind_values[index] == 0xFFFFFFFF
                    else kind_values[index],
                "t": None if primitive_values[index] == 0xFFFFFFFF
                    else hit_values[index],
            } for index in range(count))
            self._execution_count += 1
            return V4CurveCallbackResult(
                outputs, hit_rows, primitive_values, kind_values, hit_values,
                counter_values, status_rows, receipt, output_sha, self._ptx_sha,
                self._native_sha, physical, tuple(comparison_policies))
        finally:
            self._active.release()

    def close(self):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close built-in curve during execution")
        try:
            error = ctypes.create_string_buffer(16384)
            _raise(int(self._destroy(
                self._token, error, len(error))), error,
                "prepared built-in curve destroy")
            self._token = 0
            self._closed = True
        finally:
            self._active.release()

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def prepare_builtin_curve_callback(**kwargs):
    return PreparedBuiltinCurveOwner(**kwargs)


__all__ = [
    "PreparedBuiltinCurveOwner", "V4CurveBooleanResult",
    "V4CurveCallbackResult", "curve_query_commitment_sha256",
    "curve_static_input_commitment_sha256", "prepare_builtin_curve_callback",
]
