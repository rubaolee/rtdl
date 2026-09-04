"""Explicit prepared lifecycle for the existing V4 triangle-reduction family."""

from __future__ import annotations

import ctypes
import hashlib
import math
import os
import secrets
import threading
import time
from collections.abc import Iterator, Mapping, Sequence

import numpy as np

from .physical_execution_provenance import (
    NativeTraversalAuditSnapshot,
    OptixTraversalAuditSession,
    build_compact_traversal_receipt,
    captured_traversal_observation_from_snapshot,
)
from .v4_triangle_reduction import (
    MetadataDomain,
    ReducerAlgebra,
    ReducerSourceKind,
    compile_triangle_reduction_abi,
    compile_triangle_reduction_contract,
    execute_checked_reducer,
    verify_triangle_reduction_schema,
)
from .v4_triangle_reduction_optix_compiler import (
    consume_verified_triangle_reduction_executable,
)
from .v4_triangle_reduction_optix_runtime import (
    V4TriangleReductionResult,
    _digest,
    _native_path,
    _Status,
    _typed_metadata,
)


class _FastPathReceipt(ctypes.Structure):
    _fields_ = [
        ("schema_version", ctypes.c_uint32),
        ("optix_launch_count", ctypes.c_uint32),
        ("host_blocking_boundary_count", ctypes.c_uint32),
        ("control_d2h_bytes", ctypes.c_uint32),
        ("output_d2h_bytes", ctypes.c_uint64),
        ("status_before_output", ctypes.c_uint32),
        ("output_d2h_after_status_failure", ctypes.c_uint32),
        ("role_counters_materialized", ctypes.c_uint32),
        ("prepared_input_reused", ctypes.c_uint32),
        ("dynamic_device_upload_call_count", ctypes.c_uint32),
        ("dynamic_accel_build_count", ctypes.c_uint32),
        ("dynamic_explicit_sync_count", ctypes.c_uint32),
        ("dynamic_blocking_upload_call_count", ctypes.c_uint32),
        ("dynamic_device_upload_bytes", ctypes.c_uint64),
        ("dynamic_input_generation", ctypes.c_uint64),
        ("semantic_compaction_launch_count", ctypes.c_uint32),
        ("semantic_compaction_key_capacity", ctypes.c_uint32),
        ("semantic_compaction_scratch_bytes", ctypes.c_uint64),
        ("callback_status_kernel_launch_count", ctypes.c_uint32),
        ("checked_product_kernel_launch_count", ctypes.c_uint32),
        ("compact_control_finalizer_kernel_launch_count", ctypes.c_uint32),
        ("total_auxiliary_cuda_kernel_launch_count", ctypes.c_uint32),
        ("execution_parameter_h2d_bytes", ctypes.c_uint64),
        ("execution_parameter_h2d_copy_call_count", ctypes.c_uint32),
        ("stream_ordered_memset_call_count", ctypes.c_uint32),
        ("status_d2h_copy_call_count", ctypes.c_uint32),
        ("output_d2h_copy_call_count", ctypes.c_uint32),
    ]


class _ValidatedFastOperationReceipt(Mapping[str, int | bool]):
    """Lazy immutable view over one validated native fast-path receipt."""

    _names = tuple(name for name, _ctype in _FastPathReceipt._fields_)
    _boolean_names = {
        "status_before_output",
        "role_counters_materialized",
        "prepared_input_reused",
    }

    def __init__(self, receipt: _FastPathReceipt) -> None:
        self._receipt = receipt

    def __getitem__(self, key: str) -> int | bool:
        if key not in self._names:
            raise KeyError(key)
        value = int(getattr(self._receipt, key))
        return bool(value) if key in self._boolean_names else value

    def __iter__(self) -> Iterator[str]:
        return iter(self._names)

    def __len__(self) -> int:
        return len(self._names)


class _ValidatedFastStatusRows(Sequence[Mapping[str, int]]):
    """Public status view after the native compact-status gate passes."""

    native_validated_all_ok = True

    def __init__(self, query_count: int) -> None:
        self._row = {
            "first_error_claimed": 0,
            "error_code": 0,
            "validated_row_count": int(query_count),
            "success_status_control_d2h_bytes": (
                3 * ctypes.sizeof(ctypes.c_uint32)
            ),
        }

    def __len__(self) -> int:
        return 1

    def __getitem__(self, index):
        if isinstance(index, slice):
            return (self._row,)[index]
        if index in (0, -1):
            return dict(self._row)
        raise IndexError(index)

    def __iter__(self) -> Iterator[Mapping[str, int]]:
        yield dict(self._row)


