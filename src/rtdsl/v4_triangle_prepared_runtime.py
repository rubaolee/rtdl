"""Explicit prepared owner for the verified V4 built-in-triangle family."""

from __future__ import annotations

import ctypes
import hashlib
import math
import os
import secrets
import threading
import time

from .physical_execution_provenance import (
    OptixTraversalAuditSession,
    ValidatedCompactTraversalReceipt,
    validate_bound_compact_traversal_receipt,
)
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


class _CompactLifecycleSummary(ctypes.Structure):
    _fields_ = [
        ("schema_version", ctypes.c_uint32), ("ok", ctypes.c_uint32),
        ("first_error_claimed", ctypes.c_uint32),
        ("error_code", ctypes.c_uint32),
        ("validated_row_count", ctypes.c_uint64),
        ("required_invocation_mask", ctypes.c_uint32),
        ("terminal_invocation_mask", ctypes.c_uint32),
        ("invalid_row_count", ctypes.c_uint32),
        ("first_invalid_row", ctypes.c_uint64),
        ("role_counters", ctypes.c_uint64 * 7),
        ("success_status_d2h_bytes", ctypes.c_uint64),
    ]


def _validate_compact_lifecycle_summary(summary, count: int):
    counters = tuple(int(value) for value in summary.role_counters)
    if int(summary.schema_version) != 2 or int(summary.ok) != 1 \
            or int(summary.first_error_claimed) != 0 \
            or int(summary.error_code) != 0 \
            or int(summary.validated_row_count) != count \
            or int(summary.required_invocation_mask) != ((1 << 1) | (1 << 6)) \
            or int(summary.terminal_invocation_mask) != ((1 << 4) | (1 << 5)) \
            or int(summary.invalid_row_count) != 0 \
            or int(summary.first_invalid_row) != (1 << 64) - 1 \
            or int(summary.success_status_d2h_bytes) != ctypes.sizeof(
                _CompactLifecycleSummary) \
            or counters[1] != count or counters[6] != count \
            or counters[4] + counters[5] != count:
        raise RuntimeError(
            "prepared built-in triangle compact lifecycle summary is invalid")
    return counters


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
    digest.update(value.dtype.str.encode("ascii"))
    digest.update(str(tuple(value.shape)).encode("ascii"))
    digest.update(memoryview(value).cast("B"))
    return digest.hexdigest()


def _configure(library):
    prepare = getattr(library, "rtdl_optix_v4_prepare_builtin_triangle_callback_v1", None)
    execute = getattr(library, "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_v1", None)
    execute_columns = getattr(
        library,
        "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_columns_v2",
        None,
    )
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
    if execute_columns is not None:
        execute_columns.argtypes = [
            ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(_CompactLifecycleSummary),
            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
        ]
    destroy.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    for symbol in (prepare, execute, execute_columns, destroy):
        if symbol is None:
            continue
        symbol.restype = ctypes.c_int
    return prepare, execute, execute_columns, destroy


def _configure_device_resident_query_batches(library):
    prepare = getattr(
        library,
        "rtdl_optix_v4_prepare_builtin_triangle_query_batch_columns_v1",
        None,
    )
    execute = getattr(
        library,
        "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_batch_columns_v3",
        None,
    )
    destroy = getattr(
        library,
        "rtdl_optix_v4_destroy_prepared_builtin_triangle_query_batch_v1",
        None,
    )
    prepare_rows = getattr(
        library,
        "rtdl_optix_v4_prepare_builtin_triangle_query_batch_rows_v2",
        None,
    )
    execute_rows = getattr(
        library,
        "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_batch_rows_v4",
        None,
    )
    prepare_aos_rows = getattr(
        library,
        "rtdl_optix_v4_prepare_builtin_triangle_query_batch_aos_rows_v3",
        None,
    )
    symbols = (prepare, execute, destroy)
    if all(symbol is None for symbol in symbols):
        if prepare_rows is not None or execute_rows is not None \
                or prepare_aos_rows is not None:
            raise RuntimeError(
                "native library has packed-row ABI without query-batch ABI")
        return (*symbols, None, None, None)
    if any(symbol is None for symbol in symbols):
        raise RuntimeError(
            "native library has a partial prepared triangle query-batch ABI")
    prepare.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    execute.argtypes = [
        ctypes.c_uint64, ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(_CompactLifecycleSummary),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    destroy.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    if (prepare_rows is None) != (execute_rows is None):
        raise RuntimeError(
            "native library has a partial prepared triangle packed-row ABI")
    if prepare_aos_rows is not None and execute_rows is None:
        raise RuntimeError(
            "native library has a partial prepared triangle AoS-row ABI")
    if prepare_rows is not None:
        prepare_rows.argtypes = [
            ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)),
            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
        ]
        execute_rows.argtypes = [
            ctypes.c_uint64, ctypes.c_uint64,
            ctypes.POINTER(_CompactLifecycleSummary),
            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
        ]
    if prepare_aos_rows is not None:
        prepare_aos_rows.argtypes = [
            ctypes.c_uint64, ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)),
            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
        ]
    for symbol in symbols:
        symbol.restype = ctypes.c_int
    for symbol in (prepare_rows, execute_rows, prepare_aos_rows):
        if symbol is not None:
            symbol.restype = ctypes.c_int
    return (*symbols, prepare_rows, execute_rows, prepare_aos_rows)


