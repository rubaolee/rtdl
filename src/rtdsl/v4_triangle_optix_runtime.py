"""Fail-closed one-shot runtime for the trusted V4 triangle wrapper."""

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
from .v4_callback_abi import CompiledCallbackAbi, verify_compiled_callback_abi
from .v4_triangle_optix_compiler import (
    VerifiedTriangleExecutable,
    consume_verified_triangle_executable,
)
from .v4_typed_physical_schema import (
    BufferAccess,
    BufferSemantic,
    CanonicalPhysicalPlan,
    PhysicalBufferBinding,
    VerifiedPhysicalSchemaAuthority,
    default_reference_templates,
    lower_canonical_reference_plan,
    verify_buffer_bindings,
    verify_reference_triangle_contents,
    verify_typed_physical_schema,
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
class V4TriangleCallbackResult:
    output: object
    hit_observations: tuple[dict[str, int | float | None], ...]
    role_counters: tuple[int, ...]
    launch_status: tuple[dict[str, int], ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    composed_ptx_sha256: str
    native_library_sha256: str
    buffer_binding_sha256: str


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _native_path(library: object, explicit: str | Path | None) -> Path:
    candidate = explicit
    if candidate is None:
        candidate = os.environ.get("RTDL_OPTIX_LIB")
    if candidate is None:
        candidate = getattr(library, "_name", None)
    if not candidate:
        raise RuntimeError("exact native library path is required")
    path = Path(candidate).resolve()
    if not path.is_file():
        raise RuntimeError("exact native library bytes are unavailable")
    return path


def _fresh_authority(
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
) -> VerifiedPhysicalSchemaAuthority:
    orientation = authority.triangle_orientation_authority
    if orientation is None:
        raise RuntimeError("live triangle-orientation authority is required")
    fresh = verify_typed_physical_schema(
        authority.callback,
        authority.schema,
        target=authority.target,
        orientation_authorities={orientation.authority_sha256: orientation},
    )
    if fresh != authority:
        raise RuntimeError("typed physical authority does not rederive")
    expected_plan = lower_canonical_reference_plan(
        fresh, default_reference_templates())
    if plan != expected_plan or plan.executable:
        raise RuntimeError("exact non-executable Goal5755 reference plan is required")
    verify_compiled_callback_abi(
        abi, fresh.callback, physical_schema_authority=fresh)
    return fresh


def _bindings(
    authority: VerifiedPhysicalSchemaAuthority,
    *,
    vertex_count: int,
    primitive_count: int,
    query_count: int,
    maximum_index: int,
) -> tuple[PhysicalBufferBinding, ...]:
    counts = {
        BufferSemantic.VERTEX_POSITIONS: vertex_count,
        BufferSemantic.TRIANGLE_INDICES: primitive_count,
        BufferSemantic.PRIMITIVE_FRONT_VALUE: primitive_count,
        BufferSemantic.PRIMITIVE_BACK_VALUE: primitive_count,
        BufferSemantic.QUERY_INPUT: query_count,
        BufferSemantic.OUTPUT_VALUE: query_count,
        BufferSemantic.STATUS: 1,
    }
    rows = tuple(
        PhysicalBufferBinding(
            semantic=field.semantic,
            element_count=counts[field.semantic],
            device_id=0,
            stream_id=0,
            owner_nonce=authority.authority_nonce,
            mutation_epoch=0,
            alignment_bytes=field.alignment_bytes,
            contiguous=True,
            writable=field.access is not BufferAccess.READ_ONLY,
            maximum_index=(
                maximum_index
                if field.semantic is BufferSemantic.TRIANGLE_INDICES
                else None
            ),
        )
        for field in authority.schema.buffers
    )
    verify_buffer_bindings(authority.schema, rows)
    return rows


def _configure(library: object):
    symbol = getattr(
        library, "rtdl_optix_v4_run_builtin_triangle_callback_v1", None)
    if symbol is None:
        raise RuntimeError("native library lacks Goal5756 triangle callback ABI")
    symbol.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(_Status),
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    symbol.restype = ctypes.c_int
    return symbol


def run_builtin_triangle_callback(
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
    executable: VerifiedTriangleExecutable,
    *,
    vertices: Sequence[Sequence[float]],
    triangles: Sequence[Sequence[int]],
    front_values: Sequence[int],
    back_values: Sequence[int],
    queries: Sequence[tuple[Sequence[float], Sequence[float], float]],
    expected_output: Sequence[tuple[int, int, int]] | None = None,
    library: object | None = None,
    native_library_path: str | Path | None = None,
) -> V4TriangleCallbackResult:
    """Execute exact composed PTX against one verified built-in-triangle plan."""

    if len(vertices) == 0 or len(triangles) == 0 or len(queries) == 0:
        raise ValueError("vertices, triangles, and queries are required")
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
            if original.ndim != 1 or original.dtype.kind not in "iu" \
                    or (original.dtype.kind == "i" and bool((original < 0).any())) \
                    or int(original.max(initial=0)) > 0xFFFFFFFF:
                raise ValueError(f"{label} metadata must be u32")
        maximum_index = int(triangles_array.max(initial=0))
        numpy_columns = True
    else:
        if any(not 0 <= int(value) <= 0xFFFFFFFF
               for value in (*front_values, *back_values)):
            raise ValueError("front/back metadata must be u32")
        maximum_index = max(int(value) for triangle in triangles for value in triangle)
    bindings = _bindings(
        fresh,
        vertex_count=len(vertices),
        primitive_count=len(triangles),
        query_count=len(queries),
        maximum_index=maximum_index,
    )
    binding_digest = _digest([
        {
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
        }
        for item in bindings
    ])

    if numpy_columns:
        vertex_flat = vertices_array.reshape(-1)
        index_flat = triangles_array.reshape(-1)
    else:
        vertex_flat = [float(value) for row in vertices for value in row]
        index_flat = [int(value) for row in triangles for value in row]
    numpy_queries = _np is not None and isinstance(queries, _np.ndarray)
    if numpy_queries:
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
    else:
        origin_flat: list[float] = []
        direction_flat: list[float] = []
        tmax_values: list[float] = []
        for index, (origin, direction, tmax) in enumerate(queries):
            if len(origin) != 3 or len(direction) != 3:
                raise ValueError(f"query {index} must have vec3 origin/direction")
            values = [float(value) for value in (*origin, *direction, tmax)]
            if not all(math.isfinite(value) for value in values) or float(tmax) <= 0.0:
                raise ValueError(f"query {index} is nonfinite or has invalid tmax")
            if all(float(value) == 0.0 for value in direction):
                raise ValueError(f"query {index} has a zero direction")
            origin_flat.extend(float(value) for value in origin)
            direction_flat.extend(float(value) for value in direction)
            tmax_values.append(float(tmax))

    if numpy_columns:
        vertices_native = vertices_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        indices_native = triangles_array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
        front_native = front_array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
        back_native = back_array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
    else:
        vertices_native = (ctypes.c_float * len(vertex_flat))(*vertex_flat)
        indices_native = (ctypes.c_uint32 * len(index_flat))(*index_flat)
        front_native = (ctypes.c_uint32 * len(front_values))(*map(int, front_values))
        back_native = (ctypes.c_uint32 * len(back_values))(*map(int, back_values))
    if numpy_queries:
        origins_native = origins_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        directions_native = directions_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        tmax_native = tmax_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    else:
        origins_native = (ctypes.c_float * len(origin_flat))(*origin_flat)
        directions_native = (ctypes.c_float * len(direction_flat))(*direction_flat)
        tmax_native = (ctypes.c_float * len(tmax_values))(*tmax_values)
    output_0 = (ctypes.c_uint32 * len(queries))()
    output_1 = (ctypes.c_uint32 * len(queries))()
    output_2 = (ctypes.c_uint32 * len(queries))()
    observed_primitive = (ctypes.c_uint32 * len(queries))()
    observed_hit_kind = (ctypes.c_uint32 * len(queries))()
    observed_barycentric_x = (ctypes.c_float * len(queries))()
    observed_barycentric_y = (ctypes.c_float * len(queries))()
    statuses = (_Status * len(queries))()
    counters = (ctypes.c_uint64 * 7)()

    if library is None:
        from . import optix_runtime
        library = optix_runtime._load_optix_library()
    native_path = _native_path(library, native_library_path)
    native_digest = hashlib.sha256(native_path.read_bytes()).hexdigest()
    if native_digest != fresh.target.native_sha256:
        raise RuntimeError("executed native bytes do not match target authority")
    symbol = _configure(library)
    error = ctypes.create_string_buffer(16384)
    session = OptixTraversalAuditSession.open(library=library)
    try:
        status = int(symbol(
            composed_ptx.encode("utf-8"),
            vertices_native, len(vertices), indices_native, len(triangles),
            front_native, back_native, origins_native, directions_native,
            tmax_native, len(queries), output_0, output_1, output_2,
            observed_primitive, observed_hit_kind,
            observed_barycentric_x, observed_barycentric_y,
            statuses, counters, error, len(error),
        ))
        if status:
            raise RuntimeError(
                error.value.decode("utf-8", errors="replace")
                or f"triangle callback native status {status}"
            )
        observed = tuple(
            (int(output_0[index]), int(output_1[index]), int(output_2[index]))
            for index in range(len(queries))
        )
        hit_observations = tuple({
            "primitive_index": (
                None if int(observed_primitive[index]) == 0xFFFFFFFF
                else int(observed_primitive[index])
            ),
            "hit_kind": (
                None if int(observed_hit_kind[index]) == 0xFFFFFFFF
                else int(observed_hit_kind[index])
            ),
            "barycentric_x": (
                None if int(observed_primitive[index]) == 0xFFFFFFFF
                else float(observed_barycentric_x[index])
            ),
            "barycentric_y": (
                None if int(observed_primitive[index]) == 0xFFFFFFFF
                else float(observed_barycentric_y[index])
            ),
        } for index in range(len(queries)))
        status_rows = tuple({
            "first_error_claimed": int(item.first_error_claimed),
            "error_code": int(item.error_code),
            "stage": int(item.stage),
            "role": int(item.role),
            "launch_index": int(item.launch_index),
            "error_site": int(item.error_site),
            "effect_tag": int(item.effect_tag),
            "nonce_word": int(item.nonce_word),
            "invocation_mask": int(item.invocation_mask),
        } for item in statuses)
        counter_rows = tuple(int(item) for item in counters)
        if any(item["first_error_claimed"] or item["error_code"] for item in status_rows):
            raise RuntimeError("triangle callback returned a nonzero device status")
        # Role tags are stable CallbackRole enum positions: make-ray=2,
        # closest-hit=5, miss=6, finalize=7.  Each query must traverse exactly
        # one of closest-hit/miss before finalize.
        if counter_rows[1] != len(queries) or counter_rows[6] != len(queries) \
                or counter_rows[4] + counter_rows[5] != len(queries):
            raise RuntimeError("triangle callback role lifecycle is incomplete")
        required_mask = (1 << 1) | (1 << 6)
        terminal_mask = (1 << 4) | (1 << 5)
        if any(
            (item["invocation_mask"] & required_mask) != required_mask
            or (item["invocation_mask"] & terminal_mask) not in (1 << 4, 1 << 5)
            for item in status_rows
        ):
            raise RuntimeError("triangle callback per-launch role binding is incomplete")
        if expected_output is not None and observed != tuple(
            tuple(map(int, row)) for row in expected_output
        ):
            raise RuntimeError(
                f"triangle callback output mismatch: {observed!r} != {tuple(expected_output)!r}"
            )
        output_digest = _digest(observed)
        semantic_digest = _digest({
            "authority_nonce": fresh.authority_nonce,
            "schema_sha256": fresh.schema.schema_sha256,
            "plan_sha256": plan.plan_sha256,
            "abi_sha256": abi.abi_sha256,
            "composed_ptx_sha256": hashlib.sha256(composed_ptx.encode()).hexdigest(),
            "native_library_sha256": native_digest,
            "buffer_binding_sha256": binding_digest,
        })
        receipt = session.finish(
            semantic_digest=semantic_digest,
            output_digest=output_digest,
            route_identity="v4_builtin_triangle_callback_ir:four_role_composed_v1",
            expected_program_bundles=(
                "v4_builtin_triangle_callback_ir_four_role_composed",
            ),
        )
    except Exception:
        session.abort()
        raise
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("triangle callback did not produce bound OptiX traversal")
    return V4TriangleCallbackResult(
        output=observed,
        hit_observations=hit_observations,
        role_counters=counter_rows,
        launch_status=status_rows,
        traversal_receipt=receipt,
        output_sha256=output_digest,
        composed_ptx_sha256=hashlib.sha256(composed_ptx.encode()).hexdigest(),
        native_library_sha256=native_digest,
        buffer_binding_sha256=binding_digest,
    )


__all__ = ["V4TriangleCallbackResult", "run_builtin_triangle_callback"]
