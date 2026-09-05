"""One-shot functional runtime for the Goal5759 triangle-reduction target."""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_callback_abi import CompiledCallbackAbi
from .v4_triangle_reduction import (
    CompiledTriangleReductionContract,
    MetadataDomain,
    ReducerAlgebra,
    ReducerSourceKind,
    VerifiedTriangleReductionAuthority,
    compile_triangle_reduction_abi,
    compile_triangle_reduction_contract,
    execute_checked_reducer,
    verify_triangle_reduction_schema,
)
from .v4_triangle_reduction_optix_compiler import (
    VerifiedTriangleReductionExecutable,
    consume_verified_triangle_reduction_executable,
)


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
class V4TriangleReductionResult:
    reduced_output: int | tuple[tuple[tuple[int, ...], int], ...]
    per_ray_u64: Sequence[int]
    raw_reducer_rows: Sequence[Mapping[str, int]]
    role_counters: tuple[int, ...]
    launch_status: Sequence[Mapping[str, int]]
    traversal_receipt: Mapping[str, object]
    output_sha256: str
    composed_ptx_sha256: str
    native_library_sha256: str


@lru_cache(maxsize=4096)
def _int_digest(value: int) -> str:
    return hashlib.sha256(str(value).encode("ascii")).hexdigest()


def _digest(value: object) -> str:
    if type(value) is int:
        return _int_digest(value)
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _native_path(library: object, explicit: str | Path | None) -> Path:
    candidate = explicit or os.environ.get("RTDL_OPTIX_LIB") or getattr(library, "_name", None)
    if not candidate:
        raise RuntimeError("exact native library path is required")
    path = Path(candidate).resolve()
    if not path.is_file():
        raise RuntimeError("exact native library bytes are unavailable")
    return path


def _configure(library: object):
    symbol = getattr(
        library, "rtdl_optix_v4_run_builtin_triangle_reduction_callback_v1", None)
    if symbol is None:
        raise RuntimeError("native library lacks Goal5759 triangle-reduction ABI")
    symbol.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(_Status),
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    symbol.restype = ctypes.c_int
    return symbol


def _typed_metadata(
    authority: VerifiedTriangleReductionAuthority,
    metadata: Mapping[str, Sequence[int]],
    *,
    primitive_count: int,
    query_count: int,
):
    expected = {item.semantic_id for item in authority.schema.metadata_channels}
    if set(metadata) != expected:
        raise ValueError(f"metadata identities differ: {sorted(set(metadata) ^ expected)!r}")
    primitive_u64 = primitive_i64 = primitive_u32 = None
    normalized: dict[str, tuple[int, ...]] = {}
    for channel in authority.schema.metadata_channels:
        values = tuple(int(item) for item in metadata[channel.semantic_id])
        count = primitive_count if channel.domain is MetadataDomain.PRIMITIVE else query_count
        if len(values) != count:
            raise ValueError(f"metadata cardinality mismatch: {channel.semantic_id}")
        if channel.scalar.value == "u64":
            if any(not 0 <= item <= (1 << 64) - 1 for item in values):
                raise ValueError(f"u64 metadata out of range: {channel.semantic_id}")
            array = (ctypes.c_uint64 * count)(*values)
            if channel.domain is MetadataDomain.PRIMITIVE:
                if primitive_u64 is not None:
                    raise ValueError("one primitive u64 channel is supported by M1 target")
                primitive_u64 = array
        elif channel.scalar.value == "i64":
            if any(not -(1 << 63) <= item <= (1 << 63) - 1 for item in values):
                raise ValueError(f"i64 metadata out of range: {channel.semantic_id}")
            array = (ctypes.c_int64 * count)(*values)
            if channel.domain is MetadataDomain.PRIMITIVE:
                if primitive_i64 is not None:
                    raise ValueError("one primitive i64 channel is supported by M1 target")
                primitive_i64 = array
        elif channel.scalar.value == "u32":
            if any(not 0 <= item <= (1 << 32) - 1 for item in values):
                raise ValueError(f"u32 metadata out of range: {channel.semantic_id}")
            array = (ctypes.c_uint32 * count)(*values)
            if channel.domain is MetadataDomain.PRIMITIVE:
                if primitive_u32 is not None:
                    raise ValueError("one primitive u32 channel is supported by M1 target")
                primitive_u32 = array
        else:  # pragma: no cover - verified schema defense
            raise AssertionError(channel.scalar)
        normalized[channel.semantic_id] = values
    return normalized, primitive_u64, primitive_i64, primitive_u32


