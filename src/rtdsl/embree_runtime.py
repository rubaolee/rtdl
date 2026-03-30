from __future__ import annotations

import ctypes
import os
import subprocess
from pathlib import Path

from .ir import CompiledKernel
from .runtime import _normalize_records
from .runtime import _resolve_kernel
from .runtime import _validate_kernel_for_cpu


class _RtdlSegment(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x0", ctypes.c_float),
        ("y0", ctypes.c_float),
        ("x1", ctypes.c_float),
        ("y1", ctypes.c_float),
    ]


class _RtdlPoint(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]


class _RtdlPolygonRef(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("vertex_offset", ctypes.c_uint32),
        ("vertex_count", ctypes.c_uint32),
    ]


class _RtdlTriangle(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x0", ctypes.c_float),
        ("y0", ctypes.c_float),
        ("x1", ctypes.c_float),
        ("y1", ctypes.c_float),
        ("x2", ctypes.c_float),
        ("y2", ctypes.c_float),
    ]


class _RtdlRay2D(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("ox", ctypes.c_float),
        ("oy", ctypes.c_float),
        ("dx", ctypes.c_float),
        ("dy", ctypes.c_float),
        ("tmax", ctypes.c_float),
    ]


class _RtdlLsiRow(ctypes.Structure):
    _fields_ = [
        ("left_id", ctypes.c_uint32),
        ("right_id", ctypes.c_uint32),
        ("intersection_point_x", ctypes.c_float),
        ("intersection_point_y", ctypes.c_float),
    ]


class _RtdlPipRow(ctypes.Structure):
    _fields_ = [
        ("point_id", ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
        ("contains", ctypes.c_uint32),
    ]


class _RtdlOverlayRow(ctypes.Structure):
    _fields_ = [
        ("left_polygon_id", ctypes.c_uint32),
        ("right_polygon_id", ctypes.c_uint32),
        ("requires_lsi", ctypes.c_uint32),
        ("requires_pip", ctypes.c_uint32),
    ]


class _RtdlRayHitCountRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("hit_count", ctypes.c_uint32),
    ]


class _RtdlSegmentPolygonHitCountRow(ctypes.Structure):
    _fields_ = [
        ("segment_id", ctypes.c_uint32),
        ("hit_count", ctypes.c_uint32),
    ]


class _RtdlPointNearestSegmentRow(ctypes.Structure):
    _fields_ = [
        ("point_id", ctypes.c_uint32),
        ("segment_id", ctypes.c_uint32),
        ("distance", ctypes.c_float),
    ]


def run_embree(kernel_fn_or_compiled, **inputs) -> tuple[dict[str, object], ...]:
    compiled = _resolve_kernel(kernel_fn_or_compiled)
    _validate_kernel_for_cpu(compiled)
    expected_inputs = {item.name: item for item in compiled.inputs}

    missing = [name for name in expected_inputs if name not in inputs]
    unexpected = [name for name in inputs if name not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL Embree inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL Embree inputs: {', '.join(sorted(unexpected))}")

    normalized_inputs = {
        name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
        for name, payload in inputs.items()
    }

    library = _load_embree_library()
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name == "segment_intersection":
        return _run_lsi_embree(compiled, normalized_inputs, library)
    if predicate_name == "point_in_polygon":
        return _run_pip_embree(compiled, normalized_inputs, library)
    if predicate_name == "overlay_compose":
        return _run_overlay_embree(compiled, normalized_inputs, library)
    if predicate_name == "ray_triangle_hit_count":
        return _run_ray_hitcount_embree(compiled, normalized_inputs, library)
    if predicate_name == "segment_polygon_hitcount":
        return _run_segment_polygon_hitcount_embree(compiled, normalized_inputs, library)
    if predicate_name == "point_nearest_segment":
        return _run_point_nearest_segment_embree(compiled, normalized_inputs, library)
    raise ValueError(f"unsupported RTDL Embree predicate: {predicate_name}")


def embree_version() -> tuple[int, int, int]:
    library = _load_embree_library()
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    _check_status(library.rtdl_embree_get_version(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch)))
    return major.value, minor.value, patch.value