def _raise(status, error, label):
    if status:
        raise RuntimeError(
            error.value.decode("utf-8", errors="replace")
            or f"{label} failed with status {status}")


_PREPARED_QUERY_BATCH_TOKEN = object()
_PREPARED_OUTPUT_DIGEST_CACHE_TOKEN = object()


class _PreparedOutputDigestCache:
    """Materialize immutable output once, then validate reuse exactly."""

    __slots__ = ("_digest", "_output", "_payload", "_token")

    def __init__(self, *, token):
        if token is not _PREPARED_OUTPUT_DIGEST_CACHE_TOKEN:
            raise RuntimeError("prepared output digest cache requires its owner")
        object.__setattr__(self, "_digest", None)
        object.__setattr__(self, "_output", None)
        object.__setattr__(self, "_payload", None)
        object.__setattr__(self, "_token", token)

    def __setattr__(self, name, value):
        raise AttributeError("prepared output digest cache is immutable")

    def resolve(self, output):
        try:
            import numpy as _np
        except ImportError as error:  # pragma: no cover - bulk mode requires NumPy
            raise RuntimeError("bulk output identity requires NumPy") from error
        if not isinstance(output, _np.ndarray) \
                or output.ndim != 2 or output.shape[1] != 3 \
                or output.dtype.str != "<u4" or not output.flags.c_contiguous:
            raise RuntimeError(
                "prepared output must be a contiguous little-endian Nx3 u32 array")
        stable = self._output
        digest = self._digest
        if stable is not None and digest is not None \
                and stable.shape == output.shape \
                and _np.array_equal(stable, output):
            return stable, digest

        payload = memoryview(output).cast("B").tobytes()
        stable = _np.frombuffer(payload, dtype=_np.dtype("<u4")).reshape(
            output.shape)
        digest = _bulk_u32x3_digest(stable)
        object.__setattr__(self, "_payload", payload)
        object.__setattr__(self, "_output", stable)
        object.__setattr__(self, "_digest", digest)
        return stable, digest


class PreparedBuiltinTriangleQueryBatch:
    """Owner-bound immutable query snapshot admitted before execution."""

    __slots__ = (
        "_binding_digest", "_count", "_directions", "_owner",
        "_host_output", "_host_output_pointer", "_native_token", "_origins",
        "_output_digest_cache", "_pointers", "_query_rows",
        "_semantic_digest", "_tmax", "_token",
    )

    def __init__(
        self, *, owner, origins, directions, tmax, binding_digest,
        semantic_digest, native_token, host_output, host_output_pointer, token,
        query_rows=None,
    ):
        if token is not _PREPARED_QUERY_BATCH_TOKEN:
            raise RuntimeError("prepared triangle query batch requires its owner")
        if query_rows is None:
            if origins is None or directions is None or tmax is None:
                raise RuntimeError(
                    "prepared triangle query batch host columns are incomplete")
            count = int(tmax.shape[0])
            pointers = tuple(
                int(value.ctypes.data) for value in (origins, directions, tmax))
        else:
            if origins is not None or directions is not None or tmax is not None \
                    or query_rows.ndim != 2 or query_rows.shape[1] != 7:
                raise RuntimeError(
                    "prepared triangle AoS query snapshot is malformed")
            count = int(query_rows.shape[0])
            pointers = (int(query_rows.ctypes.data),)
        object.__setattr__(self, "_owner", owner)
        object.__setattr__(self, "_origins", origins)
        object.__setattr__(self, "_directions", directions)
        object.__setattr__(self, "_tmax", tmax)
        object.__setattr__(self, "_query_rows", query_rows)
        object.__setattr__(self, "_count", count)
        object.__setattr__(self, "_pointers", pointers)
        object.__setattr__(self, "_binding_digest", binding_digest)
        object.__setattr__(self, "_semantic_digest", semantic_digest)
        object.__setattr__(self, "_native_token", int(native_token))
        object.__setattr__(self, "_host_output", host_output)
        object.__setattr__(self, "_host_output_pointer", host_output_pointer)
        object.__setattr__(
            self, "_output_digest_cache",
            _PreparedOutputDigestCache(
                token=_PREPARED_OUTPUT_DIGEST_CACHE_TOKEN),
        )
        object.__setattr__(self, "_token", token)

    def __setattr__(self, name, value):
        raise AttributeError("prepared triangle query batch is immutable")

    def __getstate__(self):
        raise RuntimeError("prepared triangle query batch cannot be serialized")

    def __len__(self):
        return self._count

    @property
    def device_resident(self):
        return self._native_token != 0


