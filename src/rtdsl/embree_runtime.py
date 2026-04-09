from __future__ import annotations

import ctypes
import ctypes.util
import functools
import os
import platform
import subprocess
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

from .ir import CompiledKernel
from .runtime import _normalize_records
from .runtime import _resolve_kernel
from .runtime import _validate_kernel_for_cpu
from .runtime import _identity_cache_token
from .reference import Segment as _CanonicalSegment
from .reference import Point as _CanonicalPoint
from .reference import Polygon as _CanonicalPolygon
from .reference import Triangle as _CanonicalTriangle
from .reference import Triangle3D as _CanonicalTriangle3D
from .reference import Ray2D as _CanonicalRay2D
from .reference import Ray3D as _CanonicalRay3D


_PREPARED_CACHE_MAX_ENTRIES = 8
_prepared_embree_execution_cache: OrderedDict[tuple[object, ...], "PreparedEmbreeExecution"] = OrderedDict()


def _pkg_config_flags(package: str, option: str) -> list[str]:
    try:
        result = subprocess.run(
            ["pkg-config", option, package],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    return result.stdout.split()


def _geos_pkg_config_flags(option: str) -> list[str]:
    if platform.system() == "Windows":
        return []
    flags = _pkg_config_flags("geos", option)
    if flags:
        return flags
    flags = _pkg_config_flags("geos_c", option)
    if flags:
        return flags
    return ["-lgeos_c"] if option == "--libs" else []


class _RtdlSegment(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("x1", ctypes.c_double),
        ("y1", ctypes.c_double),
    ]


class _RtdlPoint(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
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
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("x1", ctypes.c_double),
        ("y1", ctypes.c_double),
        ("x2", ctypes.c_double),
        ("y2", ctypes.c_double),
    ]


class _RtdlTriangle3D(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("z0", ctypes.c_double),
        ("x1", ctypes.c_double),
        ("y1", ctypes.c_double),
        ("z1", ctypes.c_double),
        ("x2", ctypes.c_double),
        ("y2", ctypes.c_double),
        ("z2", ctypes.c_double),
    ]


class _RtdlRay2D(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("ox", ctypes.c_double),
        ("oy", ctypes.c_double),
        ("dx", ctypes.c_double),
        ("dy", ctypes.c_double),
        ("tmax", ctypes.c_double),
    ]


class _RtdlRay3D(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("ox", ctypes.c_double),
        ("oy", ctypes.c_double),
        ("oz", ctypes.c_double),
        ("dx", ctypes.c_double),
        ("dy", ctypes.c_double),
        ("dz", ctypes.c_double),
        ("tmax", ctypes.c_double),
    ]


class _RtdlLsiRow(ctypes.Structure):
    _fields_ = [
        ("left_id", ctypes.c_uint32),
        ("right_id", ctypes.c_uint32),
        ("intersection_point_x", ctypes.c_double),
        ("intersection_point_y", ctypes.c_double),
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


class _RtdlSegmentPolygonAnyHitRow(ctypes.Structure):
    _fields_ = [
        ("segment_id", ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
    ]


class _RtdlPointNearestSegmentRow(ctypes.Structure):
    _fields_ = [
        ("point_id", ctypes.c_uint32),
        ("segment_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
    ]


@dataclass(frozen=True)
class PackedSegments:
    records: object
    count: int


@dataclass(frozen=True)
class PackedPoints:
    records: object
    count: int


@dataclass(frozen=True)
class PackedPolygons:
    refs: object
    polygon_count: int
    vertices_xy: object
    vertex_xy_count: int


@dataclass(frozen=True)
class PackedTriangles:
    records: object
    count: int
    dimension: int = 2


@dataclass(frozen=True)
class PackedRays:
    records: object
    count: int
    dimension: int = 2


@dataclass
class EmbreeRowView:
    library: object
    rows_ptr: object
    row_count: int
    row_type: object
    field_names: tuple[str, ...]
    _closed: bool = False

    def close(self) -> None:
        if not self._closed:
            self.library.rtdl_embree_free_rows(self.rows_ptr)
            self._closed = True

    def __len__(self) -> int:
        return self.row_count

    def to_dict_rows(self) -> tuple[dict[str, object], ...]:
        return tuple(
            {
                field: getattr(self.rows_ptr[index], field)
                for field in self.field_names
            }
            for index in range(self.row_count)
        )

    def to_tuple_rows(self) -> tuple[tuple[object, ...], ...]:
        return tuple(
            tuple(getattr(self.rows_ptr[index], field) for field in self.field_names)
            for index in range(self.row_count)
        )

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


class PreparedEmbreeKernel:
    def __init__(self, kernel_fn_or_compiled):
        compiled = _resolve_kernel(kernel_fn_or_compiled)
        _validate_kernel_for_cpu(compiled)
        self.compiled = compiled
        self.library = _load_embree_library()
        self.expected_inputs = {item.name: item for item in compiled.inputs}
        predicate = compiled.refine_op.predicate.name
        if predicate not in {
            "segment_intersection",
            "point_in_polygon",
            "overlay_compose",
            "ray_triangle_hit_count",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "point_nearest_segment",
        }:
            raise ValueError(
                "the current prepared Embree path supports only Embree-backed local workloads"
            )
        self.predicate_name = predicate

    def bind(self, **inputs) -> PreparedEmbreeExecution:
        missing = [name for name in self.expected_inputs if name not in inputs]
        unexpected = [name for name in inputs if name not in self.expected_inputs]
        if missing:
            raise ValueError(f"missing RTDL Embree inputs: {', '.join(sorted(missing))}")
        if unexpected:
            raise ValueError(f"unexpected RTDL Embree inputs: {', '.join(sorted(unexpected))}")

        packed_inputs = {
            name: _pack_for_geometry(self.expected_inputs[name], payload)
            for name, payload in inputs.items()
        }
        return PreparedEmbreeExecution(self.compiled, self.library, packed_inputs)

    def run(self, **inputs) -> tuple[dict[str, object], ...]:
        return self.bind(**inputs).run()


@dataclass(frozen=True)
class PreparedEmbreeExecution:
    compiled: CompiledKernel
    library: object
    packed_inputs: dict[str, object]

    def run_raw(self) -> EmbreeRowView:
        predicate_name = self.compiled.refine_op.predicate.name
        if predicate_name == "segment_intersection":
            return _call_lsi_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "point_in_polygon":
            return _call_pip_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "overlay_compose":
            return _call_overlay_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "ray_triangle_hit_count":
            return _call_ray_hitcount_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "segment_polygon_hitcount":
            return _call_segment_polygon_hitcount_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "segment_polygon_anyhit_rows":
            return _call_segment_polygon_anyhit_rows_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "point_nearest_segment":
            return _call_point_nearest_segment_embree_packed(self.compiled, self.packed_inputs, self.library)
        raise ValueError(f"unsupported prepared RTDL Embree predicate: {predicate_name}")

    def run(self) -> tuple[dict[str, object], ...]:
        rows = self.run_raw()
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()


def prepare_embree(kernel_fn_or_compiled) -> PreparedEmbreeKernel:
    return PreparedEmbreeKernel(kernel_fn_or_compiled)


def clear_embree_prepared_cache() -> None:
    _prepared_embree_execution_cache.clear()


def pack_segments(records=None, *, ids=None, x0=None, y0=None, x1=None, y1=None) -> PackedSegments:
    if records is not None:
        normalized = records if isinstance(records, tuple) and all(isinstance(item, _CanonicalSegment) for item in records) else _normalize_records("segments", "segments", records)
        array = (_RtdlSegment * len(normalized))(*[
            _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in normalized
        ])
        return PackedSegments(records=array, count=len(normalized))

    ids_list = _coerce_list("ids", ids)
    x0_list = _coerce_list("x0", x0)
    y0_list = _coerce_list("y0", y0)
    x1_list = _coerce_list("x1", x1)
    y1_list = _coerce_list("y1", y1)
    count = _validate_equal_lengths("segments", ids_list, x0_list, y0_list, x1_list, y1_list)
    array = (_RtdlSegment * count)(*[
        _RtdlSegment(int(ids_list[i]), float(x0_list[i]), float(y0_list[i]), float(x1_list[i]), float(y1_list[i]))
        for i in range(count)
    ])
    return PackedSegments(records=array, count=count)


def pack_points(records=None, *, ids=None, x=None, y=None) -> PackedPoints:
    if records is not None:
        normalized = records if isinstance(records, tuple) and all(isinstance(item, _CanonicalPoint) for item in records) else _normalize_records("points", "points", records)
        array = (_RtdlPoint * len(normalized))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in normalized
        ])
        return PackedPoints(records=array, count=len(normalized))

    ids_list = _coerce_list("ids", ids)
    x_list = _coerce_list("x", x)
    y_list = _coerce_list("y", y)
    count = _validate_equal_lengths("points", ids_list, x_list, y_list)
    array = (_RtdlPoint * count)(*[
        _RtdlPoint(int(ids_list[i]), float(x_list[i]), float(y_list[i]))
        for i in range(count)
    ])
    return PackedPoints(records=array, count=count)


def pack_polygons(
    records=None,
    *,
    ids=None,
    vertex_offsets=None,
    vertex_counts=None,
    vertices_xy=None,
) -> PackedPolygons:
    if records is not None:
        normalized = records if isinstance(records, tuple) and all(isinstance(item, _CanonicalPolygon) for item in records) else _normalize_records("polygons", "polygons", records)
        refs, vertices = _encode_polygons(normalized)
        return PackedPolygons(
            refs=refs,
            polygon_count=len(normalized),
            vertices_xy=vertices,
            vertex_xy_count=len(vertices),
        )

    ids_list = _coerce_list("ids", ids)
    offsets_list = _coerce_list("vertex_offsets", vertex_offsets)
    counts_list = _coerce_list("vertex_counts", vertex_counts)
    vertices_list = _coerce_list("vertices_xy", vertices_xy)
    polygon_count = _validate_equal_lengths("polygons", ids_list, offsets_list, counts_list)

    if len(vertices_list) % 2 != 0:
        raise ValueError("packed polygon vertices_xy must contain an even number of coordinates")

    refs = []
    for idx in range(polygon_count):
        polygon_id = int(ids_list[idx])
        offset = int(offsets_list[idx])
        count = int(counts_list[idx])
        if count < 3:
            raise ValueError("packed polygon vertex_counts entries must be at least 3")
        if offset < 0 or offset + count > len(vertices_list) // 2:
            raise ValueError("packed polygon offsets/counts exceed the provided vertices_xy data")
        refs.append(_RtdlPolygonRef(polygon_id, offset, count))

    ref_array = (_RtdlPolygonRef * polygon_count)(*refs)
    vertex_array = (ctypes.c_double * len(vertices_list))(*[float(value) for value in vertices_list])
    return PackedPolygons(
        refs=ref_array,
        polygon_count=polygon_count,
        vertices_xy=vertex_array,
        vertex_xy_count=len(vertices_list),
    )


def pack_triangles(
    records=None,
    *,
    ids=None,
    x0=None,
    y0=None,
    x1=None,
    y1=None,
    x2=None,
    y2=None,
    dimension: int | None = None,
) -> PackedTriangles:
    if records is not None:
        normalized = (
            records
            if isinstance(records, tuple)
            and all(isinstance(item, (_CanonicalTriangle, _CanonicalTriangle3D)) for item in records)
            else _normalize_records("triangles", "triangles", records)
        )
        if dimension not in {None, 2, 3}:
            raise ValueError("triangles dimension must be one of: 2, 3")
        inferred_dimension = dimension
        if inferred_dimension is None:
            inferred_dimension = 3 if normalized and all(isinstance(item, _CanonicalTriangle3D) for item in normalized) else 2
        if inferred_dimension == 3:
            if any(not isinstance(item, _CanonicalTriangle3D) for item in normalized):
                if normalized:
                    raise ValueError("triangles packed for a 3D layout must provide 3D triangle records")
            array = (_RtdlTriangle3D * len(normalized))(*[
                _RtdlTriangle3D(item.id, item.x0, item.y0, item.z0, item.x1, item.y1, item.z1, item.x2, item.y2, item.z2)
                for item in normalized
            ])
            return PackedTriangles(records=array, count=len(normalized), dimension=3)
        if any(isinstance(item, _CanonicalTriangle3D) for item in normalized):
            if normalized:
                raise ValueError("triangles packed for a 2D layout must provide 2D triangle records")
        array = (_RtdlTriangle * len(normalized))(*[
            _RtdlTriangle(item.id, item.x0, item.y0, item.x1, item.y1, item.x2, item.y2)
            for item in normalized
        ])
        return PackedTriangles(records=array, count=len(normalized), dimension=2)

    if dimension == 3:
        raise ValueError("triangles packed from explicit coordinate columns currently support only 2D records")

    ids_list = _coerce_list("ids", ids)
    x0_list = _coerce_list("x0", x0)
    y0_list = _coerce_list("y0", y0)
    x1_list = _coerce_list("x1", x1)
    y1_list = _coerce_list("y1", y1)
    x2_list = _coerce_list("x2", x2)
    y2_list = _coerce_list("y2", y2)
    count = _validate_equal_lengths("triangles", ids_list, x0_list, y0_list, x1_list, y1_list, x2_list, y2_list)
    array = (_RtdlTriangle * count)(*[
        _RtdlTriangle(
            int(ids_list[i]),
            float(x0_list[i]),
            float(y0_list[i]),
            float(x1_list[i]),
            float(y1_list[i]),
            float(x2_list[i]),
            float(y2_list[i]),
        )
        for i in range(count)
    ])
    return PackedTriangles(records=array, count=count, dimension=2)


def pack_rays(
    records=None,
    *,
    ids=None,
    ox=None,
    oy=None,
    dx=None,
    dy=None,
    tmax=None,
    dimension: int | None = None,
) -> PackedRays:
    if records is not None:
        normalized = (
            records
            if isinstance(records, tuple)
            and all(isinstance(item, (_CanonicalRay2D, _CanonicalRay3D)) for item in records)
            else _normalize_records("rays", "rays", records)
        )
        if dimension not in {None, 2, 3}:
            raise ValueError("rays dimension must be one of: 2, 3")
        inferred_dimension = dimension
        if inferred_dimension is None:
            inferred_dimension = 3 if normalized and all(isinstance(item, _CanonicalRay3D) for item in normalized) else 2
        if inferred_dimension == 3:
            if any(not isinstance(item, _CanonicalRay3D) for item in normalized):
                if normalized:
                    raise ValueError("rays packed for a 3D layout must provide 3D ray records")
            array = (_RtdlRay3D * len(normalized))(*[
                _RtdlRay3D(item.id, item.ox, item.oy, item.oz, item.dx, item.dy, item.dz, item.tmax)
                for item in normalized
            ])
            return PackedRays(records=array, count=len(normalized), dimension=3)
        if any(isinstance(item, _CanonicalRay3D) for item in normalized):
            if normalized:
                raise ValueError("rays packed for a 2D layout must provide 2D ray records")
        array = (_RtdlRay2D * len(normalized))(*[
            _RtdlRay2D(item.id, item.ox, item.oy, item.dx, item.dy, item.tmax) for item in normalized
        ])
        return PackedRays(records=array, count=len(normalized), dimension=2)

    if dimension == 3:
        raise ValueError("rays packed from explicit coordinate columns currently support only 2D records")

    ids_list = _coerce_list("ids", ids)
    ox_list = _coerce_list("ox", ox)
    oy_list = _coerce_list("oy", oy)
    dx_list = _coerce_list("dx", dx)
    dy_list = _coerce_list("dy", dy)
    tmax_list = _coerce_list("tmax", tmax)
    count = _validate_equal_lengths("rays", ids_list, ox_list, oy_list, dx_list, dy_list, tmax_list)
    array = (_RtdlRay2D * count)(*[
        _RtdlRay2D(
            int(ids_list[i]),
            float(ox_list[i]),
            float(oy_list[i]),
            float(dx_list[i]),
            float(dy_list[i]),
            float(tmax_list[i]),
        )
        for i in range(count)
    ])
    return PackedRays(records=array, count=count, dimension=2)


def run_embree(kernel_fn_or_compiled, *, result_mode: str = "dict", **inputs):
    compiled = _resolve_kernel(kernel_fn_or_compiled)
    _validate_kernel_for_cpu(compiled)
    expected_inputs = {item.name: item for item in compiled.inputs}

    missing = [name for name in expected_inputs if name not in inputs]
    unexpected = [name for name in inputs if name not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL Embree inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL Embree inputs: {', '.join(sorted(unexpected))}")

    if result_mode not in {"dict", "raw"}:
        raise ValueError("Embree result_mode must be one of: dict, raw")

    # Current accepted honesty boundary:
    # the Jaccard workloads are closed on Python/native CPU today, but not as
    # Embree-native kernels. The public Embree run surface accepts them through
    # the native CPU/oracle implementation so they can participate in Linux
    # consistency and scale audits without overclaiming backend maturity.
    if compiled.refine_op.predicate.name in {
        "polygon_pair_overlap_area_rows",
        "polygon_set_jaccard",
    }:
        if result_mode == "raw":
            raise ValueError(
                "Embree raw mode is not supported for the Jaccard workloads "
                "while the backend uses the native CPU oracle fallback"
            )
        from .runtime import run_cpu

        return run_cpu(compiled, **inputs)

    prepared = _get_or_bind_prepared_embree_execution(compiled, expected_inputs, inputs)
    return prepared.run_raw() if result_mode == "raw" else prepared.run()


def _get_or_bind_prepared_embree_execution(compiled: CompiledKernel, expected_inputs, inputs) -> PreparedEmbreeExecution:
    cache_key = _prepared_execution_cache_key(compiled, expected_inputs, inputs)
    if cache_key is None:
        return prepare_embree(compiled).bind(**inputs)
    cached = _prepared_embree_execution_cache.get(cache_key)
    if cached is not None:
        _prepared_embree_execution_cache.move_to_end(cache_key)
        return cached
    prepared = prepare_embree(compiled).bind(**inputs)
    _prepared_embree_execution_cache[cache_key] = prepared
    if len(_prepared_embree_execution_cache) > _PREPARED_CACHE_MAX_ENTRIES:
        _prepared_embree_execution_cache.popitem(last=False)
    return prepared


def _prepared_execution_cache_key(compiled: CompiledKernel, expected_inputs, inputs) -> tuple[object, ...] | None:
    identity_tokens = []
    for name in sorted(expected_inputs):
        geometry_name = expected_inputs[name].geometry.name
        payload = inputs[name]
        if _is_packed_for_geometry(geometry_name, payload):
            return None
        token = _identity_cache_token(geometry_name, payload)
        if token is None:
            identity_tokens = []
            break
        identity_tokens.append((name, token))
    if identity_tokens:
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
            tuple(identity_tokens),
        )

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


def _run_lsi_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> tuple[dict[str, object], ...]:
    rows = _call_lsi_embree_packed(compiled, packed_inputs, library)
    try:
        return rows.to_dict_rows()
    finally:
        rows.close()


def _call_lsi_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    left_name = compiled.candidates.left.name
    right_name = compiled.candidates.right.name
    left = packed_inputs[left_name]
    right = packed_inputs[right_name]
    rows_ptr = ctypes.POINTER(_RtdlLsiRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_lsi(
        left.records,
        left.count,
        right.records,
        right.count,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return EmbreeRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlLsiRow,
        field_names=("left_id", "right_id", "intersection_point_x", "intersection_point_y"),
    )


def _run_pip_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    boundary_mode = compiled.refine_op.predicate.options.get("boundary_mode", "inclusive")
    if boundary_mode != "inclusive":
        raise ValueError("the current Embree PIP runtime supports only boundary_mode='inclusive'")
    result_mode = compiled.refine_op.predicate.options.get("result_mode", "full_matrix")
    if result_mode not in {"full_matrix", "positive_hits"}:
        raise ValueError("the current Embree PIP runtime supports only result_mode='full_matrix' or 'positive_hits'")

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
        1 if result_mode == "positive_hits" else 0,
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


def _run_pip_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> tuple[dict[str, object], ...]:
    rows = _call_pip_embree_packed(compiled, packed_inputs, library)
    try:
        return rows.to_dict_rows()
    finally:
        rows.close()


def _call_pip_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    boundary_mode = compiled.refine_op.predicate.options.get("boundary_mode", "inclusive")
    if boundary_mode != "inclusive":
        raise ValueError("the current prepared Embree PIP runtime supports only boundary_mode='inclusive'")
    result_mode = compiled.refine_op.predicate.options.get("result_mode", "full_matrix")
    if result_mode not in {"full_matrix", "positive_hits"}:
        raise ValueError("the current prepared Embree PIP runtime supports only result_mode='full_matrix' or 'positive_hits'")

    points_name = compiled.candidates.left.name
    polygons_name = compiled.candidates.right.name
    points = packed_inputs[points_name]
    polygons = packed_inputs[polygons_name]

    rows_ptr = ctypes.POINTER(_RtdlPipRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_pip(
        points.records,
        points.count,
        polygons.refs,
        polygons.polygon_count,
        polygons.vertices_xy,
        polygons.vertex_xy_count,
        1 if result_mode == "positive_hits" else 0,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return EmbreeRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlPipRow,
        field_names=("point_id", "polygon_id", "contains"),
    )


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


def _run_overlay_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> tuple[dict[str, object], ...]:
    rows = _call_overlay_embree_packed(compiled, packed_inputs, library)
    try:
        return rows.to_dict_rows()
    finally:
        rows.close()


def _call_overlay_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    left_name = compiled.candidates.left.name
    right_name = compiled.candidates.right.name
    left = packed_inputs[left_name]
    right = packed_inputs[right_name]

    rows_ptr = ctypes.POINTER(_RtdlOverlayRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_overlay(
        left.refs,
        left.polygon_count,
        left.vertices_xy,
        left.vertex_xy_count,
        right.refs,
        right.polygon_count,
        right.vertices_xy,
        right.vertex_xy_count,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return EmbreeRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlOverlayRow,
        field_names=("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"),
    )


def _run_ray_hitcount_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    rays_name = compiled.candidates.left.name
    triangles_name = compiled.candidates.right.name
    rays = normalized_inputs[rays_name]
    triangles = normalized_inputs[triangles_name]

    rows_ptr = ctypes.POINTER(_RtdlRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if rays and isinstance(rays[0], _CanonicalRay3D):
        ray_array = (_RtdlRay3D * len(rays))(*[
            _RtdlRay3D(item.id, item.ox, item.oy, item.oz, item.dx, item.dy, item.dz, item.tmax) for item in rays
        ])
        triangle_array = (_RtdlTriangle3D * len(triangles))(*[
            _RtdlTriangle3D(item.id, item.x0, item.y0, item.z0, item.x1, item.y1, item.z1, item.x2, item.y2, item.z2)
            for item in triangles
        ])
        call = _require_optional_embree_symbol(library, "rtdl_embree_run_ray_hitcount_3d")
        if call is None:
            raise RuntimeError("loaded Embree backend library does not export rtdl_embree_run_ray_hitcount_3d; rebuild the Embree backend from current main")
        status = call(
            ray_array,
            len(rays),
            triangle_array,
            len(triangles),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    else:
        ray_array = (_RtdlRay2D * len(rays))(*[
            _RtdlRay2D(item.id, item.ox, item.oy, item.dx, item.dy, item.tmax) for item in rays
        ])
        triangle_array = (_RtdlTriangle * len(triangles))(*[
            _RtdlTriangle(item.id, item.x0, item.y0, item.x1, item.y1, item.x2, item.y2)
            for item in triangles
        ])
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


def _run_ray_hitcount_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> tuple[dict[str, object], ...]:
    rows = _call_ray_hitcount_embree_packed(compiled, packed_inputs, library)
    try:
        return rows.to_dict_rows()
    finally:
        rows.close()


def _call_ray_hitcount_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    rays_name = compiled.candidates.left.name
    triangles_name = compiled.candidates.right.name
    rays = packed_inputs[rays_name]
    triangles = packed_inputs[triangles_name]

    rows_ptr = ctypes.POINTER(_RtdlRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if rays.dimension != triangles.dimension:
        raise ValueError("Embree ray_triangle_hit_count requires rays and triangles to have the same dimension")
    if rays.dimension == 3:
        call = _require_optional_embree_symbol(library, "rtdl_embree_run_ray_hitcount_3d")
        status = call(
            rays.records,
            rays.count,
            triangles.records,
            triangles.count,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    else:
        status = library.rtdl_embree_run_ray_hitcount(
            rays.records,
            rays.count,
            triangles.records,
            triangles.count,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    _check_status(status, error)
    return EmbreeRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlRayHitCountRow,
        field_names=("ray_id", "hit_count"),
    )


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


def _run_segment_polygon_hitcount_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> tuple[dict[str, object], ...]:
    rows = _call_segment_polygon_hitcount_embree_packed(compiled, packed_inputs, library)
    try:
        return rows.to_dict_rows()
    finally:
        rows.close()


def _call_segment_polygon_hitcount_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    segments_name = compiled.candidates.left.name
    polygons_name = compiled.candidates.right.name
    segments = packed_inputs[segments_name]
    polygons = packed_inputs[polygons_name]

    rows_ptr = ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_segment_polygon_hitcount(
        segments.records,
        segments.count,
        polygons.refs,
        polygons.polygon_count,
        polygons.vertices_xy,
        polygons.vertex_xy_count,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return EmbreeRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlSegmentPolygonHitCountRow,
        field_names=("segment_id", "hit_count"),
    )


def _call_segment_polygon_anyhit_rows_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    segments_name = compiled.candidates.left.name
    polygons_name = compiled.candidates.right.name
    segments = packed_inputs[segments_name]
    polygons = packed_inputs[polygons_name]

    rows_ptr = ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_segment_polygon_anyhit_rows(
        segments.records,
        segments.count,
        polygons.refs,
        polygons.polygon_count,
        polygons.vertices_xy,
        polygons.vertex_xy_count,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return EmbreeRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlSegmentPolygonAnyHitRow,
        field_names=("segment_id", "polygon_id"),
    )


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


def _run_point_nearest_segment_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> tuple[dict[str, object], ...]:
    rows = _call_point_nearest_segment_embree_packed(compiled, packed_inputs, library)
    try:
        return rows.to_dict_rows()
    finally:
        rows.close()


def _call_point_nearest_segment_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    points_name = compiled.candidates.left.name
    segments_name = compiled.candidates.right.name
    points = packed_inputs[points_name]
    segments = packed_inputs[segments_name]

    rows_ptr = ctypes.POINTER(_RtdlPointNearestSegmentRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_point_nearest_segment(
        points.records,
        points.count,
        segments.records,
        segments.count,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return EmbreeRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlPointNearestSegmentRow,
        field_names=("point_id", "segment_id", "distance"),
    )


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
    vertex_array = (ctypes.c_double * len(vertices))(*vertices) if vertices else (ctypes.c_double * 0)()
    return ref_array, vertex_array


def _coerce_list(name: str, values):
    if values is None:
        raise ValueError(f"missing packed input array `{name}`")
    return list(values)


def _validate_equal_lengths(label: str, *columns) -> int:
    lengths = {len(column) for column in columns}
    if len(lengths) != 1:
        raise ValueError(f"packed {label} arrays must have identical lengths")
    return lengths.pop()


def _geometry_layout_dimension(geometry_input) -> int:
    layout = geometry_input.layout
    field_names = set(layout.field_names())
    if layout.name.endswith("3D") or any(name in field_names for name in ("z0", "z1", "z2", "oz", "dz")):
        return 3
    return 2


def _pack_for_geometry(geometry_input, payload):
    geometry_name = geometry_input.geometry.name
    expected_dimension = _geometry_layout_dimension(geometry_input)
    if geometry_name == "segments":
        return payload if isinstance(payload, PackedSegments) else pack_segments(records=payload)
    if geometry_name == "points":
        cached = getattr(payload, "_rtdl_packed_points", None)
        if isinstance(cached, PackedPoints):
            return cached
        return payload if isinstance(payload, PackedPoints) else pack_points(records=payload)
    if geometry_name == "polygons":
        cached = getattr(payload, "_rtdl_packed_polygons", None)
        if isinstance(cached, PackedPolygons):
            return cached
        return payload if isinstance(payload, PackedPolygons) else pack_polygons(records=payload)
    if geometry_name == "triangles":
        if isinstance(payload, PackedTriangles):
            if payload.dimension != expected_dimension:
                raise ValueError(
                    "packed triangles payload dimension does not match the kernel input layout"
                )
            return payload
        return pack_triangles(records=payload, dimension=expected_dimension)
    if geometry_name == "rays":
        if isinstance(payload, PackedRays):
            if payload.dimension != expected_dimension:
                raise ValueError(
                    "packed rays payload dimension does not match the kernel input layout"
                )
            return payload
        return pack_rays(records=payload, dimension=expected_dimension)
    raise ValueError(f"the current prepared Embree path does not support geometry `{geometry_name}`")


def _is_packed_for_geometry(geometry_name: str, payload) -> bool:
    return (
        (geometry_name == "segments" and isinstance(payload, PackedSegments))
        or (geometry_name == "points" and isinstance(payload, PackedPoints))
        or (geometry_name == "polygons" and isinstance(payload, PackedPolygons))
        or (geometry_name == "triangles" and isinstance(payload, PackedTriangles))
        or (geometry_name == "rays" and isinstance(payload, PackedRays))
    )


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


def _default_embree_prefix(system: str) -> Path:
    if system == "Darwin":
        return Path("/opt/homebrew/opt/embree")
    if system == "Windows":
        if "RTDL_EMBREE_PREFIX" in os.environ:
            return Path(os.environ["RTDL_EMBREE_PREFIX"])
        home = Path.home()
        for candidate in (
            home / "vendor",
            home / "vendor" / "embree",
            home / "vendor" / "embree-4.4.0",
            home / "vendor" / "embree-4.4.0.x64.windows",
        ):
            if (candidate / "include" / "embree4").exists():
                return candidate
        return home / "vendor"
    return Path("/usr")


@functools.lru_cache(maxsize=1)
def _load_embree_library():
    library_path = _ensure_embree_library()
    if platform.system() == "Windows" and hasattr(os, "add_dll_directory"):
        embree_prefix = _default_embree_prefix("Windows")
        for candidate in (library_path.parent, embree_prefix / "bin", embree_prefix / "lib"):
            if candidate.exists():
                os.add_dll_directory(str(candidate))
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
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlPipRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_pip.restype = ctypes.c_int

    library.rtdl_embree_run_overlay.argtypes = [
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
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

    optional_ray3d = _require_optional_embree_symbol(library, "rtdl_embree_run_ray_hitcount_3d")
    if optional_ray3d is not None:
        optional_ray3d.argtypes = [
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlTriangle3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_ray3d.restype = ctypes.c_int

    library.rtdl_embree_run_segment_polygon_hitcount.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_segment_polygon_hitcount.restype = ctypes.c_int

    library.rtdl_embree_run_segment_polygon_anyhit_rows.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_segment_polygon_anyhit_rows.restype = ctypes.c_int

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


def _require_optional_embree_symbol(library, symbol_name: str):
    try:
        return getattr(library, symbol_name)
    except AttributeError:
        return None


def _ensure_embree_library() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    build_dir = repo_root / "build"
    build_dir.mkdir(exist_ok=True)
    source_path = repo_root / "src" / "native" / "rtdl_embree.cpp"
    system = platform.system()
    if system == "Darwin":
        library_ext = ".dylib"
    elif system == "Windows":
        library_ext = ".dll"
    else:
        library_ext = ".so"
    library_path = build_dir / f"librtdl_embree{library_ext}"
    if system == "Darwin":
        embree_prefix = _default_embree_prefix(system)
        tbb_prefix = Path(os.environ.get("RTDL_TBB_PREFIX", "/opt/homebrew/opt/tbb"))
        compiler = os.environ.get("CXX", "clang++")
        shared_flags = ["-dynamiclib", "-fPIC"]
    elif system == "Windows":
        embree_prefix = _default_embree_prefix(system)
        tbb_prefix = embree_prefix
        compiler = os.environ.get("CXX", r"C:\Program Files\LLVM\bin\clang++.exe")
        shared_flags = ["-shared"]
    else:
        embree_prefix = _default_embree_prefix(system)
        tbb_prefix = Path(os.environ.get("RTDL_TBB_PREFIX", "/usr"))
        compiler = os.environ.get("CXX", "g++")
        shared_flags = ["-shared", "-fPIC"]
    geos_cflags = _geos_pkg_config_flags("--cflags")
    geos_libs = _geos_pkg_config_flags("--libs")

    embree_include = embree_prefix / "include"
    if not embree_prefix.exists() or not embree_include.exists():
        raise RuntimeError(
            "Embree is not installed at the configured prefix. "
            "Set RTDL_EMBREE_PREFIX to a prefix with include/embree4 or install Embree first."
        )

    needs_build = not library_path.exists() or library_path.stat().st_mtime < source_path.stat().st_mtime
    if needs_build:
        command = [
            compiler,
            "-std=c++17",
            "-O2",
            *shared_flags,
            *geos_cflags,
            str(source_path),
            "-o",
            str(library_path),
            f"-I{embree_include}",
        ]
        embree_lib = embree_prefix / "lib"
        if embree_lib.exists():
            if system == "Windows":
                command.extend([
                    str(embree_lib / "embree4.lib"),
                    str(embree_lib / "tbb12.lib"),
                ])
            else:
                command.extend([
                    f"-L{embree_lib}",
                    "-lembree4",
                ])
                command.append(f"-Wl,-rpath,{embree_lib}")
        elif system == "Darwin":
            raise RuntimeError(
                "Embree library directory was not found under the configured prefix. "
                "Set RTDL_EMBREE_PREFIX to the Homebrew embree prefix."
            )
        elif system != "Windows":
            command.append("-lembree4")
        if system != "Windows" and tbb_prefix.exists() and (tbb_prefix / "lib").exists():
            command.append(f"-L{tbb_prefix / 'lib'}")
            command.append(f"-Wl,-rpath,{tbb_prefix / 'lib'}")
        command.extend(geos_libs)
        if system == "Windows":
            vcvars = Path(
                os.environ.get(
                    "RTDL_VCVARS64",
                    r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
                )
            )
            if not vcvars.exists():
                raise RuntimeError(
                    "Windows Embree build requires vcvars64.bat. Set RTDL_VCVARS64 to the Visual Studio Build Tools vcvars64.bat path."
                )
            quoted = " ".join(f'\"{part}\"' if " " in part else part for part in command)
            subprocess.run(
                ["cmd", "/c", f'call "{vcvars}" >nul 2>&1 && {quoted}'],
                check=True,
                cwd=repo_root,
            )
        else:
            subprocess.run(command, check=True, cwd=repo_root)
    return library_path