def _validate_fast_receipt(
    receipt: _FastPathReceipt,
    *,
    query_count: int,
    compact_status: int,
    prepared_input_reused: bool,
    use_multipliers: bool,
    expected_input_generation: int | None = None,
) -> Mapping[str, int | bool]:
    raw_status_before_output = int(receipt.status_before_output)
    raw_role_counters_materialized = int(receipt.role_counters_materialized)
    raw_prepared_input_reused = int(receipt.prepared_input_reused)
    success = compact_status == 0
    expected_upload_calls = 0 if prepared_input_reused else 7 + int(use_multipliers)
    expected_upload_bytes = (
        0
        if prepared_input_reused
        else query_count * (7 * ctypes.sizeof(ctypes.c_float))
        + int(use_multipliers) * query_count * ctypes.sizeof(ctypes.c_uint64)
    )
    if (
        ctypes.sizeof(_FastPathReceipt) != 128
        or int(receipt.schema_version) != 2
        or int(receipt.optix_launch_count) != 1
        or int(receipt.host_blocking_boundary_count) != (2 if success else 1)
        or int(receipt.control_d2h_bytes) != 3 * ctypes.sizeof(ctypes.c_uint32)
        or int(receipt.output_d2h_bytes)
        != (ctypes.sizeof(ctypes.c_uint64) if success else 0)
        or raw_status_before_output != 1
        or int(receipt.output_d2h_after_status_failure) != 0
        or raw_role_counters_materialized != 0
        or raw_prepared_input_reused != int(prepared_input_reused)
        or int(receipt.dynamic_device_upload_call_count)
        != expected_upload_calls
        or int(receipt.dynamic_device_upload_bytes) != expected_upload_bytes
        or int(receipt.dynamic_accel_build_count) != 0
        or int(receipt.dynamic_explicit_sync_count) != 0
        or int(receipt.dynamic_blocking_upload_call_count) != 0
        or int(receipt.dynamic_input_generation) <= 0
        or (
            expected_input_generation is not None
            and int(receipt.dynamic_input_generation)
                != expected_input_generation
        )
        or int(receipt.semantic_compaction_launch_count) != 0
        or int(receipt.semantic_compaction_key_capacity) != 0
        or int(receipt.semantic_compaction_scratch_bytes) != 0
        or int(receipt.callback_status_kernel_launch_count) != 0
        or int(receipt.checked_product_kernel_launch_count) != 0
        or int(receipt.compact_control_finalizer_kernel_launch_count) != 0
        or int(receipt.total_auxiliary_cuda_kernel_launch_count) != 0
        or int(receipt.execution_parameter_h2d_bytes) != 224
        or int(receipt.execution_parameter_h2d_copy_call_count) != 1
        or int(receipt.stream_ordered_memset_call_count) != 2
        or int(receipt.status_d2h_copy_call_count) != 1
        or int(receipt.output_d2h_copy_call_count) != int(success)
    ):
        values = dict(_ValidatedFastOperationReceipt(receipt))
        raise RuntimeError(
            f"prepared triangle fast-path receipt is invalid: {values!r}"
        )
    if not success:
        raise RuntimeError(
            f"prepared triangle compact device status rejected execution: "
            f"{compact_status}"
        )
    return _ValidatedFastOperationReceipt(receipt)


