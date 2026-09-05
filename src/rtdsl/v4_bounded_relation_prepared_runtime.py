"""Explicit prepared owner for verified V4 bounded-relation callbacks."""

from __future__ import annotations

import ctypes
import hashlib
import os
import secrets
import struct
import threading
import time
from collections.abc import Iterator, Mapping, Sequence
from types import MappingProxyType

from .physical_execution_provenance import (
    NativeTraversalAuditSnapshot,
    OptixTraversalAuditSession,
    build_validated_compact_traversal_receipt,
)
from .v4_bounded_relation import (
    verify_precanonical_bounded_relation,
)
from .v4_bounded_relation_optix_compiler import (
    consume_verified_bounded_relation_executable,
)
from .v4_bounded_relation_optix_runtime import (
    V4BoundedRelationResult,
    _boxes,
    _digest,
    _native_path,
    _Status,
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
    _names = tuple(name for name, _ctype in _FastPathReceipt._fields_)
    _boolean_names = {
        "status_before_output",
        "role_counters_materialized",
        "prepared_input_reused",
    }

    def __init__(self, receipt: _FastPathReceipt) -> None:
        self._values = MappingProxyType(
            {
                name: (
                    bool(int(getattr(receipt, name)))
                    if name in self._boolean_names
                    else int(getattr(receipt, name))
                )
                for name in self._names
            }
        )

    def __getitem__(self, key: str) -> int | bool:
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)


class _ValidatedFastStatusRows(Sequence[Mapping[str, int]]):
    native_validated_all_ok = True

    def __init__(self, validated_row_count: int) -> None:
        self._row = MappingProxyType(
            {
                "first_error_claimed": 0,
                "error_code": 0,
                "validated_row_count": int(validated_row_count),
                "success_status_control_d2h_bytes": 4 * ctypes.sizeof(
                    ctypes.c_uint32
                ),
            }
        )

    def __len__(self) -> int:
        return 1

    def __getitem__(self, index):
        if isinstance(index, slice):
            return (self._row,)[index]
        if index in (0, -1):
            return self._row
        raise IndexError(index)

    def __iter__(self) -> Iterator[Mapping[str, int]]:
        yield self._row


_VALIDATED_RELATION_ROWS_TOKEN = object()


class ValidatedBoundedRelationRows(tuple):
    """Factory-only immutable canonical rows with an already-bound digest."""

    def __new__(
        cls,
        rows: tuple[tuple[int, int], ...],
        *,
        output_sha256: str,
        _token: object,
    ):
        if _token is not _VALIDATED_RELATION_ROWS_TOKEN or type(rows) is not tuple:
            raise RuntimeError("validated bounded-relation rows require their factory")
        instance = tuple.__new__(cls, rows)
        object.__setattr__(instance, "_validated_output_sha256", output_sha256)
        return instance

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("validated bounded-relation rows are immutable")


def validate_bound_relation_rows(
    rows: object, *, output_sha256: str
) -> ValidatedBoundedRelationRows:
    if (
        type(rows) is not ValidatedBoundedRelationRows
        or rows._validated_output_sha256 != output_sha256
    ):
        raise RuntimeError("validated bounded-relation row binding differs")
    return rows


