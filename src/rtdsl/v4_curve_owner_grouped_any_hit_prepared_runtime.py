"""Prepared runtime for app-neutral curve owner-grouped any-hit."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import json
import os
import threading

from .physical_execution_provenance import (
    OptixTraversalAuditSession,
    validate_traversal_receipt,
)
from .v4_curve_owner_grouped_any_hit import (
    verify_curve_owner_grouped_any_hit_physical_schema,
)
from .v4_curve_owner_grouped_any_hit_optix_compiler import (
    consume_verified_curve_owner_grouped_any_hit_executable,
)
from .v4_curve_physical_schema import verify_curve_boolean_motion_segments
from .v4_owner_grouped_any_hit import (
    owner_grouped_any_hit_output_sha256,
    verify_owner_grouped_any_hit_abi,
)
from .v4_sphere_prepared_runtime import (
    _Status,
    _is_native_fingerprint,
    _loaded_native_identity,
    _native_fingerprint,
    _raise,
    _strict_version_components,
)


_EXPECTED_OPTIX9_CURVE_FACTS = {
    "build_input_type": 0x2145,
    "primitive_type": 0x2503,
    "primitive_type_flags": 1 << 3,
    "builtin_is_build_flags": 1 << 2,
    "builtin_is_curve_endcap_flags": 0,
    "build_flags": 1 << 2,
    "geometry_flags": 1 << 1,
    "traversable_graph_flags": 1 << 0,
    "endcap_flags": 0,
}


@dataclass(frozen=True)
class V4CurveOwnerGroupedAnyHitResult:
    owner_hit_bits: tuple[int, ...]
    any_hit: int
    hit_owner_count: int
    query_completion_tokens: tuple[int, ...]
    counters: tuple[int, ...]
    statuses: tuple[dict[str, int], ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    composed_ptx_sha256: str
    native_library_sha256: str
    physical_receipt: dict[str, object]


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _native_static_fingerprint(
    control_points, widths, segment_indices, owner_ids, owner_count,
) -> str:
    columns: list[tuple[str, object]] = [("u32", owner_count)]
    columns.append(("u64", len(control_points)))
    for point, width in zip(control_points, widths):
        columns.extend(("f32", value) for value in point)
        columns.append(("f32", width))
    columns.append(("u64", len(segment_indices)))
    for segment_index, owner_id in zip(segment_indices, owner_ids):
        columns.append(("u32", segment_index))
        columns.append(("u32", owner_id))
    return _native_fingerprint(
        "rtdl.v4.native_curve_owner_grouped_static.v1", tuple(columns))


def _native_query_fingerprint(normalized) -> str:
    columns: list[tuple[str, object]] = [("u64", len(normalized))]
    for row in normalized:
        columns.extend(("f32", value) for value in row)
    return _native_fingerprint("rtdl.v4.native_curve_query.v1", tuple(columns))


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


def _native_output_fingerprint(owner_bits, completion) -> str:
    return _native_fingerprint(
        "rtdl.v4.native_curve_owner_grouped_output.v1",
        (
            ("u64", len(owner_bits)),
            *(("u32", value) for value in owner_bits),
            ("u64", len(completion)),
            *(("u32", value) for value in completion),
        ),
    )


def curve_owner_grouped_static_commitment_sha256(
    control_points, widths, segment_indices, owner_ids, owner_count,
) -> str:
    return _digest({
        "schema": "rtdl.v4.curve_owner_grouped_static_host.v1",
        "control_points": control_points,
        "widths": widths,
        "segment_indices": segment_indices,
        "owner_ids": owner_ids,
        "owner_count": owner_count,
    })


def _fresh(authority, abi):
    fresh = verify_curve_owner_grouped_any_hit_physical_schema(
        authority.behavior, authority.schema, target=authority.target)
    if fresh != authority:
        raise RuntimeError("curve owner-grouped authority does not rederive")
    verify_owner_grouped_any_hit_abi(abi, fresh.behavior)
    return fresh


def _configure(library):
    names = (
        "rtdl_optix_v4_prepare_curve_owner_grouped_any_hit_v1",
        "rtdl_optix_v4_execute_curve_owner_grouped_any_hit_v1",
        "rtdl_optix_v4_describe_curve_owner_grouped_any_hit_v1",
        "rtdl_optix_v4_destroy_curve_owner_grouped_any_hit_v1",
    )
    symbols = tuple(getattr(library, name, None) for name in names)
    if any(item is None for item in symbols):
        raise RuntimeError("native library lacks curve owner-grouped any-hit ABI")
    prepare, execute, describe, destroy = symbols
    prepare.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    execute.argtypes = [
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(_Status), ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    describe.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    destroy.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    for symbol in symbols:
        symbol.restype = ctypes.c_int
    return prepare, execute, describe, destroy


def _read_descriptor(describe, token: int) -> dict[str, object]:
    size = ctypes.c_size_t()
    error = ctypes.create_string_buffer(16384)
    _raise(int(describe(
        token, None, 0, ctypes.byref(size), error, len(error))),
        error, "curve owner-grouped descriptor size")
    if size.value == 0 or size.value > 1 << 20:
        raise RuntimeError("curve owner-grouped descriptor size is invalid")
    output = ctypes.create_string_buffer(size.value + 1)
    error = ctypes.create_string_buffer(16384)
    _raise(int(describe(
        token, output, len(output), ctypes.byref(size), error, len(error))),
        error, "curve owner-grouped descriptor")
    descriptor = json.loads(output.raw[:size.value].decode("utf-8"))
    expected = {
        "schema", "native_build_id", "build_input_type", "primitive_type",
        "primitive_type_flags", "builtin_is_build_flags",
        "builtin_is_curve_endcap_flags", "builtin_is_module",
        "user_intersection_program", "uses_motion_blur", "build_flags",
        "geometry_flags", "vertex_stride_bytes", "width_stride_bytes",
        "index_stride_bytes", "normal_buffers_present",
        "primitive_index_offset", "sbt_record_count", "gas_count",
        "primitive_count", "vertex_count", "owner_count", "motion_key_count",
        "endcap_flags", "traversable_graph_flags", "max_payload_values",
        "max_attribute_values", "max_trace_depth", "program_group_count",
        "compiled_optix_version", "compiled_optix_major",
        "compiled_optix_minor", "compiled_optix_patch", "cuda_device_ordinal",
        "cuda_compute_capability_major", "cuda_compute_capability_minor",
        "cuda_driver_version", "static_input_fingerprint",
        "device_static_input_fingerprint", "vertex_device_pointer",
        "width_device_pointer", "index_device_pointer",
        "owner_id_device_pointer", "traversable_identity", "execution_count",
        "last_execution_present", "last_status_failed", "last_query_count",
        "last_status_d2h_call_count",
        "last_application_output_d2h_call_count",
        "last_output_after_status_failure_count", "last_query_fingerprint",
        "last_status_fingerprint", "last_counter_fingerprint",
        "last_output_fingerprint",
    }
    if type(descriptor) is not dict or set(descriptor) != expected:
        raise RuntimeError("curve owner-grouped descriptor fields differ")
    if descriptor["schema"] != \
            "rtdl.v4.native_curve_owner_grouped_descriptor.v1" \
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
            or descriptor["primitive_count"] <= 0 \
            or descriptor["vertex_count"] < 2 \
            or descriptor["owner_count"] <= 0 \
            or descriptor["max_payload_values"] != 1 \
            or descriptor["max_attribute_values"] != 0 \
            or descriptor["max_trace_depth"] != 1 \
            or descriptor["program_group_count"] != 3:
        raise RuntimeError("curve owner-grouped descriptor contract differs")
    bool_fields = {
        "builtin_is_module", "user_intersection_program", "uses_motion_blur",
        "normal_buffers_present", "last_execution_present", "last_status_failed",
    }
    if any(type(descriptor[name]) is not bool for name in bool_fields):
        raise RuntimeError("curve owner-grouped descriptor Boolean field differs")
    string_fields = {
        "schema", "native_build_id", "static_input_fingerprint",
        "device_static_input_fingerprint",
        "last_query_fingerprint", "last_status_fingerprint",
        "last_counter_fingerprint", "last_output_fingerprint",
    }
    integer_fields = expected - bool_fields - string_fields
    if any(not isinstance(descriptor[name], int)
           or isinstance(descriptor[name], bool) or descriptor[name] < 0
           for name in integer_fields):
        raise RuntimeError("curve owner-grouped descriptor integer field differs")
    if not _is_native_fingerprint(descriptor["native_build_id"]):
        raise RuntimeError("curve owner-grouped native build identity is malformed")
    encoded_optix = (
        descriptor["compiled_optix_major"] * 10000
        + descriptor["compiled_optix_minor"] * 100
        + descriptor["compiled_optix_patch"]
    )
    if descriptor["compiled_optix_version"] != encoded_optix \
            or descriptor["compiled_optix_major"] == 0 \
            or descriptor["compiled_optix_minor"] >= 100 \
            or descriptor["compiled_optix_patch"] >= 100 \
            or descriptor["cuda_compute_capability_major"] == 0 \
            or descriptor["cuda_compute_capability_minor"] >= 100 \
            or descriptor["cuda_driver_version"] == 0:
        raise RuntimeError("curve owner-grouped runtime identity differs")
    for name in (
        "vertex_device_pointer", "width_device_pointer",
        "index_device_pointer", "owner_id_device_pointer",
        "traversable_identity",
    ):
        if not isinstance(descriptor[name], int) or descriptor[name] <= 0:
            raise RuntimeError("curve owner-grouped device identity is invalid")
    if descriptor["static_input_fingerprint"] != \
            descriptor["device_static_input_fingerprint"]:
        raise RuntimeError("curve owner-grouped static device content differs")
    if not _is_native_fingerprint(descriptor["static_input_fingerprint"]):
        raise RuntimeError("curve owner-grouped static fingerprint is malformed")
    if descriptor["last_execution_present"]:
        for name in (
            "last_query_fingerprint", "last_status_fingerprint",
            "last_counter_fingerprint",
        ):
            if not _is_native_fingerprint(descriptor[name]):
                raise RuntimeError(f"curve owner-grouped {name} is malformed")
        if descriptor["last_query_count"] <= 0 \
                or descriptor["last_status_d2h_call_count"] != 2 \
                or descriptor["last_output_after_status_failure_count"] != 0:
            raise RuntimeError("curve owner-grouped status-first evidence differs")
        if descriptor["last_status_failed"]:
            if descriptor["last_application_output_d2h_call_count"] != 0 \
                    or descriptor["last_output_fingerprint"] != "":
                raise RuntimeError("curve owner-grouped copied output after status failure")
        elif descriptor["last_application_output_d2h_call_count"] != 2 \
                or not _is_native_fingerprint(
                    descriptor["last_output_fingerprint"]):
            raise RuntimeError("curve owner-grouped successful output evidence differs")
    elif any((
        descriptor["execution_count"], descriptor["last_query_count"],
        descriptor["last_status_d2h_call_count"],
        descriptor["last_application_output_d2h_call_count"],
        descriptor["last_output_after_status_failure_count"],
        descriptor["last_query_fingerprint"],
        descriptor["last_status_fingerprint"],
        descriptor["last_counter_fingerprint"],
        descriptor["last_output_fingerprint"],
    )):
        raise RuntimeError("curve owner-grouped initial execution state differs")
    return descriptor


def _require_native_target_binding(descriptor, target) -> None:
    expected_optix = _strict_version_components(
        target.optix_sdk, 3, "OptiX SDK")
    expected_compute = _strict_version_components(
        target.compute_capability, 2, "compute capability")
    observed_optix = tuple(descriptor[name] for name in (
        "compiled_optix_major", "compiled_optix_minor", "compiled_optix_patch"))
    observed_compute = tuple(descriptor[name] for name in (
        "cuda_compute_capability_major", "cuda_compute_capability_minor"))
    if observed_optix != expected_optix or observed_compute != expected_compute:
        raise RuntimeError("loaded curve owner-grouped target differs from authority")


def _require_descriptor_transition(before, after) -> None:
    dynamic = {name for name in before if name.startswith("last_")} | {
        "execution_count",
    }
    if set(before) != set(after) or any(
            before[name] != after[name] for name in set(before) - dynamic):
        raise RuntimeError("curve owner-grouped static descriptor changed")


def _destroy_failed_prepare(destroy, token: int, primary: Exception) -> None:
    error = ctypes.create_string_buffer(16384)
    try:
        status = int(destroy(token, error, len(error)))
    except Exception as cleanup:
        raise RuntimeError(
            "curve owner-grouped prepare validation failed and cleanup raised; "
            f"primary={type(primary).__name__}: {primary}; "
            f"cleanup={type(cleanup).__name__}: {cleanup}"
        ) from primary
    if status:
        detail = error.value.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            "curve owner-grouped prepare validation failed and cleanup failed; "
            f"primary={type(primary).__name__}: {primary}; "
            f"cleanup_status={status}; cleanup={detail or '<empty>'}"
        ) from primary


class PreparedCurveOwnerGroupedAnyHit:
    def __init__(
        self, *, authority, abi, executable, control_points, widths,
        segment_indices, owner_ids, owner_count, library=None,
        native_library_path=None,
    ) -> None:
        fresh = _fresh(authority, abi)
        self._control_points = tuple(tuple(row) for row in control_points)
        self._widths = tuple(widths)
        self._segment_indices = tuple(segment_indices)
        self._owner_ids = tuple(owner_ids)
        self._owner_count = int(owner_count)
        composed_ptx = consume_verified_curve_owner_grouped_any_hit_executable(
            executable, fresh, abi)
        if library is None:
            from . import optix_runtime
            library = optix_runtime._load_optix_library()
        prepare, execute, describe, destroy = _configure(library)
        native_path, native_sha = _loaded_native_identity(
            library, native_library_path, symbol=prepare)
        if native_sha != fresh.target.native_sha256:
            raise RuntimeError("executed native bytes do not match authority")
        points_flat = [value for row in self._control_points for value in row]
        point_native = (ctypes.c_float * len(points_flat))(*points_flat)
        width_native = (ctypes.c_float * len(self._widths))(*self._widths)
        index_native = (ctypes.c_uint32 * len(self._segment_indices))(
            *self._segment_indices)
        owner_native = (ctypes.c_uint32 * len(self._owner_ids))(*self._owner_ids)
        token = ctypes.c_uint64()
        error = ctypes.create_string_buffer(16384)
        _raise(int(prepare(
            composed_ptx.encode("utf-8"), point_native, width_native,
            index_native, owner_native, len(self._control_points),
            len(self._segment_indices), self._owner_count,
            ctypes.byref(token), error, len(error))),
            error, "curve owner-grouped prepare")
        if token.value == 0:
            raise RuntimeError("curve owner-grouped prepare returned zero token")
        try:
            descriptor = _read_descriptor(describe, int(token.value))
            if descriptor["primitive_count"] != len(self._segment_indices) \
                    or descriptor["vertex_count"] != len(self._control_points) \
                    or descriptor["owner_count"] != self._owner_count:
                raise RuntimeError("curve owner-grouped cardinality differs")
            _require_native_target_binding(descriptor, fresh.target)
            expected_fingerprint = _native_static_fingerprint(
                self._control_points, self._widths, self._segment_indices,
                self._owner_ids, self._owner_count)
            if descriptor["static_input_fingerprint"] != expected_fingerprint:
                raise RuntimeError("curve owner-grouped static fingerprint differs")
        except Exception as primary:
            _destroy_failed_prepare(destroy, int(token.value), primary)
            raise
        self._fresh = fresh
        self._abi = abi
        self._library = library
        self._execute = execute
        self._describe = describe
        self._destroy = destroy
        self._token = int(token.value)
        self._descriptor = descriptor
        self._native_sha = native_sha
        self._ptx_sha = hashlib.sha256(composed_ptx.encode("utf-8")).hexdigest()
        self._physical_receipt = {
            "schema": "rtdl.v4.curve_owner_grouped_physical_receipt.v1",
            "behavior_schema_sha256": fresh.behavior.schema.schema_sha256,
            "physical_schema_sha256": fresh.schema.schema_sha256,
            "plan_sha256": fresh.canonical_plan.plan_sha256,
            "native_library_sha256": native_sha,
            "native_library_path": str(native_path),
            "composed_ptx_sha256": self._ptx_sha,
            "static_input_commitment_sha256":
                curve_owner_grouped_static_commitment_sha256(
                    self._control_points, self._widths,
                    self._segment_indices, self._owner_ids,
                    self._owner_count),
            "status_before_output": True,
            "device_reduction": "atomic_or_u32",
            "application_identity_used": False,
        }
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._execution_count = 0
        self._closed = False

    def _check_owner(self) -> None:
        if os.getpid() != self._pid or threading.get_ident() != self._thread:
            raise RuntimeError("curve owner-grouped owner crossed ownership boundary")

    def _check(self) -> None:
        if self._closed:
            raise RuntimeError("curve owner-grouped owner is closed")
        self._check_owner()

    @property
    def lifecycle_receipt(self) -> dict[str, object]:
        self._check()
        return {
            "schema": "rtdl.v4.prepared_curve_owner_grouped_owner.v1",
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "nonreentrant": True,
            "execution_count": self._execution_count,
            "native_library_sha256": self._native_sha,
            "composed_ptx_sha256": self._ptx_sha,
        }

    def __getstate__(self):
        raise RuntimeError("curve owner-grouped owner cannot be serialized")

    def execute(self, queries) -> V4CurveOwnerGroupedAnyHitResult:
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("curve owner-grouped owner is already executing")
        try:
            starts, ends = [], []
            for index, query in enumerate(queries):
                if len(query) != 2:
                    raise ValueError(f"query {index} must be (start,end)")
                starts.append(tuple(query[0]))
                ends.append(tuple(query[1]))
            normalized = verify_curve_boolean_motion_segments(starts, ends)
            start_flat = [value for row in normalized for value in row[:3]]
            end_flat = [value for row in normalized for value in row[3:]]
            count = len(normalized)
            starts_native = (ctypes.c_float * len(start_flat))(*start_flat)
            ends_native = (ctypes.c_float * len(end_flat))(*end_flat)
            owner_bits = (ctypes.c_uint32 * self._owner_count)()
            completion = (ctypes.c_uint32 * count)()
            statuses = (_Status * count)()
            counters = (ctypes.c_uint64 * 7)()
            error = ctypes.create_string_buffer(16384)
            audit = OptixTraversalAuditSession.open(library=self._library)
            try:
                native_status = int(self._execute(
                    self._token, starts_native, ends_native, count,
                    owner_bits, completion, statuses, counters,
                    error, len(error)))
                if native_status:
                    _raise(native_status, error, "curve owner-grouped execute")
                bit_values = tuple(int(value) for value in owner_bits)
                completion_values = tuple(int(value) for value in completion)
                status_rows = tuple({
                    name: int(getattr(item, name))
                    for name, _ in _Status._fields_
                } for item in statuses)
                counter_values = tuple(int(value) for value in counters)
                if any(value not in (0, 1) for value in bit_values) \
                        or any(completion_values):
                    raise RuntimeError("curve owner-grouped output contract differs")
                if counter_values[1] != count \
                        or counter_values[5] != count \
                        or counter_values[6] != count:
                    raise RuntimeError("curve owner-grouped role lifecycle differs")
                descriptor = _read_descriptor(self._describe, self._token)
                _require_descriptor_transition(self._descriptor, descriptor)
                if descriptor["execution_count"] != self._execution_count + 1:
                    raise RuntimeError("curve owner-grouped execution count differs")
                expected_execution = {
                    "last_execution_present": True,
                    "last_status_failed": False,
                    "last_query_count": count,
                    "last_status_d2h_call_count": 2,
                    "last_application_output_d2h_call_count": 2,
                    "last_output_after_status_failure_count": 0,
                    "last_query_fingerprint": _native_query_fingerprint(normalized),
                    "last_status_fingerprint": _native_status_fingerprint(status_rows),
                    "last_counter_fingerprint": _native_counter_fingerprint(
                        counter_values),
                    "last_output_fingerprint": _native_output_fingerprint(
                        bit_values, completion_values),
                }
                if any(descriptor[name] != value
                       for name, value in expected_execution.items()):
                    raise RuntimeError(
                        "curve owner-grouped execution fingerprint differs")
                output_sha = owner_grouped_any_hit_output_sha256(bit_values)
                physical = dict(self._physical_receipt)
                physical.update({
                    "native_descriptor": descriptor,
                    "query_count": count,
                    "owner_count": self._owner_count,
                    "output_commitment_sha256": output_sha,
                })
                route = "v4_builtin_curve_callback_ir:owner_grouped_any_hit_bool_or_v1"
                receipt = audit.finish(
                    semantic_digest=_digest({
                        "authority": self._fresh.authority_nonce,
                        "abi": self._abi.abi_sha256,
                        "ptx": self._ptx_sha,
                        "native": self._native_sha,
                        "physical": physical,
                    }),
                    output_digest=output_sha,
                    route_identity=route,
                    expected_program_bundles=(
                        "v4_curve_owner_grouped_any_hit_composed",),
                )
            except Exception:
                audit.abort()
                raise
            if receipt["physical_executor_classification"] != \
                    "optix_traversal_observed":
                raise RuntimeError("curve owner-grouped path lacked bound traversal")
            validate_traversal_receipt(
                receipt,
                provider_library_sha256=self._native_sha,
                route_identity=route,
                output_digest=output_sha,
                expected_program_bundles=(
                    "v4_curve_owner_grouped_any_hit_composed",),
                expected_successful_launch_count=1,
                expected_raygen_invocation_count=count,
            )
            self._execution_count += 1
            self._descriptor = descriptor
            return V4CurveOwnerGroupedAnyHitResult(
                bit_values,
                int(any(bit_values)),
                sum(bit_values),
                completion_values,
                counter_values,
                status_rows,
                receipt,
                output_sha,
                self._ptx_sha,
                self._native_sha,
                physical,
            )
        finally:
            self._active.release()

    def close(self) -> None:
        if self._closed:
            return
        self._check_owner()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close curve owner-grouped during execution")
        try:
            error = ctypes.create_string_buffer(16384)
            _raise(int(self._destroy(
                self._token, error, len(error))), error,
                "curve owner-grouped destroy")
            self._token = 0
            self._closed = True
        finally:
            self._active.release()

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            self.close()
        except Exception as cleanup:
            if exc is None:
                raise
            raise RuntimeError(
                "curve owner-grouped context body and cleanup both failed; "
                f"primary={type(exc).__name__}: {exc}; "
                f"cleanup={type(cleanup).__name__}: {cleanup}"
            ) from exc
        return False


__all__ = [
    "PreparedCurveOwnerGroupedAnyHit", "V4CurveOwnerGroupedAnyHitResult",
    "curve_owner_grouped_static_commitment_sha256",
]
