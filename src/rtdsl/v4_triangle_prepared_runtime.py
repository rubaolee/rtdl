"""Explicit prepared owner for the verified V4 built-in-triangle family."""

from __future__ import annotations

import ctypes
import hashlib
import math
import os
import threading
import time

from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_triangle_optix_compiler import consume_verified_triangle_executable
from .v4_triangle_optix_runtime import (
    V4TriangleCallbackResult,
    _Status,
    _bindings,
    _digest,
    _fresh_authority,
    _native_path,
)
from .v4_typed_physical_schema import verify_reference_triangle_contents


_BULK_U32X3_DIGEST_DOMAIN = (
    b"rtdl.v4.builtin_triangle.bulk_output.u32x3.v1\x00"
)


def _bulk_u32x3_digest(value) -> str:
    """Hash an exact contiguous bulk output without making Python rows."""

    try:
        import numpy as _np
    except ImportError as error:  # pragma: no cover - bulk mode requires NumPy
        raise RuntimeError("bulk output identity requires NumPy") from error
    if not isinstance(value, _np.ndarray) \
            or value.ndim != 2 or value.shape[1] != 3 \
            or value.dtype.str != "<u4" or not value.flags.c_contiguous:
        raise RuntimeError("bulk output must be a contiguous little-endian Nx3 u32 array")
    digest = hashlib.sha256()
    digest.update(_BULK_U32X3_DIGEST_DOMAIN)
    digest.update(int(value.shape[0]).to_bytes(8, "little", signed=False))
    digest.update(memoryview(value).cast("B"))
    return digest.hexdigest()


