from __future__ import annotations

import ctypes
import ctypes.util
import functools
import os
import platform
import subprocess
import tempfile
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

from .ir import CompiledKernel
from .runtime import _normalize_records
from .runtime import _resolve_kernel
from .runtime import _validate_kernel_for_cpu
from .runtime import _identity_cache_token
from .graph_reference import CSRGraph
from .graph_reference import EdgeSeed
from .graph_reference import FrontierVertex
from .graph_reference import normalize_edge_set
from .graph_reference import normalize_frontier
from .graph_reference import normalize_vertex_set
from .oracle_runtime import _decode_db_group_key
from .oracle_runtime import _DB_KIND_BOOL
from .oracle_runtime import _DB_KIND_FLOAT64
from .oracle_runtime import _DB_KIND_INT64
from .oracle_runtime import _DB_KIND_TEXT
from .oracle_runtime import _RtdlDbField
from .oracle_runtime import _RtdlDbGroupedCountRow
from .oracle_runtime import _RtdlDbRowIdRow
from .oracle_runtime import _encode_db_clauses
from .oracle_runtime import _encode_db_field_kind
from .oracle_runtime import _encode_db_table
from .oracle_runtime import _encode_db_text_clause_values
from .oracle_runtime import _encode_db_text_fields
from .db_reference import PredicateClause
from .db_reference import normalize_denorm_table
from .db_reference import normalize_grouped_query
from .db_reference import normalize_predicate_bundle
from .reference import Segment as _CanonicalSegment
from .reference import Point as _CanonicalPoint
from .reference import Point3D as _CanonicalPoint3D
from .reference import Polygon as _CanonicalPolygon
from .reference import Triangle as _CanonicalTriangle
from .reference import Triangle3D as _CanonicalTriangle3D
from .reference import Ray2D as _CanonicalRay2D
from .reference import Ray3D as _CanonicalRay3D


_PREPARED_CACHE_MAX_ENTRIES = 8
_prepared_embree_execution_cache: OrderedDict[tuple[object, ...], "PreparedEmbreeExecution"] = OrderedDict()
_DB_MAX_ROWS_PER_JOB = 1_000_000
EMBREE_REQUIRED_SYMBOLS = (
    "rtdl_embree_get_version",
    "rtdl_embree_free_rows",
    "rtdl_embree_run_lsi",
    "rtdl_embree_run_pip",
    "rtdl_embree_run_overlay",
    "rtdl_embree_run_ray_hitcount",
    "rtdl_embree_run_segment_polygon_hitcount",
    "rtdl_embree_run_segment_polygon_anyhit_rows",
    "rtdl_embree_run_point_nearest_segment",
    "rtdl_embree_run_fixed_radius_neighbors",
    "rtdl_embree_run_knn_rows",
    "rtdl_embree_run_bfs_expand",
    "rtdl_embree_run_triangle_probe",
    "rtdl_embree_run_conjunctive_scan",
    "rtdl_embree_run_grouped_count",
    "rtdl_embree_run_grouped_sum",
    "rtdl_embree_db_dataset_create",
    "rtdl_embree_db_dataset_create_columnar",
    "rtdl_embree_db_dataset_destroy",
    "rtdl_embree_db_dataset_conjunctive_scan",
    "rtdl_embree_db_dataset_grouped_count",
    "rtdl_embree_db_dataset_grouped_sum",
)


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


def _run_windows_compile(command: list[str], *, vcvars: Path, cwd: Path) -> None:
    script = "\r\n".join(
        (
            "@echo off",
            f'call "{vcvars}" >nul 2>&1',
            "if errorlevel 1 exit /b %errorlevel%",
            subprocess.list2cmdline(command),
        )
    )
    with tempfile.NamedTemporaryFile("w", suffix=".bat", delete=False, encoding="utf-8", newline="") as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        subprocess.run(["cmd", "/c", str(script_path)], check=True, cwd=cwd)
    finally:
        script_path.unlink(missing_ok=True)


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


class _RtdlPoint3D(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double),
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


class _EmbreeRtdlDbGroupedSumRow(ctypes.Structure):
    _fields_ = [
        ("group_key", ctypes.c_int64),
        ("sum", ctypes.c_int64),
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


class _RtdlFixedRadiusNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
    ]


class _RtdlKnnNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
        ("neighbor_rank", ctypes.c_uint32),
    ]


class _RtdlFrontierVertex(ctypes.Structure):
    _fields_ = [
        ("vertex_id", ctypes.c_uint32),
        ("level", ctypes.c_uint32),
    ]


class _RtdlBfsExpandRow(ctypes.Structure):
    _fields_ = [
        ("src_vertex", ctypes.c_uint32),
        ("dst_vertex", ctypes.c_uint32),
        ("level", ctypes.c_uint32),
    ]


class _RtdlEdgeSeed(ctypes.Structure):
    _fields_ = [
        ("u", ctypes.c_uint32),
        ("v", ctypes.c_uint32),
    ]


class _RtdlTriangleRow(ctypes.Structure):
    _fields_ = [
        ("u", ctypes.c_uint32),
        ("v", ctypes.c_uint32),
        ("w", ctypes.c_uint32),
    ]


class _RtdlDbColumn(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("kind", ctypes.c_uint32),
        ("int_values", ctypes.POINTER(ctypes.c_int64)),
        ("double_values", ctypes.POINTER(ctypes.c_double)),
        ("string_values", ctypes.POINTER(ctypes.c_char_p)),
    ]


@dataclass(frozen=True)
class PackedSegments:
    records: object
    count: int


@dataclass(frozen=True)
class PackedPoints:
    records: object
    count: int
    dimension: int = 2


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


@dataclass(frozen=True)
class PackedGraphCSR:
    row_offsets: object
    row_offset_count: int
    column_indices: object
    column_index_count: int


@dataclass(frozen=True)
class PackedVertexFrontier:
    records: object
    count: int


@dataclass(frozen=True)
class PackedVertexSet:
    records: object
    count: int


@dataclass(frozen=True)
class PackedEdgeSet:
    records: object
    count: int


