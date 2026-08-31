"""Typed CUDA-partner composition and prepared lifecycle for V4 callbacks.

The public boundary accepts an exact cached Callback provider, immutable host
geometry, and one of two closed partner lanes (Numba or CuPy).  It never
accepts an arbitrary Python continuation or raw user PTX.  Each lane creates
typed CUDA buffers, submits the prepared OptiX launch, runs one compiler-owned
continuation on the same explicit stream, synchronizes, and only then accepts
the explicit device status and behavioral traversal receipt.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import threading
from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_callback_artifact_cache import (
    V4CallbackProviderKey,
    load_callback_artifact,
)


UINT32_MAX = (1 << 32) - 1
V4_PARTNER_RUNTIME_SCHEMA = "rtdl.v4.callback_partner_runtime.v1"
V4_PARTNER_CONTINUATION = "valid_hit_mask_and_masked_distance_v1"
V4_PARTNER_LIFECYCLE_CONTRACT = {
    "cold_endpoint_includes_prepare": True,
    "prepared_endpoint_excludes_prepare_but_reports_it_separately": True,
    "prepared_requires_explicit_cross_call_session_reuse": True,
    "prepared_result_may_replace_cold_result": False,
    "benchmark_repetition_counts_as_application_reuse": False,
    "performance_claimed": False,
}


class V4PartnerContractError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


class _NativeSphere(ctypes.Structure):
    _fields_ = [
        ("cx", ctypes.c_float), ("cy", ctypes.c_float),
        ("cz", ctypes.c_float), ("radius", ctypes.c_float),
        ("item_id", ctypes.c_uint32),
    ]


class _FormalStatus(ctypes.Structure):
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


@dataclass(frozen=True)
class V4CudaArrayView:
    name: str
    dtype: str
    shape: tuple[int, ...]
    strides_bytes: tuple[int, ...] | None
    device_pointer: int
    read_only: bool
    device_ordinal: int
    source_protocol: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "dtype": self.dtype,
            "shape": list(self.shape),
            "strides_bytes": None if self.strides_bytes is None else list(self.strides_bytes),
            "device_pointer_nonzero": self.device_pointer > 0,
            "read_only": self.read_only,
            "device_ordinal": self.device_ordinal,
            "source_protocol": self.source_protocol,
        }


@dataclass(frozen=True)
class V4PartnerExecutionResult:
    partner: str
    execution_index: int
    prepared_session_identity: str
    output_ids: tuple[int, ...]
    output_distance: tuple[float, ...]
    valid_hit_mask: tuple[bool, ...]
    masked_distance: tuple[float, ...]
    valid_hit_count: int
    role_counters: tuple[int, ...]
    launch_status: tuple[dict[str, int], ...]
    traversal_receipt: Mapping[str, object]
    buffer_receipt: Mapping[str, object]
    output_sha256: str
    lifecycle_contract: Mapping[str, object]


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _require_sha(name: str, value: str) -> None:
    if len(value) != 64 or any(item not in "0123456789abcdef" for item in value):
        raise V4PartnerContractError("identity_sha256", f"{name} is not lowercase SHA-256")


def _native_sha256(library: object) -> str:
    name = getattr(library, "_name", None)
    if not name:
        raise V4PartnerContractError("native_identity", "native library path is unavailable")
    path = Path(str(name)).resolve()
    if not path.is_file():
        raise V4PartnerContractError("native_identity", "native library bytes are unavailable")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _configure_native(library: object):
    prepare = getattr(library, "rtdl_optix_v4_prepare_formal_callback_v1", None)
    execute = getattr(
        library, "rtdl_optix_v4_execute_prepared_formal_callback_device_v1", None)
    destroy = getattr(library, "rtdl_optix_v4_destroy_prepared_formal_callback_v1", None)
    if prepare is None or execute is None or destroy is None:
        raise V4PartnerContractError(
            "native_symbols", "native library lacks the Goal5752 prepared callback ABI")
    prepare.argtypes = [
        ctypes.c_char_p, ctypes.POINTER(_NativeSphere), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    prepare.restype = ctypes.c_int
    execute.argtypes = [
        ctypes.c_uint64,
        ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64,
        ctypes.c_size_t,
        ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    execute.restype = ctypes.c_int
    destroy.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    destroy.restype = ctypes.c_int
    return prepare, execute, destroy


def _native_error(status: int, error: ctypes.Array[ctypes.c_char], operation: str) -> None:
    if status:
        message = error.value.decode("utf-8", errors="replace") or \
            f"native status {status}"
        raise V4PartnerContractError("native_" + operation, message)


def _sphere_rows(
    spheres: Sequence[tuple[Sequence[float], float, int]],
) -> tuple[ctypes.Array[_NativeSphere], tuple[tuple[float, float, float, float, int], ...]]:
    if not spheres:
        raise V4PartnerContractError("geometry", "prepared geometry must be nonempty")
    native = (_NativeSphere * len(spheres))()
    canonical: list[tuple[float, float, float, float, int]] = []
    for index, (center, radius, item_id) in enumerate(spheres):
        if (len(center) != 3 or not all(math.isfinite(float(value)) for value in center)
                or not math.isfinite(float(radius)) or float(radius) < 0.0
                or not 0 <= int(item_id) <= UINT32_MAX):
            raise V4PartnerContractError("geometry", f"invalid sphere at index {index}")
        row = (
            float(center[0]), float(center[1]), float(center[2]),
            float(radius), int(item_id),
        )
        canonical.append(row)
        native[index] = _NativeSphere(*row)
    return native, tuple(canonical)


def _device_ordinal(value: object) -> int:
    device = getattr(value, "device", None)
    identifier = getattr(device, "id", None)
    if identifier is None:
        identifier = getattr(value, "device_id", 0)
    return int(identifier or 0)


def describe_cuda_array(
    name: str,
    value: object,
    *,
    dtype: np.dtype,
    length: int,
    writable: bool,
) -> V4CudaArrayView:
    """Strictly validate a rank-one contiguous CUDA Array Interface buffer."""

    interface = getattr(value, "__cuda_array_interface__", None)
    if not isinstance(interface, dict):
        raise V4PartnerContractError(
            "cuda_array_interface", f"{name} lacks __cuda_array_interface__")
    if int(interface.get("version", 0)) < 2:
        raise V4PartnerContractError("cuda_array_version", f"{name} uses an old protocol")
    shape = tuple(int(item) for item in interface.get("shape", ()))
    if shape != (int(length),):
        raise V4PartnerContractError(
            "buffer_shape", f"{name} expected {(int(length),)!r}, got {shape!r}")
    try:
        observed_dtype = np.dtype(str(interface.get("typestr", "")))
    except TypeError as error:
        raise V4PartnerContractError("buffer_dtype", f"{name} has invalid dtype") from error
    expected_dtype = np.dtype(dtype)
    if observed_dtype != expected_dtype:
        raise V4PartnerContractError(
            "buffer_dtype", f"{name} expected {expected_dtype}, got {observed_dtype}")
    strides_raw = interface.get("strides")
    strides = None if strides_raw is None else tuple(int(item) for item in strides_raw)
    if strides not in {None, (expected_dtype.itemsize,)}:
        raise V4PartnerContractError("buffer_strides", f"{name} is not contiguous")
    data = interface.get("data")
    if not isinstance(data, tuple) or len(data) != 2:
        raise V4PartnerContractError("buffer_pointer", f"{name} lacks pointer/read-only data")
    pointer = int(data[0])
    read_only = bool(data[1])
    if pointer <= 0 or pointer % max(1, expected_dtype.alignment):
        raise V4PartnerContractError("buffer_pointer", f"{name} pointer is zero or misaligned")
    if writable and read_only:
        raise V4PartnerContractError("buffer_read_only", f"{name} must be writable")
    return V4CudaArrayView(
        name=str(name), dtype=expected_dtype.str, shape=shape,
        strides_bytes=strides, device_pointer=pointer, read_only=read_only,
        device_ordinal=_device_ordinal(value),
        source_protocol="cuda_array_interface",
    )


def _stream_pointer(stream: object) -> int:
    value = getattr(stream, "ptr", None)
    if value is None:
        value = getattr(stream, "handle", None)
    if hasattr(value, "value"):
        value = value.value
    try:
        pointer = int(value)
    except (TypeError, ValueError) as error:
        raise V4PartnerContractError("stream", "CUDA stream handle is unavailable") from error
    if pointer <= 2:
        raise V4PartnerContractError(
            "stream", "Goal5752 requires an explicit non-default CUDA stream")
    return pointer


def _status_rows(raw: bytes, count: int) -> tuple[dict[str, int], ...]:
    expected = ctypes.sizeof(_FormalStatus) * count
    if len(raw) != expected:
        raise V4PartnerContractError(
            "status_bytes", f"expected {expected} status bytes, got {len(raw)}")
    rows = []
    size = ctypes.sizeof(_FormalStatus)
    for index in range(count):
        item = _FormalStatus.from_buffer_copy(raw[index * size:(index + 1) * size])
        rows.append({
            "first_error_claimed": int(item.first_error_claimed),
            "error_code": int(item.error_code), "stage": int(item.stage),
            "role": int(item.role), "launch_index": int(item.launch_index),
            "error_site": int(item.error_site), "effect_tag": int(item.effect_tag),
            "nonce_word": int(item.nonce_word),
            "invocation_mask": int(item.invocation_mask),
        })
    return tuple(rows)


def _validate_device_result(
    *,
    statuses: tuple[dict[str, int], ...],
    counters: tuple[int, ...],
    output_ids: tuple[int, ...],
    output_distance: tuple[float, ...],
    valid_mask: tuple[bool, ...],
    masked_distance: tuple[float, ...],
) -> None:
    if len(counters) != 7 or any(item <= 0 for item in counters):
        raise V4PartnerContractError(
            "role_counters", "prepared execution did not exercise all seven roles")
    if any(item["first_error_claimed"] or item["error_code"] for item in statuses):
        raise V4PartnerContractError("device_status", f"device callback failed: {statuses!r}")
    if not (len(output_ids) == len(output_distance) == len(valid_mask) == len(masked_distance)):
        raise V4PartnerContractError("output_shape", "partner outputs disagree in length")
    for index, (item_id, distance, valid, masked) in enumerate(zip(
            output_ids, output_distance, valid_mask, masked_distance)):
        expected_valid = item_id != UINT32_MAX
        if valid != expected_valid:
            raise V4PartnerContractError(
                "partner_continuation", f"valid mask mismatch at index {index}")
        expected_masked = ctypes.c_float(distance if expected_valid else 0.0).value
        if ctypes.c_float(masked).value != expected_masked:
            raise V4PartnerContractError(
                "partner_continuation", f"masked distance mismatch at index {index}")


class V4PreparedCallbackSession:
    """Process/thread-bound, nonserializable owner of one prepared V4 pipeline."""

    def __init__(
        self,
        *,
        library: object,
        token: int,
        semantic_digest: str,
        provider_identity: str,
        provider_key_sha256: str,
        composed_ptx_sha256: str,
        native_sha256: str,
        geometry_sha256: str,
        sphere_count: int,
    ) -> None:
        self._library = library
        self._prepare, self._execute, self._destroy = _configure_native(library)
        self._token = int(token)
        self._semantic_digest = semantic_digest
        self._provider_identity = provider_identity
        self._provider_key_sha256 = provider_key_sha256
        self._composed_ptx_sha256 = composed_ptx_sha256
        self._native_sha256 = native_sha256
        self._geometry_sha256 = geometry_sha256
        self._sphere_count = int(sphere_count)
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._nonce = secrets.token_hex(16)
        self._closed = False
        self._execution_count = 0
        self._active = threading.Lock()
        self._session_identity = _sha({
            "schema": V4_PARTNER_RUNTIME_SCHEMA,
            "provider": provider_identity,
            "provider_key": provider_key_sha256,
            "ptx": composed_ptx_sha256,
            "native": native_sha256,
            "geometry": geometry_sha256,
            "pid": self._pid,
            "thread": self._thread,
            "nonce": self._nonce,
        })

    @property
    def session_identity(self) -> str:
        return self._session_identity

    @property
    def execution_count(self) -> int:
        return self._execution_count

    @property
    def closed(self) -> bool:
        return self._closed

    def __getstate__(self):
        raise V4PartnerContractError(
            "session_serialization", "prepared callback sessions are process-local")

    def _check_owner(self) -> None:
        if self._closed:
            raise V4PartnerContractError("session_closed", "prepared callback session is closed")
        if os.getpid() != self._pid:
            raise V4PartnerContractError("session_process", "prepared callback session crossed process")
        if threading.get_ident() != self._thread:
            raise V4PartnerContractError("session_thread", "prepared callback session crossed thread")

    def _execute_arrays(
        self,
        *,
        partner: str,
        stream: object,
        query_x: object,
        query_y: object,
        query_z: object,
        query_tmax: object,
        output_ids: object,
        output_distance: object,
        output_status: object,
        output_counters: object,
        valid_mask: object,
        masked_distance: object,
        synchronize,
        to_host,
        expected_output: Sequence[tuple[int, float]] | None,
    ) -> V4PartnerExecutionResult:
        self._check_owner()
        if partner not in {"cupy", "numba"}:
            raise V4PartnerContractError("partner", "partner must be cupy or numba")
        if not self._active.acquire(blocking=False):
            raise V4PartnerContractError("session_reentrant", "prepared execution is already active")
        audit = None
        try:
            stream_pointer = _stream_pointer(stream)
            count = int(getattr(query_x, "size", -1))
            if count <= 0:
                raise V4PartnerContractError("query_count", "query arrays must be nonempty")
            arrays = (
                ("query_x", query_x, np.dtype(np.float32), False),
                ("query_y", query_y, np.dtype(np.float32), False),
                ("query_z", query_z, np.dtype(np.float32), False),
                ("query_tmax", query_tmax, np.dtype(np.float32), False),
                ("output_ids", output_ids, np.dtype(np.uint32), True),
                ("output_distance", output_distance, np.dtype(np.float32), True),
                ("output_status", output_status, np.dtype(np.uint8), True),
                ("output_counters", output_counters, np.dtype(np.uint64), True),
                ("valid_mask", valid_mask, np.dtype(np.bool_), True),
                ("masked_distance", masked_distance, np.dtype(np.float32), True),
            )
            views: dict[str, V4CudaArrayView] = {}
            for name, value, dtype, writable in arrays:
                length = count
                if name == "output_status":
                    length = count * ctypes.sizeof(_FormalStatus)
                elif name == "output_counters":
                    length = 7
                views[name] = describe_cuda_array(
                    name, value, dtype=dtype, length=length, writable=writable)
            device_ordinals = {view.device_ordinal for view in views.values()}
            if len(device_ordinals) != 1:
                raise V4PartnerContractError("device", "all partner buffers must share one device")
            error = ctypes.create_string_buffer(16384)
            audit = OptixTraversalAuditSession.open(library=self._library)
            status = int(self._execute(
                self._token,
                views["query_x"].device_pointer,
                views["query_y"].device_pointer,
                views["query_z"].device_pointer,
                views["query_tmax"].device_pointer,
                count,
                views["output_ids"].device_pointer,
                views["output_distance"].device_pointer,
                views["output_status"].device_pointer,
                views["output_counters"].device_pointer,
                stream_pointer,
                error, len(error),
            ))
            _native_error(status, error, "execute")
            # The caller already enqueued the compiler-owned continuation on
            # the same stream.  Synchronization here proves both traversal and
            # continuation are complete before buffers may be released.
            synchronize()
            # Re-describe the two native outputs after the fixed partner
            # continuation.  This is an observed pointer comparison, not a
            # metadata assertion: relocation, dtype or shape drift fails here.
            partner_id_view = describe_cuda_array(
                "partner_output_ids", output_ids, dtype=np.dtype(np.uint32),
                length=count, writable=True)
            partner_distance_view = describe_cuda_array(
                "partner_output_distance", output_distance,
                dtype=np.dtype(np.float32), length=count, writable=True)
            native_output_pointers = (
                views["output_ids"].device_pointer,
                views["output_distance"].device_pointer,
            )
            partner_input_pointers = (
                partner_id_view.device_pointer,
                partner_distance_view.device_pointer,
            )
            if native_output_pointers != partner_input_pointers:
                raise V4PartnerContractError(
                    "partner_pointer_identity",
                    "partner continuation did not retain the native output pointers",
                )
            ids_host = np.asarray(to_host(output_ids), dtype=np.uint32)
            distance_host = np.asarray(to_host(output_distance), dtype=np.float32)
            status_host = np.asarray(to_host(output_status), dtype=np.uint8)
            counters_host = np.asarray(to_host(output_counters), dtype=np.uint64)
            valid_host = np.asarray(to_host(valid_mask), dtype=np.bool_)
            masked_host = np.asarray(to_host(masked_distance), dtype=np.float32)
            ids = tuple(int(item) for item in ids_host.tolist())
            distances = tuple(float(item) for item in distance_host.tolist())
            statuses = _status_rows(status_host.tobytes(), count)
            counters = tuple(int(item) for item in counters_host.tolist())
            valid = tuple(bool(item) for item in valid_host.tolist())
            masked = tuple(float(item) for item in masked_host.tolist())
            _validate_device_result(
                statuses=statuses, counters=counters, output_ids=ids,
                output_distance=distances, valid_mask=valid,
                masked_distance=masked,
            )
            if expected_output is not None:
                expected = tuple((int(item[0]), ctypes.c_float(item[1]).value)
                                 for item in expected_output)
                observed = tuple((item_id, ctypes.c_float(distance).value)
                                 for item_id, distance in zip(ids, distances))
                if observed != expected:
                    raise V4PartnerContractError(
                        "expected_output", f"{observed!r} != {expected!r}")
            output_sha256 = _sha({
                "ids": ids, "distance": distances,
                "valid_mask": valid, "masked_distance": masked,
            })
            receipt = audit.finish(
                semantic_digest=self._semantic_digest,
                output_digest=output_sha256,
                route_identity="v4_formal_callback_ir:prepared_partner_v1",
                expected_program_bundles=(
                    "v4_formal_callback_ir_seven_role_composed_prepared",),
            )
            audit = None
            if receipt["physical_executor_classification"] != "optix_traversal_observed":
                raise V4PartnerContractError(
                    "traversal_receipt", "prepared callback lacks bound OptiX traversal")
            self._execution_count += 1
            buffer_receipt = {
                "schema": "rtdl.v4.callback_partner_buffer_receipt.v1",
                "partner": partner,
                "continuation": V4_PARTNER_CONTINUATION,
                "stream_handle": stream_pointer,
                "single_explicit_nondefault_stream": True,
                "native_boundary_host_staging": False,
                "same_device_pointer_passed_to_native_and_partner":
                    native_output_pointers == partner_input_pointers,
                "native_output_pointer_digest": _sha(native_output_pointers),
                "partner_input_pointer_digest": _sha(partner_input_pointers),
                "host_materialization_count_before_partner_continuation": 0,
                "host_materialization_count_after_stream_synchronization": 6,
                "partner_buffers_retained_through_synchronization": True,
                "views": {name: view.to_metadata() for name, view in views.items()},
            }
            return V4PartnerExecutionResult(
                partner=partner, execution_index=self._execution_count,
                prepared_session_identity=self._session_identity,
                output_ids=ids, output_distance=distances,
                valid_hit_mask=valid, masked_distance=masked,
                valid_hit_count=sum(valid), role_counters=counters,
                launch_status=statuses, traversal_receipt=receipt,
                buffer_receipt=buffer_receipt, output_sha256=output_sha256,
                lifecycle_contract=dict(V4_PARTNER_LIFECYCLE_CONTRACT),
            )
        except Exception:
            if audit is not None:
                audit.abort()
            raise
        finally:
            self._active.release()

    def execute_cupy(
        self,
        queries: Sequence[tuple[Sequence[float], float]],
        *,
        expected_output: Sequence[tuple[int, float]] | None = None,
    ) -> V4PartnerExecutionResult:
        """Run CuPy preprocessing and continuation on one non-default stream."""

        self._check_owner()
        try:
            import cupy as cp
        except ImportError as error:
            raise V4PartnerContractError("cupy_unavailable", str(error)) from error
        host = _query_columns(queries)
        stream = cp.cuda.Stream(non_blocking=True)
        with stream:
            query_x = cp.asarray(host[0], dtype=cp.float32)
            query_y = cp.asarray(host[1], dtype=cp.float32)
            query_z = cp.asarray(host[2], dtype=cp.float32)
            query_tmax = cp.asarray(host[3], dtype=cp.float32)
            output_ids = cp.empty(len(queries), dtype=cp.uint32)
            output_distance = cp.empty(len(queries), dtype=cp.float32)
            output_status = cp.empty(
                len(queries) * ctypes.sizeof(_FormalStatus), dtype=cp.uint8)
            output_counters = cp.empty(7, dtype=cp.uint64)
            valid_mask = cp.empty(len(queries), dtype=cp.bool_)
            masked_distance = cp.empty(len(queries), dtype=cp.float32)
            # Pre-enqueue the continuation only after the native call.  The
            # helper closure is fixed by RTDL and is not a user callback.
            def enqueue_continuation() -> None:
                cp.not_equal(output_ids, cp.uint32(UINT32_MAX), out=valid_mask)
                cp.copyto(masked_distance, output_distance, where=valid_mask)
                cp.copyto(masked_distance, cp.float32(0.0), where=~valid_mask)

            return self._execute_with_enqueued_continuation(
                enqueue_continuation=enqueue_continuation,
                partner="cupy", stream=stream,
                arrays=(query_x, query_y, query_z, query_tmax, output_ids,
                        output_distance, output_status, output_counters,
                        valid_mask, masked_distance),
                synchronize=stream.synchronize, to_host=cp.asnumpy,
                expected_output=expected_output,
            )

    def execute_numba(
        self,
        queries: Sequence[tuple[Sequence[float], float]],
        *,
        expected_output: Sequence[tuple[int, float]] | None = None,
    ) -> V4PartnerExecutionResult:
        """Run Numba preprocessing and continuation on one non-default stream."""

        self._check_owner()
        try:
            from numba import cuda
        except ImportError as error:
            raise V4PartnerContractError("numba_unavailable", str(error)) from error
        host = _query_columns(queries)
        stream = cuda.stream()
        query_x = cuda.to_device(host[0], stream=stream)
        query_y = cuda.to_device(host[1], stream=stream)
        query_z = cuda.to_device(host[2], stream=stream)
        query_tmax = cuda.to_device(host[3], stream=stream)
        output_ids = cuda.device_array(len(queries), dtype=np.uint32, stream=stream)
        output_distance = cuda.device_array(len(queries), dtype=np.float32, stream=stream)
        output_status = cuda.device_array(
            len(queries) * ctypes.sizeof(_FormalStatus), dtype=np.uint8, stream=stream)
        output_counters = cuda.device_array(7, dtype=np.uint64, stream=stream)
        valid_mask = cuda.device_array(len(queries), dtype=np.bool_, stream=stream)
        masked_distance = cuda.device_array(len(queries), dtype=np.float32, stream=stream)

        def enqueue_continuation() -> None:
            kernel = _numba_valid_hit_kernel()
            threads = 128
            blocks = (len(queries) + threads - 1) // threads
            kernel[blocks, threads, stream](
                output_ids, output_distance, valid_mask, masked_distance)

        return self._execute_with_enqueued_continuation(
            enqueue_continuation=enqueue_continuation,
            partner="numba", stream=stream,
            arrays=(query_x, query_y, query_z, query_tmax, output_ids,
                    output_distance, output_status, output_counters,
                    valid_mask, masked_distance),
            synchronize=stream.synchronize,
            # The explicit stream was already synchronized.  A default-stream
            # host copy is therefore ordered after completed device work and
            # returns materialized bytes before validation.
            to_host=lambda value: value.copy_to_host(),
            expected_output=expected_output,
        )

    def _execute_with_enqueued_continuation(
        self, *, enqueue_continuation, partner: str, stream: object,
        arrays: tuple[object, ...], synchronize, to_host,
        expected_output: Sequence[tuple[int, float]] | None,
    ) -> V4PartnerExecutionResult:
        # `_execute_arrays` invokes native first.  This wrapper supplies a
        # synchronization hook that enqueues exactly one closed continuation
        # on the same stream before waiting.
        continuation_enqueued = False

        def enqueue_then_sync() -> None:
            nonlocal continuation_enqueued
            if continuation_enqueued:
                raise V4PartnerContractError(
                    "partner_continuation", "continuation was enqueued twice")
            enqueue_continuation()
            continuation_enqueued = True
            synchronize()

        return self._execute_arrays(
            partner=partner, stream=stream,
            query_x=arrays[0], query_y=arrays[1], query_z=arrays[2],
            query_tmax=arrays[3], output_ids=arrays[4],
            output_distance=arrays[5], output_status=arrays[6],
            output_counters=arrays[7], valid_mask=arrays[8],
            masked_distance=arrays[9], synchronize=enqueue_then_sync,
            to_host=to_host, expected_output=expected_output,
        )

    def close(self) -> None:
        if self._closed:
            return
        self._check_owner()
        error = ctypes.create_string_buffer(16384)
        status = int(self._destroy(self._token, error, len(error)))
        _native_error(status, error, "destroy")
        self._closed = True
        self._token = 0

    def __enter__(self) -> "V4PreparedCallbackSession":
        self._check_owner()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def __del__(self) -> None:
        if getattr(self, "_closed", True):
            return
        # Destructors cannot safely report failure.  Best effort only; normal
        # callers must use `with` or explicit `close` so failures are visible.
        try:
            error = ctypes.create_string_buffer(1024)
            self._destroy(self._token, error, len(error))
        except Exception:
            pass


def _query_columns(
    queries: Sequence[tuple[Sequence[float], float]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if not queries:
        raise V4PartnerContractError("queries", "queries must be nonempty")
    rows: list[tuple[float, float, float, float]] = []
    for index, (origin, tmax) in enumerate(queries):
        if (len(origin) != 3 or not all(math.isfinite(float(value)) for value in origin)
                or not math.isfinite(float(tmax)) or float(tmax) <= 0.0):
            raise V4PartnerContractError("queries", f"invalid query at index {index}")
        rows.append((float(origin[0]), float(origin[1]), float(origin[2]), float(tmax)))
    matrix = np.asarray(rows, dtype=np.float32)
    return tuple(np.ascontiguousarray(matrix[:, index]) for index in range(4))  # type: ignore[return-value]


_NUMBA_VALID_HIT_KERNEL = None


def _numba_valid_hit_kernel():
    global _NUMBA_VALID_HIT_KERNEL
    if _NUMBA_VALID_HIT_KERNEL is None:
        from numba import cuda

        @cuda.jit
        def valid_hit_kernel(ids, distances, valid, masked):
            index = cuda.grid(1)
            if index < ids.size:
                present = ids[index] != UINT32_MAX
                valid[index] = present
                masked[index] = distances[index] if present else 0.0

        _NUMBA_VALID_HIT_KERNEL = valid_hit_kernel
    return _NUMBA_VALID_HIT_KERNEL


def prepare_v4_partner_session(
    cache_root: str | os.PathLike[str],
    provider_key: V4CallbackProviderKey,
    *,
    spheres: Sequence[tuple[Sequence[float], float, int]],
    semantic_digest: str,
    library: object | None = None,
) -> V4PreparedCallbackSession:
    """Load/reverify exact provider bytes and construct one prepared owner."""

    _require_sha("semantic_digest", semantic_digest)
    cached = load_callback_artifact(cache_root, provider_key)
    if not cached.cache_hit:
        raise V4PartnerContractError("provider_cache", "prepared provider must be reloaded")
    if library is None:
        from . import optix_runtime
        library = optix_runtime._load_optix_library()
    native_sha256 = _native_sha256(library)
    if native_sha256 != provider_key.native_provider_sha256:
        raise V4PartnerContractError(
            "native_identity", "executed native bytes differ from provider key")
    prepare, _execute, _destroy = _configure_native(library)
    native_spheres, canonical_spheres = _sphere_rows(spheres)
    error = ctypes.create_string_buffer(16384)
    token = ctypes.c_uint64()
    status = int(prepare(
        cached.composed_ptx.encode("utf-8"), native_spheres,
        len(canonical_spheres), ctypes.byref(token), error, len(error),
    ))
    _native_error(status, error, "prepare")
    if token.value == 0:
        raise V4PartnerContractError("native_prepare", "native returned a zero token")
    return V4PreparedCallbackSession(
        library=library, token=int(token.value), semantic_digest=semantic_digest,
        provider_identity=cached.provider_identity,
        provider_key_sha256=provider_key.key_sha256,
        composed_ptx_sha256=cached.composed_ptx_sha256,
        native_sha256=native_sha256,
        geometry_sha256=_sha(canonical_spheres),
        sphere_count=len(canonical_spheres),
    )


__all__ = [
    "UINT32_MAX", "V4CudaArrayView", "V4PartnerContractError",
    "V4PartnerExecutionResult", "V4PreparedCallbackSession",
    "V4_PARTNER_CONTINUATION", "V4_PARTNER_LIFECYCLE_CONTRACT",
    "describe_cuda_array", "prepare_v4_partner_session",
]