def run_builtin_triangle_reduction_callback(
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
    executable: VerifiedTriangleReductionExecutable,
    *,
    any_hit_proof_authority,
    vertices: Sequence[Sequence[float]],
    triangles: Sequence[Sequence[int]],
    queries: Sequence[tuple[Sequence[float], Sequence[float], float]],
    metadata: Mapping[str, Sequence[int]],
    event_capacity: int,
    expected_reduced_output=None,
    library: object | None = None,
    native_library_path: str | Path | None = None,
) -> V4TriangleReductionResult:
    if not vertices or not triangles or not queries or event_capacity <= 0:
        raise ValueError("nonempty geometry/queries and positive event capacity required")
    fresh = verify_triangle_reduction_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority \
            or compile_triangle_reduction_abi(
                fresh, any_hit_proof_authority=any_hit_proof_authority) != abi \
            or compile_triangle_reduction_contract(
                fresh, abi_sha256=abi.abi_sha256) != contract:
        raise RuntimeError("triangle-reduction authority/ABI/contract drift")
    composed_ptx = consume_verified_triangle_reduction_executable(
        executable, fresh, contract, abi,
        any_hit_proof_authority=any_hit_proof_authority)

    vertex_flat = [float(value) for row in vertices for value in row]
    index_flat = [int(value) for row in triangles for value in row]
    if any(len(row) != 3 for row in vertices) or any(len(row) != 3 for row in triangles):
        raise ValueError("vertices and triangles must have arity three")
    if not all(math.isfinite(item) for item in vertex_flat):
        raise ValueError("vertices must be finite")
    if any(not 0 <= item < len(vertices) for item in index_flat):
        raise ValueError("triangle index is outside vertex domain")
    origin_flat: list[float] = []
    direction_flat: list[float] = []
    tmax_values: list[float] = []
    for index, (origin, direction, tmax) in enumerate(queries):
        if len(origin) != 3 or len(direction) != 3:
            raise ValueError(f"query {index} must have vec3 origin/direction")
        values = [float(item) for item in (*origin, *direction, tmax)]
        if not all(math.isfinite(item) for item in values) or float(tmax) <= 0 \
                or all(float(item) == 0 for item in direction):
            raise ValueError(f"query {index} is invalid")
        origin_flat.extend(map(float, origin))
        direction_flat.extend(map(float, direction))
        tmax_values.append(float(tmax))
    normalized, primitive_u64, primitive_i64, primitive_u32 = _typed_metadata(
        fresh, metadata, primitive_count=len(triangles), query_count=len(queries))

    vertices_native = (ctypes.c_float * len(vertex_flat))(*vertex_flat)
    triangles_native = (ctypes.c_uint32 * len(index_flat))(*index_flat)
    origins_native = (ctypes.c_float * len(origin_flat))(*origin_flat)
    directions_native = (ctypes.c_float * len(direction_flat))(*direction_flat)
    tmax_native = (ctypes.c_float * len(tmax_values))(*tmax_values)
    per_ray = (ctypes.c_uint64 * len(queries))()
    event_count = ctypes.c_uint64()
    event_query = (ctypes.c_uint32 * event_capacity)()
    event_primitive = (ctypes.c_uint32 * event_capacity)()
    event_stable = (ctypes.c_uint64 * event_capacity)()
    event_signed = (ctypes.c_int64 * event_capacity)()
    event_include = (ctypes.c_uint32 * event_capacity)()
    statuses = (_Status * len(queries))()
    counters = (ctypes.c_uint64 * 7)()
    if library is None:
        from . import optix_runtime
        library = optix_runtime._load_optix_library()
    native_path = _native_path(library, native_library_path)
    native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
    if native_sha != fresh.target.native_sha256:
        raise RuntimeError("executed native bytes do not match target authority")
    symbol = _configure(library)
    error = ctypes.create_string_buffer(16384)
    audit = OptixTraversalAuditSession.open(library=library)
    try:
        status = int(symbol(
            composed_ptx.encode("utf-8"),
            vertices_native, len(vertices), triangles_native, len(triangles),
            origins_native, directions_native, tmax_native, len(queries),
            primitive_u64, primitive_i64, primitive_u32, event_capacity,
            per_ray, ctypes.byref(event_count), event_query, event_primitive,
            event_stable, event_signed, event_include, statuses, counters,
            error, len(error)))
        if status:
            raise RuntimeError(
                error.value.decode("utf-8", errors="replace")
                or f"triangle-reduction native status {status}")
        status_rows = tuple({name: int(getattr(item, name)) for name, _ in _Status._fields_}
                            for item in statuses)
        counter_rows = tuple(int(item) for item in counters)
        if any(item["first_error_claimed"] or item["error_code"] for item in status_rows):
            raise RuntimeError("triangle-reduction returned a nonzero device status")
        # make-ray=2, any-hit=4, miss=6, finalize=7.  Every launch must have
        # make-ray/miss/finalize; any-hit is required globally for this route.
        if counter_rows[1] != len(queries) or counter_rows[5] != len(queries) \
                or counter_rows[6] != len(queries) or counter_rows[3] <= 0:
            raise RuntimeError(
                f"triangle-reduction role lifecycle is incomplete: {counter_rows!r}")
        required_mask = (1 << 1) | (1 << 5) | (1 << 6)
        if any((item["invocation_mask"] & required_mask) != required_mask
               for item in status_rows):
            raise RuntimeError("triangle-reduction per-launch binding is incomplete")

        per_ray_values = tuple(int(item) for item in per_ray)
        rows: list[dict[str, int]] = []
        reducer = fresh.schema.reducer
        if reducer.algebra is ReducerAlgebra.CHECKED_KEYED_I64_SUM:
            for index in range(int(event_count.value)):
                rows.append({
                    "launch_index": int(event_query[index]),
                    "primitive_index": int(event_primitive[index]),
                    "primitive.stable_id": int(event_stable[index]),
                    "primitive.signed_value": int(event_signed[index]),
                    "primitive.include": int(event_include[index]),
                })
            if sum(per_ray_values) != len(rows):
                raise RuntimeError("accepted event count disagrees with per-ray payload")
        else:
            value_field = reducer.value_source.output_field
            assert reducer.value_source.kind is ReducerSourceKind.PER_RAY_OUTPUT
            for index, value in enumerate(per_ray_values):
                row = {"launch_index": index, value_field: value}
                if reducer.multiplicand_source is not None:
                    semantic = reducer.multiplicand_source.semantic_id
                    assert semantic is not None
                    row[semantic] = normalized[semantic][index]
                rows.append(row)
        reduced = execute_checked_reducer(reducer, rows)
        if expected_reduced_output is not None and reduced != expected_reduced_output:
            raise RuntimeError(
                f"triangle-reduction output mismatch: {reduced!r} != {expected_reduced_output!r}")
        output_sha = _digest(reduced)
        receipt = audit.finish(
            semantic_digest=_digest({
                "authority": fresh.authority_nonce,
                "contract": contract.contract_sha256,
                "abi": abi.abi_sha256,
                "composed_ptx": hashlib.sha256(composed_ptx.encode()).hexdigest(),
                "native": native_sha,
            }),
            output_digest=output_sha,
            route_identity="v4_builtin_triangle_callback_ir:checked_reduction_v1",
            expected_program_bundles=(
                "v4_builtin_triangle_checked_reduction_composed",),
        )
    except Exception:
        audit.abort()
        raise
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("triangle-reduction did not produce bound OptiX traversal")
    return V4TriangleReductionResult(
        reduced_output=reduced,
        per_ray_u64=per_ray_values,
        raw_reducer_rows=tuple(rows),
        role_counters=counter_rows,
        launch_status=status_rows,
        traversal_receipt=receipt,
        output_sha256=output_sha,
        composed_ptx_sha256=hashlib.sha256(composed_ptx.encode()).hexdigest(),
        native_library_sha256=native_sha,
    )


__all__ = ["V4TriangleReductionResult", "run_builtin_triangle_reduction_callback"]
