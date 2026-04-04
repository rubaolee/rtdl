"""optix_runtime.py — NVIDIA/OptiX backend for rtdl.

Public API mirrors embree_runtime.py:
  run_optix(kernel_fn_or_compiled, **inputs)       → tuple[dict, ...]
  prepare_optix(kernel_fn_or_compiled)              → PreparedOptixKernel
  optix_version()                                   → tuple[int, int, int]

All six workloads are supported:
  segment_intersection, point_in_polygon, overlay_compose,
  ray_triangle_hit_count, segment_polygon_hitcount, point_nearest_segment

Data marshaling: inputs are double-precision on the Python/CPU side (matching
the Embree backend); the C++/CUDA layer converts to float32 before uploading to
the GPU and converts back to float64 in output records.

Library search order (first found wins):
  1. $RTDL_OPTIX_LIB environment variable (full path to the .so/.dylib)
  2. build/librtdl_optix.so  (relative to the repository root)
  3. librtdl_optix.so / librtdl_optix.dylib on LD_LIBRARY_PATH/DYLD_LIBRARY_PATH
"""

from __future__ import annotations

import ctypes
import ctypes.util
import functools
import os
import platform
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

from .embree_runtime import _RtdlSegment
from .embree_runtime import _RtdlPoint
from .embree_runtime import _RtdlPolygonRef
from .embree_runtime import _RtdlTriangle
from .embree_runtime import _RtdlRay2D
from .embree_runtime import PackedPoints
from .embree_runtime import PackedPolygons
from .embree_runtime import PackedRays
from .embree_runtime import PackedSegments
from .embree_runtime import PackedTriangles
from .ir import CompiledKernel
from .runtime import _normalize_records
from .runtime import _resolve_kernel
from .runtime import _validate_kernel_for_cpu


_PREPARED_CACHE_MAX_ENTRIES = 8
_prepared_optix_execution_cache: OrderedDict[tuple[object, ...], "PreparedOptixExecution"] = OrderedDict()


# ─────────────────────────────────────────────────────────────────────────────
# ctypes struct definitions  (must match rtdl_optix.cpp)
# Input geometry structs are imported from embree_runtime (same memory layout,
# shared so that Packed* objects from either backend are interchangeable).
# ─────────────────────────────────────────────────────────────────────────────

class _RtdlLsiRow(ctypes.Structure):
    _fields_ = [
        ("left_id",              ctypes.c_uint32),
        ("right_id",             ctypes.c_uint32),
        ("intersection_point_x", ctypes.c_double),
        ("intersection_point_y", ctypes.c_double),
    ]