_VALIDATED_PREPARED_EXECUTION_TOKEN = object()


class _ValidatedPreparedTriangleExecution:
    """Owner-created proof that runtime output and receipt were checked."""

    __slots__ = (
        "binding_digest", "native_library_sha256", "output", "output_sha256",
        "output_snapshot", "owner", "query_count", "receipt", "token",
        "composed_ptx_sha256",
    )

    def __init__(
        self, *, owner, output, output_sha256, receipt, query_count,
        composed_ptx_sha256, native_library_sha256, binding_digest, token,
    ):
        if token is not _VALIDATED_PREPARED_EXECUTION_TOKEN:
            raise RuntimeError("validated prepared execution requires its owner")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "output", output)
        object.__setattr__(self, "output_sha256", output_sha256)
        object.__setattr__(self, "receipt", receipt)
        object.__setattr__(self, "query_count", query_count)
        object.__setattr__(self, "composed_ptx_sha256", composed_ptx_sha256)
        object.__setattr__(self, "native_library_sha256", native_library_sha256)
        object.__setattr__(self, "binding_digest", binding_digest)
        object.__setattr__(
            self, "output_snapshot",
            (
                id(output), int(output.ctypes.data), output.dtype.str,
                tuple(output.shape), tuple(output.strides),
                bool(output.flags.c_contiguous),
            ),
        )
        object.__setattr__(self, "token", token)

    def __setattr__(self, name, value):
        raise AttributeError("validated prepared execution is immutable")