def _configure(library):
    prepare = getattr(
        library, "rtdl_optix_v4_prepare_triangle_reduction_callback_v1", None
    )
    execute = getattr(
        library, "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v2", None
    )
    execute_scalar = getattr(
        library, "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v7", None
    )
    execute_scalar_integrated = getattr(
        library, "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v8", None
    )
    commit = getattr(
        library, "rtdl_optix_v4_commit_prepared_triangle_reduction_cache_v1", None
    )
    cache_digest = getattr(
        library, "rtdl_optix_v4_prepared_triangle_reduction_cache_digest_v1", None
    )
    destroy = getattr(
        library, "rtdl_optix_v4_destroy_prepared_triangle_reduction_callback_v1", None
    )
    reduce_u64 = getattr(library, "rtdl_optix_v4_checked_u64_product_sum_host_v1", None)
    if any(
        symbol is None
        for symbol in (
            prepare,
            execute,
            execute_scalar,
            commit,
            cache_digest,
            destroy,
            reduce_u64,
        )
    ):
        raise RuntimeError(
            "native library lacks prepared triangle diagnostic-v2/scalar-v7 cache ABI"
        )
    prepare.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    execute.argtypes = [
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(_Status),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    execute_scalar.argtypes = [
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(_FastPathReceipt),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    if execute_scalar_integrated is not None:
        execute_scalar_integrated.argtypes = [
            *execute_scalar.argtypes[:-2],
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.POINTER(NativeTraversalAuditSnapshot),
            ctypes.POINTER(ctypes.c_char),
            ctypes.c_size_t,
        ]
    commit.argtypes = [
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    cache_digest.argtypes = [
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    destroy.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    reduce_u64.argtypes = [
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    for symbol in (
        prepare,
        execute,
        execute_scalar,
        commit,
        cache_digest,
        destroy,
        reduce_u64,
    ):
        symbol.restype = ctypes.c_int
    if execute_scalar_integrated is not None:
        execute_scalar_integrated.restype = ctypes.c_int
    return (
        prepare,
        execute,
        execute_scalar,
        execute_scalar_integrated,
        commit,
        cache_digest,
        destroy,
        reduce_u64,
    )


def _raise(status, error, label):
    if status:
        raise RuntimeError(
            error.value.decode("utf-8", errors="replace")
            or f"{label} failed with status {status}"
        )


def _packed_query_digest(origins_f32, directions_f32, tmax_f32) -> str:
    digest = hashlib.sha256(b"RTDL-V4-TRIANGLE-QUERY-CACHE-V1\x00")
    for values in (origins_f32, directions_f32, tmax_f32):
        payload = values.tobytes(order="C")
        digest.update(len(payload).to_bytes(8, "little"))
        digest.update(payload)
    return digest.hexdigest()


def _query_rows_are_immutable(queries, query_metadata) -> bool:
    return (
        isinstance(queries, tuple)
        and all(
            isinstance(row, tuple)
            and len(row) == 3
            and isinstance(row[0], tuple)
            and isinstance(row[1], tuple)
            and all(type(value) in (int, float) for value in (*row[0], *row[1], row[2]))
            for row in queries
        )
        and all(
            isinstance(values, tuple) and all(type(value) is int for value in values)
            for values in query_metadata.values()
        )
    )


class _ValidatedStatusRows(Sequence[Mapping[str, int]]):
    """Immutable, lazily materialized status rows validated by the native ABI.

    The native call scans every row and fails before returning output.  Keeping
    the ctypes owner here preserves the complete per-ray evidence without
    allocating nine Python objects per field on every hot execution.
    """

    native_validated_all_ok = True

    def __init__(self, rows) -> None:
        self._rows = rows

    def __len__(self) -> int:
        return len(self._rows)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple(self[item] for item in range(*index.indices(len(self))))
        if index < 0:
            index += len(self)
        if index < 0 or index >= len(self):
            raise IndexError(index)
        row = self._rows[index]
        return {name: int(getattr(row, name)) for name, _ in _Status._fields_}

    def __iter__(self) -> Iterator[Mapping[str, int]]:
        for index in range(len(self)):
            yield self[index]


class _U64Values(Sequence[int]):
    """Immutable lazy view over one execution's compiler-owned U64 output."""

    def __init__(self, values) -> None:
        self._values = values

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple(self[item] for item in range(*index.indices(len(self))))
        if index < 0:
            index += len(self)
        if index < 0 or index >= len(self):
            raise IndexError(index)
        return int(self._values[index])

    def __iter__(self) -> Iterator[int]:
        return iter(np.ctypeslib.as_array(self._values).tolist())

    def to_list(self) -> list[int]:
        return np.ctypeslib.as_array(self._values).tolist()


class _PerRayReducerRows(Sequence[Mapping[str, int]]):
    """Lazy public witness rows for the two scalar U64 reducer algebras."""

    def __init__(
        self,
        values: Sequence[int],
        *,
        value_field: str,
        multiplier_semantic: str | None = None,
        multipliers: tuple[int, ...] | None = None,
    ) -> None:
        self._values = values
        self._value_field = value_field
        self._multiplier_semantic = multiplier_semantic
        self._multipliers = multipliers

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple(self[item] for item in range(*index.indices(len(self))))
        if index < 0:
            index += len(self)
        if index < 0 or index >= len(self):
            raise IndexError(index)
        row = {"launch_index": index, self._value_field: self._values[index]}
        if self._multiplier_semantic is not None:
            assert self._multipliers is not None
            row[self._multiplier_semantic] = self._multipliers[index]
        return row

    def __iter__(self) -> Iterator[Mapping[str, int]]:
        for index in range(len(self)):
            yield self[index]


class PreparedTriangleReductionOwner:
    def __init__(
        self,
        *,
        authority,
        contract,
        abi,
        any_hit_proof_authority,
        executable,
        vertices,
        triangles,
        metadata,
        event_capacity,
        library=None,
        native_library_path=None,
    ):
        started = time.perf_counter()
        fresh = verify_triangle_reduction_schema(
            authority.callback, authority.schema, target=authority.target
        )
        if (
            fresh != authority
            or compile_triangle_reduction_abi(
                fresh, any_hit_proof_authority=any_hit_proof_authority
            )
            != abi
            or compile_triangle_reduction_contract(fresh, abi_sha256=abi.abi_sha256)
            != contract
        ):
            raise RuntimeError("triangle-reduction authority/ABI/contract drift")
        composed_ptx = consume_verified_triangle_reduction_executable(
            executable,
            fresh,
            contract,
            abi,
            any_hit_proof_authority=any_hit_proof_authority,
        )
        vertex_flat = [float(value) for row in vertices for value in row]
        index_flat = [int(value) for row in triangles for value in row]
        if (
            not vertices
            or not triangles
            or any(len(row) != 3 for row in vertices)
            or any(len(row) != 3 for row in triangles)
        ):
            raise ValueError("nonempty arity-three vertices and triangles required")
        if not all(math.isfinite(item) for item in vertex_flat) or any(
            not 0 <= item < len(vertices) for item in index_flat
        ):
            raise ValueError("invalid prepared triangle geometry")
        if not isinstance(event_capacity, int) or event_capacity <= 0:
            raise ValueError("positive event capacity required")
        primitive_names = {
            channel.semantic_id
            for channel in fresh.schema.metadata_channels
            if channel.domain is MetadataDomain.PRIMITIVE
        }
        if set(metadata) != primitive_names:
            raise ValueError("prepared metadata must contain exact primitive channels")
        seed_metadata = dict(metadata)
        seed_metadata.update(
            {
                channel.semantic_id: ()
                for channel in fresh.schema.metadata_channels
                if channel.domain is MetadataDomain.QUERY
            }
        )
        normalized, p_u64, p_i64, p_u32 = _typed_metadata(
            fresh, seed_metadata, primitive_count=len(triangles), query_count=0
        )
        if library is None:
            from . import optix_runtime

            library = optix_runtime._load_optix_library()
        native_path = _native_path(library, native_library_path)
        native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
        if native_sha != fresh.target.native_sha256:
            raise RuntimeError("executed native bytes do not match target authority")
        (
            prepare,
            execute,
            execute_scalar,
            execute_scalar_integrated,
            commit,
            cache_digest,
            destroy,
            reduce_u64,
        ) = _configure(library)
        vertices_native = (ctypes.c_float * len(vertex_flat))(*vertex_flat)
        triangles_native = (ctypes.c_uint32 * len(index_flat))(*index_flat)
        token = ctypes.c_uint64()
        error = ctypes.create_string_buffer(16384)
        _raise(
            int(
                prepare(
                    composed_ptx.encode(),
                    vertices_native,
                    len(vertices),
                    triangles_native,
                    len(triangles),
                    p_u64,
                    p_i64,
                    p_u32,
                    event_capacity,
                    ctypes.byref(token),
                    error,
                    len(error),
                )
            ),
            error,
            "prepared triangle prepare",
        )
        if not token.value:
            raise RuntimeError("prepared triangle returned zero token")
        self._token = int(token.value)
        self._library = library
        self._execute = execute
        self._execute_scalar = execute_scalar
        self._execute_scalar_integrated = execute_scalar_integrated
        self._commit = commit
        self._cache_digest = cache_digest
        self._destroy = destroy
        self._reduce_u64 = reduce_u64
        self._fresh = fresh
        self._contract = contract
        self._abi = abi
        self._normalized_metadata = normalized
        self._primitive_count = len(triangles)
        self._event_capacity = event_capacity
        self._event_query_host = (ctypes.c_uint32 * event_capacity)()
        self._event_primitive_host = (ctypes.c_uint32 * event_capacity)()
        self._event_stable_host = (ctypes.c_uint64 * event_capacity)()
        self._event_signed_host = (ctypes.c_int64 * event_capacity)()
        self._event_include_host = (ctypes.c_uint32 * event_capacity)()
        self._cached_queries = None
        self._cached_query_metadata = None
        self._cached_query_inputs = None
        self._cached_query_digest = None
        self._cached_query_generation = None
        self._cached_query_pointers = None
        self._native_sha = native_sha
        self._composed_ptx_sha = hashlib.sha256(composed_ptx.encode()).hexdigest()
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._closed = False
        self._execution_count = 0
        self._last_execution_receipt = None
        self._scalar_output = ctypes.c_uint64()
        self._fast_compact_status = ctypes.c_uint32()
        self._fast_receipt = _FastPathReceipt()
        self._call_error = ctypes.create_string_buffer(16384)
        self._integrated_audit_snapshot = NativeTraversalAuditSnapshot()
        self._integrated_audit_sequence = 0
        self._integrated_audit_nonce_hi = secrets.randbits(64) or 1
        self._integrated_audit_output_sha = None
        self._integrated_status_rows = None
        self._route_identity = (
            "v4_builtin_triangle_callback_ir:checked_reduction_v1"
        )
        self._program_bundle = "v4_builtin_triangle_checked_reduction_composed"
        self._semantic_digest = _digest(
            {
                "authority": self._fresh.authority_nonce,
                "contract": self._contract.contract_sha256,
                "abi": self._abi.abi_sha256,
                "composed_ptx": self._composed_ptx_sha,
                "native": self._native_sha,
            }
        )
        self._native_path = native_path
        self.prepare_seconds = time.perf_counter() - started
        self._session_identity = _digest(
            {
                "schema": "rtdl.v4.prepared_triangle_reduction_owner.v1",
                "authority": fresh.authority_nonce,
                "contract": contract.contract_sha256,
                "abi": abi.abi_sha256,
                "ptx": self._composed_ptx_sha,
                "native": native_sha,
                "pid": self._pid,
                "thread": self._thread,
                "token": self._token,
            }
        )

    def __getstate__(self):
        raise RuntimeError("prepared triangle owner cannot be serialized")

    def _check(self):
        if self._closed:
            raise RuntimeError("prepared triangle owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError("prepared triangle owner crossed process boundary")
        if threading.get_ident() != self._thread:
            raise RuntimeError("prepared triangle owner crossed thread boundary")

    def _clear_query_cache_identity(self) -> None:
        self._cached_queries = None
        self._cached_query_metadata = None
        self._cached_query_inputs = None
        self._cached_query_digest = None
        self._cached_query_generation = None
        self._cached_query_pointers = None

    def _commit_query_cache(self, digest_hex: str) -> None:
        digest = (ctypes.c_uint8 * 32).from_buffer_copy(bytes.fromhex(digest_hex))
        error = ctypes.create_string_buffer(16384)
        _raise(
            int(self._commit(self._token, digest, 32, error, len(error))),
            error,
            "prepared triangle query-cache commit",
        )

    def _native_query_cache_digest(self) -> str | None:
        digest = (ctypes.c_uint8 * 32)()
        present = ctypes.c_uint32()
        error = ctypes.create_string_buffer(16384)
        _raise(
            int(
                self._cache_digest(
                    self._token, digest, 32, ctypes.byref(present), error, len(error)
                )
            ),
            error,
            "prepared triangle query-cache digest",
        )
        return bytes(digest).hex() if present.value else None

    def _query_cache_reusable(
        self,
        queries,
        metadata_key,
        *,
        in_call_reuse_validation: bool = False,
    ) -> bool:
        cached_metadata = self._cached_query_metadata
        local_match = (
            queries is self._cached_queries
            and cached_metadata is not None
            and len(metadata_key) == len(cached_metadata)
            and all(
                key == cached_key and values is cached_values
                for (key, values), (cached_key, cached_values)
                in zip(metadata_key, cached_metadata, strict=True)
            )
            and self._cached_query_inputs is not None
            and self._cached_query_digest is not None
            and (
                not in_call_reuse_validation
                or self._cached_query_generation is not None
            )
        )
        if not local_match:
            return False
        if in_call_reuse_validation:
            return True
        return self._native_query_cache_digest() == self._cached_query_digest

    def last_forensic_traversal_receipt(self) -> Mapping[str, object]:
        """Expand the latest integrated compact stamp outside ordinary execute."""

        self._check()
        if (
            self._integrated_audit_sequence == 0
            or self._integrated_audit_output_sha is None
        ):
            raise RuntimeError("no integrated traversal observation is available")
        observation = captured_traversal_observation_from_snapshot(
            self._integrated_audit_snapshot,
            provider_library_path=self._native_path,
            provider_library_sha256=self._native_sha,
            nonce=(
                self._integrated_audit_nonce_hi,
                self._integrated_audit_sequence,
            ),
            expected_program_bundles=(self._program_bundle,),
        )
        return observation.build_receipt(
            semantic_digest=self._semantic_digest,
            output_digest=self._integrated_audit_output_sha,
            route_identity=self._route_identity,
        )

    @property
    def lifecycle_receipt(self):
        self._check()
        last_execution = self._last_execution_receipt
        if last_execution is not None:
            last_execution = dict(last_execution)
            fast = last_execution.get("fast_operation_receipt")
            if isinstance(fast, Mapping):
                last_execution["fast_operation_receipt"] = dict(fast)
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
            "last_execution": last_execution,
            "native_library_sha256": self._native_sha,
            "composed_ptx_sha256": self._composed_ptx_sha,
        }

    def execute(self, queries, *, query_metadata=None, include_diagnostics=True):
        self._check()
        if type(include_diagnostics) is not bool:
            raise TypeError("include_diagnostics must be an exact bool")
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared triangle owner is already executing")
        try:
            if not queries:
                raise ValueError("nonempty queries required")
            count = len(queries)
            query_metadata = {} if query_metadata is None else dict(query_metadata)
            expected_query_names = {
                channel.semantic_id
                for channel in self._fresh.schema.metadata_channels
                if channel.domain is MetadataDomain.QUERY
            }
            if set(query_metadata) != expected_query_names:
                raise ValueError("query metadata must contain exact query channels")
            metadata_key = tuple(sorted(query_metadata.items()))
            reducer = self._fresh.schema.reducer
            scalar_only = (
                not include_diagnostics
                and reducer.algebra
                in {
                    ReducerAlgebra.CHECKED_U64_SUM,
                    ReducerAlgebra.CHECKED_U64_PRODUCT_SUM,
                }
            )
            integrated_scalar = (
                scalar_only
                and getattr(self, "_execute_scalar_integrated", None) is not None
            )
            try:
                cache_hit = self._query_cache_reusable(
                    queries,
                    metadata_key,
                    in_call_reuse_validation=integrated_scalar,
                )
            except BaseException:
                self._clear_query_cache_identity()
                raise
            cacheable = cache_hit or _query_rows_are_immutable(
                queries, query_metadata
            )
            next_cached_query_inputs = None
            next_cached_query_pointers = None
            if cache_hit:
                (
                    origins_f32,
                    directions_f32,
                    tmax_f32,
                    normalized,
                    multiplier_native,
                    query_digest_native,
                ) = self._cached_query_inputs
                query_digest = self._cached_query_digest
                cached_pointers = getattr(self, "_cached_query_pointers", None)
                if cached_pointers is not None:
                    origin_native, direction_native, tmax_native = cached_pointers
            else:
                # Retire the old identity before native state can change.  A
                # failed A->B transition must never make a later A look like
                # a valid device-cache hit.
                self._clear_query_cache_identity()
                if any(
                    len(origin) != 3 or len(direction) != 3
                    for origin, direction, _tmax in queries
                ):
                    raise ValueError("query arity is invalid")
                try:
                    origins_f64 = np.asarray(
                        [origin for origin, _direction, _tmax in queries],
                        dtype=np.float64,
                    )
                    directions_f64 = np.asarray(
                        [direction for _origin, direction, _tmax in queries],
                        dtype=np.float64,
                    )
                    tmax_f64 = np.asarray(
                        [tmax for _origin, _direction, tmax in queries],
                        dtype=np.float64,
                    )
                except (TypeError, ValueError, OverflowError) as exc:
                    raise ValueError("query contains a nonnumeric value") from exc
                if (
                    origins_f64.shape != (count, 3)
                    or directions_f64.shape != (count, 3)
                    or tmax_f64.shape != (count,)
                    or not np.isfinite(origins_f64).all()
                    or not np.isfinite(directions_f64).all()
                    or not np.isfinite(tmax_f64).all()
                    or np.any(tmax_f64 <= 0.0)
                    or np.any(np.all(directions_f64 == 0.0, axis=1))
                ):
                    raise ValueError("query contains an invalid ray")
                origins_f32 = np.ascontiguousarray(origins_f64, dtype=np.float32)
                directions_f32 = np.ascontiguousarray(directions_f64, dtype=np.float32)
                tmax_f32 = np.ascontiguousarray(tmax_f64, dtype=np.float32)
                if (
                    not np.isfinite(origins_f32).all()
                    or not np.isfinite(directions_f32).all()
                    or not np.isfinite(tmax_f32).all()
                ):
                    raise ValueError(
                        "query is outside the finite float32 target domain"
                    )
                all_metadata = {
                    key: value
                    for key, value in self._normalized_metadata.items()
                    if key not in expected_query_names
                }
                all_metadata.update(query_metadata)
                normalized, _p_u64, _p_i64, _p_u32 = _typed_metadata(
                    self._fresh,
                    all_metadata,
                    primitive_count=self._primitive_count,
                    query_count=count,
                )
                reducer = self._fresh.schema.reducer
                multiplier_native = None
                if reducer.algebra is ReducerAlgebra.CHECKED_U64_PRODUCT_SUM:
                    assert reducer.multiplicand_source is not None
                    multiplier_semantic = reducer.multiplicand_source.semantic_id
                    assert multiplier_semantic is not None
                    multiplier_native = (ctypes.c_uint64 * count)(
                        *normalized[multiplier_semantic]
                    )
                query_digest = _packed_query_digest(
                    origins_f32, directions_f32, tmax_f32
                )
                query_digest_native = (ctypes.c_uint8 * 32).from_buffer_copy(
                    bytes.fromhex(query_digest)
                )
                if cacheable:
                    next_cached_query_inputs = (
                        origins_f32,
                        directions_f32,
                        tmax_f32,
                        normalized,
                        multiplier_native,
                        query_digest_native,
                    )
            assert query_digest is not None
            if not cache_hit or getattr(self, "_cached_query_pointers", None) is None:
                origin_native = origins_f32.ctypes.data_as(
                    ctypes.POINTER(ctypes.c_float)
                )
                direction_native = directions_f32.ctypes.data_as(
                    ctypes.POINTER(ctypes.c_float)
                )
                tmax_native = tmax_f32.ctypes.data_as(
                    ctypes.POINTER(ctypes.c_float)
                )
                if cacheable:
                    next_cached_query_pointers = (
                        origin_native,
                        direction_native,
                        tmax_native,
                    )
            error = getattr(self, "_call_error", None)
            if error is None:
                error = ctypes.create_string_buffer(16384)
                self._call_error = error
            audit = None
            integrated_sequence = None
            if integrated_scalar:
                integrated_sequence = self._integrated_audit_sequence + 1
                if integrated_sequence >= 1 << 64:
                    raise RuntimeError(
                        "prepared triangle integrated audit sequence exhausted"
                    )
                self._integrated_audit_sequence = integrated_sequence
            else:
                audit = OptixTraversalAuditSession.open(library=self._library)
            self._integrated_audit_output_sha = None
            observed_input_generation = None
            try:
                if scalar_only:
                    reduced_native = getattr(self, "_scalar_output", None)
                    if reduced_native is None:
                        reduced_native = ctypes.c_uint64()
                        self._scalar_output = reduced_native
                    compact_status = getattr(self, "_fast_compact_status", None)
                    if compact_status is None:
                        compact_status = ctypes.c_uint32()
                        self._fast_compact_status = compact_status
                    fast_receipt = getattr(self, "_fast_receipt", None)
                    if fast_receipt is None:
                        fast_receipt = _FastPathReceipt()
                        self._fast_receipt = fast_receipt
                    use_multipliers = int(multiplier_native is not None)
                    scalar_symbol = (
                        self._execute_scalar_integrated
                        if integrated_scalar
                        else self._execute_scalar
                    )
                    scalar_args = [
                        self._token,
                        origin_native,
                        direction_native,
                        tmax_native,
                        count,
                        int(cache_hit),
                        use_multipliers,
                        int(cache_hit and use_multipliers),
                        query_digest_native,
                        32,
                        multiplier_native,
                        ctypes.byref(reduced_native),
                        ctypes.byref(compact_status),
                        ctypes.byref(fast_receipt),
                    ]
                    if integrated_scalar:
                        scalar_args.extend(
                            (
                                self._integrated_audit_nonce_hi,
                                integrated_sequence,
                                ctypes.byref(self._integrated_audit_snapshot),
                            )
                        )
                    scalar_args.extend((error, len(error)))
                    _raise(
                        int(scalar_symbol(*scalar_args)),
                        error,
                        (
                            "prepared triangle integrated scalar execute"
                            if integrated_scalar
                            else "prepared triangle scalar execute"
                        ),
                    )
                    fast_operation_receipt = _validate_fast_receipt(
                        fast_receipt,
                        query_count=count,
                        compact_status=int(compact_status.value),
                        prepared_input_reused=bool(cache_hit),
                        use_multipliers=bool(use_multipliers),
                        expected_input_generation=(
                            self._cached_query_generation
                            if integrated_scalar and cache_hit
                            else None
                        ),
                    )
                    observed_input_generation = int(
                        fast_receipt.dynamic_input_generation
                    )
                    status_rows = getattr(self, "_integrated_status_rows", None)
                    if status_rows is None or status_rows[0][
                        "validated_row_count"
                    ] != count:
                        status_rows = _ValidatedFastStatusRows(count)
                        if integrated_scalar:
                            self._integrated_status_rows = status_rows
                    counter_rows: Sequence[int] = ()
                    reduced = int(reduced_native.value)
                    per_ray_values: Sequence[int] = ()
                    reducer_rows: Sequence[Mapping[str, int]] = ()
                else:
                    fast_operation_receipt = None
                    per_ray = (ctypes.c_uint64 * count)()
                    event_count = ctypes.c_uint64()
                    event_query = self._event_query_host
                    event_primitive = self._event_primitive_host
                    event_stable = self._event_stable_host
                    event_signed = self._event_signed_host
                    event_include = self._event_include_host
                    statuses = (_Status * count)()
                    counters = (ctypes.c_uint64 * 7)()
                    _raise(
                        int(
                            self._execute(
                                self._token,
                                origin_native,
                                direction_native,
                                tmax_native,
                                count,
                                int(cache_hit),
                                per_ray,
                                ctypes.byref(event_count),
                                event_query,
                                event_primitive,
                                event_stable,
                                event_signed,
                                event_include,
                                statuses,
                                counters,
                                error,
                                len(error),
                            )
                        ),
                        error,
                        "prepared triangle diagnostic execute",
                    )
                    status_rows = _ValidatedStatusRows(statuses)
                    counter_rows = tuple(int(item) for item in counters)
                    if (
                        counter_rows[1] != count
                        or counter_rows[5] != count
                        or counter_rows[6] != count
                        or counter_rows[3] <= 0
                    ):
                        raise RuntimeError(
                            "prepared triangle role lifecycle incomplete"
                        )
                    per_ray_values = _U64Values(per_ray)
                    if reducer.algebra is ReducerAlgebra.CHECKED_KEYED_I64_SUM:
                        rows = []
                        for index in range(int(event_count.value)):
                            rows.append(
                                {
                                    "launch_index": int(event_query[index]),
                                    "primitive_index": int(event_primitive[index]),
                                    "primitive.stable_id": int(event_stable[index]),
                                    "primitive.signed_value": int(event_signed[index]),
                                    "primitive.include": int(event_include[index]),
                                }
                            )
                        reduced = execute_checked_reducer(reducer, rows)
                        reducer_rows = tuple(rows)
                    else:
                        value_field = reducer.value_source.output_field
                        assert (
                            reducer.value_source.kind
                            is ReducerSourceKind.PER_RAY_OUTPUT
                        )
                        assert value_field is not None
                        multipliers = None
                        multiplier_semantic = None
                        if reducer.multiplicand_source is not None:
                            multiplier_semantic = (
                                reducer.multiplicand_source.semantic_id
                            )
                            assert multiplier_semantic is not None
                            multipliers = normalized[multiplier_semantic]
                        reduced_native = ctypes.c_uint64()
                        _raise(
                            int(
                                self._reduce_u64(
                                    per_ray,
                                    multiplier_native,
                                    count,
                                    ctypes.byref(reduced_native),
                                    error,
                                    len(error),
                                )
                            ),
                            error,
                            "prepared triangle checked U64 reduction",
                        )
                        reduced = int(reduced_native.value)
                        reducer_rows = _PerRayReducerRows(
                            per_ray_values,
                            value_field=value_field,
                            multiplier_semantic=multiplier_semantic,
                            multipliers=multipliers,
                        )
                output_sha = _digest(reduced)
                if integrated_scalar:
                    receipt = build_compact_traversal_receipt(
                        self._integrated_audit_snapshot,
                        provider_library_sha256=self._native_sha,
                        route_identity=self._route_identity,
                        semantic_digest=self._semantic_digest,
                        output_digest=output_sha,
                        expected_program_bundle=self._program_bundle,
                        expected_raygen_invocation_count=count,
                        execution_sequence=integrated_sequence,
                    )
                else:
                    assert audit is not None
                    semantic_digest = getattr(self, "_semantic_digest", None)
                    if semantic_digest is None:
                        semantic_digest = _digest(
                            {
                                "authority": self._fresh.authority_nonce,
                                "contract": self._contract.contract_sha256,
                                "abi": self._abi.abi_sha256,
                                "composed_ptx": self._composed_ptx_sha,
                                "native": self._native_sha,
                            }
                        )
                    receipt = audit.finish(
                        semantic_digest=semantic_digest,
                        output_digest=output_sha,
                        route_identity=(
                            "v4_builtin_triangle_callback_ir:checked_reduction_v1"
                        ),
                        expected_program_bundles=(
                            "v4_builtin_triangle_checked_reduction_composed",
                        ),
                    )
                if (
                    receipt["physical_executor_classification"]
                    != "optix_traversal_observed"
                ):
                    raise RuntimeError("prepared triangle lacked bound traversal")
                if not cache_hit:
                    self._commit_query_cache(query_digest)
                    if self._native_query_cache_digest() != query_digest:
                        raise RuntimeError(
                            "prepared triangle query-cache commit mismatch"
                        )
            except BaseException:
                if audit is not None:
                    audit.abort()
                self._clear_query_cache_identity()
                raise
            if not cache_hit:
                if next_cached_query_inputs is not None:
                    self._cached_queries = queries
                    self._cached_query_metadata = metadata_key
                    self._cached_query_inputs = next_cached_query_inputs
                    self._cached_query_digest = query_digest
                    self._cached_query_generation = observed_input_generation
                    self._cached_query_pointers = next_cached_query_pointers
                else:
                    self._clear_query_cache_identity()
            elif next_cached_query_pointers is not None:
                self._cached_query_pointers = next_cached_query_pointers
            if integrated_scalar:
                self._integrated_audit_output_sha = output_sha
            self._last_execution_receipt = {
                "schema": "rtdl.v4.triangle_reduction_execution_boundary.v1",
                "execution_path": (
                    "device_resident_checked_u64_scalar_v8_integrated_audit"
                    if integrated_scalar
                    else "device_resident_checked_u64_scalar_v7"
                    if scalar_only
                    else "diagnostic_per_ray_v2"
                ),
                "prepared_query_input_reused": bool(cache_hit),
                "per_ray_u64_materialized_on_host": not scalar_only,
                "event_rows_materialized_on_host": not scalar_only,
                "public_output_scalar_bytes": (
                    ctypes.sizeof(ctypes.c_uint64) if scalar_only else None
                ),
                "fast_operation_receipt": fast_operation_receipt,
            }
            self._execution_count += 1
            return V4TriangleReductionResult(
                reduced_output=reduced,
                per_ray_u64=per_ray_values,
                raw_reducer_rows=reducer_rows,
                role_counters=counter_rows,
                launch_status=status_rows,
                traversal_receipt=receipt,
                output_sha256=output_sha,
                composed_ptx_sha256=self._composed_ptx_sha,
                native_library_sha256=self._native_sha,
            )
        finally:
            self._active.release()

    def close(self):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close prepared triangle during execution")
        try:
            error = ctypes.create_string_buffer(16384)
            _raise(
                int(self._destroy(self._token, error, len(error))),
                error,
                "prepared triangle destroy",
            )
            self._token = 0
            self._closed = True
        finally:
            self._active.release()

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def prepare_triangle_reduction_callback(**kwargs):
    return PreparedTriangleReductionOwner(**kwargs)


__all__ = ["PreparedTriangleReductionOwner", "prepare_triangle_reduction_callback"]