class _RtdlPipRow(ctypes.Structure):
    _fields_ = [
        ("point_id",   ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
        ("contains",   ctypes.c_uint32),
    ]


class _RtdlOverlayRow(ctypes.Structure):
    _fields_ = [
        ("left_polygon_id",  ctypes.c_uint32),
        ("right_polygon_id", ctypes.c_uint32),
        ("requires_lsi",     ctypes.c_uint32),
        ("requires_pip",     ctypes.c_uint32),
    ]


class _RtdlRayHitCountRow(ctypes.Structure):
    _fields_ = [
        ("ray_id",    ctypes.c_uint32),
        ("hit_count", ctypes.c_uint32),
    ]


class _RtdlSegmentPolygonHitCountRow(ctypes.Structure):
    _fields_ = [
        ("segment_id", ctypes.c_uint32),
        ("hit_count",  ctypes.c_uint32),
    ]


class _RtdlPointNearestSegmentRow(ctypes.Structure):
    _fields_ = [
        ("point_id",   ctypes.c_uint32),
        ("segment_id", ctypes.c_uint32),
        ("distance",   ctypes.c_double),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Row-view wrapper (RAII-style, mirrors EmbreeRowView)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class OptixRowView:
    library: object
    rows_ptr: object
    row_count: int
    row_type: object
    field_names: tuple
    _closed: bool = False

    def close(self) -> None:
        if not self._closed:
            self.library.rtdl_optix_free_rows(self.rows_ptr)
            self._closed = True

    def __len__(self) -> int:
        return self.row_count

    def to_dict_rows(self) -> tuple:
        return tuple(
            {field: getattr(self.rows_ptr[i], field) for field in self.field_names}
            for i in range(self.row_count)
        )

    def to_tuple_rows(self) -> tuple:
        return tuple(
            tuple(getattr(self.rows_ptr[i], field) for field in self.field_names)
            for i in range(self.row_count)
        )

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Prepared-kernel API
# ─────────────────────────────────────────────────────────────────────────────

class PreparedOptixKernel:
    """Compiled-once handle for the OptiX backend.  Mirrors PreparedEmbreeKernel."""

    _SUPPORTED_PREDICATES = {
        "segment_intersection",
        "point_in_polygon",
        "overlay_compose",
        "ray_triangle_hit_count",
        "segment_polygon_hitcount",
        "point_nearest_segment",
    }

    def __init__(self, kernel_fn_or_compiled):
        compiled = _resolve_kernel(kernel_fn_or_compiled)
        _validate_kernel_for_cpu(compiled)
        self.compiled = compiled
        self.library = _load_optix_library()
        self.expected_inputs = {item.name: item for item in compiled.inputs}
        predicate = compiled.refine_op.predicate.name
        if predicate not in self._SUPPORTED_PREDICATES:
            raise ValueError(
                f"unsupported predicate for OptiX backend: {predicate!r}"
            )
        self.predicate_name = predicate

    def bind(self, **inputs) -> PreparedOptixExecution:
        missing    = [n for n in self.expected_inputs if n not in inputs]
        unexpected = [n for n in inputs if n not in self.expected_inputs]
        if missing:
            raise ValueError(f"missing RTDL OptiX inputs: {', '.join(sorted(missing))}")
        if unexpected:
            raise ValueError(f"unexpected RTDL OptiX inputs: {', '.join(sorted(unexpected))}")
        packed = {
            name: _pack_for_geometry(self.expected_inputs[name].geometry.name, payload)
            for name, payload in inputs.items()
        }
        return PreparedOptixExecution(self.compiled, self.library, packed)

    def run(self, **inputs) -> tuple:
        return self.bind(**inputs).run()


@dataclass(frozen=True)
class PreparedOptixExecution:
    compiled: CompiledKernel
    library: object
    packed_inputs: dict

    def run_raw(self) -> OptixRowView:
        pred = self.compiled.refine_op.predicate.name
        dispatch = {
            "segment_intersection":   _call_lsi_optix_packed,
            "point_in_polygon":       _call_pip_optix_packed,
            "overlay_compose":        _call_overlay_optix_packed,
            "ray_triangle_hit_count": _call_ray_hitcount_optix_packed,
            "segment_polygon_hitcount": _call_segment_polygon_hitcount_optix_packed,
            "point_nearest_segment":  _call_point_nearest_segment_optix_packed,
        }
        fn = dispatch.get(pred)
        if fn is None:
            raise ValueError(f"unsupported prepared OptiX predicate: {pred!r}")
        return fn(self.compiled, self.packed_inputs, self.library)

    def run(self) -> tuple:
        rows = self.run_raw()
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()


def prepare_optix(kernel_fn_or_compiled) -> PreparedOptixKernel:
    return PreparedOptixKernel(kernel_fn_or_compiled)


def clear_optix_prepared_cache() -> None:
    _prepared_optix_execution_cache.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Public run_optix
# ─────────────────────────────────────────────────────────────────────────────

def run_optix(kernel_fn_or_compiled, *, result_mode: str = "dict", **inputs):
    """Execute a compiled kernel on the NVIDIA OptiX backend.

    Parameters
    ----------
    kernel_fn_or_compiled:
        A function decorated with ``@rt.kernel`` or a ``CompiledKernel``.
    result_mode:
        ``"dict"`` (default) — returns ``tuple[dict[str, object], ...]``
        ``"raw"`` — returns an ``OptixRowView`` (caller must call ``.close()``)
    **inputs:
        Geometry inputs; may be raw records or pre-packed ``Packed*`` objects.
    """
    compiled = _resolve_kernel(kernel_fn_or_compiled)
    _validate_kernel_for_cpu(compiled)
    expected_inputs = {item.name: item for item in compiled.inputs}

    missing    = [n for n in expected_inputs if n not in inputs]
    unexpected = [n for n in inputs if n not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL OptiX inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL OptiX inputs: {', '.join(sorted(unexpected))}")
    if result_mode not in {"dict", "raw"}:
        raise ValueError("OptiX result_mode must be 'dict' or 'raw'")

    prepared = _get_or_bind_prepared_optix_execution(compiled, expected_inputs, inputs)
    return prepared.run_raw() if result_mode == "raw" else prepared.run()


def _get_or_bind_prepared_optix_execution(compiled: CompiledKernel, expected_inputs, inputs) -> PreparedOptixExecution:
    cache_key = _prepared_execution_cache_key(compiled, expected_inputs, inputs)
    if cache_key is None:
        return prepare_optix(compiled).bind(**inputs)
    cached = _prepared_optix_execution_cache.get(cache_key)
    if cached is not None:
        _prepared_optix_execution_cache.move_to_end(cache_key)
        return cached
    normalized_inputs = {
        name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
        for name, payload in inputs.items()
    }
    prepared = prepare_optix(compiled).bind(**normalized_inputs)
    _prepared_optix_execution_cache[cache_key] = prepared
    if len(_prepared_optix_execution_cache) > _PREPARED_CACHE_MAX_ENTRIES:
        _prepared_optix_execution_cache.popitem(last=False)
    return prepared


def _prepared_execution_cache_key(compiled: CompiledKernel, expected_inputs, inputs) -> tuple[object, ...] | None:
    canonical_inputs = []
    for name in sorted(expected_inputs):
        geometry_name = expected_inputs[name].geometry.name
        payload = inputs[name]
        if _is_packed_for_geometry(geometry_name, payload):
            return None
        normalized = _normalize_records(name, geometry_name, payload)
        canonical_inputs.append((name, normalized))
    predicate = compiled.refine_op.predicate
    predicate_options = tuple(sorted(predicate.options.items()))
    input_signature = tuple(
        (
            item.name,
            item.geometry.name,
            item.layout.name,
            item.role,
        )
        for item in compiled.inputs
    )
    return (
        compiled.name,
        compiled.backend,
        compiled.precision,
        predicate.name,
        predicate_options,
        input_signature,
        tuple(compiled.emit_op.fields),
        tuple(canonical_inputs),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Version query
# ─────────────────────────────────────────────────────────────────────────────

def optix_version() -> tuple:
    """Return (major, minor, patch) of the OptiX SDK linked into the library."""
    lib = _load_optix_library()
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    _check_status(lib.rtdl_optix_get_version(
        ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch)))
    return major.value, minor.value, patch.value


# ─────────────────────────────────────────────────────────────────────────────
# Packing helpers  (same interface as embree_runtime.py)
# ─────────────────────────────────────────────────────────────────────────────

def pack_segments(records=None, *, ids=None, x0=None, y0=None, x1=None, y1=None) -> PackedSegments:
    if records is not None:
        norm = _normalize_records("segments", "segments", records)
        arr  = (_RtdlSegment * len(norm))(*[
            _RtdlSegment(r.id, r.x0, r.y0, r.x1, r.y1) for r in norm
        ])
        return PackedSegments(records=arr, count=len(norm))
    ids_l = _coerce_list("ids", ids)
    x0_l  = _coerce_list("x0",  x0)
    y0_l  = _coerce_list("y0",  y0)
    x1_l  = _coerce_list("x1",  x1)
    y1_l  = _coerce_list("y1",  y1)
    n = _validate_equal_lengths("segments", ids_l, x0_l, y0_l, x1_l, y1_l)
    arr = (_RtdlSegment * n)(*[
        _RtdlSegment(int(ids_l[i]), float(x0_l[i]), float(y0_l[i]),
                     float(x1_l[i]), float(y1_l[i]))
        for i in range(n)
    ])
    return PackedSegments(records=arr, count=n)


def pack_points(records=None, *, ids=None, x=None, y=None) -> PackedPoints:
    if records is not None:
        norm = _normalize_records("points", "points", records)
        arr  = (_RtdlPoint * len(norm))(*[_RtdlPoint(r.id, r.x, r.y) for r in norm])
        return PackedPoints(records=arr, count=len(norm))
    ids_l = _coerce_list("ids", ids)
    x_l   = _coerce_list("x", x)
    y_l   = _coerce_list("y", y)
    n = _validate_equal_lengths("points", ids_l, x_l, y_l)
    arr = (_RtdlPoint * n)(*[
        _RtdlPoint(int(ids_l[i]), float(x_l[i]), float(y_l[i]))
        for i in range(n)
    ])
    return PackedPoints(records=arr, count=n)


def pack_polygons(records=None, *, ids=None, vertex_offsets=None,
                  vertex_counts=None, vertices_xy=None) -> PackedPolygons:
    if records is not None:
        norm = _normalize_records("polygons", "polygons", records)
        refs, verts = _encode_polygons(norm)
        return PackedPolygons(
            refs=refs, polygon_count=len(norm),
            vertices_xy=verts, vertex_xy_count=len(verts))
    ids_l  = _coerce_list("ids",            ids)
    off_l  = _coerce_list("vertex_offsets", vertex_offsets)
    cnt_l  = _coerce_list("vertex_counts",  vertex_counts)
    vxy_l  = _coerce_list("vertices_xy",    vertices_xy)
    n = _validate_equal_lengths("polygons", ids_l, off_l, cnt_l)
    if len(vxy_l) % 2 != 0:
        raise ValueError("vertices_xy must have an even number of values")
    refs_list = []
    for i in range(n):
        off = int(off_l[i]); cnt = int(cnt_l[i])
        if cnt < 3:
            raise ValueError("vertex_counts must be at least 3")
        if off < 0 or off + cnt > len(vxy_l) // 2:
            raise ValueError("polygon offsets/counts exceed vertices_xy")
        refs_list.append(_RtdlPolygonRef(int(ids_l[i]), off, cnt))
    ref_arr  = (_RtdlPolygonRef * n)(*refs_list)
    vert_arr = (ctypes.c_double * len(vxy_l))(*[float(v) for v in vxy_l])
    return PackedPolygons(refs=ref_arr, polygon_count=n,
                          vertices_xy=vert_arr, vertex_xy_count=len(vxy_l))


def pack_triangles(records=None, *, ids=None, x0=None, y0=None,
                   x1=None, y1=None, x2=None, y2=None) -> PackedTriangles:
    if records is not None:
        norm = _normalize_records("triangles", "triangles", records)
        arr  = (_RtdlTriangle * len(norm))(*[
            _RtdlTriangle(r.id, r.x0, r.y0, r.x1, r.y1, r.x2, r.y2) for r in norm
        ])
        return PackedTriangles(records=arr, count=len(norm))
    ids_l = _coerce_list("ids", ids)
    x0_l  = _coerce_list("x0",  x0);  y0_l  = _coerce_list("y0",  y0)
    x1_l  = _coerce_list("x1",  x1);  y1_l  = _coerce_list("y1",  y1)
    x2_l  = _coerce_list("x2",  x2);  y2_l  = _coerce_list("y2",  y2)
    n = _validate_equal_lengths("triangles", ids_l, x0_l, y0_l, x1_l, y1_l, x2_l, y2_l)
    arr = (_RtdlTriangle * n)(*[
        _RtdlTriangle(int(ids_l[i]), float(x0_l[i]), float(y0_l[i]),
                      float(x1_l[i]), float(y1_l[i]),
                      float(x2_l[i]), float(y2_l[i]))
        for i in range(n)
    ])
    return PackedTriangles(records=arr, count=n)


def pack_rays(records=None, *, ids=None, ox=None, oy=None,
              dx=None, dy=None, tmax=None) -> PackedRays:
    if records is not None:
        norm = _normalize_records("rays", "rays", records)
        arr  = (_RtdlRay2D * len(norm))(*[
            _RtdlRay2D(r.id, r.ox, r.oy, r.dx, r.dy, r.tmax) for r in norm
        ])
        return PackedRays(records=arr, count=len(norm))
    ids_l  = _coerce_list("ids",  ids)
    ox_l   = _coerce_list("ox",   ox);   oy_l   = _coerce_list("oy",   oy)
    dx_l   = _coerce_list("dx",   dx);   dy_l   = _coerce_list("dy",   dy)
    tmax_l = _coerce_list("tmax", tmax)
    n = _validate_equal_lengths("rays", ids_l, ox_l, oy_l, dx_l, dy_l, tmax_l)
    arr = (_RtdlRay2D * n)(*[
        _RtdlRay2D(int(ids_l[i]), float(ox_l[i]), float(oy_l[i]),
                   float(dx_l[i]), float(dy_l[i]), float(tmax_l[i]))
        for i in range(n)
    ])
    return PackedRays(records=arr, count=n)


# ─────────────────────────────────────────────────────────────────────────────
# Internal packed call helpers
# ─────────────────────────────────────────────────────────────────────────────

def _call_lsi_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    left  = packed[compiled.candidates.left.name]
    right = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlLsiRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_optix_run_lsi(
        left.records, left.count,
        right.records, right.count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlLsiRow,
        field_names=("left_id", "right_id",
                     "intersection_point_x", "intersection_point_y"))


def _call_pip_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    boundary_mode = compiled.refine_op.predicate.options.get("boundary_mode", "inclusive")
    if boundary_mode != "inclusive":
        raise ValueError("the OptiX PIP backend supports only boundary_mode='inclusive'")
    result_mode = compiled.refine_op.predicate.options.get("result_mode", "full_matrix")
    if result_mode not in {"full_matrix", "positive_hits"}:
        raise ValueError("the OptiX PIP backend supports only result_mode='full_matrix' or 'positive_hits'")
    points   = packed[compiled.candidates.left.name]
    polygons = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlPipRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_optix_run_pip(
        points.records, points.count,
        polygons.refs, polygons.polygon_count,
        polygons.vertices_xy, polygons.vertex_xy_count,
        1 if result_mode == "positive_hits" else 0,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlPipRow,
        field_names=("point_id", "polygon_id", "contains"))


def _call_overlay_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    left  = packed[compiled.candidates.left.name]
    right = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlOverlayRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_optix_run_overlay(
        left.refs, left.polygon_count,
        left.vertices_xy, left.vertex_xy_count,
        right.refs, right.polygon_count,
        right.vertices_xy, right.vertex_xy_count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlOverlayRow,
        field_names=("left_polygon_id", "right_polygon_id",
                     "requires_lsi", "requires_pip"))


def _call_ray_hitcount_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    rays      = packed[compiled.candidates.left.name]
    triangles = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_optix_run_ray_hitcount(
        rays.records, rays.count,
        triangles.records, triangles.count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlRayHitCountRow,
        field_names=("ray_id", "hit_count"))


def _call_segment_polygon_hitcount_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    segments = packed[compiled.candidates.left.name]
    polygons = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_optix_run_segment_polygon_hitcount(
        segments.records, segments.count,
        polygons.refs, polygons.polygon_count,
        polygons.vertices_xy, polygons.vertex_xy_count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlSegmentPolygonHitCountRow,
        field_names=("segment_id", "hit_count"))


def _call_point_nearest_segment_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    points   = packed[compiled.candidates.left.name]
    segments = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlPointNearestSegmentRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_optix_run_point_nearest_segment(
        points.records, points.count,
        segments.records, segments.count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlPointNearestSegmentRow,
        field_names=("point_id", "segment_id", "distance"))


# ─────────────────────────────────────────────────────────────────────────────
# Library loading
# ─────────────────────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _load_optix_library():
    lib_path = _find_optix_library()
    lib = ctypes.CDLL(str(lib_path))
    _register_argtypes(lib)
    return lib


def _find_optix_library() -> Path:
    # 1. Explicit env var
    env = os.environ.get("RTDL_OPTIX_LIB")
    if env:
        p = Path(env)
        if p.exists():
            return p
        raise FileNotFoundError(
            f"RTDL_OPTIX_LIB is set to {env!r} but the file does not exist")

    # 2. build/ in the repository root (two levels above this file)
    here = Path(__file__).resolve().parent
    repo_root = here.parent.parent
    suffix = ".dylib" if platform.system() == "Darwin" else ".so"
    candidate = repo_root / "build" / f"librtdl_optix{suffix}"
    if candidate.exists():
        return candidate

    # 3. System library path
    name = ctypes.util.find_library("rtdl_optix")
    if name:
        return Path(name)

    raise FileNotFoundError(
        "librtdl_optix not found.  "
        "Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib."
    )


def _register_argtypes(lib) -> None:
    lib.rtdl_optix_get_version.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.rtdl_optix_get_version.restype = ctypes.c_int

    lib.rtdl_optix_free_rows.argtypes = [ctypes.c_void_p]
    lib.rtdl_optix_free_rows.restype  = None

    lib.rtdl_optix_run_lsi.argtypes = [
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_lsi.restype = ctypes.c_int

    lib.rtdl_optix_run_pip.argtypes = [
        ctypes.POINTER(_RtdlPoint),      ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlPipRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_pip.restype = ctypes.c_int

    lib.rtdl_optix_run_overlay.argtypes = [
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlOverlayRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_overlay.restype = ctypes.c_int

    lib.rtdl_optix_run_ray_hitcount.argtypes = [
        ctypes.POINTER(_RtdlRay2D),      ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle),   ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_ray_hitcount.restype = ctypes.c_int

    lib.rtdl_optix_run_segment_polygon_hitcount.argtypes = [
        ctypes.POINTER(_RtdlSegment),    ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_segment_polygon_hitcount.restype = ctypes.c_int

    lib.rtdl_optix_run_point_nearest_segment.argtypes = [
        ctypes.POINTER(_RtdlPoint),   ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPointNearestSegmentRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_point_nearest_segment.restype = ctypes.c_int


# ─────────────────────────────────────────────────────────────────────────────
# Small internal utilities
# ─────────────────────────────────────────────────────────────────────────────

def _check_status(status: int, error=None) -> None:
    if status == 0:
        return
    msg = ""
    if error is not None:
        msg = error.value.decode("utf-8", errors="replace").strip()
    if not msg:
        msg = f"OptiX backend call failed with status {status}"
    raise RuntimeError(msg)


def _coerce_list(name: str, values):
    if values is None:
        raise ValueError(f"missing packed input array `{name}`")
    return list(values)


def _validate_equal_lengths(label: str, *columns) -> int:
    lengths = {len(c) for c in columns}
    if len(lengths) != 1:
        raise ValueError(f"packed {label} arrays must have identical lengths")
    return lengths.pop()


def _encode_polygons(polygons):
    refs, vertices = [], []
    offset = 0
    for poly in polygons:
        refs.append(_RtdlPolygonRef(poly.id, offset, len(poly.vertices)))
        for v in poly.vertices:
            vertices.extend([float(v[0]), float(v[1])])
        offset += len(poly.vertices)
    ref_arr  = (_RtdlPolygonRef * len(refs))(*refs)
    vert_arr = (ctypes.c_double * len(vertices))(*vertices) if vertices else (ctypes.c_double * 0)()
    return ref_arr, vert_arr


def _pack_for_geometry(geometry_name: str, payload):
    if geometry_name == "segments":
        return payload if isinstance(payload, PackedSegments)  else pack_segments(records=payload)
    if geometry_name == "points":
        return payload if isinstance(payload, PackedPoints)    else pack_points(records=payload)
    if geometry_name == "polygons":
        return payload if isinstance(payload, PackedPolygons)  else pack_polygons(records=payload)
    if geometry_name == "triangles":
        return payload if isinstance(payload, PackedTriangles) else pack_triangles(records=payload)
    if geometry_name == "rays":
        return payload if isinstance(payload, PackedRays)      else pack_rays(records=payload)
    raise ValueError(f"unsupported geometry type for OptiX backend: {geometry_name!r}")


def _is_packed_for_geometry(geometry_name: str, payload) -> bool:
    if geometry_name == "segments":
        return isinstance(payload, PackedSegments)
    if geometry_name == "points":
        return isinstance(payload, PackedPoints)
    if geometry_name == "polygons":
        return isinstance(payload, PackedPolygons)
    if geometry_name == "triangles":
        return isinstance(payload, PackedTriangles)
    if geometry_name == "rays":
        return isinstance(payload, PackedRays)
    raise ValueError(f"unsupported geometry type for OptiX backend: {geometry_name!r}")