def validate_prepared_triangle_execution(
    result, *, owner, query_count, composed_ptx_sha256,
    native_library_sha256, binding_digest,
):
    """Consume the runtime's in-process proof without rescanning output bytes."""

    authority = getattr(result, "_validated_prepared_execution", None)
    if type(authority) is not _ValidatedPreparedTriangleExecution \
            or authority.token is not _VALIDATED_PREPARED_EXECUTION_TOKEN \
            or authority.owner is not owner \
            or authority.output is not result.output \
            or authority.output_sha256 != result.output_sha256 \
            or authority.receipt is not result.traversal_receipt \
            or authority.query_count != query_count \
            or authority.composed_ptx_sha256 != composed_ptx_sha256 \
            or authority.native_library_sha256 != native_library_sha256 \
            or authority.binding_digest != binding_digest \
            or authority.output_snapshot != (
                id(result.output), int(result.output.ctypes.data),
                result.output.dtype.str, tuple(result.output.shape),
                tuple(result.output.strides),
                bool(result.output.flags.c_contiguous),
            ):
        raise RuntimeError("validated prepared triangle execution binding differs")
    return authority


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
        prepare, execute, execute_columns, destroy = _configure(library)
        (
            prepare_query_batch,
            execute_query_batch,
            destroy_query_batch,
            prepare_query_batch_rows,
            execute_query_batch_rows,
            prepare_query_batch_aos_rows,
        ) = _configure_device_resident_query_batches(library)
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
        self._execute_columns = execute_columns
        self._prepare_query_batch = prepare_query_batch
        self._execute_query_batch = execute_query_batch
        self._destroy_query_batch = destroy_query_batch
        self._prepare_query_batch_rows = prepare_query_batch_rows
        self._execute_query_batch_rows = execute_query_batch_rows
        self._prepare_query_batch_aos_rows = prepare_query_batch_aos_rows
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
        self._audit_sequence = 0
        self._audit_nonce_hi = secrets.randbits(64) or 1
        self._audit_error_buffer = ctypes.create_string_buffer(16384)
        self._execution_error_buffer = ctypes.create_string_buffer(16384)
        self._native_query_batch_tokens = set()
        self._prepared_query_batch_authorities = {}
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

    def _binding_identity(self, count: int):
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
        semantic_digest = _digest({
            "authority": self._fresh.authority_nonce,
            "plan": self._plan.plan_sha256,
            "abi": self._abi.abi_sha256,
            "ptx": self._ptx_sha,
            "native": self._native_sha,
            "bindings": binding_digest,
        })
        return binding_digest, semantic_digest

    def prepare_query_batch(self, queries):
        """Snapshot and admit one reusable query batch outside execution."""

        self._check()
        try:
            import numpy as _np
        except ImportError as error:  # pragma: no cover - NumPy batch API
            raise RuntimeError(
                "prepared triangle query batches require NumPy") from error
        if not isinstance(queries, _np.ndarray) \
                or queries.ndim != 2 or queries.shape[1] != 7:
            raise ValueError("prepared triangle queries must be an Nx7 NumPy array")
        query_array = _np.ascontiguousarray(queries, dtype=_np.float32)
        count = len(query_array)
        if count == 0:
            raise ValueError("prepared triangle queries contain an invalid ray")
        binding_digest, semantic_digest = self._binding_identity(count)
        native_token = 0
        host_output = None
        host_output_pointer = None
        query_rows = None
        prepare_device_batch = getattr(self, "_prepare_query_batch", None)
        prepare_device_rows = getattr(self, "_prepare_query_batch_rows", None)
        prepare_device_aos_rows = getattr(
            self, "_prepare_query_batch_aos_rows", None)
        if prepare_device_aos_rows is not None:
            # One immutable AoS snapshot replaces the older Python-side
            # transpose plus three immutable copies.  Native code validates
            # every row before publishing the device-resident batch token.
            query_rows = _np.frombuffer(
                query_array.tobytes(order="C"), dtype=_np.float32,
            ).reshape(count, 7)
            origins = directions = tmax = None
            returned_token = ctypes.c_uint64()
            returned_output = ctypes.POINTER(ctypes.c_uint32)()
            error = getattr(self, "_execution_error_buffer", None)
            if error is None:
                error = ctypes.create_string_buffer(16384)
            error[0] = b"\0"
            _raise(int(prepare_device_aos_rows(
                self._token,
                query_rows.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                count, ctypes.byref(returned_token),
                ctypes.byref(returned_output), error, len(error),
            )), error, "prepared built-in triangle AoS-row batch prepare")
            native_token = int(returned_token.value)
            if native_token == 0 or not returned_output:
                raise RuntimeError(
                    "prepared built-in triangle AoS-row batch returned null")
            host_output = _np.ctypeslib.as_array(
                returned_output, shape=(count * 3,)).reshape(count, 3)
            host_output.setflags(write=False)
            host_output_pointer = returned_output
            self._native_query_batch_tokens.add(native_token)
        else:
            if not bool(_np.isfinite(query_array).all()) \
                    or bool((query_array[:, 6] <= 0.0).any()) \
                    or bool(_np.all(
                        query_array[:, 3:6] == 0.0, axis=1).any()):
                raise ValueError(
                    "prepared triangle queries contain an invalid ray")

            def frozen(value, shape):
                raw = _np.ascontiguousarray(value).tobytes(order="C")
                return _np.frombuffer(raw, dtype=_np.float32).reshape(shape)

            origins = frozen(query_array[:, :3], (count, 3))
            directions = frozen(query_array[:, 3:6], (count, 3))
            tmax = frozen(query_array[:, 6], (count,))
        if prepare_device_aos_rows is None and prepare_device_rows is not None:
            returned_token = ctypes.c_uint64()
            returned_output = ctypes.POINTER(ctypes.c_uint32)()
            error = getattr(self, "_execution_error_buffer", None)
            if error is None:
                error = ctypes.create_string_buffer(16384)
            error[0] = b"\0"
            _raise(int(prepare_device_rows(
                self._token,
                origins.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                directions.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                tmax.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                count, ctypes.byref(returned_token),
                ctypes.byref(returned_output), error, len(error),
            )), error, "prepared built-in triangle packed-row batch prepare")
            native_token = int(returned_token.value)
            if native_token == 0 or not returned_output:
                raise RuntimeError(
                    "prepared built-in triangle packed-row batch returned null")
            host_output = _np.ctypeslib.as_array(
                returned_output, shape=(count * 3,)).reshape(count, 3)
            host_output.setflags(write=False)
            host_output_pointer = returned_output
            self._native_query_batch_tokens.add(native_token)
        elif prepare_device_aos_rows is None and prepare_device_batch is not None:
            returned_token = ctypes.c_uint64()
            error = ctypes.create_string_buffer(16384)
            _raise(int(prepare_device_batch(
                self._token,
                origins.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                directions.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                tmax.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                count, ctypes.byref(returned_token), error, len(error),
            )), error, "prepared built-in triangle query batch prepare")
            native_token = int(returned_token.value)
            if native_token == 0:
                raise RuntimeError(
                    "prepared built-in triangle query batch returned zero token")
            self._native_query_batch_tokens.add(native_token)
        value = PreparedBuiltinTriangleQueryBatch(
            owner=self, origins=origins, directions=directions, tmax=tmax,
            binding_digest=binding_digest, semantic_digest=semantic_digest,
            native_token=native_token, host_output=host_output,
            host_output_pointer=host_output_pointer,
            token=_PREPARED_QUERY_BATCH_TOKEN, query_rows=query_rows,
        )
        authorities = getattr(self, "_prepared_query_batch_authorities", None)
        if authorities is None:
            authorities = {}
            self._prepared_query_batch_authorities = authorities
        authorities[id(value)] = (
            value, origins, directions, tmax, count,
            binding_digest, semantic_digest, native_token,
            host_output, host_output_pointer, value._output_digest_cache,
        )
        return value

    def _prepared_query_batch_execution_state(self, value):
        registered = getattr(
            self, "_prepared_query_batch_authorities", {}).get(id(value))
        if registered is not None:
            if registered[0] is not value:
                raise RuntimeError(
                    "prepared triangle query batch registry identity drifted")
            return registered[1:]
        columns = (value._origins, value._directions, value._tmax) \
            if type(value) is PreparedBuiltinTriangleQueryBatch else ()
        if type(value) is not PreparedBuiltinTriangleQueryBatch \
                or value._token is not _PREPARED_QUERY_BATCH_TOKEN \
                or value._owner is not self \
                or value._count <= 0 \
                or type(value._output_digest_cache) \
                    is not _PreparedOutputDigestCache \
                or value._output_digest_cache._token \
                    is not _PREPARED_OUTPUT_DIGEST_CACHE_TOKEN \
                or (value._native_token != 0 and (
                    getattr(self, "_execute_query_batch", None) is None
                    or value._native_token not in getattr(
                        self, "_native_query_batch_tokens", ()))) \
                or tuple(int(item.ctypes.data) for item in columns) \
                    != value._pointers \
                or value._origins.shape != (value._count, 3) \
                or value._directions.shape != (value._count, 3) \
                or value._tmax.shape != (value._count,) \
                or (value._host_output is not None and (
                    value._host_output_pointer is None
                    or value._host_output.shape != (value._count, 3)
                    or value._host_output.dtype.str != "<u4"
                    or not value._host_output.flags.c_contiguous
                    or value._host_output.flags.writeable
                    or int(value._host_output.ctypes.data)
                    != ctypes.addressof(value._host_output_pointer.contents))) \
                or any(item.dtype.str != "<f4" or not item.flags.c_contiguous
                       or item.flags.writeable for item in columns):
            raise RuntimeError("prepared triangle query batch identity drifted")
        return (
            value._origins, value._directions, value._tmax, value._count,
            value._binding_digest, value._semantic_digest,
            value._native_token, value._host_output,
            value._host_output_pointer, value._output_digest_cache,
        )

    def _prepared_query_batch_columns(self, value):
        return self._prepared_query_batch_execution_state(value)[:6]

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
            prepared_query_batch = type(queries) is PreparedBuiltinTriangleQueryBatch
            numpy_queries = False
            try:
                import numpy as _np
            except ImportError:  # pragma: no cover - optional partner
                _np = None
            if prepared_query_batch:
                if _np is None:  # pragma: no cover - construction required NumPy
                    raise RuntimeError("prepared triangle query batch lost NumPy")
                (
                    origins_array, directions_array, tmax_array, count,
                    binding_digest, semantic_digest,
                    native_token, host_output, host_output_pointer,
                    output_digest_cache,
                ) = self._prepared_query_batch_execution_state(queries)
                numpy_queries = True
            elif _np is not None and isinstance(queries, _np.ndarray):
                if len(queries) == 0:
                    raise ValueError("queries are required")
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
                if len(queries) == 0:
                    raise ValueError("queries are required")
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
            if not prepared_query_batch:
                count = len(queries)
                binding_digest, semantic_digest = self._binding_identity(count)
            if prepared_query_batch and native_token and partner_column_output:
                origins_native = directions_native = tmax_native = None
            elif numpy_queries:
                if origins_array is None:
                    query_rows = queries._query_rows
                    if query_rows is None:
                        raise RuntimeError(
                            "prepared triangle query batch lost host input")
                    origins_array = _np.ascontiguousarray(query_rows[:, :3])
                    directions_array = _np.ascontiguousarray(query_rows[:, 3:6])
                    tmax_array = _np.ascontiguousarray(query_rows[:, 6])
                origins_native = origins_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
                directions_native = directions_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
                tmax_native = tmax_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            else:
                origins_native = (ctypes.c_float * len(origins))(*origins)
                directions_native = (ctypes.c_float * len(directions))(*directions)
                tmax_native = (ctypes.c_float * count)(*tmax_values)
            packed_row_mode = bool(
                partner_column_output
                and prepared_query_batch
                and host_output is not None
                and host_output_pointer is not None
                and getattr(self, "_execute_query_batch_rows", None) is not None)
            if not packed_row_mode:
                output_0 = (ctypes.c_uint32 * count)()
                output_1 = (ctypes.c_uint32 * count)()
                output_2 = (ctypes.c_uint32 * count)()
            error = getattr(self, "_execution_error_buffer", None)
            if error is None:
                error = ctypes.create_string_buffer(16384)
            error[0] = b"\0"
            compact_columns = partner_column_output and self._execute_columns is not None
            compact_columns = compact_columns or (
                partner_column_output and packed_row_mode)
            if compact_columns:
                summary = _CompactLifecycleSummary()
            else:
                observed_primitive = (ctypes.c_uint32 * count)()
                observed_kind = (ctypes.c_uint32 * count)()
                observed_bx = (ctypes.c_float * count)()
                observed_by = (ctypes.c_float * count)()
                statuses = (_Status * count)()
                counters = (ctypes.c_uint64 * 7)()
            self._audit_sequence += 1
            audit = OptixTraversalAuditSession.open(
                library=self._library,
                nonce=(
                    getattr(self, "_audit_nonce_hi", None)
                    or (secrets.randbits(64) or 1),
                    self._audit_sequence,
                ),
                _error_buffer=getattr(self, "_audit_error_buffer", None),
            )
            try:
                if compact_columns:
                    if packed_row_mode:
                        _raise(int(self._execute_query_batch_rows(
                            self._token, native_token,
                            ctypes.byref(summary), error, len(error))), error,
                            "prepared built-in triangle packed-row execute")
                    elif prepared_query_batch and native_token:
                        _raise(int(self._execute_query_batch(
                            self._token, native_token,
                            output_0, output_1, output_2,
                            ctypes.byref(summary), error, len(error))), error,
                            "prepared built-in triangle device-batch execute")
                    else:
                        _raise(int(self._execute_columns(
                            self._token, origins_native, directions_native,
                            tmax_native, count, output_0, output_1, output_2,
                            ctypes.byref(summary), error, len(error))), error,
                            "prepared built-in triangle compact execute")
                    counter_rows = _validate_compact_lifecycle_summary(
                        summary, count)
                else:
                    _raise(int(self._execute(
                        self._token, origins_native, directions_native, tmax_native,
                        count, output_0, output_1, output_2, observed_primitive,
                        observed_kind, observed_bx, observed_by, statuses, counters,
                        error, len(error))), error,
                        "prepared built-in triangle execute")
                if partner_column_output:
                    if not numpy_queries:
                        raise ValueError(
                            "partner column output requires NumPy query columns")
                    if packed_row_mode:
                        # The native query batch owns this reusable pinned
                        # staging area.  The digest cache returns an immutable
                        # bytes-backed result that remains valid after reuse or
                        # teardown; equal executions reuse it after an exact
                        # comparison instead of copying and hashing it again.
                        observed, output_sha = output_digest_cache.resolve(
                            host_output)
                    else:
                        observed = _np.column_stack((
                            _np.ctypeslib.as_array(output_0),
                            _np.ctypeslib.as_array(output_1),
                            _np.ctypeslib.as_array(output_2),
                        )).astype(_np.uint32, copy=False)
                    if not compact_columns and any(
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
                if not compact_columns:
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
                if packed_row_mode:
                    pass
                elif partner_column_output:
                    output_sha = _bulk_u32x3_digest(observed)
                else:
                    output_sha = _digest(observed)
                if compact_columns:
                    receipt = audit.finish_validated_compact(
                        semantic_digest=semantic_digest,
                        output_digest=output_sha,
                        route_identity=(
                            "v4_builtin_triangle_callback_ir:four_role_composed_v1"),
                        expected_program_bundle=(
                            "v4_builtin_triangle_callback_ir_four_role_composed"),
                        expected_raygen_invocation_count=count,
                    )
                else:
                    receipt = audit.finish(
                        semantic_digest=semantic_digest,
                        output_digest=output_sha,
                        route_identity=(
                            "v4_builtin_triangle_callback_ir:four_role_composed_v1"),
                        expected_program_bundles=(
                            "v4_builtin_triangle_callback_ir_four_role_composed",))
            except Exception:
                audit.abort()
                raise
            if type(receipt) is ValidatedCompactTraversalReceipt:
                validate_bound_compact_traversal_receipt(
                    receipt,
                    provider_library_sha256=self._native_sha,
                    route_identity=(
                        "v4_builtin_triangle_callback_ir:four_role_composed_v1"),
                    output_digest=output_sha,
                    expected_program_bundle=(
                        "v4_builtin_triangle_callback_ir_four_role_composed"),
                    expected_raygen_invocation_count=count,
                )
            elif receipt["physical_executor_classification"] \
                    != "optix_traversal_observed":
                raise RuntimeError("prepared built-in triangle lacked bound traversal")
            hit_rows = (() if partner_column_output else tuple({
                "primitive_index": None if int(observed_primitive[index]) == 0xFFFFFFFF else int(observed_primitive[index]),
                "hit_kind": None if int(observed_kind[index]) == 0xFFFFFFFF else int(observed_kind[index]),
                "barycentric_x": None if int(observed_primitive[index]) == 0xFFFFFFFF else float(observed_bx[index]),
                "barycentric_y": None if int(observed_primitive[index]) == 0xFFFFFFFF else float(observed_by[index]),
            } for index in range(count)))
            self._execution_count += 1
            result = V4TriangleCallbackResult(
                observed, hit_rows, counter_rows, status_rows, receipt,
                output_sha, self._ptx_sha, self._native_sha, binding_digest)
            if partner_column_output and compact_columns:
                object.__setattr__(
                    result,
                    "_validated_prepared_execution",
                    _ValidatedPreparedTriangleExecution(
                        owner=self,
                        output=observed,
                        output_sha256=output_sha,
                        receipt=receipt,
                        query_count=count,
                        composed_ptx_sha256=self._ptx_sha,
                        native_library_sha256=self._native_sha,
                        binding_digest=binding_digest,
                        token=_VALIDATED_PREPARED_EXECUTION_TOKEN,
                    ),
                )
            return result
        finally:
            self._active.release()

    def close(self):
        if self._closed:
            return
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close prepared built-in triangle during execution")
        try:
            destroy_query_batch = getattr(self, "_destroy_query_batch", None)
            native_batch_tokens = getattr(
                self, "_native_query_batch_tokens", set())
            if destroy_query_batch is not None:
                for batch_token in tuple(native_batch_tokens):
                    error = ctypes.create_string_buffer(16384)
                    _raise(int(destroy_query_batch(
                        batch_token, error, len(error))), error,
                        "prepared built-in triangle query batch destroy")
                    native_batch_tokens.remove(batch_token)
            getattr(self, "_prepared_query_batch_authorities", {}).clear()
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


__all__ = [
    "PreparedBuiltinTriangleOwner",
    "PreparedBuiltinTriangleQueryBatch",
    "prepare_builtin_triangle_callback",
]
