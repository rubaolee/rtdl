"""Explicit prepared owner for verified V4 bounded-relation callbacks."""

from __future__ import annotations

import ctypes
import hashlib
import os
import threading
import time
from typing import Iterator, Mapping, Sequence

from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_bounded_relation import (
    compile_bounded_relation_contract,
    verify_precanonical_bounded_relation,
    verify_bounded_relation_schema,
)
from .v4_bounded_relation_optix_compiler import consume_verified_bounded_relation_executable
from .v4_bounded_relation_optix_runtime import (
    V4BoundedRelationResult, _Status, _boxes, _digest, _native_path)
from .v4_callback_abi import verify_compiled_callback_abi


def _configure(library):
    prepare = getattr(library, "rtdl_optix_v4_prepare_bounded_relation_callback_v1", None)
    execute = getattr(library, "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v3", None)
    destroy = getattr(library, "rtdl_optix_v4_destroy_prepared_bounded_relation_callback_v1", None)
    if prepare is None or execute is None or destroy is None:
        raise RuntimeError(
            "native library lacks Goal5798 immutable-input-reuse bounded-relation ABI")
    prepare.argtypes = [
        ctypes.c_char_p, ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t, ctypes.c_float,
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    execute.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(_Status),
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t]
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
        self, *, authority, contract, abi, executable,
        any_hit_proof_authority, indexed_boxes, library=None,
        native_library_path=None,
    ):
        started = time.perf_counter()
        fresh = verify_bounded_relation_schema(authority.physical, authority.schema)
        if fresh != authority \
                or verify_compiled_callback_abi(
                    abi, fresh.physical.callback,
                    any_hit_proof_authority=any_hit_proof_authority,
                    physical_schema_authority=fresh.physical) != abi \
                or compile_bounded_relation_contract(
                    fresh, abi_sha256=abi.abi_sha256) != contract:
            raise RuntimeError("bounded-relation authority/ABI/contract drift")
        composed_ptx = consume_verified_bounded_relation_executable(
            executable, fresh, contract, abi,
            any_hit_proof_authority=any_hit_proof_authority)
        indexed_native, indexed_ids = _boxes(indexed_boxes, "indexed_boxes")
        if library is None:
            from . import optix_runtime
            library = optix_runtime._load_optix_library()
        native_path = _native_path(library, native_library_path)
        native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
        if native_sha != fresh.physical.target.native_sha256:
            raise RuntimeError("executed native bytes do not match target authority")
        prepare, execute, destroy = _configure(library)
        token = ctypes.c_uint64(); error = ctypes.create_string_buffer(16384)
        _raise(int(prepare(
            composed_ptx.encode(), indexed_native, indexed_ids,
            len(indexed_boxes), float(contract.minimum_overlap_f32),
            contract.capacity, ctypes.byref(token), error, len(error))),
            error, "prepared bounded relation prepare")
        if not token.value:
            raise RuntimeError("prepared bounded relation returned zero token")
        self._token = int(token.value)
        self._fresh = fresh
        self._contract = contract
        self._abi = abi
        self._library = library
        self._execute = execute
        self._destroy = destroy
        self._indexed_count = len(indexed_boxes)
        self._native_sha = native_sha
        self._ptx_sha = hashlib.sha256(composed_ptx.encode()).hexdigest()
        self._pid = os.getpid(); self._thread = threading.get_ident()
        self._active = threading.Lock(); self._closed = False
        self._execution_count = 0
        self._cached_source_object = None
        self._cached_source_native = None
        self._cached_expected_object = None
        self._cached_expected_rows = None
        self._cached_output_rows = None
        self._cached_output_sha = None
        self._row_storage = (
            ctypes.c_uint32 * (self._contract.capacity * 2))()
        self._status_capacity = self._indexed_count
        self._statuses = (_Status * self._status_capacity)()
        self._counters = (ctypes.c_uint64 * 7)()
        self._raw_count = ctypes.c_uint64()
        self._unique_count = ctypes.c_uint64()
        self._overflowed = ctypes.c_uint32()
        self._error = ctypes.create_string_buffer(16384)
        self.prepare_seconds = time.perf_counter() - started
        self._session_identity = _digest({
            "schema": "rtdl.v4.prepared_bounded_relation_owner.v1",
            "authority": fresh.authority_nonce,
            "contract": contract.contract_sha256, "abi": abi.abi_sha256,
            "ptx": self._ptx_sha, "native": native_sha,
            "pid": self._pid, "thread": self._thread, "token": self._token,
        })

    def __getstate__(self):
        raise RuntimeError("prepared bounded relation owner cannot be serialized")

    def _check(self):
        if self._closed:
            raise RuntimeError("prepared bounded relation owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError("prepared bounded relation owner crossed process boundary")
        if threading.get_ident() != self._thread:
            raise RuntimeError("prepared bounded relation owner crossed thread boundary")

    @property
    def lifecycle_receipt(self):
        self._check()
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "session_identity": self._session_identity,
            "process_bound": True, "thread_bound": True,
            "nonserializable": True, "nonreentrant": True,
            "prepare_seconds_reported_separately": True,
            "cold_result_replaced": False,
            "execution_count": self._execution_count,
            "native_library_sha256": self._native_sha,
            "composed_ptx_sha256": self._ptx_sha,
        }

    def execute(self, source_boxes, *, expected_rows=None):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared bounded relation owner is already executing")
        try:
            cache_hit = (
                source_boxes is self._cached_source_object
                and self._cached_source_native is not None
            )
            if cache_hit:
                source_native, source_ids = self._cached_source_native
            else:
                # Retire the old identity before native state can change.  A
                # failed A->B transition must never make a later A look like
                # a valid device-cache hit.
                self._cached_source_object = None
                self._cached_source_native = None
                source_native, source_ids = _boxes(source_boxes, "source_boxes")
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
            audit = OptixTraversalAuditSession.open(library=self._library)
            try:
                _raise(int(self._execute(
                    self._token, source_native, source_ids, len(source_boxes),
                    int(cache_hit),
                    ctypes.byref(raw_count), ctypes.byref(unique_count),
                    ctypes.byref(overflowed), row_storage,
                    statuses, counters, error, len(error))), error,
                    "prepared bounded relation execute")
                # The paired native ABI scanned every status row and failed
                # before returning output.  Preserve the complete evidence
                # without allocating thousands of Python dictionaries in the
                # hot path.
                status_rows = _ValidatedStatusRows(statuses, required_status)
                counter_rows = tuple(int(item) for item in counters)
                launch_count = len(source_boxes) + self._indexed_count
                if counter_rows[1] != launch_count or counter_rows[6] != launch_count \
                        or counter_rows[4] + counter_rows[5] != launch_count:
                    raise RuntimeError("prepared bounded relation lifecycle incomplete")
                stored = min(int(unique_count.value), capacity)
                raw_rows = tuple(
                    (int(row_storage[index * 2]), int(row_storage[index * 2 + 1]))
                    for index in range(stored))
                rows = verify_precanonical_bounded_relation(
                    raw_rows, capacity=capacity,
                    observed_unique_count=int(unique_count.value),
                    overflowed=bool(overflowed.value))
                if expected_rows is not None:
                    if expected_rows is self._cached_expected_object:
                        normalized_expected = self._cached_expected_rows
                    else:
                        normalized_expected = tuple(sorted(
                            (int(row[0]), int(row[1])) for row in expected_rows))
                        if isinstance(expected_rows, tuple):
                            self._cached_expected_object = expected_rows
                            self._cached_expected_rows = normalized_expected
                    if rows != normalized_expected:
                        raise RuntimeError(
                            "prepared bounded relation output mismatch")
                if rows == self._cached_output_rows:
                    output_sha = self._cached_output_sha
                else:
                    output_sha = _digest(rows)
                    self._cached_output_rows = rows
                    self._cached_output_sha = output_sha
                receipt = audit.finish(
                    semantic_digest=_digest({
                        "authority": self._fresh.authority_nonce,
                        "contract": self._contract.contract_sha256,
                        "abi": self._abi.abi_sha256, "ptx": self._ptx_sha,
                        "native": self._native_sha,
                    }), output_digest=output_sha,
                    route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
                    expected_program_bundles=(
                        "v4_custom_aabb_bounded_relation_composed",))
            except Exception:
                audit.abort()
                self._cached_source_object = None
                self._cached_source_native = None
                raise
            if receipt["physical_executor_classification"] != "optix_traversal_observed":
                raise RuntimeError("prepared bounded relation lacked bound traversal")
            if not cache_hit:
                if isinstance(source_boxes, tuple):
                    self._cached_source_object = source_boxes
                    self._cached_source_native = (source_native, source_ids)
                else:
                    self._cached_source_object = None
                    self._cached_source_native = None
            self._execution_count += 1
            return V4BoundedRelationResult(
                rows, raw_rows, int(raw_count.value),
                int(raw_count.value) - int(unique_count.value),
                counter_rows, status_rows, receipt, output_sha, self._ptx_sha,
                self._native_sha)
        finally:
            self._active.release()

    def close(self):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close prepared bounded relation during execution")
        try:
            error = ctypes.create_string_buffer(16384)
            _raise(int(self._destroy(self._token, error, len(error))), error,
                   "prepared bounded relation destroy")
            self._token = 0; self._closed = True
        finally:
            self._active.release()

    def __enter__(self):
        self._check(); return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def prepare_bounded_relation_callback(**kwargs):
    return PreparedBoundedRelationOwner(**kwargs)


__all__ = ["PreparedBoundedRelationOwner", "prepare_bounded_relation_callback"]