def _validate_fast_receipt(
    receipt: _FastPathReceipt,
    *,
    compact_status: int,
    output_row_count: int,
    prepared_input_reused: bool,
    source_count: int,
    semantic_capacity: int,
    previous_input_generation: int,
    expected_reused_generation: int | None,
) -> _ValidatedFastOperationReceipt:
    success = compact_status == 0
    key_capacity = 1
    while key_capacity < 2 * semantic_capacity:
        key_capacity <<= 1
    raw_booleans = {
        "status_before_output": int(receipt.status_before_output),
        "role_counters_materialized": int(receipt.role_counters_materialized),
        "prepared_input_reused": int(receipt.prepared_input_reused),
    }
    expected_output_bytes = output_row_count * 2 * ctypes.sizeof(ctypes.c_uint32)
    generation = int(receipt.dynamic_input_generation)
    expected_upload_calls = 0 if prepared_input_reused else 2
    expected_upload_bytes = 0 if prepared_input_reused else source_count * 52
    expected_build_count = 0 if prepared_input_reused else 1
    invalid = (
        ctypes.sizeof(_FastPathReceipt) != 128
        or int(receipt.schema_version) != 2
        or any(value not in (0, 1) for value in raw_booleans.values())
        or raw_booleans["status_before_output"] != 1
        or raw_booleans["role_counters_materialized"] != 0
        or raw_booleans["prepared_input_reused"] != int(prepared_input_reused)
        or int(receipt.optix_launch_count) != 2
        or int(receipt.host_blocking_boundary_count) != (2 if success else 1)
        or int(receipt.control_d2h_bytes) != 7 * ctypes.sizeof(ctypes.c_uint32)
        or int(receipt.output_d2h_bytes)
            != (expected_output_bytes if success else 0)
        or int(receipt.output_d2h_after_status_failure) != 0
        or int(receipt.dynamic_device_upload_call_count) != expected_upload_calls
        or int(receipt.dynamic_device_upload_bytes) != expected_upload_bytes
        or int(receipt.dynamic_accel_build_count) != expected_build_count
        or int(receipt.dynamic_explicit_sync_count) != 0
        or int(receipt.dynamic_blocking_upload_call_count) != 0
        or generation <= 0
        or (
            prepared_input_reused
            and (
                expected_reused_generation is None
                or generation != expected_reused_generation
            )
        )
        or (not prepared_input_reused and generation <= previous_input_generation)
        or int(receipt.semantic_compaction_launch_count) != 1
        or int(receipt.semantic_compaction_key_capacity) != key_capacity
        or int(receipt.semantic_compaction_scratch_bytes)
            != (
                8 * key_capacity
                + 8 * semantic_capacity
                + 2 * ctypes.sizeof(ctypes.c_uint32)
            )
        or int(receipt.callback_status_kernel_launch_count) != 0
        or int(receipt.checked_product_kernel_launch_count) != 0
        or int(receipt.compact_control_finalizer_kernel_launch_count) != 0
        or int(receipt.total_auxiliary_cuda_kernel_launch_count) != 1
        or int(receipt.execution_parameter_h2d_bytes) != 240
        or int(receipt.execution_parameter_h2d_copy_call_count) != 2
        or int(receipt.stream_ordered_memset_call_count) != 4
        or int(receipt.status_d2h_copy_call_count) != 1
        or int(receipt.output_d2h_copy_call_count)
            != int(success and output_row_count > 0)
    )
    if invalid:
        raise RuntimeError(
            "prepared bounded-relation fast-path receipt is invalid: "
            f"{dict(_ValidatedFastOperationReceipt(receipt))!r}"
        )
    if not success:
        raise RuntimeError(
            "prepared bounded-relation compact device status rejected execution: "
            f"{compact_status}"
        )
    return _ValidatedFastOperationReceipt(receipt)


