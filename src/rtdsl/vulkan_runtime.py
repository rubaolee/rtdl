"""vulkan_runtime.py — Vulkan KHR ray-tracing backend for rtdl.

Public API mirrors optix_runtime.py (just substitute "vulkan" for "optix"):
  run_vulkan(kernel_fn_or_compiled, **inputs)        → tuple[dict, ...]
  prepare_vulkan(kernel_fn_or_compiled)               → PreparedVulkanKernel
  vulkan_version()                                    → tuple[int, int, int]

All six workloads are supported:
  segment_intersection, point_in_polygon, overlay_compose,
  ray_triangle_hit_count, segment_polygon_hitcount, point_nearest_segment

Data marshaling: inputs are double-precision on the Python/CPU side (matching
the Embree and OptiX backends); the C++ Vulkan layer converts to float32 before
uploading to the GPU and converts results back to float64 in output records.

Library search order (first found wins):
  1. $RTDL_VULKAN_LIB environment variable (full path to the .so/.dylib)
  2. build/librtdl_vulkan.so  (relative to the repository root)
  3. librtdl_vulkan.so / librtdl_vulkan.dylib on LD_LIBRARY_PATH/DYLD_LIBRARY_PATH
"""

from __future__ import annotations

import ctypes
import ctypes.util
import functools
import os
import platform
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


# ─────────────────────────────────────────────────────────────────────────────
# ctypes output row structs  (must match rtdl_vulkan.cpp)
# Input geometry structs are imported from embree_runtime (same memory layout).
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
# Row-view wrapper (RAII-style, mirrors OptixRowView)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class VulkanRowView:
    library: object
    rows_ptr: object
    row_count: int
    row_type: object
    field_names: tuple
    _closed: bool = False

    def close(self) -> None:
        if not self._closed:
            self.library.rtdl_vulkan_free_rows(self.rows_ptr)
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

class PreparedVulkanKernel:
    """Compiled-once handle for the Vulkan backend.  Mirrors PreparedOptixKernel."""

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
        self.library = _load_vulkan_library()
        self.expected_inputs = {item.name: item for item in compiled.inputs}
        predicate = compiled.refine_op.predicate.name
        if predicate not in self._SUPPORTED_PREDICATES:
            raise ValueError(
                f"unsupported predicate for Vulkan backend: {predicate!r}"
            )
        self.predicate_name = predicate

    def bind(self, **inputs) -> PreparedVulkanExecution:
        missing    = [n for n in self.expected_inputs if n not in inputs]
        unexpected = [n for n in inputs if n not in self.expected_inputs]
        if missing:
            raise ValueError(f"missing RTDL Vulkan inputs: {', '.join(sorted(missing))}")
        if unexpected:
            raise ValueError(f"unexpected RTDL Vulkan inputs: {', '.join(sorted(unexpected))}")
        packed = {
            name: _pack_for_geometry(self.expected_inputs[name].geometry.name, payload)
            for name, payload in inputs.items()
        }
        return PreparedVulkanExecution(self.compiled, self.library, packed)

    def run(self, **inputs) -> tuple:
        return self.bind(**inputs).run()


@dataclass(frozen=True)
class PreparedVulkanExecution:
    compiled: CompiledKernel
    library: object
    packed_inputs: dict

    def run_raw(self) -> VulkanRowView:
        pred = self.compiled.refine_op.predicate.name
        dispatch = {
            "segment_intersection":   _call_lsi_vulkan_packed,
            "point_in_polygon":       _call_pip_vulkan_packed,
            "overlay_compose":        _call_overlay_vulkan_packed,
            "ray_triangle_hit_count": _call_ray_hitcount_vulkan_packed,
            "segment_polygon_hitcount": _call_segment_polygon_hitcount_vulkan_packed,
            "point_nearest_segment":  _call_point_nearest_segment_vulkan_packed,
        }
        fn = dispatch.get(pred)
        if fn is None:
            raise ValueError(f"unsupported prepared Vulkan predicate: {pred!r}")
        return fn(self.compiled, self.packed_inputs, self.library)

    def run(self) -> tuple:
        rows = self.run_raw()
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()


def prepare_vulkan(kernel_fn_or_compiled) -> PreparedVulkanKernel:
    return PreparedVulkanKernel(kernel_fn_or_compiled)


# ─────────────────────────────────────────────────────────────────────────────
# Public run_vulkan
# ─────────────────────────────────────────────────────────────────────────────

def run_vulkan(kernel_fn_or_compiled, *, result_mode: str = "dict", **inputs):
    """Execute a compiled kernel on the Vulkan KHR ray-tracing backend.

    Parameters
    ----------
    kernel_fn_or_compiled:
        A function decorated with ``@rt.kernel`` or a ``CompiledKernel``.
    result_mode:
        ``"dict"`` (default) — returns ``tuple[dict[str, object], ...]``
        ``"raw"`` — returns a ``VulkanRowView`` (caller must call ``.close()``)
    **inputs:
        Geometry inputs; may be raw records or pre-packed ``Packed*`` objects.
    """
    compiled = _resolve_kernel(kernel_fn_or_compiled)
    _validate_kernel_for_cpu(compiled)
    expected_inputs = {item.name: item for item in compiled.inputs}

    missing    = [n for n in expected_inputs if n not in inputs]
    unexpected = [n for n in inputs if n not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL Vulkan inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL Vulkan inputs: {', '.join(sorted(unexpected))}")
    if result_mode not in {"dict", "raw"}:
        raise ValueError("Vulkan result_mode must be 'dict' or 'raw'")

    prepared = prepare_vulkan(compiled).bind(**inputs)
    return prepared.run_raw() if result_mode == "raw" else prepared.run()


# ─────────────────────────────────────────────────────────────────────────────
# Version query
# ─────────────────────────────────────────────────────────────────────────────

def vulkan_version() -> tuple:
    """Return (major, minor, patch) of the Vulkan backend library."""
    lib = _load_vulkan_library()
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    _check_status(lib.rtdl_vulkan_get_version(
        ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch)))
    return major.value, minor.value, patch.value