@dataclass
class EmbreeRowView:
    library: object
    rows_ptr: object
    row_count: int
    row_type: object
    field_names: tuple[str, ...]
    _closed: bool = False
    _free_on_close: bool = True
    _owner: object | None = None

    def close(self) -> None:
        if not self._closed and self._free_on_close and self.library is not None:
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
            "fixed_radius_neighbors",
            "bounded_knn_rows",
            "knn_rows",
            "bfs_discover",
            "triangle_match",
            "conjunctive_scan",
            "grouped_count",
            "grouped_sum",
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

        if self.predicate_name in {"conjunctive_scan", "grouped_count", "grouped_sum"}:
            normalized_inputs = {
                name: _normalize_records(name, self.expected_inputs[name].geometry.name, payload)
                for name, payload in inputs.items()
            }
            return _prepare_db_embree_execution(self.compiled, normalized_inputs, self.library)

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
        if predicate_name == "fixed_radius_neighbors":
            return _call_fixed_radius_neighbors_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "bounded_knn_rows":
            return _call_bounded_knn_rows_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "knn_rows":
            return _call_knn_rows_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "bfs_discover":
            return _call_bfs_expand_embree_packed(self.compiled, self.packed_inputs, self.library)
        if predicate_name == "triangle_match":
            return _call_triangle_probe_embree_packed(self.compiled, self.packed_inputs, self.library)
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


def pack_points(records=None, *, ids=None, x=None, y=None, z=None, dimension: int | None = None) -> PackedPoints:
    if records is not None:
        normalized = (
            records
            if isinstance(records, tuple) and all(isinstance(item, (_CanonicalPoint, _CanonicalPoint3D)) for item in records)
            else _normalize_records("points", "points", records)
        )
        if dimension not in {None, 2, 3}:
            raise ValueError("points dimension must be one of: 2, 3")
        inferred_dimension = dimension
        if inferred_dimension is None:
            inferred_dimension = 3 if normalized and all(isinstance(item, _CanonicalPoint3D) for item in normalized) else 2
        if inferred_dimension == 3:
            if any(not isinstance(item, _CanonicalPoint3D) for item in normalized):
                if normalized:
                    raise ValueError("points packed for a 3D layout must provide 3D point records")
            array = (_RtdlPoint3D * len(normalized))(*[
                _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in normalized
            ])
            return PackedPoints(records=array, count=len(normalized), dimension=3)
        if any(isinstance(item, _CanonicalPoint3D) for item in normalized):
            if normalized:
                raise ValueError("points packed for a 2D layout must provide 2D point records")
        array = (_RtdlPoint * len(normalized))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in normalized
        ])
        return PackedPoints(records=array, count=len(normalized), dimension=2)

    ids_list = _coerce_list("ids", ids)
    x_list = _coerce_list("x", x)
    y_list = _coerce_list("y", y)
    if dimension not in {None, 2, 3}:
        raise ValueError("points dimension must be one of: 2, 3")
    if dimension == 3 or z is not None:
        z_list = _coerce_list("z", z)
        count = _validate_equal_lengths("points", ids_list, x_list, y_list, z_list)
        array = (_RtdlPoint3D * count)(*[
            _RtdlPoint3D(int(ids_list[i]), float(x_list[i]), float(y_list[i]), float(z_list[i]))
            for i in range(count)
        ])
        return PackedPoints(records=array, count=count, dimension=3)
    count = _validate_equal_lengths("points", ids_list, x_list, y_list)
    array = (_RtdlPoint * count)(*[
        _RtdlPoint(int(ids_list[i]), float(x_list[i]), float(y_list[i]))
        for i in range(count)
    ])
    return PackedPoints(records=array, count=count, dimension=2)


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

    if compiled.refine_op.predicate.name in {"conjunctive_scan", "grouped_count", "grouped_sum"}:
        normalized_inputs = {
            name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
            for name, payload in inputs.items()
        }
        rows = _run_db_embree(compiled, normalized_inputs, _load_embree_library(), result_mode=result_mode)
        return rows

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


