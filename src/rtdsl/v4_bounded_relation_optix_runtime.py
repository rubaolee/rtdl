"""One-shot functional runtime for verified bounded relation emission."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Sequence

from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_bounded_relation import (
    BoundedRelationError,
    CompiledBoundedRelationContract,
    VerifiedBoundedRelationAuthority,
    compile_bounded_relation_contract,
    materialize_bounded_relation,
    verify_bounded_relation_schema,
)
from .v4_bounded_relation_optix_compiler import (
    VerifiedBoundedRelationExecutable,
    consume_verified_bounded_relation_executable,
)
from .v4_callback_abi import CompiledCallbackAbi, verify_compiled_callback_abi


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


@dataclass(frozen=True)
class V4BoundedRelationResult:
    rows: tuple[tuple[int, int], ...]
    raw_rows: tuple[tuple[int, int], ...]
    raw_event_count: int
    duplicate_count: int
    role_counters: tuple[int, ...]
    launch_status: tuple[dict[str, int], ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    composed_ptx_sha256: str
    native_library_sha256: str


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _native_path(library: object, explicit: str | Path | None) -> Path:
    candidate = explicit or os.environ.get("RTDL_OPTIX_LIB") \
        or getattr(library, "_name", None)
    if not candidate:
        raise RuntimeError("exact native library path is required")
    path = Path(candidate).resolve()
    if not path.is_file():
        raise RuntimeError("exact native library bytes are unavailable")
    return path


def _configure(library: object):
    symbol = getattr(
        library, "rtdl_optix_v4_run_bounded_relation_callback_v1", None)
    if symbol is None:
        raise RuntimeError("native library lacks Goal5760 bounded-relation ABI")
    symbol.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.c_float, ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(_Status),
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    symbol.restype = ctypes.c_int
    return symbol


def _boxes(values: Sequence[Sequence[float | int]], label: str):
    if not values:
        raise ValueError(f"{label} must be nonempty")
    flat: list[float] = []
    ids: list[int] = []
    for index, row in enumerate(values):
        if len(row) != 5:
            raise ValueError(f"{label}[{index}] must be (x0,y0,x1,y1,id)")
        x0, y0, x1, y1 = map(float, row[:4])
        item_id = int(row[4])
        if not all(math.isfinite(item) for item in (x0, y0, x1, y1)) \
                or x0 > x1 or y0 > y1 or not 0 <= item_id <= (1 << 32) - 1:
            raise ValueError(f"{label}[{index}] is invalid")
        flat.extend((x0, y0, x1, y1))
        ids.append(item_id)
    return (
        (ctypes.c_float * len(flat))(*flat),
        (ctypes.c_uint32 * len(ids))(*ids),
    )


def run_bounded_relation_callback(
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    executable: VerifiedBoundedRelationExecutable,
    *,
    any_hit_proof_authority,
    indexed_boxes: Sequence[Sequence[float | int]],
    source_boxes: Sequence[Sequence[float | int]],
    expected_rows: Sequence[Sequence[int]] | None = None,
    library: object | None = None,
    native_library_path: str | Path | None = None,
) -> V4BoundedRelationResult:
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
    source_native, source_ids = _boxes(source_boxes, "source_boxes")
    capacity = contract.capacity
    row_storage = (ctypes.c_uint32 * (capacity * 2))()
    raw_count = ctypes.c_uint64()
    overflowed = ctypes.c_uint32()
    statuses = (_Status * (len(source_boxes) + len(indexed_boxes)))()
    counters = (ctypes.c_uint64 * 7)()
    if library is None:
        from . import optix_runtime
        library = optix_runtime._load_optix_library()
    native_path = _native_path(library, native_library_path)
    native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
    if native_sha != fresh.physical.target.native_sha256:
        raise RuntimeError("executed native bytes do not match target authority")
    symbol = _configure(library)
    error = ctypes.create_string_buffer(16384)
    audit = OptixTraversalAuditSession.open(library=library)
    try:
        status = int(symbol(
            composed_ptx.encode("utf-8"),
            indexed_native, indexed_ids, len(indexed_boxes),
            source_native, source_ids, len(source_boxes),
            float(contract.minimum_overlap_f32), capacity,
            ctypes.byref(raw_count), ctypes.byref(overflowed), row_storage,
            statuses, counters, error, len(error)))
        if status:
            raise RuntimeError(
                error.value.decode("utf-8", errors="replace")
                or f"bounded-relation native status {status}")
        status_rows = tuple(
            {name: int(getattr(item, name)) for name, _ in _Status._fields_}
            for item in statuses)
        if any(item["first_error_claimed"] or item["error_code"]
               for item in status_rows):
            raise RuntimeError("bounded-relation returned nonzero device status")
        counter_rows = tuple(int(item) for item in counters)
        launch_count = len(source_boxes) + len(indexed_boxes)
        if counter_rows[1] != launch_count or counter_rows[6] != launch_count \
                or counter_rows[4] + counter_rows[5] != launch_count:
            raise RuntimeError(
                f"bounded-relation lifecycle is incomplete: {counter_rows!r}")
        stored = min(int(raw_count.value), capacity)
        raw_rows = tuple(
            (int(row_storage[index * 2]), int(row_storage[index * 2 + 1]))
            for index in range(stored))
        rows = materialize_bounded_relation(
            raw_rows, capacity=capacity,
            duplicate_policy=fresh.schema.duplicate_policy,
            observed_raw_count=int(raw_count.value),
            overflowed=bool(overflowed.value))
        if expected_rows is not None:
            normalized_expected = tuple(
                sorted((int(row[0]), int(row[1])) for row in expected_rows))
            if rows != normalized_expected:
                raise RuntimeError(
                    f"bounded-relation output mismatch: {rows!r} != "
                    f"{normalized_expected!r}")
        output_sha = _digest(rows)
        receipt = audit.finish(
            semantic_digest=_digest({
                "authority": fresh.authority_nonce,
                "contract": contract.contract_sha256,
                "abi": abi.abi_sha256,
                "composed_ptx": hashlib.sha256(composed_ptx.encode()).hexdigest(),
                "native": native_sha,
            }),
            output_digest=output_sha,
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
            expected_program_bundles=(
                "v4_custom_aabb_bounded_relation_composed",),
        )
    except Exception:
        audit.abort()
        raise
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("bounded relation did not produce bound OptiX traversal")
    return V4BoundedRelationResult(
        rows=rows,
        raw_rows=raw_rows,
        raw_event_count=int(raw_count.value),
        duplicate_count=int(raw_count.value) - len(rows),
        role_counters=counter_rows,
        launch_status=status_rows,
        traversal_receipt=receipt,
        output_sha256=output_sha,
        composed_ptx_sha256=hashlib.sha256(composed_ptx.encode()).hexdigest(),
        native_library_sha256=native_sha,
    )


__all__ = ["V4BoundedRelationResult", "run_bounded_relation_callback"]