# ─────────────────────────────────────────────────────────────────────────────
# Internal packed call helpers
# ─────────────────────────────────────────────────────────────────────────────

def _call_lsi_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    left  = packed[compiled.candidates.left.name]
    right = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlLsiRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_vulkan_run_lsi(
        left.records, left.count,
        right.records, right.count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return VulkanRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlLsiRow,
        field_names=("left_id", "right_id",
                     "intersection_point_x", "intersection_point_y"))


def _call_pip_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    boundary_mode = compiled.refine_op.predicate.options.get("boundary_mode", "inclusive")
    if boundary_mode != "inclusive":
        raise ValueError("the Vulkan PIP backend supports only boundary_mode='inclusive'")
    points   = packed[compiled.candidates.left.name]
    polygons = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlPipRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_vulkan_run_pip(
        points.records, points.count,
        polygons.refs, polygons.polygon_count,
        polygons.vertices_xy, polygons.vertex_xy_count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return VulkanRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlPipRow,
        field_names=("point_id", "polygon_id", "contains"))


def _call_overlay_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    left  = packed[compiled.candidates.left.name]
    right = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlOverlayRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_vulkan_run_overlay(
        left.refs, left.polygon_count,
        left.vertices_xy, left.vertex_xy_count,
        right.refs, right.polygon_count,
        right.vertices_xy, right.vertex_xy_count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return VulkanRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlOverlayRow,
        field_names=("left_polygon_id", "right_polygon_id",
                     "requires_lsi", "requires_pip"))


def _call_ray_hitcount_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    rays      = packed[compiled.candidates.left.name]
    triangles = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_vulkan_run_ray_hitcount(
        rays.records, rays.count,
        triangles.records, triangles.count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return VulkanRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlRayHitCountRow,
        field_names=("ray_id", "hit_count"))


def _call_segment_polygon_hitcount_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    segments = packed[compiled.candidates.left.name]
    polygons = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_vulkan_run_segment_polygon_hitcount(
        segments.records, segments.count,
        polygons.refs, polygons.polygon_count,
        polygons.vertices_xy, polygons.vertex_xy_count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return VulkanRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlSegmentPolygonHitCountRow,
        field_names=("segment_id", "hit_count"))


def _call_point_nearest_segment_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    points   = packed[compiled.candidates.left.name]
    segments = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlPointNearestSegmentRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_vulkan_run_point_nearest_segment(
        points.records, points.count,
        segments.records, segments.count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return VulkanRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlPointNearestSegmentRow,
        field_names=("point_id", "segment_id", "distance"))


# ─────────────────────────────────────────────────────────────────────────────
# Library loading
# ─────────────────────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _load_vulkan_library():
    lib_path = _find_vulkan_library()
    lib = ctypes.CDLL(str(lib_path))
    _register_argtypes(lib)
    return lib


def _find_vulkan_library() -> Path:
    # 1. Explicit env var
    env = os.environ.get("RTDL_VULKAN_LIB")
    if env:
        p = Path(env)
        if p.exists():
            return p
        raise FileNotFoundError(
            f"RTDL_VULKAN_LIB is set to {env!r} but the file does not exist")

    # 2. build/ in the repository root (two levels above this file)
    here = Path(__file__).resolve().parent
    repo_root = here.parent.parent
    suffix = ".dylib" if platform.system() == "Darwin" else ".so"
    candidate = repo_root / "build" / f"librtdl_vulkan{suffix}"
    if candidate.exists():
        return candidate

    # 3. System library path
    name = ctypes.util.find_library("rtdl_vulkan")
    if name:
        return Path(name)

    raise FileNotFoundError(
        "librtdl_vulkan not found.  "
        "Build it with 'make build-vulkan' or set RTDL_VULKAN_LIB=/path/to/lib."
    )


def _register_argtypes(lib) -> None:
    lib.rtdl_vulkan_get_version.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.rtdl_vulkan_get_version.restype = ctypes.c_int

    lib.rtdl_vulkan_free_rows.argtypes = [ctypes.c_void_p]
    lib.rtdl_vulkan_free_rows.restype  = None

    lib.rtdl_vulkan_run_lsi.argtypes = [
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_lsi.restype = ctypes.c_int

    lib.rtdl_vulkan_run_pip.argtypes = [
        ctypes.POINTER(_RtdlPoint),      ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPipRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_pip.restype = ctypes.c_int

    lib.rtdl_vulkan_run_overlay.argtypes = [
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlOverlayRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_overlay.restype = ctypes.c_int

    lib.rtdl_vulkan_run_ray_hitcount.argtypes = [
        ctypes.POINTER(_RtdlRay2D),      ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle),   ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_ray_hitcount.restype = ctypes.c_int

    lib.rtdl_vulkan_run_segment_polygon_hitcount.argtypes = [
        ctypes.POINTER(_RtdlSegment),    ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_segment_polygon_hitcount.restype = ctypes.c_int

    lib.rtdl_vulkan_run_point_nearest_segment.argtypes = [
        ctypes.POINTER(_RtdlPoint),   ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPointNearestSegmentRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_point_nearest_segment.restype = ctypes.c_int


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
        msg = f"Vulkan backend call failed with status {status}"
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
    from .embree_runtime import (
        pack_segments, pack_points, pack_polygons,
        pack_triangles, pack_rays,
    )
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
    raise ValueError(f"unsupported geometry type for Vulkan backend: {geometry_name!r}")