def _configure(library):
    prepare = getattr(library, "rtdl_optix_v4_prepare_builtin_triangle_callback_v1", None)
    execute = getattr(library, "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_v1", None)
    destroy = getattr(library, "rtdl_optix_v4_destroy_prepared_builtin_triangle_callback_v1", None)
    if prepare is None or execute is None or destroy is None:
        raise RuntimeError("native library lacks Goal5773 prepared built-in triangle ABI")
    prepare.argtypes = [
        ctypes.c_char_p, ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    execute.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(_Status), ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    destroy.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    for symbol in (prepare, execute, destroy):
        symbol.restype = ctypes.c_int
    return prepare, execute, destroy


def _raise(status, error, label):
    if status:
        raise RuntimeError(
            error.value.decode("utf-8", errors="replace")
            or f"{label} failed with status {status}")


class PreparedBuiltinTriangleOwner:
    def __init__(
        self, *, authority, plan, abi, executable, vertices, triangles,
        front_values, back_values, library=None, native_library_path=None,
    ):
        started = time.perf_counter()
        fresh = _fresh_authority(authority, plan, abi)
        composed_ptx = consume_verified_triangle_executable(
            executable, fresh, plan, abi)
        verify_reference_triangle_contents(vertices, triangles)
        if len(front_values) != len(triangles) or len(back_values) != len(triangles):
            raise ValueError("front/back metadata cardinality must equal primitive count")
        numpy_columns = False
        try:
            import numpy as _np
        except ImportError:  # pragma: no cover - optional partner
            _np = None
        if _np is not None and all(isinstance(value, _np.ndarray) for value in (
                vertices, triangles, front_values, back_values)):
            vertices_array = _np.ascontiguousarray(vertices, dtype=_np.float32)
            triangles_array = _np.ascontiguousarray(triangles, dtype=_np.uint32)
            front_array = _np.ascontiguousarray(front_values, dtype=_np.uint32)
            back_array = _np.ascontiguousarray(back_values, dtype=_np.uint32)
            for label, original in (("front", front_values), ("back", back_values)):
                if original.ndim != 1 or original.dtype.kind not in "iu":
                    raise ValueError(f"{label} metadata must be a one-dimensional integer array")
                if original.dtype.kind == "i" and bool((original < 0).any()):
                    raise ValueError(f"{label} metadata must be u32")
                if int(original.max(initial=0)) > 0xFFFFFFFF:
                    raise ValueError(f"{label} metadata must be u32")
            vertices_native = vertices_array.ctypes.data_as(
                ctypes.POINTER(ctypes.c_float))
            indices_native = triangles_array.ctypes.data_as(
                ctypes.POINTER(ctypes.c_uint32))
            front_native = front_array.ctypes.data_as(
                ctypes.POINTER(ctypes.c_uint32))
            back_native = back_array.ctypes.data_as(
                ctypes.POINTER(ctypes.c_uint32))
            maximum_index = int(triangles_array.max(initial=0))
            numpy_columns = True
        else:
            if any(not 0 <= int(value) <= 0xFFFFFFFF
                   for value in (*front_values, *back_values)):
                raise ValueError("front/back metadata must be u32")
            vertex_flat = [float(value) for row in vertices for value in row]
            index_flat = [int(value) for row in triangles for value in row]
            if not all(math.isfinite(value) for value in vertex_flat):
                raise ValueError("prepared triangle vertices must be finite")
            vertices_native = (ctypes.c_float * len(vertex_flat))(*vertex_flat)
            indices_native = (ctypes.c_uint32 * len(index_flat))(*index_flat)
            front_native = (ctypes.c_uint32 * len(front_values))(*map(int, front_values))
            back_native = (ctypes.c_uint32 * len(back_values))(*map(int, back_values))
            maximum_index = max(index_flat)
        if library is None:
            from . import optix_runtime
            library = optix_runtime._load_optix_library()
        native_path = _native_path(library, native_library_path)
        native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
        if native_sha != fresh.target.native_sha256:
            raise RuntimeError("executed native bytes do not match target authority")
        prepare, execute, destroy = _configure(library)
        token = ctypes.c_uint64()
        error = ctypes.create_string_buffer(16384)
        _raise(int(prepare(
            composed_ptx.encode(), vertices_native, len(vertices),
            indices_native, len(triangles), front_native, back_native,
            ctypes.byref(token), error, len(error))), error,
            "prepared built-in triangle prepare")
        if not token.value:
            raise RuntimeError("prepared built-in triangle returned zero token")
        self._token = int(token.value)
        self._fresh = fresh
        self._plan = plan
        self._abi = abi
        self._library = library
        self._execute = execute
        self._destroy = destroy
        self._vertex_count = len(vertices)
        self._primitive_count = len(triangles)
        self._maximum_index = maximum_index
        self._numpy_column_fast_path = numpy_columns
        self._native_sha = native_sha
        self._ptx_sha = hashlib.sha256(composed_ptx.encode()).hexdigest()
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._closed = False
        self._execution_count = 0
        self.prepare_seconds = time.perf_counter() - started
        self._session_identity = _digest({
            "schema": "rtdl.v4.prepared_builtin_triangle_owner.v1",
            "authority": fresh.authority_nonce,
            "plan": plan.plan_sha256,
            "abi": abi.abi_sha256,
            "ptx": self._ptx_sha,
            "native": native_sha,
            "pid": self._pid,
            "thread": self._thread,
            "token": self._token,
        })

    def __getstate__(self):
        raise RuntimeError("prepared built-in triangle owner cannot be serialized")

    def _check(self):
        if self._closed:
            raise RuntimeError("prepared built-in triangle owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError("prepared built-in triangle owner crossed process boundary")
        if threading.get_ident() != self._thread:
            raise RuntimeError("prepared built-in triangle owner crossed thread boundary")

    @property
    def lifecycle_receipt(self):
        self._check()
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "session_identity": self._session_identity,
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "nonreentrant": True,
            "prepare_seconds_reported_separately": True,
            "cold_result_replaced": False,
            "execution_count": self._execution_count,
            "native_library_sha256": self._native_sha,
            "composed_ptx_sha256": self._ptx_sha,
            "numpy_column_fast_path": self._numpy_column_fast_path,
        }

    def execute(
        self, queries, *, expected_output=None,
        partner_column_output: bool = False,
    ):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared built-in triangle owner is already executing")
        try:
            if len(queries) == 0:
                raise ValueError("queries are required")
            numpy_queries = False
            try:
                import numpy as _np
            except ImportError:  # pragma: no cover - optional partner
                _np = None
            if _np is not None and isinstance(queries, _np.ndarray):
                if queries.ndim != 2 or queries.shape[1] != 7:
                    raise ValueError("NumPy queries must be an Nx7 f32 array")
                query_array = _np.ascontiguousarray(queries, dtype=_np.float32)
                if not bool(_np.isfinite(query_array).all()) \
                        or bool((query_array[:, 6] <= 0.0).any()) \
                        or bool(_np.all(query_array[:, 3:6] == 0.0, axis=1).any()):
                    raise ValueError("NumPy queries contain an invalid ray")
                origins_array = _np.ascontiguousarray(query_array[:, :3])
                directions_array = _np.ascontiguousarray(query_array[:, 3:6])
                tmax_array = _np.ascontiguousarray(query_array[:, 6])
                numpy_queries = True
            else:
                origins, directions, tmax_values = [], [], []
                for index, (origin, direction, tmax) in enumerate(queries):
                    if len(origin) != 3 or len(direction) != 3:
                        raise ValueError(f"query {index} must have vec3 origin/direction")
                    values = [float(value) for value in (*origin, *direction, tmax)]
                    if not all(math.isfinite(value) for value in values) \
                            or float(tmax) <= 0.0 \
                            or all(float(value) == 0.0 for value in direction):
                        raise ValueError(f"query {index} is invalid")
                    origins.extend(map(float, origin)); directions.extend(map(float, direction))
                    tmax_values.append(float(tmax))
            count = len(queries)
            bindings = _bindings(
                self._fresh, vertex_count=self._vertex_count,
                primitive_count=self._primitive_count, query_count=count,
                maximum_index=self._maximum_index)
            binding_digest = _digest([{
                "semantic": item.semantic.value,
                "element_count": item.element_count,
                "device_id": item.device_id,
                "stream_id": item.stream_id,
                "owner_nonce": item.owner_nonce,
                "mutation_epoch": item.mutation_epoch,
                "alignment_bytes": item.alignment_bytes,
                "contiguous": item.contiguous,
                "writable": item.writable,
                "maximum_index": item.maximum_index,
            } for item in bindings])
            if numpy_queries:
                origins_native = origins_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
                directions_native = directions_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
                tmax_native = tmax_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            else:
                origins_native = (ctypes.c_float * len(origins))(*origins)
                directions_native = (ctypes.c_float * len(directions))(*directions)
                tmax_native = (ctypes.c_float * count)(*tmax_values)
            output_0 = (ctypes.c_uint32 * count)(); output_1 = (ctypes.c_uint32 * count)()
            output_2 = (ctypes.c_uint32 * count)(); observed_primitive = (ctypes.c_uint32 * count)()
            observed_kind = (ctypes.c_uint32 * count)(); observed_bx = (ctypes.c_float * count)()
            observed_by = (ctypes.c_float * count)(); statuses = (_Status * count)()
            counters = (ctypes.c_uint64 * 7)(); error = ctypes.create_string_buffer(16384)
            audit = OptixTraversalAuditSession.open(library=self._library)
            try:
                _raise(int(self._execute(
                    self._token, origins_native, directions_native, tmax_native,
                    count, output_0, output_1, output_2, observed_primitive,
                    observed_kind, observed_bx, observed_by, statuses, counters,
                    error, len(error))), error, "prepared built-in triangle execute")
                if partner_column_output:
                    if not numpy_queries:
                        raise ValueError(
                            "partner column output requires NumPy query columns")
                    observed = _np.column_stack((
                        _np.ctypeslib.as_array(output_0),
                        _np.ctypeslib.as_array(output_1),
                        _np.ctypeslib.as_array(output_2),
                    )).astype(_np.uint32, copy=False)
                    if any(
                        int(item.first_error_claimed) or int(item.error_code)
                        for item in statuses
                    ):
                        raise RuntimeError(
                            "prepared built-in triangle returned device error")
                    status_rows = ({
                        "validated_row_count": count,
                        "first_error_claimed": 0,
                        "error_code": 0,
                    },)
                else:
                    observed = tuple(
                        (int(output_0[index]), int(output_1[index]), int(output_2[index]))
                        for index in range(count))
                    status_rows = tuple({
                        name: int(getattr(item, name)) for name, _ in _Status._fields_}
                        for item in statuses)
                counter_rows = tuple(int(item) for item in counters)
                if not partner_column_output and any(
                    row["first_error_claimed"] or row["error_code"]
                    for row in status_rows
                ):
                    raise RuntimeError("prepared built-in triangle returned device error")
                if counter_rows[1] != count or counter_rows[6] != count \
                        or counter_rows[4] + counter_rows[5] != count:
                    raise RuntimeError("prepared built-in triangle role lifecycle incomplete")
                if expected_output is not None:
                    if partner_column_output:
                        if not _np.array_equal(
                            observed,
                            _np.asarray(expected_output, dtype=_np.uint32),
                        ):
                            raise RuntimeError(
                                "prepared built-in triangle output mismatch")
                    elif observed != tuple(
                            tuple(map(int, row)) for row in expected_output):
                        raise RuntimeError(
                            "prepared built-in triangle output mismatch")
                output_sha = (
                    _bulk_u32x3_digest(observed)
                    if partner_column_output else _digest(observed)
                )
                receipt = audit.finish(
                    semantic_digest=_digest({
                        "authority": self._fresh.authority_nonce,
                        "plan": self._plan.plan_sha256, "abi": self._abi.abi_sha256,
                        "ptx": self._ptx_sha, "native": self._native_sha,
                        "bindings": binding_digest,
                    }), output_digest=output_sha,
                    route_identity="v4_builtin_triangle_callback_ir:four_role_composed_v1",
                    expected_program_bundles=(
                        "v4_builtin_triangle_callback_ir_four_role_composed",))
            except Exception:
                audit.abort()
                raise
            if receipt["physical_executor_classification"] != "optix_traversal_observed":
                raise RuntimeError("prepared built-in triangle lacked bound traversal")
            hit_rows = (() if partner_column_output else tuple({
                "primitive_index": None if int(observed_primitive[index]) == 0xFFFFFFFF else int(observed_primitive[index]),
                "hit_kind": None if int(observed_kind[index]) == 0xFFFFFFFF else int(observed_kind[index]),
                "barycentric_x": None if int(observed_primitive[index]) == 0xFFFFFFFF else float(observed_bx[index]),
                "barycentric_y": None if int(observed_primitive[index]) == 0xFFFFFFFF else float(observed_by[index]),
            } for index in range(count)))
            self._execution_count += 1
            return V4TriangleCallbackResult(
                observed, hit_rows, counter_rows, status_rows, receipt,
                output_sha, self._ptx_sha, self._native_sha, binding_digest)
        finally:
            self._active.release()

    def close(self):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close prepared built-in triangle during execution")
        try:
            error = ctypes.create_string_buffer(16384)
            _raise(int(self._destroy(self._token, error, len(error))), error,
                   "prepared built-in triangle destroy")
            self._token = 0
            self._closed = True
        finally:
            self._active.release()

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def prepare_builtin_triangle_callback(**kwargs):
    return PreparedBuiltinTriangleOwner(**kwargs)


__all__ = ["PreparedBuiltinTriangleOwner", "prepare_builtin_triangle_callback"]