def _configure(library):
    prepare = getattr(
        library, "rtdl_optix_v4_prepare_bounded_relation_callback_v1", None
    )
    execute = getattr(
        library, "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v3", None
    )
    execute_fast_integrated = getattr(
        library,
        "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v8",
        None,
    )
    commit = getattr(
        library,
        "rtdl_optix_v4_commit_prepared_bounded_relation_source_cache_v2",
        None,
    )
    cache_digest = getattr(
        library,
        "rtdl_optix_v4_prepared_bounded_relation_source_cache_digest_v1",
        None,
    )
    destroy = getattr(
        library, "rtdl_optix_v4_destroy_prepared_bounded_relation_callback_v1", None
    )
    if any(
        symbol is None for symbol in (prepare, execute, commit, cache_digest, destroy)
    ):
        raise RuntimeError(
            "native library lacks two-phase prepared bounded-relation cache ABI"
        )
    prepare.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.c_float,
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    execute.argtypes = [
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(_Status),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    if execute_fast_integrated is not None:
        execute_fast_integrated.argtypes = [
            ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(_FastPathReceipt),
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
    for symbol in (
        prepare,
        execute,
        execute_fast_integrated,
        commit,
        cache_digest,
        destroy,
    ):
        if symbol is None:
            continue
        symbol.restype = ctypes.c_int
    return (
        prepare,
        execute,
        execute_fast_integrated,
        commit,
        cache_digest,
        destroy,
    )


def _raise(status, error, label):
    if status:
        raise RuntimeError(
            error.value.decode("utf-8", errors="replace")
            or f"{label} failed with status {status}"
        )


def _packed_source_digest(source_native, source_ids) -> str:
    digest = hashlib.sha256(b"RTDL-V4-BOUNDED-SOURCE-CACHE-V1\x00")
    for values in (source_native, source_ids):
        payload = bytes(values)
        digest.update(len(payload).to_bytes(8, "little"))
        digest.update(payload)
    return digest.hexdigest()


def _source_rows_are_immutable(source_boxes) -> bool:
    return (
        isinstance(source_boxes, tuple)
        and all(isinstance(row, tuple) and len(row) == 5 for row in source_boxes)
        and all(type(value) in (int, float) for row in source_boxes for value in row)
    )


class _ValidatedStatusRows(Sequence[Mapping[str, int]]):
    """Complete lazy status evidence after the native ABI scanned every row."""

    native_validated_all_ok = True

    def __init__(self, rows, length=None) -> None:
        self._rows = rows
        self._length = len(rows) if length is None else int(length)
        if self._length < 0 or self._length > len(rows):
            raise ValueError("validated status length is outside backing storage")

    def __len__(self) -> int:
        return self._length

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


class PreparedBoundedRelationOwner:
    def __init__(
        self,
        *,
        authority,
        contract,
        abi,
        executable,
        any_hit_proof_authority,
        indexed_boxes,
        library=None,
        native_library_path=None,
    ):
        started = time.perf_counter()
        # The compiler registered this executable as a one-shot live
        # capability after full schema/ABI/contract verification.  Consuming
        # its structural seal rechecks every bound byte and rejects drift;
        # replaying the three derivations here proved no additional fact.
        composed_ptx = consume_verified_bounded_relation_executable(
            executable,
            authority,
            contract,
            abi,
            any_hit_proof_authority=any_hit_proof_authority,
        )
        indexed_native, indexed_ids = _boxes(indexed_boxes, "indexed_boxes")
        if library is None:
            from . import optix_runtime

            library = optix_runtime._load_optix_library()
        native_path = _native_path(library, native_library_path)
        native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
        if native_sha != authority.physical.target.native_sha256:
            raise RuntimeError("executed native bytes do not match target authority")
        (
            prepare,
            execute,
            execute_fast_integrated,
            commit,
            cache_digest,
            destroy,
        ) = _configure(library)
        token = ctypes.c_uint64()
        error = ctypes.create_string_buffer(16384)
        _raise(
            int(
                prepare(
                    composed_ptx.encode(),
                    indexed_native,
                    indexed_ids,
                    len(indexed_boxes),
                    float(contract.minimum_overlap_f32),
                    contract.capacity,
                    ctypes.byref(token),
                    error,
                    len(error),
                )
            ),
            error,
            "prepared bounded relation prepare",
        )
        if not token.value:
            raise RuntimeError("prepared bounded relation returned zero token")
        self._token = int(token.value)
        self._fresh = authority
        self._contract = contract
        self._abi = abi
        self._library = library
        self._execute = execute
        self._execute_fast_integrated = execute_fast_integrated
        self._commit = commit
        self._cache_digest = cache_digest
        self._destroy = destroy
        self._indexed_count = len(indexed_boxes)
        self._native_sha = native_sha
        self._ptx_sha = hashlib.sha256(composed_ptx.encode()).hexdigest()
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._closed = False
        self._execution_count = 0
        self._cached_source_object = None
        self._cached_source_native = None
        self._cached_source_digest = None
        self._cached_source_generation = None
        self._last_observed_source_generation = 0
        self._cached_expected_object = None
        self._cached_expected_rows = None
        self._cached_expected_output = None
        self._cached_output_packed = None
        self._cached_output_rows = None
        self._cached_output_sha = None
        self._row_storage = (ctypes.c_uint32 * (self._contract.capacity * 2))()
        self._status_capacity = self._indexed_count
        self._statuses = (_Status * self._status_capacity)()
        self._counters = (ctypes.c_uint64 * 7)()
        self._raw_count = ctypes.c_uint64()
        self._unique_count = ctypes.c_uint64()
        self._overflowed = ctypes.c_uint32()
        self._fast_compact_status = ctypes.c_uint32()
        self._fast_receipt = _FastPathReceipt()
        self._integrated_audit_snapshot = NativeTraversalAuditSnapshot()
        self._integrated_audit_sequence = 0
        self._integrated_audit_nonce_hi = secrets.randbits(64) or 1
        self._integrated_audit_output_sha = None
        self._integrated_status_rows = None
        self._last_fast_operation_receipt = None
        self._error = ctypes.create_string_buffer(16384)
        self._route_identity = "v4_callback_ir:custom_aabb_bounded_relation_v1"
        self._program_bundle = "v4_custom_aabb_bounded_relation_composed"
        self._semantic_digest = _digest(
            {
                "authority": self._fresh.authority_nonce,
                "contract": self._contract.contract_sha256,
                "abi": self._abi.abi_sha256,
                "ptx": self._ptx_sha,
                "native": self._native_sha,
            }
        )
        self._native_path = native_path
        self.prepare_seconds = time.perf_counter() - started
        self._session_identity = _digest(
            {
                "schema": "rtdl.v4.prepared_bounded_relation_owner.v1",
                "authority": authority.authority_nonce,
                "contract": contract.contract_sha256,
                "abi": abi.abi_sha256,
                "ptx": self._ptx_sha,
                "native": native_sha,
                "pid": self._pid,
                "thread": self._thread,
                "token": self._token,
            }
        )

    def __getstate__(self):
        raise RuntimeError("prepared bounded relation owner cannot be serialized")

    def _check(self):
        if self._closed:
            raise RuntimeError("prepared bounded relation owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError(
                "prepared bounded relation owner crossed process boundary"
            )
        if threading.get_ident() != self._thread:
            raise RuntimeError(
                "prepared bounded relation owner crossed thread boundary"
            )

    def _clear_source_cache_identity(self) -> None:
        self._cached_source_object = None
        self._cached_source_native = None
        self._cached_source_digest = None
        self._cached_source_generation = None

    def _commit_source_cache(self, digest_hex: str) -> None:
        digest = (ctypes.c_uint8 * 32).from_buffer_copy(bytes.fromhex(digest_hex))
        error = ctypes.create_string_buffer(16384)
        _raise(
            int(self._commit(self._token, digest, 32, error, len(error))),
            error,
            "prepared bounded relation source-cache commit",
        )

    def _native_source_cache_digest(self) -> str | None:
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
            "prepared bounded relation source-cache digest",
        )
        return bytes(digest).hex() if present.value else None

    def _source_cache_reusable(self, source_boxes) -> bool:
        local_match = (
            source_boxes is self._cached_source_object
            and self._cached_source_native is not None
            and self._cached_source_digest is not None
        )
        return (
            local_match
            and self._native_source_cache_digest() == self._cached_source_digest
        )

    @property
    def indexed_count(self) -> int:
        return self._indexed_count

    def _validate_expected_rows(self, rows, expected_rows) -> None:
        if expected_rows is None:
            return
        if (
            expected_rows is self._cached_expected_object
            and rows is self._cached_expected_output
        ):
            return
        if expected_rows is self._cached_expected_object:
            normalized_expected = self._cached_expected_rows
        else:
            normalized_expected = tuple(
                sorted((int(row[0]), int(row[1])) for row in expected_rows)
            )
        if rows != normalized_expected:
            raise RuntimeError("prepared bounded relation output mismatch")
        if isinstance(expected_rows, tuple):
            self._cached_expected_object = expected_rows
            self._cached_expected_rows = normalized_expected
            self._cached_expected_output = rows

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
        }

    def execute(
        self,
        source_boxes,
        *,
        expected_rows=None,
        include_diagnostics: bool = False,
    ):
        self._check()
        if type(include_diagnostics) is not bool:
            raise TypeError("include_diagnostics must be an exact bool")
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared bounded relation owner is already executing")
        try:
            try:
                cache_hit = self._source_cache_reusable(source_boxes)
            except BaseException:
                self._clear_source_cache_identity()
                raise
            if cache_hit:
                source_native, source_ids = self._cached_source_native
                source_digest = self._cached_source_digest
            else:
                # Retire the old identity before native state can change.  A
                # failed A->B transition must never make a later A look like
                # a valid device-cache hit.
                self._clear_source_cache_identity()
                source_native, source_ids = _boxes(source_boxes, "source_boxes")
                source_digest = _packed_source_digest(source_native, source_ids)
            assert source_digest is not None
            capacity = self._contract.capacity
            row_storage = self._row_storage
            required_status = len(source_boxes) + self._indexed_count
            if required_status > self._status_capacity:
                self._status_capacity = required_status
                self._statuses = (_Status * required_status)()
            statuses = self._statuses
            counters = self._counters
            raw_count = self._raw_count
            unique_count = self._unique_count
            overflowed = self._overflowed
            error = self._error
            integrated_fast = (
                not include_diagnostics
                and getattr(self, "_execute_fast_integrated", None) is not None
            )
            audit = (
                None
                if integrated_fast
                else OptixTraversalAuditSession.open(library=self._library)
            )
            integrated_sequence = None
            if integrated_fast:
                integrated_sequence = self._integrated_audit_sequence + 1
                if integrated_sequence >= 1 << 64:
                    raise RuntimeError(
                        "prepared bounded-relation integrated audit sequence exhausted"
                    )
                self._integrated_audit_sequence = integrated_sequence
            self._integrated_audit_output_sha = None
            next_output_cache = None
            try:
                launch_count = len(source_boxes) + self._indexed_count
                if integrated_fast:
                    compact_status = self._fast_compact_status
                    fast_receipt = self._fast_receipt
                    snapshot = self._integrated_audit_snapshot
                    assert integrated_sequence is not None
                    _raise(
                        int(
                            self._execute_fast_integrated(
                                self._token,
                                source_native,
                                source_ids,
                                len(source_boxes),
                                int(cache_hit),
                                ctypes.byref(raw_count),
                                ctypes.byref(unique_count),
                                ctypes.byref(overflowed),
                                row_storage,
                                ctypes.byref(compact_status),
                                ctypes.byref(fast_receipt),
                                self._integrated_audit_nonce_hi,
                                integrated_sequence,
                                ctypes.byref(snapshot),
                                error,
                                len(error),
                            )
                        ),
                        error,
                        "prepared bounded relation integrated fast execute",
                    )
                    row_count = int(unique_count.value)
                    fast_operation_receipt = _validate_fast_receipt(
                        fast_receipt,
                        compact_status=int(compact_status.value),
                        output_row_count=row_count,
                        prepared_input_reused=cache_hit,
                        source_count=len(source_boxes),
                        semantic_capacity=capacity,
                        previous_input_generation=(
                            self._last_observed_source_generation
                        ),
                        expected_reused_generation=(
                            self._cached_source_generation
                        ),
                    )
                    self._last_observed_source_generation = int(
                        fast_operation_receipt["dynamic_input_generation"]
                    )
                    if overflowed.value or row_count > capacity:
                        raise RuntimeError(
                            "prepared bounded relation output overflow"
                        )
                    packed_rows = ctypes.string_at(
                        ctypes.addressof(row_storage), row_count * 8
                    )
                    if (
                        packed_rows == self._cached_output_packed
                        and self._cached_output_rows is not None
                        and self._cached_output_sha is not None
                    ):
                        rows = self._cached_output_rows
                        output_sha = self._cached_output_sha
                    else:
                        decoded_rows = tuple(struct.iter_unpack("<II", packed_rows))
                        canonical_rows = verify_precanonical_bounded_relation(
                            decoded_rows,
                            capacity=capacity,
                            observed_unique_count=row_count,
                            overflowed=bool(overflowed.value),
                        )
                        output_sha = _digest(canonical_rows)
                        rows = ValidatedBoundedRelationRows(
                            canonical_rows,
                            output_sha256=output_sha,
                            _token=_VALIDATED_RELATION_ROWS_TOKEN,
                        )
                        next_output_cache = (packed_rows, rows, output_sha)
                    self._validate_expected_rows(rows, expected_rows)
                    receipt = build_validated_compact_traversal_receipt(
                        snapshot,
                        provider_library_sha256=self._native_sha,
                        route_identity=self._route_identity,
                        semantic_digest=self._semantic_digest,
                        output_digest=output_sha,
                        expected_program_bundle=self._program_bundle,
                        expected_raygen_invocation_count=launch_count,
                        execution_sequence=integrated_sequence,
                        expected_successful_launch_count=2,
                    )
                    status_rows = self._integrated_status_rows
                    if (
                        status_rows is None
                        or status_rows[0]["validated_row_count"] != launch_count
                    ):
                        status_rows = _ValidatedFastStatusRows(launch_count)
                        self._integrated_status_rows = status_rows
                    counter_rows = ()
                    raw_rows = ()
                else:
                    _raise(
                        int(
                            self._execute(
                                self._token,
                                source_native,
                                source_ids,
                                len(source_boxes),
                                int(cache_hit),
                                ctypes.byref(raw_count),
                                ctypes.byref(unique_count),
                                ctypes.byref(overflowed),
                                row_storage,
                                statuses,
                                counters,
                                error,
                                len(error),
                            )
                        ),
                        error,
                        "prepared bounded relation diagnostic execute",
                    )
                    status_rows = _ValidatedStatusRows(statuses, required_status)
                    counter_rows = tuple(int(item) for item in counters)
                    if (
                        counter_rows[1] != launch_count
                        or counter_rows[6] != launch_count
                        or counter_rows[4] + counter_rows[5] != launch_count
                    ):
                        raise RuntimeError(
                            "prepared bounded relation lifecycle incomplete"
                        )
                    stored = min(int(unique_count.value), capacity)
                    raw_rows = tuple(
                        (
                            int(row_storage[index * 2]),
                            int(row_storage[index * 2 + 1]),
                        )
                        for index in range(stored)
                    )
                    canonical_rows = verify_precanonical_bounded_relation(
                        raw_rows,
                        capacity=capacity,
                        observed_unique_count=int(unique_count.value),
                        overflowed=bool(overflowed.value),
                    )
                    output_sha = _digest(canonical_rows)
                    rows = ValidatedBoundedRelationRows(
                        canonical_rows,
                        output_sha256=output_sha,
                        _token=_VALIDATED_RELATION_ROWS_TOKEN,
                    )
                    self._validate_expected_rows(rows, expected_rows)
                    assert audit is not None
                    semantic_digest = getattr(self, "_semantic_digest", None)
                    if semantic_digest is None:
                        semantic_digest = _digest(
                            {
                                "authority": self._fresh.authority_nonce,
                                "contract": self._contract.contract_sha256,
                                "abi": self._abi.abi_sha256,
                                "ptx": self._ptx_sha,
                                "native": self._native_sha,
                            }
                        )
                    receipt = audit.finish(
                        semantic_digest=semantic_digest,
                        output_digest=output_sha,
                        route_identity=getattr(
                            self,
                            "_route_identity",
                            "v4_callback_ir:custom_aabb_bounded_relation_v1",
                        ),
                        expected_program_bundles=(
                            getattr(
                                self,
                                "_program_bundle",
                                "v4_custom_aabb_bounded_relation_composed",
                            ),
                        ),
                    )
                    if (
                        receipt["physical_executor_classification"]
                        != "optix_traversal_observed"
                    ):
                        raise RuntimeError(
                            "prepared bounded relation lacked bound traversal"
                        )
                if not cache_hit:
                    self._commit_source_cache(source_digest)
                    if self._native_source_cache_digest() != source_digest:
                        raise RuntimeError(
                            "prepared bounded relation source-cache commit mismatch"
                        )
            except BaseException:
                if audit is not None:
                    audit.abort()
                self._clear_source_cache_identity()
                raise
            if not cache_hit:
                if _source_rows_are_immutable(source_boxes):
                    self._cached_source_object = source_boxes
                    self._cached_source_native = (source_native, source_ids)
                    self._cached_source_digest = source_digest
                    if integrated_fast:
                        self._cached_source_generation = int(
                            fast_operation_receipt["dynamic_input_generation"]
                        )
                else:
                    self._clear_source_cache_identity()
            if next_output_cache is not None:
                (
                    self._cached_output_packed,
                    self._cached_output_rows,
                    self._cached_output_sha,
                ) = next_output_cache
            if integrated_fast:
                self._integrated_audit_output_sha = output_sha
                self._last_fast_operation_receipt = fast_operation_receipt
            self._execution_count += 1
            return V4BoundedRelationResult(
                rows,
                raw_rows,
                int(raw_count.value),
                int(raw_count.value) - int(unique_count.value),
                counter_rows,
                status_rows,
                receipt,
                output_sha,
                self._ptx_sha,
                self._native_sha,
                include_diagnostics,
            )
        finally:
            self._active.release()

    def close(self):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError(
                "cannot close prepared bounded relation during execution"
            )
        try:
            error = ctypes.create_string_buffer(16384)
            _raise(
                int(self._destroy(self._token, error, len(error))),
                error,
                "prepared bounded relation destroy",
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


def prepare_bounded_relation_callback(**kwargs):
    return PreparedBoundedRelationOwner(**kwargs)


__all__ = [
    "PreparedBoundedRelationOwner",
    "ValidatedBoundedRelationRows",
    "prepare_bounded_relation_callback",
    "validate_bound_relation_rows",
]