def _run_db_embree(compiled: CompiledKernel, normalized_inputs, library, *, result_mode: str):
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name == "conjunctive_scan":
        predicates_name = compiled.candidates.left.name
        table_name = compiled.candidates.right.name
        table_rows = normalized_inputs[table_name]
        if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
            raise ValueError("first-wave Embree DB lowering supports at most 1000000 rows per RT job")
        predicates = normalized_inputs[predicates_name]
        fields_array, row_values_array, row_count = _encode_db_table(table_rows)
        clauses_array = _encode_db_clauses(predicates.clauses)
        rows_ptr = ctypes.POINTER(_RtdlDbRowIdRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = library.rtdl_embree_run_conjunctive_scan(
            fields_array,
            ctypes.c_size_t(len(fields_array)),
            row_values_array,
            ctypes.c_size_t(row_count),
            clauses_array,
            ctypes.c_size_t(len(clauses_array)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
        _check_status(status, error)
        row_view = EmbreeRowView(
            library=library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbRowIdRow,
            field_names=("row_id",),
        )
        return row_view if result_mode == "raw" else row_view.to_dict_rows()

    query_name = compiled.candidates.left.name
    table_name = compiled.candidates.right.name
    table_rows = normalized_inputs[table_name]
    if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
        raise ValueError("first-wave Embree DB lowering supports at most 1000000 rows per RT job")
    query = normalized_inputs[query_name]
    if len(query.group_keys) != 1:
        raise ValueError("first-wave Embree DB grouped kernels support exactly one group key")
    extra_fields = [query.group_keys[0]]
    if predicate_name == "grouped_sum" and query.value_field:
        extra_fields.append(query.value_field)
    encoded_rows, encoded_predicates, reverse_maps = _encode_db_text_fields(
        table_rows,
        query.predicates,
        extra_fields=tuple(extra_fields),
    )
    fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
    clauses_array = _encode_db_clauses(encoded_predicates)
    group_key_field = query.group_keys[0].encode("utf-8")
    error = ctypes.create_string_buffer(4096)

    if predicate_name == "grouped_count":
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
        row_count_out = ctypes.c_size_t()
        status = library.rtdl_embree_run_grouped_count(
            fields_array,
            ctypes.c_size_t(len(fields_array)),
            row_values_array,
            ctypes.c_size_t(row_count),
            clauses_array,
            ctypes.c_size_t(len(clauses_array)),
            group_key_field,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
        _check_status(status, error)
        row_view = EmbreeRowView(
            library=library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbGroupedCountRow,
            field_names=("group_key", "count"),
        )
        if result_mode == "raw":
            return row_view
        try:
            reverse_map = reverse_maps.get(query.group_keys[0])
            rows = []
            for index in range(row_view.row_count):
                row = row_view.rows_ptr[index]
                rows.append(
                    {
                        query.group_keys[0]: _decode_db_group_key(reverse_map, row.group_key),
                        "count": row.count,
                    }
                )
            return tuple(rows)
        finally:
            row_view.close()

    rows_ptr = ctypes.POINTER(_EmbreeRtdlDbGroupedSumRow)()
    row_count_out = ctypes.c_size_t()
    status = library.rtdl_embree_run_grouped_sum(
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        row_values_array,
        ctypes.c_size_t(row_count),
        clauses_array,
        ctypes.c_size_t(len(clauses_array)),
        group_key_field,
        query.value_field.encode("utf-8"),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        error,
        len(error),
    )
    _check_status(status, error)
    row_view = EmbreeRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count_out.value,
        row_type=_EmbreeRtdlDbGroupedSumRow,
        field_names=("group_key", "sum"),
    )
    if result_mode == "raw":
        return row_view
    try:
        reverse_map = reverse_maps.get(query.group_keys[0])
        rows = []
        for index in range(row_view.row_count):
            row = row_view.rows_ptr[index]
            total = row.sum
            rows.append(
                {
                    query.group_keys[0]: _decode_db_group_key(reverse_map, row.group_key),
                    "sum": int(total),
                }
            )
        return tuple(rows)
    finally:
        row_view.close()


@dataclass(frozen=True)
class PreparedEmbreeDbExecution:
    compiled: CompiledKernel
    library: object
    predicate_name: str
    dataset: object
    clauses_array: object
    group_key_name: str | None = None
    group_key_field: bytes | None = None
    reverse_map: object | None = None
    value_field: bytes | None = None

    def run_raw(self) -> EmbreeRowView:
        if self.predicate_name == "conjunctive_scan":
            return self.dataset.conjunctive_scan(self.clauses_array)

        if self.predicate_name == "grouped_count":
            return self.dataset.grouped_count(self.clauses_array, self.group_key_field)

        return self.dataset.grouped_sum(self.clauses_array, self.group_key_field, self.value_field)

    def run(self) -> tuple[dict[str, object], ...]:
        rows = self.run_raw()
        try:
            if self.predicate_name == "conjunctive_scan":
                return rows.to_dict_rows()
            if self.predicate_name == "grouped_count":
                return tuple(
                    {
                        self.group_key_name: _decode_db_group_key(self.reverse_map, rows.rows_ptr[index].group_key),
                        "count": rows.rows_ptr[index].count,
                    }
                    for index in range(rows.row_count)
                )
            return tuple(
                {
                    self.group_key_name: _decode_db_group_key(self.reverse_map, rows.rows_ptr[index].group_key),
                    "sum": int(rows.rows_ptr[index].sum),
                }
                for index in range(rows.row_count)
            )
        finally:
            rows.close()


class EmbreePreparedDbDataset:
    def __init__(
        self,
        library,
        fields_array,
        row_values_array,
        row_count: int,
        *,
        primary_fields=(),
        columns_array=None,
        column_count: int | None = None,
        transfer: str = "row",
        keepalive=(),
    ):
        self.library = library
        self.fields_array = fields_array
        self.row_values_array = row_values_array
        self.columns_array = columns_array
        self.column_count = int(column_count or 0)
        self.row_count = int(row_count)
        self.transfer = transfer
        self._keepalive = keepalive
        primary_field_bytes = tuple(str(name).encode("utf-8") for name in primary_fields)
        primary_fields_array = (
            (ctypes.c_char_p * len(primary_field_bytes))(*primary_field_bytes)
            if primary_field_bytes
            else None
        )
        handle = ctypes.c_void_p()
        error = ctypes.create_string_buffer(4096)
        if transfer == "columnar":
            if not hasattr(self.library, "rtdl_embree_db_dataset_create_columnar"):
                raise RuntimeError(
                    "loaded Embree backend does not export rtdl_embree_db_dataset_create_columnar; "
                    "rebuild the Embree backend from the current checkout"
                )
            status = self.library.rtdl_embree_db_dataset_create_columnar(
                self.columns_array,
                ctypes.c_size_t(self.column_count),
                ctypes.c_size_t(self.row_count),
                primary_fields_array,
                ctypes.c_size_t(len(primary_field_bytes)),
                ctypes.byref(handle),
                error,
                len(error),
            )
        else:
            status = self.library.rtdl_embree_db_dataset_create(
                self.fields_array,
                ctypes.c_size_t(len(self.fields_array)),
                self.row_values_array,
                ctypes.c_size_t(self.row_count),
                primary_fields_array,
                ctypes.c_size_t(len(primary_field_bytes)),
                ctypes.byref(handle),
                error,
                len(error),
            )
        _check_status(status, error)
        self.handle = handle
        self._closed = False

    def close(self) -> None:
        if not self._closed and self.handle:
            self.library.rtdl_embree_db_dataset_destroy(self.handle)
        self._closed = True

    def conjunctive_scan(self, clauses_array) -> EmbreeRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbRowIdRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_embree_db_dataset_conjunctive_scan(
            self.handle,
            clauses_array,
            ctypes.c_size_t(len(clauses_array)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
        _check_status(status, error)
        return EmbreeRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbRowIdRow,
            field_names=("row_id",),
        )

    def grouped_count(self, clauses_array, group_key_field: bytes) -> EmbreeRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_embree_db_dataset_grouped_count(
            self.handle,
            clauses_array,
            ctypes.c_size_t(len(clauses_array)),
            group_key_field,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
        _check_status(status, error)
        return EmbreeRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbGroupedCountRow,
            field_names=("group_key", "count"),
        )

    def grouped_sum(self, clauses_array, group_key_field: bytes, value_field: bytes) -> EmbreeRowView:
        rows_ptr = ctypes.POINTER(_EmbreeRtdlDbGroupedSumRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_embree_db_dataset_grouped_sum(
            self.handle,
            clauses_array,
            ctypes.c_size_t(len(clauses_array)),
            group_key_field,
            value_field,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
        _check_status(status, error)
        return EmbreeRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_EmbreeRtdlDbGroupedSumRow,
            field_names=("group_key", "sum"),
        )

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


class PreparedEmbreeDbDataset:
    def __init__(self, table_rows, *, primary_fields=(), transfer: str = "row"):
        if transfer not in {"row", "columnar"}:
            raise ValueError("Embree DB dataset transfer must be 'row' or 'columnar'")
        rows = normalize_denorm_table(table_rows)
        if len(rows) > _DB_MAX_ROWS_PER_JOB:
            raise ValueError("first-wave Embree DB lowering supports at most 1000000 rows per RT job")
        encoded_rows, self._field_maps, self._reverse_maps = _encode_all_db_text_columns(rows)
        if transfer == "columnar":
            columns_array, row_count, keepalive = _encode_db_table_columnar(encoded_rows)
            fields_array = None
            row_values_array = None
        else:
            fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
            columns_array = None
            keepalive = ()
        self._dataset = EmbreePreparedDbDataset(
            _load_embree_library(),
            fields_array,
            row_values_array,
            row_count,
            primary_fields=primary_fields,
            columns_array=columns_array,
            column_count=len(columns_array) if columns_array is not None else None,
            transfer=transfer,
            keepalive=keepalive,
        )
        self._fields_array = fields_array
        self._row_values_array = row_values_array
        self._columns_array = columns_array
        self._transfer = transfer
        self.row_count = row_count

    def close(self) -> None:
        self._dataset.close()

    def conjunctive_scan(self, predicates) -> tuple[dict[str, object], ...]:
        bundle = normalize_predicate_bundle(predicates)
        clauses_array = _encode_db_clauses(self._encode_clauses(bundle.clauses))
        rows = self._dataset.conjunctive_scan(clauses_array)
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()

    def grouped_count(self, query) -> tuple[dict[str, object], ...]:
        normalized_query = normalize_grouped_query(query)
        if len(normalized_query.group_keys) != 1:
            raise ValueError("first-wave Embree DB grouped kernels support exactly one group key")
        group_key = normalized_query.group_keys[0]
        clauses_array = _encode_db_clauses(self._encode_clauses(normalized_query.predicates))
        rows = self._dataset.grouped_count(clauses_array, group_key.encode("utf-8"))
        try:
            reverse_map = self._reverse_maps.get(group_key)
            return tuple(
                {
                    group_key: _decode_db_group_key(reverse_map, rows.rows_ptr[index].group_key),
                    "count": rows.rows_ptr[index].count,
                }
                for index in range(rows.row_count)
            )
        finally:
            rows.close()

    def grouped_sum(self, query) -> tuple[dict[str, object], ...]:
        normalized_query = normalize_grouped_query(query)
        if len(normalized_query.group_keys) != 1:
            raise ValueError("first-wave Embree DB grouped kernels support exactly one group key")
        if not normalized_query.value_field:
            raise ValueError("grouped_sum requires a value_field")
        group_key = normalized_query.group_keys[0]
        clauses_array = _encode_db_clauses(self._encode_clauses(normalized_query.predicates))
        rows = self._dataset.grouped_sum(
            clauses_array,
            group_key.encode("utf-8"),
            normalized_query.value_field.encode("utf-8"),
        )
        try:
            reverse_map = self._reverse_maps.get(group_key)
            return tuple(
                {
                    group_key: _decode_db_group_key(reverse_map, rows.rows_ptr[index].group_key),
                    "sum": int(rows.rows_ptr[index].sum),
                }
                for index in range(rows.row_count)
            )
        finally:
            rows.close()

    def _encode_clauses(self, clauses) -> tuple[PredicateClause, ...]:
        encoded = []
        for clause in clauses:
            if clause.field not in self._field_maps:
                encoded.append(clause)
                continue
            encode_map = self._field_maps[clause.field]
            value, value_hi = _encode_db_text_clause_values(clause, encode_map)
            encoded.append(PredicateClause(field=clause.field, op=clause.op, value=value, value_hi=value_hi))
        return tuple(encoded)

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def prepare_embree_db_dataset(table_rows, *, primary_fields=(), transfer: str = "row") -> PreparedEmbreeDbDataset:
    return PreparedEmbreeDbDataset(table_rows, primary_fields=primary_fields, transfer=transfer)


def _encode_all_db_text_columns(table_rows):
    field_maps: dict[str, dict[object, int]] = {}
    reverse_maps: dict[str, dict[int, object]] = {}
    field_names = tuple(table_rows[0].keys()) if table_rows else ()
    for field in field_names:
        values = [row[field] for row in table_rows]
        if not any(isinstance(value, str) for value in values):
            continue
        unique_values = sorted(set(values))
        encode_map = {value: index + 1 for index, value in enumerate(unique_values)}
        field_maps[field] = encode_map
        reverse_maps[field] = {code: value for value, code in encode_map.items()}
    encoded_rows = []
    for row in table_rows:
        encoded = dict(row)
        for field, encode_map in field_maps.items():
            encoded[field] = encode_map[row[field]]
        encoded_rows.append(encoded)
    return tuple(encoded_rows), field_maps, reverse_maps


def _encode_db_table_columnar(table_rows) -> tuple[object, int, tuple[object, ...]]:
    if not table_rows:
        raise ValueError("Embree columnar DB path requires at least one denormalized table row")
    field_names = tuple(str(name) for name in table_rows[0].keys())
    if "row_id" not in field_names:
        raise ValueError("Embree columnar DB path requires a `row_id` field")
    field_set = set(field_names)
    for index, row in enumerate(table_rows):
        if set(str(name) for name in row.keys()) != field_set:
            raise ValueError(f"denorm table row {index} does not match the first-row schema")

    columns = []
    keepalive: list[object] = []
    null_int_values = ctypes.POINTER(ctypes.c_int64)()
    null_double_values = ctypes.POINTER(ctypes.c_double)()
    null_string_values = ctypes.POINTER(ctypes.c_char_p)()
    for name in field_names:
        kind = _encode_db_field_kind(table_rows[0][name])
        name_bytes = name.encode("utf-8")
        keepalive.append(name_bytes)
        int_values = null_int_values
        double_values = null_double_values
        string_values = null_string_values
        if kind == _DB_KIND_FLOAT64:
            values = (ctypes.c_double * len(table_rows))(*(float(row[name]) for row in table_rows))
            keepalive.append(values)
            double_values = values
        elif kind == _DB_KIND_TEXT:
            encoded_values = tuple(str(row[name]).encode("utf-8") for row in table_rows)
            values = (ctypes.c_char_p * len(encoded_values))(*encoded_values)
            keepalive.extend(encoded_values)
            keepalive.append(values)
            string_values = values
        else:
            values = (ctypes.c_int64 * len(table_rows))(
                *((1 if row[name] else 0) if kind == _DB_KIND_BOOL else int(row[name]) for row in table_rows)
            )
            keepalive.append(values)
            int_values = values
        columns.append(
            _RtdlDbColumn(
                name=name_bytes,
                kind=kind,
                int_values=int_values,
                double_values=double_values,
                string_values=string_values,
            )
        )

    columns_array = (_RtdlDbColumn * len(columns))(*columns)
    keepalive.append(columns_array)
    return columns_array, len(table_rows), tuple(keepalive)


def _db_primary_fields_from_clauses(clauses) -> tuple[str, ...]:
    fields = []
    for clause in clauses:
        name = str(clause.field)
        if name not in fields:
            fields.append(name)
        if len(fields) == 3:
            break
    return tuple(fields)


def _prepare_db_embree_execution(compiled: CompiledKernel, normalized_inputs, library) -> PreparedEmbreeDbExecution:
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name == "conjunctive_scan":
        predicates_name = compiled.candidates.left.name
        table_name = compiled.candidates.right.name
        table_rows = normalized_inputs[table_name]
        if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
            raise ValueError("first-wave Embree DB lowering supports at most 1000000 rows per RT job")
        predicates = normalized_inputs[predicates_name]
        columns_array, row_count, keepalive = _encode_db_table_columnar(table_rows)
        clauses_array = _encode_db_clauses(predicates.clauses)
        dataset = EmbreePreparedDbDataset(
            library,
            None,
            None,
            row_count,
            primary_fields=_db_primary_fields_from_clauses(predicates.clauses),
            columns_array=columns_array,
            column_count=len(columns_array),
            transfer="columnar",
            keepalive=keepalive,
        )
        return PreparedEmbreeDbExecution(
            compiled=compiled,
            library=library,
            predicate_name=predicate_name,
            dataset=dataset,
            clauses_array=clauses_array,
        )

    query_name = compiled.candidates.left.name
    table_name = compiled.candidates.right.name
    table_rows = normalized_inputs[table_name]
    if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
        raise ValueError("first-wave Embree DB lowering supports at most 1000000 rows per RT job")
    query = normalized_inputs[query_name]
    if len(query.group_keys) != 1:
        raise ValueError("first-wave Embree DB grouped kernels support exactly one group key")
    extra_fields = [query.group_keys[0]]
    if predicate_name == "grouped_sum" and query.value_field:
        extra_fields.append(query.value_field)
    encoded_rows, encoded_predicates, reverse_maps = _encode_db_text_fields(
        table_rows,
        query.predicates,
        extra_fields=tuple(extra_fields),
    )
    columns_array, row_count, keepalive = _encode_db_table_columnar(encoded_rows)
    clauses_array = _encode_db_clauses(encoded_predicates)
    dataset = EmbreePreparedDbDataset(
        library,
        None,
        None,
        row_count,
        primary_fields=_db_primary_fields_from_clauses(encoded_predicates),
        columns_array=columns_array,
        column_count=len(columns_array),
        transfer="columnar",
        keepalive=keepalive,
    )
    return PreparedEmbreeDbExecution(
        compiled=compiled,
        library=library,
        predicate_name=predicate_name,
        dataset=dataset,
        clauses_array=clauses_array,
        group_key_name=query.group_keys[0],
        group_key_field=query.group_keys[0].encode("utf-8"),
        reverse_map=reverse_maps.get(query.group_keys[0]),
        value_field=query.value_field.encode("utf-8") if predicate_name == "grouped_sum" else None,
    )


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


def _run_fixed_radius_neighbors_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    query_name = compiled.candidates.left.name
    search_name = compiled.candidates.right.name
    query_points = normalized_inputs[query_name]
    search_points = normalized_inputs[search_name]
    radius = float(compiled.refine_op.predicate.options["radius"])
    k_max = int(compiled.refine_op.predicate.options["k_max"])

    rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if (
        (query_points and isinstance(query_points[0], _CanonicalPoint3D))
        or (search_points and isinstance(search_points[0], _CanonicalPoint3D))
    ):
        call = _require_optional_embree_symbol(library, "rtdl_embree_run_fixed_radius_neighbors_3d")
        if call is None:
            raise RuntimeError(
                "loaded Embree backend library does not export rtdl_embree_run_fixed_radius_neighbors_3d; "
                "rebuild the Embree backend from current main"
            )
        query_array = (_RtdlPoint3D * len(query_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in query_points
        ])
        search_array = (_RtdlPoint3D * len(search_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in search_points
        ])
        status = call(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            radius,
            k_max,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    else:
        query_array = (_RtdlPoint * len(query_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in query_points
        ])
        search_array = (_RtdlPoint * len(search_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in search_points
        ])
        status = library.rtdl_embree_run_fixed_radius_neighbors(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            radius,
            k_max,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    _check_status(status, error)
    try:
        return tuple(
            {
                "query_id": rows_ptr[index].query_id,
                "neighbor_id": rows_ptr[index].neighbor_id,
                "distance": rows_ptr[index].distance,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_embree_free_rows(rows_ptr)


def _run_fixed_radius_neighbors_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> tuple[dict[str, object], ...]:
    rows = _call_fixed_radius_neighbors_embree_packed(compiled, packed_inputs, library)
    try:
        return rows.to_dict_rows()
    finally:
        rows.close()


def _rank_fixed_radius_rows(fixed_radius_rows) -> tuple[dict[str, object], ...]:
    ranked_rows = []
    current_query_id = None
    current_rank = 0
    for row in fixed_radius_rows:
        query_id = row["query_id"]
        if query_id != current_query_id:
            current_query_id = query_id
            current_rank = 1
        else:
            current_rank += 1
        ranked_rows.append(
            {
                "query_id": query_id,
                "neighbor_id": row["neighbor_id"],
                "distance": row["distance"],
                "neighbor_rank": current_rank,
            }
        )
    return tuple(ranked_rows)


def _make_owned_row_view(row_type, rows, field_names: tuple[str, ...]) -> EmbreeRowView:
    array = (row_type * len(rows))(*rows)
    rows_ptr = ctypes.cast(array, ctypes.POINTER(row_type))
    return EmbreeRowView(
        library=None,
        rows_ptr=rows_ptr,
        row_count=len(rows),
        row_type=row_type,
        field_names=field_names,
        _free_on_close=False,
        _owner=array,
    )


def _run_bounded_knn_rows_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    fixed_radius_rows = _run_fixed_radius_neighbors_embree(compiled, normalized_inputs, library)
    return _rank_fixed_radius_rows(fixed_radius_rows)


def _run_bounded_knn_rows_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> tuple[dict[str, object], ...]:
    rows = _call_bounded_knn_rows_embree_packed(compiled, packed_inputs, library)
    try:
        return rows.to_dict_rows()
    finally:
        rows.close()


def _call_bounded_knn_rows_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    fixed_radius_rows = _call_fixed_radius_neighbors_embree_packed(compiled, packed_inputs, library)
    try:
        ranked_rows = []
        current_query_id = None
        current_rank = 0
        for index in range(len(fixed_radius_rows)):
            row = fixed_radius_rows.rows_ptr[index]
            query_id = row.query_id
            if query_id != current_query_id:
                current_query_id = query_id
                current_rank = 1
            else:
                current_rank += 1
            ranked_rows.append(
                _RtdlKnnNeighborRow(
                    row.query_id,
                    row.neighbor_id,
                    row.distance,
                    current_rank,
                )
            )
    finally:
        fixed_radius_rows.close()
    return _make_owned_row_view(
        _RtdlKnnNeighborRow,
        ranked_rows,
        ("query_id", "neighbor_id", "distance", "neighbor_rank"),
    )


def _call_fixed_radius_neighbors_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    query_name = compiled.candidates.left.name
    search_name = compiled.candidates.right.name
    query_points = packed_inputs[query_name]
    search_points = packed_inputs[search_name]
    radius = float(compiled.refine_op.predicate.options["radius"])
    k_max = int(compiled.refine_op.predicate.options["k_max"])

    rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if query_points.dimension == 3:
        call = _require_optional_embree_symbol(library, "rtdl_embree_run_fixed_radius_neighbors_3d")
        if call is None:
            raise RuntimeError(
                "loaded Embree backend library does not export rtdl_embree_run_fixed_radius_neighbors_3d; "
                "rebuild the Embree backend from current main"
            )
        status = call(
            query_points.records,
            query_points.count,
            search_points.records,
            search_points.count,
            radius,
            k_max,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    else:
        status = library.rtdl_embree_run_fixed_radius_neighbors(
            query_points.records,
            query_points.count,
            search_points.records,
            search_points.count,
            radius,
            k_max,
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
        row_type=_RtdlFixedRadiusNeighborRow,
        field_names=("query_id", "neighbor_id", "distance"),
    )


def _run_knn_rows_embree(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    query_name = compiled.candidates.left.name
    search_name = compiled.candidates.right.name
    query_points = normalized_inputs[query_name]
    search_points = normalized_inputs[search_name]
    k = int(compiled.refine_op.predicate.options["k"])
    rows_ptr = ctypes.POINTER(_RtdlKnnNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if (
        (query_points and isinstance(query_points[0], _CanonicalPoint3D))
        or (search_points and isinstance(search_points[0], _CanonicalPoint3D))
    ):
        call = _require_optional_embree_symbol(library, "rtdl_embree_run_knn_rows_3d")
        if call is None:
            raise RuntimeError(
                "loaded Embree backend library does not export rtdl_embree_run_knn_rows_3d; "
                "rebuild the Embree backend from current main"
            )
        query_array = (_RtdlPoint3D * len(query_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in query_points
        ])
        search_array = (_RtdlPoint3D * len(search_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in search_points
        ])
        status = call(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            k,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    else:
        query_array = (_RtdlPoint * len(query_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in query_points
        ])
        search_array = (_RtdlPoint * len(search_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in search_points
        ])
        status = library.rtdl_embree_run_knn_rows(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            k,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    _check_status(status, error)
    try:
        return tuple(
            {
                "query_id": rows_ptr[index].query_id,
                "neighbor_id": rows_ptr[index].neighbor_id,
                "distance": rows_ptr[index].distance,
                "neighbor_rank": rows_ptr[index].neighbor_rank,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_embree_free_rows(rows_ptr)


def _run_knn_rows_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> tuple[dict[str, object], ...]:
    rows = _call_knn_rows_embree_packed(compiled, packed_inputs, library)
    try:
        return rows.to_dict_rows()
    finally:
        rows.close()


def _call_knn_rows_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    query_name = compiled.candidates.left.name
    search_name = compiled.candidates.right.name
    query_points = packed_inputs[query_name]
    search_points = packed_inputs[search_name]
    k = int(compiled.refine_op.predicate.options["k"])
    rows_ptr = ctypes.POINTER(_RtdlKnnNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if query_points.dimension == 3:
        call = _require_optional_embree_symbol(library, "rtdl_embree_run_knn_rows_3d")
        if call is None:
            raise RuntimeError(
                "loaded Embree backend library does not export rtdl_embree_run_knn_rows_3d; "
                "rebuild the Embree backend from current main"
            )
        status = call(
            query_points.records,
            query_points.count,
            search_points.records,
            search_points.count,
            k,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    else:
        status = library.rtdl_embree_run_knn_rows(
            query_points.records,
            query_points.count,
            search_points.records,
            search_points.count,
            k,
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
        row_type=_RtdlKnnNeighborRow,
        field_names=("query_id", "neighbor_id", "distance", "neighbor_rank"),
    )


def _call_bfs_expand_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    frontier_name = compiled.candidates.left.name
    graph_name = compiled.candidates.right.name
    visited_name = str(compiled.refine_op.predicate.options["visited_input"])
    frontier = packed_inputs[frontier_name]
    graph = packed_inputs[graph_name]
    visited = packed_inputs[visited_name]
    rows_ptr = ctypes.POINTER(_RtdlBfsExpandRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_bfs_expand(
        graph.row_offsets,
        graph.row_offset_count,
        graph.column_indices,
        graph.column_index_count,
        frontier.records,
        frontier.count,
        visited.records,
        visited.count,
        ctypes.c_uint32(1 if compiled.refine_op.predicate.options.get("dedupe", True) else 0),
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
        row_type=_RtdlBfsExpandRow,
        field_names=("src_vertex", "dst_vertex", "level"),
    )


def _call_triangle_probe_embree_packed(compiled: CompiledKernel, packed_inputs, library) -> EmbreeRowView:
    seeds_name = compiled.candidates.left.name
    graph_name = compiled.candidates.right.name
    seeds = packed_inputs[seeds_name]
    graph = packed_inputs[graph_name]
    rows_ptr = ctypes.POINTER(_RtdlTriangleRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_embree_run_triangle_probe(
        graph.row_offsets,
        graph.row_offset_count,
        graph.column_indices,
        graph.column_index_count,
        seeds.records,
        seeds.count,
        ctypes.c_uint32(1 if compiled.refine_op.predicate.options.get("order") == "id_ascending" else 0),
        ctypes.c_uint32(1 if compiled.refine_op.predicate.options.get("unique", True) else 0),
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
        row_type=_RtdlTriangleRow,
        field_names=("u", "v", "w"),
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
    if geometry_name == "graph_csr":
        if isinstance(payload, PackedGraphCSR):
            return payload
        normalized = payload if isinstance(payload, CSRGraph) else _normalize_records(geometry_input.name, geometry_name, payload)
        row_offsets = (ctypes.c_uint32 * len(normalized.row_offsets))(*normalized.row_offsets)
        column_indices = (ctypes.c_uint32 * len(normalized.column_indices))(*normalized.column_indices)
        return PackedGraphCSR(
            row_offsets=row_offsets,
            row_offset_count=len(normalized.row_offsets),
            column_indices=column_indices,
            column_index_count=len(normalized.column_indices),
        )
    if geometry_name == "vertex_frontier":
        if isinstance(payload, PackedVertexFrontier):
            return payload
        normalized = payload if isinstance(payload, tuple) and all(isinstance(item, FrontierVertex) for item in payload) else normalize_frontier(payload)
        records = (_RtdlFrontierVertex * len(normalized))(*[
            _RtdlFrontierVertex(item.vertex_id, item.level) for item in normalized
        ])
        return PackedVertexFrontier(records=records, count=len(normalized))
    if geometry_name == "vertex_set":
        if isinstance(payload, PackedVertexSet):
            return payload
        normalized = normalize_vertex_set(payload)
        records = (ctypes.c_uint32 * len(normalized))(*normalized)
        return PackedVertexSet(records=records, count=len(normalized))
    if geometry_name == "edge_set":
        if isinstance(payload, PackedEdgeSet):
            return payload
        normalized = payload if isinstance(payload, tuple) and all(isinstance(item, EdgeSeed) for item in payload) else normalize_edge_set(payload)
        records = (_RtdlEdgeSeed * len(normalized))(*[
            _RtdlEdgeSeed(item.u, item.v) for item in normalized
        ])
        return PackedEdgeSet(records=records, count=len(normalized))
    if geometry_name == "segments":
        return payload if isinstance(payload, PackedSegments) else pack_segments(records=payload)
    if geometry_name == "points":
        cached = getattr(payload, "_rtdl_packed_points", None)
        if isinstance(cached, PackedPoints):
            if cached.dimension != expected_dimension:
                raise ValueError(
                    "packed points payload dimension does not match the kernel input layout"
                )
            return cached
        if isinstance(payload, PackedPoints):
            if payload.dimension != expected_dimension:
                raise ValueError(
                    "packed points payload dimension does not match the kernel input layout"
                )
            return payload
        return pack_points(records=payload, dimension=expected_dimension)
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
        (geometry_name == "graph_csr" and isinstance(payload, PackedGraphCSR))
        or (geometry_name == "vertex_frontier" and isinstance(payload, PackedVertexFrontier))
        or (geometry_name == "vertex_set" and isinstance(payload, PackedVertexSet))
        or (geometry_name == "edge_set" and isinstance(payload, PackedEdgeSet))
        or (geometry_name == "segments" and isinstance(payload, PackedSegments))
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
    _require_embree_symbols(library, library_path)
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

    library.rtdl_embree_run_fixed_radius_neighbors.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_fixed_radius_neighbors.restype = ctypes.c_int

    optional_fixed_radius_3d = _require_optional_embree_symbol(library, "rtdl_embree_run_fixed_radius_neighbors_3d")
    if optional_fixed_radius_3d is not None:
        optional_fixed_radius_3d.argtypes = [
            ctypes.POINTER(_RtdlPoint3D),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlPoint3D),
            ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_fixed_radius_3d.restype = ctypes.c_int

    library.rtdl_embree_run_knn_rows.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_embree_run_knn_rows.restype = ctypes.c_int

    optional_knn_rows_3d = _require_optional_embree_symbol(library, "rtdl_embree_run_knn_rows_3d")
    if optional_knn_rows_3d is not None:
        optional_knn_rows_3d.argtypes = [
            ctypes.POINTER(_RtdlPoint3D),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlPoint3D),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_knn_rows_3d.restype = ctypes.c_int

    optional_bfs_expand = _require_optional_embree_symbol(library, "rtdl_embree_run_bfs_expand")
    if optional_bfs_expand is not None:
        optional_bfs_expand.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlFrontierVertex),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.POINTER(_RtdlBfsExpandRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_bfs_expand.restype = ctypes.c_int

    optional_triangle_probe = _require_optional_embree_symbol(library, "rtdl_embree_run_triangle_probe")
    if optional_triangle_probe is not None:
        optional_triangle_probe.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlEdgeSeed),
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.POINTER(_RtdlTriangleRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_triangle_probe.restype = ctypes.c_int

    optional_db_conjunctive_scan = _require_optional_embree_symbol(library, "rtdl_embree_run_conjunctive_scan")
    if optional_db_conjunctive_scan is not None:
        optional_db_conjunctive_scan.argtypes = [
            ctypes.POINTER(_RtdlDbField),
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbRowIdRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_db_conjunctive_scan.restype = ctypes.c_int

    optional_db_grouped_count = _require_optional_embree_symbol(library, "rtdl_embree_run_grouped_count")
    if optional_db_grouped_count is not None:
        optional_db_grouped_count.argtypes = [
            ctypes.POINTER(_RtdlDbField),
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_db_grouped_count.restype = ctypes.c_int

    optional_db_grouped_sum = _require_optional_embree_symbol(library, "rtdl_embree_run_grouped_sum")
    if optional_db_grouped_sum is not None:
        optional_db_grouped_sum.argtypes = [
            ctypes.POINTER(_RtdlDbField),
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_EmbreeRtdlDbGroupedSumRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_db_grouped_sum.restype = ctypes.c_int

    optional_db_dataset_create = _require_optional_embree_symbol(library, "rtdl_embree_db_dataset_create")
    if optional_db_dataset_create is not None:
        optional_db_dataset_create.argtypes = [
            ctypes.POINTER(_RtdlDbField),
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_db_dataset_create.restype = ctypes.c_int

    optional_db_dataset_create_columnar = _require_optional_embree_symbol(
        library, "rtdl_embree_db_dataset_create_columnar"
    )
    if optional_db_dataset_create_columnar is not None:
        optional_db_dataset_create_columnar.argtypes = [
            ctypes.POINTER(_RtdlDbColumn),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_db_dataset_create_columnar.restype = ctypes.c_int

    optional_db_dataset_destroy = _require_optional_embree_symbol(library, "rtdl_embree_db_dataset_destroy")
    if optional_db_dataset_destroy is not None:
        optional_db_dataset_destroy.argtypes = [ctypes.c_void_p]
        optional_db_dataset_destroy.restype = None

    optional_db_dataset_conjunctive_scan = _require_optional_embree_symbol(
        library, "rtdl_embree_db_dataset_conjunctive_scan"
    )
    if optional_db_dataset_conjunctive_scan is not None:
        optional_db_dataset_conjunctive_scan.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbRowIdRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_db_dataset_conjunctive_scan.restype = ctypes.c_int

    optional_db_dataset_grouped_count = _require_optional_embree_symbol(
        library, "rtdl_embree_db_dataset_grouped_count"
    )
    if optional_db_dataset_grouped_count is not None:
        optional_db_dataset_grouped_count.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_db_dataset_grouped_count.restype = ctypes.c_int

    optional_db_dataset_grouped_sum = _require_optional_embree_symbol(
        library, "rtdl_embree_db_dataset_grouped_sum"
    )
    if optional_db_dataset_grouped_sum is not None:
        optional_db_dataset_grouped_sum.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_EmbreeRtdlDbGroupedSumRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_db_dataset_grouped_sum.restype = ctypes.c_int

    return library


def _require_optional_embree_symbol(library, symbol_name: str):
    try:
        return getattr(library, symbol_name)
    except AttributeError:
        return None


def _require_embree_symbols(library, library_path: Path) -> None:
    missing = [symbol for symbol in EMBREE_REQUIRED_SYMBOLS if not hasattr(library, symbol)]
    if not missing:
        return
    missing_text = ", ".join(missing)
    raise RuntimeError(
        "loaded Embree backend library is stale or incomplete: "
        f"{library_path} is missing required export(s): {missing_text}. "
        "Rebuild the Embree backend from this checkout. On Unix-like hosts run "
        "`make build-embree`; on Windows ensure RTDL_EMBREE_PREFIX points to an "
        "Embree prefix with include/ and lib/, ensure RTDL_VCVARS64 points to "
        "vcvars64.bat, remove the stale build/librtdl_embree.dll if present, "
        "then run `python -c \"import rtdsl as rt; print(rt.embree_version())\"`."
    )


def _ensure_embree_library() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    build_dir = repo_root / "build"
    build_dir.mkdir(exist_ok=True)
    source_path = repo_root / "src" / "native" / "rtdl_embree.cpp"
    source_paths = (source_path, *sorted((repo_root / "src" / "native" / "embree").glob("*")))
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

    newest_source_mtime = max(path.stat().st_mtime for path in source_paths)
    force_build = os.environ.get("RTDL_FORCE_EMBREE_REBUILD", "").lower() in {"1", "true", "yes"}
    needs_build = force_build or not library_path.exists() or library_path.stat().st_mtime < newest_source_mtime
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
            _run_windows_compile(command, vcvars=vcvars, cwd=repo_root)
        else:
            subprocess.run(command, check=True, cwd=repo_root)
    return library_path