def _run_lsi_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    left_name = compiled.candidates.left.name
    right_name = compiled.candidates.right.name
    left = normalized_inputs[left_name]
    right = normalized_inputs[right_name]
    left_array = (_RtdlSegment * len(left))(*[
        _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in left
    ])
    right_array = (_RtdlSegment * len(right))(*[
        _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in right
    ])

    rows_ptr = ctypes.POINTER(_RtdlLsiRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_lsi(
        left_array,
        len(left),
        right_array,
        len(right),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "left_id": rows_ptr[index].left_id,
                "right_id": rows_ptr[index].right_id,
                "intersection_point_x": rows_ptr[index].intersection_point_x,
                "intersection_point_y": rows_ptr[index].intersection_point_y,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_embree_free_rows(rows_ptr)


def _run_pip_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    points_name = compiled.candidates.left.name
    polygons_name = compiled.candidates.right.name
    points = normalized_inputs[points_name]
    polygons = normalized_inputs[polygons_name]

    point_array = (_RtdlPoint * len(points))(*[
        _RtdlPoint(item.id, item.x, item.y) for item in points
    ])
    polygon_refs, vertex_array = _encode_polygons(polygons)

    rows_ptr = ctypes.POINTER(_RtdlPipRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_pip(
        point_array,
        len(points),
        polygon_refs,
        len(polygons),
        vertex_array,
        len(vertex_array),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "point_id": rows_ptr[index].point_id,
                "polygon_id": rows_ptr[index].polygon_id,
                "contains": rows_ptr[index].contains,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_embree_free_rows(rows_ptr)


def _run_overlay_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    left_name = compiled.candidates.left.name
    right_name = compiled.candidates.right.name
    left = normalized_inputs[left_name]
    right = normalized_inputs[right_name]
    left_refs, left_vertices = _encode_polygons(left)
    right_refs, right_vertices = _encode_polygons(right)

    rows_ptr = ctypes.POINTER(_RtdlOverlayRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_overlay(
        left_refs,
        len(left),
        left_vertices,
        len(left_vertices),
        right_refs,
        len(right),
        right_vertices,
        len(right_vertices),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "left_polygon_id": rows_ptr[index].left_polygon_id,
                "right_polygon_id": rows_ptr[index].right_polygon_id,
                "requires_lsi": rows_ptr[index].requires_lsi,
                "requires_pip": rows_ptr[index].requires_pip,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_embree_free_rows(rows_ptr)


def _run_ray_hitcount_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    rays_name = compiled.candidates.left.name
    triangles_name = compiled.candidates.right.name
    rays = normalized_inputs[rays_name]
    triangles = normalized_inputs[triangles_name]

    ray_array = (_RtdlRay2D * len(rays))(*[
        _RtdlRay2D(item.id, item.ox, item.oy, item.dx, item.dy, item.tmax) for item in rays
    ])
    triangle_array = (_RtdlTriangle * len(triangles))(*[
        _RtdlTriangle(item.id, item.x0, item.y0, item.x1, item.y1, item.x2, item.y2)
        for item in triangles
    ])

    rows_ptr = ctypes.POINTER(_RtdlRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_ray_hitcount(
        ray_array,
        len(rays),
        triangle_array,
        len(triangles),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "ray_id": rows_ptr[index].ray_id,
                "hit_count": rows_ptr[index].hit_count,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_embree_free_rows(rows_ptr)


def _run_segment_polygon_hitcount_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    segments_name = compiled.candidates.left.name
    polygons_name = compiled.candidates.right.name
    segments = normalized_inputs[segments_name]
    polygons = normalized_inputs[polygons_name]

    segment_array = (_RtdlSegment * len(segments))(*[
        _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in segments
    ])
    polygon_refs, vertex_array = _encode_polygons(polygons)

    rows_ptr = ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_segment_polygon_hitcount(
        segment_array,
        len(segments),
        polygon_refs,
        len(polygons),
        vertex_array,
        len(vertex_array),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "segment_id": rows_ptr[index].segment_id,
                "hit_count": rows_ptr[index].hit_count,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_embree_free_rows(rows_ptr)


def _run_point_nearest_segment_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    points_name = compiled.candidates.left.name
    segments_name = compiled.candidates.right.name
    points = normalized_inputs[points_name]
    segments = normalized_inputs[segments_name]

    point_array = (_RtdlPoint * len(points))(*[
        _RtdlPoint(item.id, item.x, item.y) for item in points
    ])
    segment_array = (_RtdlSegment * len(segments))(*[
        _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in segments
    ])

    rows_ptr = ctypes.POINTER(_RtdlPointNearestSegmentRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_point_nearest_segment(
        point_array,
        len(points),
        segment_array,
        len(segments),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "point_id": rows_ptr[index].point_id,
                "segment_id": rows_ptr[index].segment_id,
                "distance": rows_ptr[index].distance,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_embree_free_rows(rows_ptr)


def _encode_polygons(polygons):
    refs = []
    vertices = []
    offset = 0
    for polygon in polygons:
        refs.append(_RtdlPolygonRef(polygon.id, offset, len(polygon.vertices)))
        for vertex in polygon.vertices:
            vertices.extend([float(vertex[0]), float(vertex[1])])
        offset += len(polygon.vertices)
    ref_array = (_RtdlPolygonRef * len(refs))(*refs)
    vertex_array = (ctypes.c_float * len(vertices))(*vertices) if vertices else (ctypes.c_float * 0)()
    return ref_array, vertex_array


def _check_status(status: int, error=None) -> None:
    if status == 0:
        return
    if error is not None:
        message = error.value.decode("utf-8", errors="replace").strip()
    else:
        message = ""
    if not message:
        message = f"Embree backend call failed with status {status}"
    raise RuntimeError(message)


def _load_embree_library():
    library_path = _ensure_embree_library()
    library = ctypes.CDLL(str(library_path))
    library.rtdl_embree_get_version.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    library.rtdl_embree_get_version.restype = ctypes.c_int
    library.rtdl_embree_free_rows.argtypes = [ctypes.c_void_p]
    library.rtdl_embree_free_rows.restype = None

    library.rtdl_embree_run_lsi.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_lsi.restype = ctypes.c_int

    library.rtdl_embree_run_pip.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPipRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_pip.restype = ctypes.c_int

    library.rtdl_embree_run_overlay.argtypes = [
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlOverlayRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_overlay.restype = ctypes.c_int

    library.rtdl_embree_run_ray_hitcount.argtypes = [
        ctypes.POINTER(_RtdlRay2D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_ray_hitcount.restype = ctypes.c_int

    library.rtdl_embree_run_segment_polygon_hitcount.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_segment_polygon_hitcount.restype = ctypes.c_int

    library.rtdl_embree_run_point_nearest_segment.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPointNearestSegmentRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_point_nearest_segment.restype = ctypes.c_int

    return library


def _ensure_embree_library() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    build_dir = repo_root / "build"
    build_dir.mkdir(exist_ok=True)
    library_path = build_dir / "librtdl_embree.dylib"
    source_path = repo_root / "src" / "native" / "rtdl_embree.cpp"
    embree_prefix = Path(os.environ.get("RTDL_EMBREE_PREFIX", "/opt/homebrew/opt/embree"))
    tbb_prefix = Path(os.environ.get("RTDL_TBB_PREFIX", "/opt/homebrew/opt/tbb"))

    if not embree_prefix.exists():
        raise RuntimeError(
            "Embree is not installed at the configured prefix. "
            "Set RTDL_EMBREE_PREFIX or install Embree via Homebrew."
        )

    needs_build = not library_path.exists() or library_path.stat().st_mtime < source_path.stat().st_mtime
    if needs_build:
        command = [
            "clang++",
            "-std=c++17",
            "-O2",
            "-dynamiclib",
            "-fPIC",
            str(source_path),
            "-o",
            str(library_path),
            f"-I{embree_prefix / 'include'}",
            f"-L{embree_prefix / 'lib'}",
            f"-Wl,-rpath,{embree_prefix / 'lib'}",
            "-lembree4",
        ]
        if tbb_prefix.exists():
            command.extend([
                f"-L{tbb_prefix / 'lib'}",
                f"-Wl,-rpath,{tbb_prefix / 'lib'}",
            ])
        subprocess.run(command, check=True, cwd=repo_root)
    return library_path
