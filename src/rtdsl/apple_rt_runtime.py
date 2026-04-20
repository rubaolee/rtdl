"""Apple Metal/MPS ray-intersection backend for RTDL.

The v0.9.1 surface starts with a bounded 3D ray/triangle closest-hit
primitive backed by MPSRayIntersector. It intentionally does not claim parity
with the Linux GPU backends yet.
"""

from __future__ import annotations

import ctypes
import math
import os
import platform
from pathlib import Path

from .db_reference import GroupedAggregateQuery
from .db_reference import PredicateBundle
from .db_reference import grouped_count_cpu
from .db_reference import grouped_sum_cpu
from .db_reference import normalize_denorm_table
from .db_reference import normalize_grouped_query
from .db_reference import normalize_predicate_bundle
from .graph_reference import CSRGraph as _CanonicalCSRGraph
from .graph_reference import FrontierVertex as _CanonicalFrontierVertex
from .graph_reference import normalize_edge_set
from .graph_reference import normalize_frontier
from .graph_reference import normalize_vertex_set
from .graph_reference import validate_csr_graph
from .ir import CompiledKernel
from .reference import Point as _CanonicalPoint2D
from .reference import Point3D as _CanonicalPoint3D
from .reference import Polygon as _CanonicalPolygon
from .reference import Ray2D as _CanonicalRay2D
from .reference import Ray3D as _CanonicalRay3D
from .reference import Segment as _CanonicalSegment
from .reference import Triangle as _CanonicalTriangle2D
from .reference import Triangle3D as _CanonicalTriangle3D
from .runtime import _normalize_records
from .runtime import _run_cpu_python_reference_from_normalized
from .runtime import _resolve_kernel
from .runtime import _validate_kernel_for_cpu
from .reference import _point_in_polygon as _reference_point_in_polygon
from .reference import _point_segment_distance as _reference_point_segment_distance
from .reference import _polygon_unit_cells as _reference_polygon_unit_cells
from .reference import _segment_hits_polygon as _reference_segment_hits_polygon

APPLE_RT_NATIVE_PREDICATES = frozenset(
    {
        "bfs_discover",
        "conjunctive_scan",
        "grouped_count",
        "grouped_sum",
        "point_in_polygon",
        "point_nearest_segment",
        "overlay_compose",
        "polygon_pair_overlap_area_rows",
        "polygon_set_jaccard",
        "ray_triangle_closest_hit",
        "ray_triangle_any_hit",
        "ray_triangle_hit_count",
        "segment_intersection",
        "segment_polygon_anyhit_rows",
        "segment_polygon_hitcount",
        "triangle_match",
    }
)
APPLE_RT_METAL_COMPUTE_PREDICATES = frozenset({"bfs_discover", "conjunctive_scan", "triangle_match"})
APPLE_RT_METAL_FILTER_CPU_AGGREGATE_PREDICATES = frozenset({"grouped_count", "grouped_sum"})
APPLE_RT_COMPATIBILITY_PREDICATES = frozenset(
    {
        "bfs_discover",
        "bounded_knn_rows",
        "conjunctive_scan",
        "fixed_radius_neighbors",
        "grouped_count",
        "grouped_sum",
        "knn_rows",
        "overlay_compose",
        "point_in_polygon",
        "point_nearest_segment",
        "polygon_pair_overlap_area_rows",
        "polygon_set_jaccard",
        "ray_triangle_closest_hit",
        "ray_triangle_any_hit",
        "ray_triangle_hit_count",
        "segment_intersection",
        "segment_polygon_anyhit_rows",
        "segment_polygon_hitcount",
        "triangle_match",
    }
)

_DB_OP_EQ = 1
_DB_OP_LT = 2
_DB_OP_LE = 3
_DB_OP_GT = 4
_DB_OP_GE = 5
_DB_OP_BETWEEN = 6
_DB_OP_CODES = {
    "eq": _DB_OP_EQ,
    "lt": _DB_OP_LT,
    "le": _DB_OP_LE,
    "gt": _DB_OP_GT,
    "ge": _DB_OP_GE,
    "between": _DB_OP_BETWEEN,
}

_APPLE_RT_SUPPORT_NOTES = {
    "bfs_discover": {
        "native_candidate_discovery": "no",
        "cpu_refinement": "dedupe_and_sorted_row_materialization",
        "native_only": "supported_for_csr_frontier_vertex_set",
        "native_shapes": ("VertexFrontier/CSRGraph/VertexSet",),
        "notes": "Apple Metal compute expands CSR frontier edges and filters visited vertices; CPU performs deterministic dedupe and result ordering.",
    },
    "bounded_knn_rows": {
        "native_candidate_discovery": "shape_dependent",
        "cpu_refinement": "distance_ranking",
        "native_only": "supported_for_point2d_and_point3d",
        "native_shapes": ("Point2D/Point2D", "Point3D/Point3D"),
        "notes": "Apple Metal/MPS point-neighborhood box traversal for 2D/3D candidates, then exact distance ranking.",
    },
    "fixed_radius_neighbors": {
        "native_candidate_discovery": "shape_dependent",
        "cpu_refinement": "exact_distance_filter_and_sort",
        "native_only": "supported_for_point2d_and_point3d",
        "native_shapes": ("Point2D/Point2D", "Point3D/Point3D"),
        "notes": "Apple Metal/MPS box traversal around 2D/3D search points, then exact Euclidean filtering.",
    },
    "knn_rows": {
        "native_candidate_discovery": "shape_dependent",
        "cpu_refinement": "distance_ranking",
        "native_only": "supported_for_point2d_and_point3d",
        "native_shapes": ("Point2D/Point2D", "Point3D/Point3D"),
        "notes": "Apple Metal/MPS broad box traversal for 2D/3D candidate discovery, then exact kNN ranking.",
    },
    "point_in_polygon": {
        "native_candidate_discovery": "shape_dependent",
        "cpu_refinement": "exact_point_in_polygon",
        "native_only": "supported_for_point2d_polygon2d",
        "native_shapes": ("Point2D/Polygon2D positive_hits", "Point2D/Polygon2D full_matrix"),
        "notes": "Apple Metal/MPS polygon bounding-box traversal discovers positive hits; CPU materializes full_matrix false rows when requested.",
    },
    "point_nearest_segment": {
        "native_candidate_discovery": "yes",
        "cpu_refinement": "exact_distance_ranking",
        "native_only": "supported_for_point2d_segment2d",
        "native_shapes": ("Point2D/Segment2D",),
        "notes": "Apple Metal/MPS expanded segment-box traversal for candidates, then exact point-segment distance ranking.",
    },
    "overlay_compose": {
        "native_candidate_discovery": "yes",
        "cpu_refinement": "full_pair_row_materialization",
        "native_only": "supported_for_polygon2d_polygon2d",
        "native_shapes": ("Polygon2D/Polygon2D",),
        "notes": "Apple Metal/MPS segment-intersection and point-in-polygon traversal discover overlay flags; CPU materializes the required all-pairs rows.",
    },
    "polygon_pair_overlap_area_rows": {
        "native_candidate_discovery": "yes",
        "cpu_refinement": "exact_unit_cell_area",
        "native_only": "supported_for_polygon2d_polygon2d",
        "native_shapes": ("Polygon2D/Polygon2D",),
        "notes": "Apple Metal/MPS point-polygon and segment-polygon traversal finds candidate polygon pairs, then exact unit-cell area is computed.",
    },
    "polygon_set_jaccard": {
        "native_candidate_discovery": "yes",
        "cpu_refinement": "exact_unit_cell_set_jaccard",
        "native_only": "supported_for_polygon2d_polygon2d",
        "native_shapes": ("Polygon2D/Polygon2D",),
        "notes": "Apple Metal/MPS polygon-pair candidate discovery bounds the intersection phase; exact set areas remain CPU-refined.",
    },
    "ray_triangle_closest_hit": {
        "native_candidate_discovery": "yes",
        "cpu_refinement": "row_materialization_only",
        "native_only": "supported_for_3d",
        "native_shapes": ("Ray3D/Triangle3D",),
        "notes": "Apple Metal/MPS nearest-hit traversal over 3D triangles.",
    },
    "ray_triangle_hit_count": {
        "native_candidate_discovery": "shape_dependent",
        "cpu_refinement": "count_accumulation",
        "native_only": "supported_for_2d_and_3d",
        "native_shapes": ("Ray2D/Triangle2D", "Ray3D/Triangle3D"),
        "notes": "2D ray/triangle uses Apple Metal/MPS prism candidate traversal; 3D uses Apple Metal/MPS triangle traversal.",
    },
    "ray_triangle_any_hit": {
        "native_candidate_discovery": "shape_dependent",
        "cpu_refinement": "3d_row_materialization_or_2d_hit_count_projection",
        "native_only": "supported_for_2d_and_3d",
        "native_shapes": ("Ray2D/Triangle2D", "Ray3D/Triangle3D"),
        "notes": "Current main uses Apple Metal/MPS nearest-intersection any-hit for 3D when the loaded library exports it; 2D still uses the Apple hit-count traversal and projects hit_count > 0 to any_hit.",
    },
    "segment_intersection": {
        "native_candidate_discovery": "yes",
        "cpu_refinement": "exact_intersection_point",
        "native_only": "supported_for_2d",
        "native_shapes": ("Segment2D/Segment2D",),
        "notes": "Apple Metal/MPS traversal over extruded segment slabs plus exact CPU endpoint/intersection refinement.",
    },
    "segment_polygon_anyhit_rows": {
        "native_candidate_discovery": "yes",
        "cpu_refinement": "exact_segment_polygon",
        "native_only": "supported_for_segment2d_polygon2d",
        "native_shapes": ("Segment2D/Polygon2D",),
        "notes": "Apple Metal/MPS polygon bounding-box traversal for segment candidates, then exact segment/polygon refinement.",
    },
    "segment_polygon_hitcount": {
        "native_candidate_discovery": "yes",
        "cpu_refinement": "exact_segment_polygon",
        "native_only": "supported_for_segment2d_polygon2d",
        "native_shapes": ("Segment2D/Polygon2D",),
        "notes": "Apple Metal/MPS polygon bounding-box traversal for segment candidates, then exact hit-count refinement.",
    },
    "triangle_match": {
        "native_candidate_discovery": "no",
        "cpu_refinement": "unique_and_sorted_row_materialization",
        "native_only": "supported_for_csr_edge_seeds",
        "native_shapes": ("EdgeSet/CSRGraph",),
        "notes": "Apple Metal compute performs per-seed neighbor-list intersection; CPU preserves uniqueness and ordering.",
    },
    "conjunctive_scan": {
        "native_candidate_discovery": "no",
        "cpu_refinement": "row_id_materialization_only",
        "native_only": "supported_for_numeric_predicates",
        "native_shapes": ("PredicateSet/DenormTable numeric",),
        "notes": "Apple Metal compute evaluates bounded numeric conjunctive predicates over packed table columns; CPU only packs inputs and materializes matched row_ids.",
    },
    "grouped_count": {
        "native_candidate_discovery": "no",
        "cpu_refinement": "cpu_group_aggregation_after_metal_filter",
        "native_only": "supported_for_numeric_predicates_cpu_aggregation",
        "native_shapes": ("GroupedQuery/DenormTable numeric predicates",),
        "notes": "Apple Metal compute evaluates bounded numeric predicate filters, then CPU performs deterministic grouped count aggregation.",
    },
    "grouped_sum": {
        "native_candidate_discovery": "no",
        "cpu_refinement": "cpu_group_aggregation_after_metal_filter",
        "native_only": "supported_for_numeric_predicates_cpu_aggregation",
        "native_shapes": ("GroupedQuery/DenormTable numeric predicates",),
        "notes": "Apple Metal compute evaluates bounded numeric predicate filters, then CPU performs deterministic grouped sum aggregation.",
    },
}


def _apple_rt_support_notes(predicate_name: str) -> dict[str, object]:
    if predicate_name in _APPLE_RT_SUPPORT_NOTES:
        return dict(_APPLE_RT_SUPPORT_NOTES[predicate_name])
    return {
        "native_candidate_discovery": "no",
        "cpu_refinement": "full_cpu_reference_compat",
        "native_only": "unsupported_until_v0_9_3_native_lowering",
        "native_shapes": (),
        "notes": "Callable through run_apple_rt compatibility dispatch, but not Apple hardware-backed yet.",
    }


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


class _RtdlTriangle2D(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("x1", ctypes.c_double),
        ("y1", ctypes.c_double),
        ("x2", ctypes.c_double),
        ("y2", ctypes.c_double),
    ]


class _RtdlPoint2D(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]


class _RtdlPoint3D(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double),
    ]


class _RtdlSegment(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("x1", ctypes.c_double),
        ("y1", ctypes.c_double),
    ]


class _RtdlLsiRow(ctypes.Structure):
    _fields_ = [
        ("left_id", ctypes.c_uint32),
        ("right_id", ctypes.c_uint32),
        ("intersection_point_x", ctypes.c_double),
        ("intersection_point_y", ctypes.c_double),
    ]


class _RtdlRayClosestHitRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("triangle_id", ctypes.c_uint32),
        ("t", ctypes.c_double),
    ]


class _RtdlRayHitCountRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("hit_count", ctypes.c_uint32),
    ]


class _RtdlRayAnyHitRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("any_hit", ctypes.c_uint32),
    ]


class _RtdlNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
    ]


class _RtdlPolygonBounds2D(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("minx", ctypes.c_double),
        ("miny", ctypes.c_double),
        ("maxx", ctypes.c_double),
        ("maxy", ctypes.c_double),
    ]


class _RtdlPointPolygonCandidateRow(ctypes.Structure):
    _fields_ = [
        ("point_id", ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
    ]


class _RtdlSegmentPolygonCandidateRow(ctypes.Structure):
    _fields_ = [
        ("segment_id", ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
    ]


class _RtdlAppleDbNumericClause(ctypes.Structure):
    _fields_ = [
        ("field_index", ctypes.c_uint32),
        ("op", ctypes.c_uint32),
        ("value", ctypes.c_float),
        ("value_hi", ctypes.c_float),
    ]


class _RtdlAppleFrontierVertex(ctypes.Structure):
    _fields_ = [
        ("vertex_id", ctypes.c_uint32),
        ("level", ctypes.c_uint32),
    ]


class _RtdlAppleBfsRow(ctypes.Structure):
    _fields_ = [
        ("src_vertex", ctypes.c_uint32),
        ("dst_vertex", ctypes.c_uint32),
        ("level", ctypes.c_uint32),
    ]


class _RtdlAppleEdgeSeed(ctypes.Structure):
    _fields_ = [
        ("u", ctypes.c_uint32),
        ("v", ctypes.c_uint32),
    ]


class _RtdlAppleTriangleRow(ctypes.Structure):
    _fields_ = [
        ("u", ctypes.c_uint32),
        ("v", ctypes.c_uint32),
        ("w", ctypes.c_uint32),
    ]


_LIBRARY: ctypes.CDLL | None = None


class AppleRtRowView:
    def __init__(self, *, library: ctypes.CDLL, rows_ptr, row_count: int, row_type, field_names: tuple[str, ...]):
        self._library = library
        self._rows_ptr = rows_ptr
        self._row_count = int(row_count)
        self._row_type = row_type
        self._field_names = field_names
        self._freed = False

    def __iter__(self):
        for index in range(self._row_count):
            row = self._rows_ptr[index]
            yield {field: getattr(row, field) for field in self._field_names}

    def __len__(self) -> int:
        return self._row_count

    def __getitem__(self, index: int) -> dict[str, object]:
        if index < 0:
            index += self._row_count
        if index < 0 or index >= self._row_count:
            raise IndexError(index)
        row = self._rows_ptr[index]
        return {field: getattr(row, field) for field in self._field_names}

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        if self._freed:
            return
        if bool(self._rows_ptr):
            self._library.rtdl_apple_rt_free_rows(self._rows_ptr)
        self._freed = True


def _candidate_library_paths() -> list[Path]:
    env = os.environ.get("RTDL_APPLE_RT_LIB")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env))
    root = Path(__file__).resolve().parents[2]
    candidates.append(root / "build" / "librtdl_apple_rt.dylib")
    return candidates


def _load_library() -> ctypes.CDLL:
    global _LIBRARY
    if _LIBRARY is not None:
        return _LIBRARY
    if platform.system() != "Darwin":
        raise RuntimeError("Apple RT backend is only available on macOS")
    errors: list[str] = []
    for path in _candidate_library_paths():
        try:
            library = ctypes.CDLL(str(path))
        except OSError as exc:
            errors.append(f"{path}: {exc}")
            continue
        _configure_library(library)
        _LIBRARY = library
        return library
    raise RuntimeError("Apple RT backend library not found; run `make build-apple-rt`. Tried: " + "; ".join(errors))


def _configure_library(library: ctypes.CDLL) -> None:
    library.rtdl_apple_rt_get_version.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    library.rtdl_apple_rt_get_version.restype = ctypes.c_int
    library.rtdl_apple_rt_free_rows.argtypes = [ctypes.c_void_p]
    library.rtdl_apple_rt_free_rows.restype = None
    library.rtdl_apple_rt_context_probe.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
    library.rtdl_apple_rt_context_probe.restype = ctypes.c_int
    library.rtdl_apple_rt_run_u32_add_compute.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_u32_add_compute.restype = ctypes.c_int
    library.rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlAppleDbNumericClause),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute.restype = ctypes.c_int
    library.rtdl_apple_rt_run_bfs_discover_compute.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlAppleFrontierVertex),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlAppleBfsRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_bfs_discover_compute.restype = ctypes.c_int
    library.rtdl_apple_rt_run_triangle_match_compute.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlAppleEdgeSeed),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlAppleTriangleRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_triangle_match_compute.restype = ctypes.c_int
    library.rtdl_apple_rt_run_ray_closest_hit_3d.argtypes = [
        ctypes.POINTER(_RtdlRay3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle3D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayClosestHitRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_ray_closest_hit_3d.restype = ctypes.c_int
    library.rtdl_apple_rt_prepare_ray_closest_hit_3d.argtypes = [
        ctypes.POINTER(_RtdlTriangle3D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_prepare_ray_closest_hit_3d.restype = ctypes.c_int
    library.rtdl_apple_rt_run_prepared_ray_closest_hit_3d.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_RtdlRay3D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayClosestHitRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_prepared_ray_closest_hit_3d.restype = ctypes.c_int
    library.rtdl_apple_rt_destroy_prepared_ray_closest_hit_3d.argtypes = [ctypes.c_void_p]
    library.rtdl_apple_rt_destroy_prepared_ray_closest_hit_3d.restype = None
    library.rtdl_apple_rt_run_ray_hitcount_3d.argtypes = [
        ctypes.POINTER(_RtdlRay3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle3D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_ray_hitcount_3d.restype = ctypes.c_int
    optional_anyhit_3d = getattr(library, "rtdl_apple_rt_run_ray_anyhit_3d", None)
    if optional_anyhit_3d is not None:
        optional_anyhit_3d.argtypes = [
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlTriangle3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayAnyHitRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_anyhit_3d.restype = ctypes.c_int
    library.rtdl_apple_rt_run_ray_hitcount_2d.argtypes = [
        ctypes.POINTER(_RtdlRay2D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle2D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_ray_hitcount_2d.restype = ctypes.c_int
    library.rtdl_apple_rt_run_fixed_radius_neighbors_2d.argtypes = [
        ctypes.POINTER(_RtdlPoint2D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint2D),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_fixed_radius_neighbors_2d.restype = ctypes.c_int
    library.rtdl_apple_rt_run_fixed_radius_neighbors_3d.argtypes = [
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_fixed_radius_neighbors_3d.restype = ctypes.c_int
    library.rtdl_apple_rt_run_point_polygon_candidates_2d.argtypes = [
        ctypes.POINTER(_RtdlPoint2D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonBounds2D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPointPolygonCandidateRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_point_polygon_candidates_2d.restype = ctypes.c_int
    library.rtdl_apple_rt_run_segment_polygon_candidates_2d.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonBounds2D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonCandidateRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_segment_polygon_candidates_2d.restype = ctypes.c_int
    library.rtdl_apple_rt_run_lsi.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_lsi.restype = ctypes.c_int


def _check_status(status: int, error_buffer: ctypes.Array[ctypes.c_char]) -> None:
    if status == 0:
        return
    message = error_buffer.value.decode("utf-8", errors="replace") or f"Apple RT backend returned status {status}"
    raise RuntimeError(message)


def apple_rt_version() -> tuple[int, int, int]:
    library = _load_library()
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    status = library.rtdl_apple_rt_get_version(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch))
    if status != 0:
        raise RuntimeError("Apple RT backend rejected version query")
    return (major.value, minor.value, patch.value)


def apple_rt_context_probe() -> str:
    library = _load_library()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_context_probe(error, len(error))
    _check_status(status, error)
    return error.value.decode("utf-8", errors="replace")


def apple_rt_compute_u32_add(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    """Run the v0.9.4 Apple Metal compute smoke kernel.

    This helper is intentionally not a workload API. It proves the backend can
    compile a Metal compute kernel, dispatch over buffers, and return data.
    """
    if len(left) != len(right):
        raise ValueError("Apple RT compute add requires equal-length inputs")
    for value in (*left, *right):
        if not isinstance(value, int) or value < 0 or value > 0xFFFFFFFF:
            raise ValueError("Apple RT compute add inputs must be uint32 values")
    if not left:
        return ()

    library = _load_library()
    left_records = (ctypes.c_uint32 * len(left))(*left)
    right_records = (ctypes.c_uint32 * len(right))(*right)
    values_ptr = ctypes.POINTER(ctypes.c_uint32)()
    value_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_u32_add_compute(
        left_records,
        right_records,
        len(left),
        ctypes.byref(values_ptr),
        ctypes.byref(value_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(int(values_ptr[index]) for index in range(value_count.value))
    finally:
        if bool(values_ptr):
            library.rtdl_apple_rt_free_rows(values_ptr)


def _numeric_db_value(value, *, role: str) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, int):
        if abs(value) > 2**24:
            raise ValueError(f"Apple RT DB numeric scan {role} integer exceeds exact float32 range")
        return float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"Apple RT DB numeric scan {role} float must be finite")
        return float(value)
    raise ValueError(f"Apple RT DB numeric scan {role} must be bool, int, or float")


def _normalize_apple_db_predicates(predicates) -> PredicateBundle:
    bundle = normalize_predicate_bundle(predicates)
    for clause in bundle.clauses:
        _numeric_db_value(clause.value, role=f"predicate `{clause.field}` value")
        if clause.op == "between":
            _numeric_db_value(clause.value_hi, role=f"predicate `{clause.field}` upper value")
    return bundle


def conjunctive_scan_apple_rt(table_rows, predicates) -> tuple[dict[str, int], ...]:
    """Run bounded numeric DB conjunctive_scan with Apple Metal compute filtering."""
    table = normalize_denorm_table(table_rows)
    bundle = _normalize_apple_db_predicates(predicates)
    if not table:
        return ()

    predicate_fields = tuple(dict.fromkeys(str(clause.field) for clause in bundle.clauses)) or ("row_id",)
    field_to_index = {field: index for index, field in enumerate(predicate_fields)}
    row_ids = []
    values = []
    first_schema = set(str(name) for name in table[0].keys())
    for row_index, row in enumerate(table):
        if set(str(name) for name in row.keys()) != first_schema:
            raise ValueError(f"Apple RT DB scan row {row_index} does not match the first-row schema")
        row_ids.append(int(row["row_id"]))
        for field in predicate_fields:
            if field not in row:
                raise ValueError(f"Apple RT DB scan row {row_index} is missing predicate field `{field}`")
            values.append(_numeric_db_value(row[field], role=f"row {row_index} field `{field}`"))

    clause_records = []
    for clause in bundle.clauses:
        clause_records.append(
            _RtdlAppleDbNumericClause(
                field_to_index[str(clause.field)],
                _DB_OP_CODES[str(clause.op)],
                _numeric_db_value(clause.value, role=f"predicate `{clause.field}` value"),
                0.0 if clause.value_hi is None else _numeric_db_value(clause.value_hi, role=f"predicate `{clause.field}` upper value"),
            )
        )

    library = _load_library()
    row_ids_array = (ctypes.c_uint32 * len(row_ids))(*row_ids)
    values_array = (ctypes.c_float * len(values))(*values)
    clauses_array = (_RtdlAppleDbNumericClause * len(clause_records))(*clause_records)
    rows_ptr = ctypes.POINTER(ctypes.c_uint32)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute(
        row_ids_array,
        values_array,
        len(row_ids),
        len(predicate_fields),
        clauses_array,
        len(clause_records),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple({"row_id": int(rows_ptr[index])} for index in range(row_count.value))
    finally:
        if bool(rows_ptr):
            library.rtdl_apple_rt_free_rows(rows_ptr)


def _filter_table_rows_with_apple_metal(table, predicates) -> tuple[dict[str, object], ...]:
    row_ids = [int(row["row_id"]) for row in table]
    if len(set(row_ids)) != len(row_ids):
        raise ValueError("Apple RT grouped DB path requires unique row_id values")
    matched = conjunctive_scan_apple_rt(table, PredicateBundle(tuple(predicates)))
    matched_ids = {int(row["row_id"]) for row in matched}
    return tuple(row for row in table if int(row["row_id"]) in matched_ids)


def grouped_count_apple_rt(table_rows, query) -> tuple[dict[str, object], ...]:
    """Run grouped_count with Apple Metal predicate filtering and CPU aggregation."""
    table = normalize_denorm_table(table_rows)
    grouped_query = normalize_grouped_query(query)
    if not table:
        return ()
    filtered = _filter_table_rows_with_apple_metal(table, grouped_query.predicates)
    return grouped_count_cpu(
        filtered,
        GroupedAggregateQuery(predicates=(), group_keys=grouped_query.group_keys),
    )


def grouped_sum_apple_rt(table_rows, query) -> tuple[dict[str, object], ...]:
    """Run grouped_sum with Apple Metal predicate filtering and CPU aggregation."""
    table = normalize_denorm_table(table_rows)
    grouped_query = normalize_grouped_query(query)
    if not table:
        return ()
    filtered = _filter_table_rows_with_apple_metal(table, grouped_query.predicates)
    return grouped_sum_cpu(
        filtered,
        GroupedAggregateQuery(
            predicates=(),
            group_keys=grouped_query.group_keys,
            value_field=grouped_query.value_field,
        ),
    )


def bfs_discover_apple_rt(
    graph,
    frontier,
    visited,
    *,
    dedupe: bool = True,
) -> tuple[dict[str, int], ...]:
    """Run BFS discovery with Apple Metal frontier expansion and CPU ordering."""
    graph_record = graph if isinstance(graph, _CanonicalCSRGraph) else _normalize_records("graph", "graph_csr", graph)
    validate_csr_graph(graph_record)
    frontier_records = normalize_frontier(frontier)
    visited_records = normalize_vertex_set(visited)
    if not frontier_records:
        return ()

    frontier_edge_offsets = [0]
    for item in frontier_records:
        if item.vertex_id < 0 or item.vertex_id >= graph_record.vertex_count:
            raise ValueError("Apple RT BFS frontier vertex_id must be a valid graph vertex")
        degree = graph_record.row_offsets[item.vertex_id + 1] - graph_record.row_offsets[item.vertex_id]
        frontier_edge_offsets.append(frontier_edge_offsets[-1] + degree)
    output_capacity = frontier_edge_offsets[-1]
    if output_capacity == 0:
        return ()

    library = _load_library()
    row_offsets_array = (ctypes.c_uint32 * len(graph_record.row_offsets))(*graph_record.row_offsets)
    column_indices_array = (ctypes.c_uint32 * max(1, len(graph_record.column_indices)))(*(graph_record.column_indices or (0,)))
    frontier_array = (_RtdlAppleFrontierVertex * len(frontier_records))(
        *[_RtdlAppleFrontierVertex(item.vertex_id, item.level) for item in frontier_records]
    )
    frontier_offsets_array = (ctypes.c_uint32 * len(frontier_edge_offsets))(*frontier_edge_offsets)
    visited_array = (ctypes.c_uint32 * max(1, len(visited_records)))(*(visited_records or (0,)))
    rows_ptr = ctypes.POINTER(_RtdlAppleBfsRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_bfs_discover_compute(
        row_offsets_array,
        len(graph_record.row_offsets),
        column_indices_array,
        len(graph_record.column_indices),
        frontier_array,
        len(frontier_records),
        frontier_offsets_array,
        output_capacity,
        visited_array,
        len(visited_records),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        rows = []
        seen: set[int] = set()
        for index in range(row_count.value):
            row = rows_ptr[index]
            dst = int(row.dst_vertex)
            if dedupe and dst in seen:
                continue
            seen.add(dst)
            rows.append(
                {
                    "src_vertex": int(row.src_vertex),
                    "dst_vertex": dst,
                    "level": int(row.level),
                }
            )
    finally:
        if bool(rows_ptr):
            library.rtdl_apple_rt_free_rows(rows_ptr)
    rows.sort(key=lambda row: (row["level"], row["dst_vertex"], row["src_vertex"]))
    return tuple(rows)


def triangle_match_apple_rt(
    graph,
    seeds,
    *,
    order: str = "id_ascending",
    unique: bool = True,
) -> tuple[dict[str, int], ...]:
    """Run triangle matching with Apple Metal neighbor intersection and CPU uniqueness/order."""
    if order != "id_ascending":
        raise ValueError("triangle_match_apple_rt currently supports only order='id_ascending'")
    graph_record = graph if isinstance(graph, _CanonicalCSRGraph) else _normalize_records("graph", "graph_csr", graph)
    validate_csr_graph(graph_record)
    seed_records = normalize_edge_set(seeds)
    if not seed_records:
        return ()

    seed_output_offsets = [0]
    for seed in seed_records:
        if seed.u < 0 or seed.u >= graph_record.vertex_count or seed.v < 0 or seed.v >= graph_record.vertex_count:
            raise ValueError("Apple RT triangle_match seed vertices must be valid graph vertex IDs")
        degree = graph_record.row_offsets[seed.u + 1] - graph_record.row_offsets[seed.u]
        seed_output_offsets.append(seed_output_offsets[-1] + degree)
    output_capacity = seed_output_offsets[-1]
    if output_capacity == 0:
        return ()

    library = _load_library()
    row_offsets_array = (ctypes.c_uint32 * len(graph_record.row_offsets))(*graph_record.row_offsets)
    column_indices_array = (ctypes.c_uint32 * max(1, len(graph_record.column_indices)))(*(graph_record.column_indices or (0,)))
    seeds_array = (_RtdlAppleEdgeSeed * len(seed_records))(*[_RtdlAppleEdgeSeed(item.u, item.v) for item in seed_records])
    seed_offsets_array = (ctypes.c_uint32 * len(seed_output_offsets))(*seed_output_offsets)
    rows_ptr = ctypes.POINTER(_RtdlAppleTriangleRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_triangle_match_compute(
        row_offsets_array,
        len(graph_record.row_offsets),
        column_indices_array,
        len(graph_record.column_indices),
        seeds_array,
        len(seed_records),
        seed_offsets_array,
        output_capacity,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        rows = []
        seen: set[tuple[int, int, int]] = set()
        for index in range(row_count.value):
            row = rows_ptr[index]
            triangle = (int(row.u), int(row.v), int(row.w))
            if unique and triangle in seen:
                continue
            seen.add(triangle)
            rows.append({"u": triangle[0], "v": triangle[1], "w": triangle[2]})
    finally:
        if bool(rows_ptr):
            library.rtdl_apple_rt_free_rows(rows_ptr)
    rows.sort(key=lambda row: (row["u"], row["v"], row["w"]))
    return tuple(rows)


def _pack_rays_3d(rays: tuple[_CanonicalRay3D, ...]):
    records = (_RtdlRay3D * len(rays))()
    for index, ray in enumerate(rays):
        records[index] = _RtdlRay3D(ray.id, ray.ox, ray.oy, ray.oz, ray.dx, ray.dy, ray.dz, ray.tmax)
    return records


def _pack_triangles_3d(triangles: tuple[_CanonicalTriangle3D, ...]):
    records = (_RtdlTriangle3D * len(triangles))()
    for index, triangle in enumerate(triangles):
        records[index] = _RtdlTriangle3D(
            triangle.id,
            triangle.x0,
            triangle.y0,
            triangle.z0,
            triangle.x1,
            triangle.y1,
            triangle.z1,
            triangle.x2,
            triangle.y2,
            triangle.z2,
        )
    return records


def _pack_rays_2d(rays: tuple[_CanonicalRay2D, ...]):
    records = (_RtdlRay2D * len(rays))()
    for index, ray in enumerate(rays):
        records[index] = _RtdlRay2D(ray.id, ray.ox, ray.oy, ray.dx, ray.dy, ray.tmax)
    return records


def _pack_triangles_2d(triangles: tuple[_CanonicalTriangle2D, ...]):
    records = (_RtdlTriangle2D * len(triangles))()
    for index, triangle in enumerate(triangles):
        records[index] = _RtdlTriangle2D(
            triangle.id,
            triangle.x0,
            triangle.y0,
            triangle.x1,
            triangle.y1,
            triangle.x2,
            triangle.y2,
        )
    return records


def _pack_points_2d(points: tuple[_CanonicalPoint2D, ...]):
    records = (_RtdlPoint2D * len(points))()
    for index, point in enumerate(points):
        records[index] = _RtdlPoint2D(point.id, point.x, point.y)
    return records


def _pack_points_3d(points: tuple[_CanonicalPoint3D, ...]):
    records = (_RtdlPoint3D * len(points))()
    for index, point in enumerate(points):
        records[index] = _RtdlPoint3D(point.id, point.x, point.y, point.z)
    return records


def _polygon_bounds_2d(polygon: _CanonicalPolygon) -> tuple[float, float, float, float]:
    xs = [x for x, _ in polygon.vertices]
    ys = [y for _, y in polygon.vertices]
    return (min(xs), min(ys), max(xs), max(ys))


def _pack_polygon_bounds_2d(polygons: tuple[_CanonicalPolygon, ...]):
    records = (_RtdlPolygonBounds2D * len(polygons))()
    for index, polygon in enumerate(polygons):
        minx, miny, maxx, maxy = _polygon_bounds_2d(polygon)
        records[index] = _RtdlPolygonBounds2D(polygon.id, minx, miny, maxx, maxy)
    return records


def _pack_segments(segments: tuple[_CanonicalSegment, ...]):
    records = (_RtdlSegment * len(segments))()
    for index, segment in enumerate(segments):
        records[index] = _RtdlSegment(segment.id, segment.x0, segment.y0, segment.x1, segment.y1)
    return records


def ray_triangle_closest_hit_apple_rt(
    rays: tuple[_CanonicalRay3D, ...],
    triangles: tuple[_CanonicalTriangle3D, ...],
) -> AppleRtRowView:
    if any(not isinstance(ray, _CanonicalRay3D) for ray in rays):
        raise ValueError("Apple RT ray_triangle_closest_hit currently requires 3D rays")
    if any(not isinstance(triangle, _CanonicalTriangle3D) for triangle in triangles):
        raise ValueError("Apple RT ray_triangle_closest_hit currently requires 3D triangles")
    library = _load_library()
    ray_records = _pack_rays_3d(rays)
    triangle_records = _pack_triangles_3d(triangles)
    rows_ptr = ctypes.POINTER(_RtdlRayClosestHitRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_ray_closest_hit_3d(
        ray_records,
        len(rays),
        triangle_records,
        len(triangles),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return AppleRtRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlRayClosestHitRow,
        field_names=("ray_id", "triangle_id", "t"),
    )


class PreparedAppleRtRayTriangleClosestHit3D:
    def __init__(self, triangles: tuple[_CanonicalTriangle3D, ...]):
        if any(not isinstance(triangle, _CanonicalTriangle3D) for triangle in triangles):
            raise ValueError("prepared Apple RT ray_triangle_closest_hit currently requires 3D triangles")
        self._library = _load_library()
        self._closed = False
        triangle_records = _pack_triangles_3d(triangles)
        handle = ctypes.c_void_p()
        error = ctypes.create_string_buffer(4096)
        status = self._library.rtdl_apple_rt_prepare_ray_closest_hit_3d(
            triangle_records,
            len(triangles),
            ctypes.byref(handle),
            error,
            len(error),
        )
        _check_status(status, error)
        self._handle = handle

    def run(self, rays: tuple[_CanonicalRay3D, ...]) -> AppleRtRowView:
        if self._closed:
            raise RuntimeError("prepared Apple RT closest-hit handle is closed")
        if any(not isinstance(ray, _CanonicalRay3D) for ray in rays):
            raise ValueError("prepared Apple RT ray_triangle_closest_hit currently requires 3D rays")
        ray_records = _pack_rays_3d(rays)
        rows_ptr = ctypes.POINTER(_RtdlRayClosestHitRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self._library.rtdl_apple_rt_run_prepared_ray_closest_hit_3d(
            self._handle,
            ray_records,
            len(rays),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return AppleRtRowView(
            library=self._library,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlRayClosestHitRow,
            field_names=("ray_id", "triangle_id", "t"),
        )

    def close(self) -> None:
        if self._closed:
            return
        if self._handle:
            self._library.rtdl_apple_rt_destroy_prepared_ray_closest_hit_3d(self._handle)
        self._closed = True

    def __enter__(self) -> "PreparedAppleRtRayTriangleClosestHit3D":
        if self._closed:
            raise RuntimeError("prepared Apple RT closest-hit handle is closed")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()


def prepare_apple_rt_ray_triangle_closest_hit(
    triangles: tuple[_CanonicalTriangle3D, ...],
) -> PreparedAppleRtRayTriangleClosestHit3D:
    return PreparedAppleRtRayTriangleClosestHit3D(triangles)


def segment_intersection_apple_rt(
    left_segments: tuple[_CanonicalSegment, ...],
    right_segments: tuple[_CanonicalSegment, ...],
) -> AppleRtRowView:
    if any(not isinstance(segment, _CanonicalSegment) for segment in left_segments):
        raise ValueError("Apple RT segment_intersection currently requires 2D segments on the left")
    if any(not isinstance(segment, _CanonicalSegment) for segment in right_segments):
        raise ValueError("Apple RT segment_intersection currently requires 2D segments on the right")
    library = _load_library()
    left_records = _pack_segments(left_segments)
    right_records = _pack_segments(right_segments)
    rows_ptr = ctypes.POINTER(_RtdlLsiRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_lsi(
        left_records,
        len(left_segments),
        right_records,
        len(right_segments),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return AppleRtRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlLsiRow,
        field_names=("left_id", "right_id", "intersection_point_x", "intersection_point_y"),
    )


def ray_triangle_hit_count_apple_rt(
    rays: tuple[_CanonicalRay2D | _CanonicalRay3D, ...],
    triangles: tuple[_CanonicalTriangle2D | _CanonicalTriangle3D, ...],
) -> AppleRtRowView:
    library = _load_library()
    if all(isinstance(ray, _CanonicalRay2D) for ray in rays) and all(
        isinstance(triangle, _CanonicalTriangle2D) for triangle in triangles
    ):
        ray_records = _pack_rays_2d(rays)
        triangle_records = _pack_triangles_2d(triangles)
        rows_ptr = ctypes.POINTER(_RtdlRayHitCountRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = library.rtdl_apple_rt_run_ray_hitcount_2d(
            ray_records,
            len(rays),
            triangle_records,
            len(triangles),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return AppleRtRowView(
            library=library,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlRayHitCountRow,
            field_names=("ray_id", "hit_count"),
        )
    if any(not isinstance(ray, _CanonicalRay3D) for ray in rays):
        raise ValueError("Apple RT ray_triangle_hit_count requires all rays to be Ray2D or all rays to be Ray3D")
    if any(not isinstance(triangle, _CanonicalTriangle3D) for triangle in triangles):
        raise ValueError("Apple RT ray_triangle_hit_count requires all triangles to be Triangle2D or all triangles to be Triangle3D")
    ray_records = _pack_rays_3d(rays)
    triangle_records = _pack_triangles_3d(triangles)
    rows_ptr = ctypes.POINTER(_RtdlRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_ray_hitcount_3d(
        ray_records,
        len(rays),
        triangle_records,
        len(triangles),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return AppleRtRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlRayHitCountRow,
        field_names=("ray_id", "hit_count"),
    )


def ray_triangle_any_hit_apple_rt(
    rays: tuple[_CanonicalRay2D | _CanonicalRay3D, ...],
    triangles: tuple[_CanonicalTriangle2D | _CanonicalTriangle3D, ...],
) -> tuple[dict[str, int], ...]:
    if all(isinstance(ray, _CanonicalRay3D) for ray in rays) and all(
        isinstance(triangle, _CanonicalTriangle3D) for triangle in triangles
    ):
        library = _load_library()
        native_anyhit = getattr(library, "rtdl_apple_rt_run_ray_anyhit_3d", None)
        if native_anyhit is not None:
            ray_records = _pack_rays_3d(rays)
            triangle_records = _pack_triangles_3d(triangles)
            rows_ptr = ctypes.POINTER(_RtdlRayAnyHitRow)()
            row_count = ctypes.c_size_t()
            error = ctypes.create_string_buffer(4096)
            status = native_anyhit(
                ray_records,
                len(rays),
                triangle_records,
                len(triangles),
                ctypes.byref(rows_ptr),
                ctypes.byref(row_count),
                error,
                len(error),
            )
            _check_status(status, error)
            rows = AppleRtRowView(
                library=library,
                rows_ptr=rows_ptr,
                row_count=row_count.value,
                row_type=_RtdlRayAnyHitRow,
                field_names=("ray_id", "any_hit"),
            )
            try:
                return tuple(rows)
            finally:
                rows.close()
    rows = ray_triangle_hit_count_apple_rt(rays, triangles)
    try:
        return tuple(
            {
                "ray_id": int(row["ray_id"]),
                "any_hit": 1 if int(row["hit_count"]) else 0,
            }
            for row in rows
        )
    finally:
        rows.close()


def fixed_radius_neighbors_2d_apple_rt(
    query_points: tuple[_CanonicalPoint2D, ...],
    search_points: tuple[_CanonicalPoint2D, ...],
    *,
    radius: float,
    k_max: int,
) -> AppleRtRowView:
    if any(not isinstance(point, _CanonicalPoint2D) for point in query_points):
        raise ValueError("Apple RT fixed_radius_neighbors_2d currently requires 2D query points")
    if any(not isinstance(point, _CanonicalPoint2D) for point in search_points):
        raise ValueError("Apple RT fixed_radius_neighbors_2d currently requires 2D search points")
    if radius < 0.0:
        raise ValueError("Apple RT fixed_radius_neighbors_2d radius must be non-negative")
    if k_max <= 0:
        raise ValueError("Apple RT fixed_radius_neighbors_2d k_max must be positive")
    library = _load_library()
    query_records = _pack_points_2d(query_points)
    search_records = _pack_points_2d(search_points)
    rows_ptr = ctypes.POINTER(_RtdlNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_fixed_radius_neighbors_2d(
        query_records,
        len(query_points),
        search_records,
        len(search_points),
        float(radius),
        int(k_max),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return AppleRtRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlNeighborRow,
        field_names=("query_id", "neighbor_id", "distance"),
    )


def fixed_radius_neighbors_3d_apple_rt(
    query_points: tuple[_CanonicalPoint3D, ...],
    search_points: tuple[_CanonicalPoint3D, ...],
    *,
    radius: float,
    k_max: int,
) -> AppleRtRowView:
    if any(not isinstance(point, _CanonicalPoint3D) for point in query_points):
        raise ValueError("Apple RT fixed_radius_neighbors_3d currently requires 3D query points")
    if any(not isinstance(point, _CanonicalPoint3D) for point in search_points):
        raise ValueError("Apple RT fixed_radius_neighbors_3d currently requires 3D search points")
    if radius < 0.0:
        raise ValueError("Apple RT fixed_radius_neighbors_3d radius must be non-negative")
    if k_max <= 0:
        raise ValueError("Apple RT fixed_radius_neighbors_3d k_max must be positive")
    library = _load_library()
    query_records = _pack_points_3d(query_points)
    search_records = _pack_points_3d(search_points)
    rows_ptr = ctypes.POINTER(_RtdlNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_fixed_radius_neighbors_3d(
        query_records,
        len(query_points),
        search_records,
        len(search_points),
        float(radius),
        int(k_max),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return AppleRtRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlNeighborRow,
        field_names=("query_id", "neighbor_id", "distance"),
    )


def point_in_polygon_positive_hits_apple_rt(
    points: tuple[_CanonicalPoint2D, ...],
    polygons: tuple[_CanonicalPolygon, ...],
    *,
    boundary_mode: str = "inclusive",
) -> tuple[dict[str, object], ...]:
    if any(not isinstance(point, _CanonicalPoint2D) for point in points):
        raise ValueError("Apple RT point_in_polygon currently requires 2D point inputs")
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in polygons):
        raise ValueError("Apple RT point_in_polygon currently requires 2D polygon inputs")
    if boundary_mode != "inclusive":
        raise ValueError("Apple RT point_in_polygon currently supports only boundary_mode='inclusive'")
    library = _load_library()
    point_records = _pack_points_2d(points)
    polygon_records = _pack_polygon_bounds_2d(polygons)
    rows_ptr = ctypes.POINTER(_RtdlPointPolygonCandidateRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_point_polygon_candidates_2d(
        point_records,
        len(points),
        polygon_records,
        len(polygons),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    point_by_id = {point.id: point for point in points}
    polygon_by_id = {polygon.id: polygon for polygon in polygons}
    rows = []
    try:
        for index in range(row_count.value):
            candidate = rows_ptr[index]
            point = point_by_id[int(candidate.point_id)]
            polygon = polygon_by_id[int(candidate.polygon_id)]
            if _reference_point_in_polygon(point.x, point.y, polygon.vertices, boundary_mode=boundary_mode):
                rows.append({"point_id": point.id, "polygon_id": polygon.id, "contains": 1})
    finally:
        if bool(rows_ptr):
            library.rtdl_apple_rt_free_rows(rows_ptr)
    return tuple(rows)


def point_in_polygon_full_matrix_apple_rt(
    points: tuple[_CanonicalPoint2D, ...],
    polygons: tuple[_CanonicalPolygon, ...],
    *,
    boundary_mode: str = "inclusive",
) -> tuple[dict[str, object], ...]:
    positive_pairs = {
        (int(row["point_id"]), int(row["polygon_id"]))
        for row in point_in_polygon_positive_hits_apple_rt(points, polygons, boundary_mode=boundary_mode)
    }
    return tuple(
        {"point_id": point.id, "polygon_id": polygon.id, "contains": 1 if (point.id, polygon.id) in positive_pairs else 0}
        for point in points
        for polygon in polygons
    )


def _point_segment_candidate_radius(
    points: tuple[_CanonicalPoint2D, ...],
    segments: tuple[_CanonicalSegment, ...],
) -> float:
    xs = [point.x for point in points]
    ys = [point.y for point in points]
    for segment in segments:
        xs.extend((segment.x0, segment.x1))
        ys.extend((segment.y0, segment.y1))
    if not xs or not ys:
        return 0.0
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    return (dx * dx + dy * dy) ** 0.5 + 1.0e-6


def point_segment_candidates_apple_rt(
    points: tuple[_CanonicalPoint2D, ...],
    segments: tuple[_CanonicalSegment, ...],
) -> tuple[dict[str, object], ...]:
    if any(not isinstance(point, _CanonicalPoint2D) for point in points):
        raise ValueError("Apple RT point_nearest_segment currently requires 2D point inputs")
    if any(not isinstance(segment, _CanonicalSegment) for segment in segments):
        raise ValueError("Apple RT point_nearest_segment currently requires 2D segment inputs")
    if not points or not segments:
        return ()
    radius = _point_segment_candidate_radius(points, segments)
    segment_boxes = (_RtdlPolygonBounds2D * len(segments))()
    for index, segment in enumerate(segments):
        segment_boxes[index] = _RtdlPolygonBounds2D(
            segment.id,
            min(segment.x0, segment.x1) - radius,
            min(segment.y0, segment.y1) - radius,
            max(segment.x0, segment.x1) + radius,
            max(segment.y0, segment.y1) + radius,
        )
    library = _load_library()
    point_records = _pack_points_2d(points)
    rows_ptr = ctypes.POINTER(_RtdlPointPolygonCandidateRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_point_polygon_candidates_2d(
        point_records,
        len(points),
        segment_boxes,
        len(segments),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        candidates = {
            (int(rows_ptr[index].point_id), int(rows_ptr[index].polygon_id))
            for index in range(row_count.value)
        }
    finally:
        if bool(rows_ptr):
            library.rtdl_apple_rt_free_rows(rows_ptr)
    return tuple(
        {"point_id": point_id, "segment_id": segment_id}
        for point_id, segment_id in sorted(candidates, key=lambda item: (item[0], item[1]))
    )


def point_nearest_segment_apple_rt(
    points: tuple[_CanonicalPoint2D, ...],
    segments: tuple[_CanonicalSegment, ...],
) -> tuple[dict[str, object], ...]:
    point_by_id = {point.id: point for point in points}
    segment_by_id = {segment.id: segment for segment in segments}
    best_by_point: dict[int, tuple[int, float]] = {}
    for candidate in point_segment_candidates_apple_rt(points, segments):
        point_id = int(candidate["point_id"])
        segment_id = int(candidate["segment_id"])
        distance = _reference_point_segment_distance(point_by_id[point_id], segment_by_id[segment_id])
        best = best_by_point.get(point_id)
        if best is None or distance < best[1] - 1.0e-7 or (
            abs(distance - best[1]) <= 1.0e-7 and segment_id < best[0]
        ):
            best_by_point[point_id] = (segment_id, distance)
    rows = []
    for point in points:
        best = best_by_point.get(point.id)
        if best is None:
            continue
        rows.append({"point_id": point.id, "segment_id": best[0], "distance": best[1]})
    return tuple(rows)


def segment_polygon_candidates_apple_rt(
    segments: tuple[_CanonicalSegment, ...],
    polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, object], ...]:
    if any(not isinstance(segment, _CanonicalSegment) for segment in segments):
        raise ValueError("Apple RT segment-polygon candidates currently require 2D segments")
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in polygons):
        raise ValueError("Apple RT segment-polygon candidates currently require 2D polygons")
    library = _load_library()
    segment_records = _pack_segments(segments)
    polygon_records = _pack_polygon_bounds_2d(polygons)
    rows_ptr = ctypes.POINTER(_RtdlSegmentPolygonCandidateRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_segment_polygon_candidates_2d(
        segment_records,
        len(segments),
        polygon_records,
        len(polygons),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        candidates = {
            (int(rows_ptr[index].segment_id), int(rows_ptr[index].polygon_id))
            for index in range(row_count.value)
        }
    finally:
        if bool(rows_ptr):
            library.rtdl_apple_rt_free_rows(rows_ptr)

    # A segment fully contained inside a polygon's candidate box does not cross
    # a box face, so surface-ray traversal alone cannot discover it. Endpoint
    # point-in-polygon uses the existing MPS box candidate path and keeps
    # native_only candidate discovery hardware-backed before exact refinement.
    endpoint_points = []
    endpoint_to_segment: dict[int, int] = {}
    for index, segment in enumerate(segments):
        start_id = index * 2 + 1
        end_id = index * 2 + 2
        endpoint_points.append(_CanonicalPoint2D(start_id, segment.x0, segment.y0))
        endpoint_points.append(_CanonicalPoint2D(end_id, segment.x1, segment.y1))
        endpoint_to_segment[start_id] = segment.id
        endpoint_to_segment[end_id] = segment.id
    for row in point_in_polygon_positive_hits_apple_rt(tuple(endpoint_points), polygons):
        candidates.add((endpoint_to_segment[int(row["point_id"])], int(row["polygon_id"])))

    return tuple(
        {"segment_id": segment_id, "polygon_id": polygon_id}
        for segment_id, polygon_id in sorted(candidates, key=lambda item: (item[0], item[1]))
    )


def segment_polygon_hitcount_apple_rt(
    segments: tuple[_CanonicalSegment, ...],
    polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, object], ...]:
    segment_by_id = {segment.id: segment for segment in segments}
    polygon_by_id = {polygon.id: polygon for polygon in polygons}
    counts = {segment.id: 0 for segment in segments}
    for candidate in segment_polygon_candidates_apple_rt(segments, polygons):
        segment = segment_by_id[int(candidate["segment_id"])]
        polygon = polygon_by_id[int(candidate["polygon_id"])]
        if _reference_segment_hits_polygon(segment, polygon):
            counts[segment.id] += 1
    return tuple({"segment_id": segment.id, "hit_count": counts[segment.id]} for segment in segments)


def segment_polygon_anyhit_rows_apple_rt(
    segments: tuple[_CanonicalSegment, ...],
    polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, object], ...]:
    segment_by_id = {segment.id: segment for segment in segments}
    polygon_by_id = {polygon.id: polygon for polygon in polygons}
    rows = []
    for candidate in segment_polygon_candidates_apple_rt(segments, polygons):
        segment = segment_by_id[int(candidate["segment_id"])]
        polygon = polygon_by_id[int(candidate["polygon_id"])]
        if _reference_segment_hits_polygon(segment, polygon):
            rows.append({"segment_id": segment.id, "polygon_id": polygon.id})
    return tuple(rows)


def _polygon_edge_segments(
    polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[tuple[_CanonicalSegment, ...], dict[int, int]]:
    segments = []
    segment_to_polygon: dict[int, int] = {}
    next_id = 1
    for polygon in polygons:
        vertices = list(polygon.vertices)
        if not vertices:
            continue
        for start, end in zip(vertices, vertices[1:] + vertices[:1]):
            segments.append(_CanonicalSegment(next_id, start[0], start[1], end[0], end[1]))
            segment_to_polygon[next_id] = polygon.id
            next_id += 1
    return tuple(segments), segment_to_polygon


def _polygon_vertices_as_points(
    polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[tuple[_CanonicalPoint2D, ...], dict[int, int]]:
    points = []
    point_to_polygon: dict[int, int] = {}
    next_id = 1
    for polygon in polygons:
        for x, y in polygon.vertices:
            points.append(_CanonicalPoint2D(next_id, x, y))
            point_to_polygon[next_id] = polygon.id
            next_id += 1
    return tuple(points), point_to_polygon


def polygon_pair_candidates_apple_rt(
    left_polygons: tuple[_CanonicalPolygon, ...],
    right_polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, object], ...]:
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in left_polygons):
        raise ValueError("Apple RT polygon-pair candidates currently require 2D left polygons")
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in right_polygons):
        raise ValueError("Apple RT polygon-pair candidates currently require 2D right polygons")
    candidates: set[tuple[int, int]] = set()

    left_edges, left_edge_to_polygon = _polygon_edge_segments(left_polygons)
    for row in segment_polygon_anyhit_rows_apple_rt(left_edges, right_polygons):
        candidates.add((left_edge_to_polygon[int(row["segment_id"])], int(row["polygon_id"])))

    right_edges, right_edge_to_polygon = _polygon_edge_segments(right_polygons)
    for row in segment_polygon_anyhit_rows_apple_rt(right_edges, left_polygons):
        candidates.add((int(row["polygon_id"]), right_edge_to_polygon[int(row["segment_id"])]))

    left_points, left_point_to_polygon = _polygon_vertices_as_points(left_polygons)
    for row in point_in_polygon_positive_hits_apple_rt(left_points, right_polygons):
        candidates.add((left_point_to_polygon[int(row["point_id"])], int(row["polygon_id"])))

    right_points, right_point_to_polygon = _polygon_vertices_as_points(right_polygons)
    for row in point_in_polygon_positive_hits_apple_rt(right_points, left_polygons):
        candidates.add((int(row["polygon_id"]), right_point_to_polygon[int(row["point_id"])]))

    left_order = {polygon.id: index for index, polygon in enumerate(left_polygons)}
    right_order = {polygon.id: index for index, polygon in enumerate(right_polygons)}
    return tuple(
        {"left_polygon_id": left_id, "right_polygon_id": right_id}
        for left_id, right_id in sorted(candidates, key=lambda item: (left_order[item[0]], right_order[item[1]]))
    )


def polygon_pair_overlap_area_rows_apple_rt(
    left_polygons: tuple[_CanonicalPolygon, ...],
    right_polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, object], ...]:
    candidate_pairs = {
        (int(row["left_polygon_id"]), int(row["right_polygon_id"]))
        for row in polygon_pair_candidates_apple_rt(left_polygons, right_polygons)
    }
    right_by_id = {polygon.id: polygon for polygon in right_polygons}
    left_cells_by_id = {polygon.id: tuple(_reference_polygon_unit_cells(polygon)) for polygon in left_polygons}
    right_cells_by_id = {polygon.id: tuple(_reference_polygon_unit_cells(polygon)) for polygon in right_polygons}
    rows = []
    for left_polygon in left_polygons:
        left_cells = left_cells_by_id[left_polygon.id]
        left_cell_lookup = set(left_cells)
        left_area = len(left_cells)
        for right_polygon in right_polygons:
            if (left_polygon.id, right_polygon.id) not in candidate_pairs:
                continue
            right_cells = right_cells_by_id[right_polygon.id]
            intersection_area = sum(1 for cell in right_cells if cell in left_cell_lookup)
            if intersection_area <= 0:
                continue
            right_area = len(right_cells)
            rows.append(
                {
                    "left_polygon_id": left_polygon.id,
                    "right_polygon_id": right_by_id[right_polygon.id].id,
                    "intersection_area": intersection_area,
                    "left_area": left_area,
                    "right_area": right_area,
                    "union_area": left_area + right_area - intersection_area,
                }
            )
    return tuple(rows)


def polygon_set_jaccard_apple_rt(
    left_polygons: tuple[_CanonicalPolygon, ...],
    right_polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, object], ...]:
    candidate_pairs = {
        (int(row["left_polygon_id"]), int(row["right_polygon_id"]))
        for row in polygon_pair_candidates_apple_rt(left_polygons, right_polygons)
    }
    left_cells_by_id = {polygon.id: set(_reference_polygon_unit_cells(polygon)) for polygon in left_polygons}
    right_cells_by_id = {polygon.id: set(_reference_polygon_unit_cells(polygon)) for polygon in right_polygons}
    left_cells = set().union(*left_cells_by_id.values()) if left_cells_by_id else set()
    right_cells = set().union(*right_cells_by_id.values()) if right_cells_by_id else set()
    intersection_cells = set()
    for left_id, right_id in candidate_pairs:
        intersection_cells.update(left_cells_by_id[left_id] & right_cells_by_id[right_id])
    intersection_area = len(intersection_cells)
    left_area = len(left_cells)
    right_area = len(right_cells)
    union_area = left_area + right_area - intersection_area
    return (
        {
            "intersection_area": intersection_area,
            "left_area": left_area,
            "right_area": right_area,
            "union_area": union_area,
            "jaccard_similarity": 0.0 if union_area == 0 else intersection_area / union_area,
        },
    )


def overlay_compose_apple_rt(
    left_polygons: tuple[_CanonicalPolygon, ...],
    right_polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, object], ...]:
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in left_polygons):
        raise ValueError("Apple RT overlay_compose currently requires 2D left polygons")
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in right_polygons):
        raise ValueError("Apple RT overlay_compose currently requires 2D right polygons")

    left_edges, left_edge_to_polygon = _polygon_edge_segments(left_polygons)
    right_edges, right_edge_to_polygon = _polygon_edge_segments(right_polygons)
    lsi_pairs = {
        (left_edge_to_polygon[int(row["left_id"])], right_edge_to_polygon[int(row["right_id"])])
        for row in segment_intersection_apple_rt(left_edges, right_edges)
    }

    left_first_points = tuple(
        _CanonicalPoint2D(polygon.id, polygon.vertices[0][0], polygon.vertices[0][1])
        for polygon in left_polygons
        if polygon.vertices
    )
    right_first_points = tuple(
        _CanonicalPoint2D(polygon.id, polygon.vertices[0][0], polygon.vertices[0][1])
        for polygon in right_polygons
        if polygon.vertices
    )
    pip_pairs = {
        (int(row["point_id"]), int(row["polygon_id"]))
        for row in point_in_polygon_positive_hits_apple_rt(left_first_points, right_polygons)
    }
    pip_pairs.update(
        (int(row["polygon_id"]), int(row["point_id"]))
        for row in point_in_polygon_positive_hits_apple_rt(right_first_points, left_polygons)
    )

    rows = []
    for left_polygon in left_polygons:
        for right_polygon in right_polygons:
            rows.append(
                {
                    "left_polygon_id": left_polygon.id,
                    "right_polygon_id": right_polygon.id,
                    "requires_lsi": 1 if (left_polygon.id, right_polygon.id) in lsi_pairs else 0,
                    "requires_pip": 1 if (left_polygon.id, right_polygon.id) in pip_pairs else 0,
                }
            )
    return tuple(rows)


def _rank_neighbor_rows(rows, *, k_max: int) -> tuple[dict[str, object], ...]:
    by_query: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        by_query.setdefault(int(row["query_id"]), []).append(dict(row))
    ranked: list[dict[str, object]] = []
    for query_id in sorted(by_query):
        query_rows = by_query[query_id]
        query_rows.sort(key=lambda item: (float(item["distance"]), int(item["neighbor_id"])))
        for rank, row in enumerate(query_rows[:k_max], start=1):
            ranked.append(
                {
                    "query_id": query_id,
                    "neighbor_id": int(row["neighbor_id"]),
                    "distance": float(row["distance"]),
                    "neighbor_rank": rank,
                }
            )
    return tuple(ranked)


def _combined_point2d_radius(query_points: tuple[_CanonicalPoint2D, ...], search_points: tuple[_CanonicalPoint2D, ...]) -> float:
    if not query_points or not search_points:
        return 0.0
    xs = [point.x for point in (*query_points, *search_points)]
    ys = [point.y for point in (*query_points, *search_points)]
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    return (dx * dx + dy * dy) ** 0.5 + 1.0e-9


def _combined_point3d_radius(query_points: tuple[_CanonicalPoint3D, ...], search_points: tuple[_CanonicalPoint3D, ...]) -> float:
    if not query_points or not search_points:
        return 0.0
    xs = [point.x for point in (*query_points, *search_points)]
    ys = [point.y for point in (*query_points, *search_points)]
    zs = [point.z for point in (*query_points, *search_points)]
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    dz = max(zs) - min(zs)
    return (dx * dx + dy * dy + dz * dz) ** 0.5 + 1.0e-9


def apple_rt_predicate_mode(predicate_name: str) -> str:
    """Return the current Apple RT dispatch class for a predicate.

    `native_mps_rt` means the operation uses the Apple Metal/MPS ray
    intersector. `native_metal_compute` means Apple Metal compute performs the
    main predicate/filter stage without MPS RT traversal. `cpu_reference_compat`
    means the public Apple RT dispatcher is callable for parity but the
    operation is not yet hardware-backed.
    """
    if predicate_name in APPLE_RT_METAL_COMPUTE_PREDICATES:
        return "native_metal_compute"
    if predicate_name in APPLE_RT_METAL_FILTER_CPU_AGGREGATE_PREDICATES:
        return "native_metal_filter_cpu_aggregate"
    if predicate_name in {"fixed_radius_neighbors", "bounded_knn_rows", "knn_rows"}:
        return "native_mps_rt_2d_3d"
    if predicate_name in {"ray_triangle_any_hit", "ray_triangle_hit_count"}:
        return "native_mps_rt_2d_3d"
    if predicate_name in APPLE_RT_NATIVE_PREDICATES:
        return "native_mps_rt"
    if predicate_name in APPLE_RT_COMPATIBILITY_PREDICATES:
        return "cpu_reference_compat"
    return "unsupported"


def apple_rt_support_matrix() -> tuple[dict[str, object], ...]:
    rows = []
    for predicate_name in sorted(APPLE_RT_COMPATIBILITY_PREDICATES):
        row: dict[str, object] = {
            "predicate": predicate_name,
            "mode": apple_rt_predicate_mode(predicate_name),
        }
        row.update(_apple_rt_support_notes(predicate_name))
        rows.append(row)
    return tuple(rows)


def run_apple_rt(
    kernel: CompiledKernel | object,
    *,
    native_only: bool = False,
    **inputs,
) -> tuple[dict[str, object], ...]:
    compiled = _resolve_kernel(kernel)
    _validate_kernel_for_cpu(compiled)
    _load_library()
    if compiled.candidates is None:
        raise ValueError("run_apple_rt currently requires a traversal candidate stage")
    if compiled.refine_op is None:
        raise ValueError("run_apple_rt currently requires a refine stage")
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name not in APPLE_RT_COMPATIBILITY_PREDICATES:
        raise NotImplementedError(f"Apple RT dispatcher does not support predicate `{predicate_name}`")
    expected_inputs = {item.name: item for item in compiled.inputs}
    missing = [name for name in expected_inputs if name not in inputs]
    unexpected = [name for name in inputs if name not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL Apple RT inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL Apple RT inputs: {', '.join(sorted(unexpected))}")
    normalized = {
        name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
        for name, payload in inputs.items()
    }
    left_records = normalized[compiled.candidates.left.name]
    right_records = normalized[compiled.candidates.right.name]
    if predicate_name == "ray_triangle_closest_hit" and all(
        isinstance(ray, _CanonicalRay3D) for ray in left_records
    ) and all(isinstance(triangle, _CanonicalTriangle3D) for triangle in right_records):
        return tuple(ray_triangle_closest_hit_apple_rt(left_records, right_records))
    if predicate_name == "ray_triangle_hit_count" and all(
        isinstance(ray, _CanonicalRay3D) for ray in left_records
    ) and all(isinstance(triangle, _CanonicalTriangle3D) for triangle in right_records):
        return tuple(ray_triangle_hit_count_apple_rt(left_records, right_records))
    if predicate_name == "ray_triangle_hit_count" and all(
        isinstance(ray, _CanonicalRay2D) for ray in left_records
    ) and all(isinstance(triangle, _CanonicalTriangle2D) for triangle in right_records):
        return tuple(ray_triangle_hit_count_apple_rt(left_records, right_records))
    if predicate_name == "ray_triangle_any_hit" and all(
        isinstance(ray, (_CanonicalRay2D, _CanonicalRay3D)) for ray in left_records
    ) and all(isinstance(triangle, (_CanonicalTriangle2D, _CanonicalTriangle3D)) for triangle in right_records):
        return ray_triangle_any_hit_apple_rt(left_records, right_records)
    if predicate_name == "fixed_radius_neighbors" and all(
        isinstance(point, _CanonicalPoint2D) for point in left_records
    ) and all(isinstance(point, _CanonicalPoint2D) for point in right_records):
        options = compiled.refine_op.predicate.options
        return tuple(
            fixed_radius_neighbors_2d_apple_rt(
                left_records,
                right_records,
                radius=float(options["radius"]),
                k_max=int(options["k_max"]),
            )
        )
    if predicate_name == "fixed_radius_neighbors" and all(
        isinstance(point, _CanonicalPoint3D) for point in left_records
    ) and all(isinstance(point, _CanonicalPoint3D) for point in right_records):
        options = compiled.refine_op.predicate.options
        return tuple(
            fixed_radius_neighbors_3d_apple_rt(
                left_records,
                right_records,
                radius=float(options["radius"]),
                k_max=int(options["k_max"]),
            )
        )
    if predicate_name == "bounded_knn_rows" and all(
        isinstance(point, _CanonicalPoint2D) for point in left_records
    ) and all(isinstance(point, _CanonicalPoint2D) for point in right_records):
        options = compiled.refine_op.predicate.options
        fixed_rows = fixed_radius_neighbors_2d_apple_rt(
            left_records,
            right_records,
            radius=float(options["radius"]),
            k_max=int(options["k_max"]),
        )
        return _rank_neighbor_rows(fixed_rows, k_max=int(options["k_max"]))
    if predicate_name == "bounded_knn_rows" and all(
        isinstance(point, _CanonicalPoint3D) for point in left_records
    ) and all(isinstance(point, _CanonicalPoint3D) for point in right_records):
        options = compiled.refine_op.predicate.options
        fixed_rows = fixed_radius_neighbors_3d_apple_rt(
            left_records,
            right_records,
            radius=float(options["radius"]),
            k_max=int(options["k_max"]),
        )
        return _rank_neighbor_rows(fixed_rows, k_max=int(options["k_max"]))
    if predicate_name == "knn_rows" and all(
        isinstance(point, _CanonicalPoint2D) for point in left_records
    ) and all(isinstance(point, _CanonicalPoint2D) for point in right_records):
        options = compiled.refine_op.predicate.options
        k = int(options["k"])
        fixed_rows = fixed_radius_neighbors_2d_apple_rt(
            left_records,
            right_records,
            radius=_combined_point2d_radius(left_records, right_records),
            k_max=max(k, len(right_records)),
        )
        return _rank_neighbor_rows(fixed_rows, k_max=k)
    if predicate_name == "knn_rows" and all(
        isinstance(point, _CanonicalPoint3D) for point in left_records
    ) and all(isinstance(point, _CanonicalPoint3D) for point in right_records):
        options = compiled.refine_op.predicate.options
        k = int(options["k"])
        fixed_rows = fixed_radius_neighbors_3d_apple_rt(
            left_records,
            right_records,
            radius=_combined_point3d_radius(left_records, right_records),
            k_max=max(k, len(right_records)),
        )
        return _rank_neighbor_rows(fixed_rows, k_max=k)
    if predicate_name == "point_in_polygon" and all(
        isinstance(point, _CanonicalPoint2D) for point in left_records
    ) and all(isinstance(polygon, _CanonicalPolygon) for polygon in right_records):
        options = compiled.refine_op.predicate.options
        if options.get("result_mode", "full_matrix") == "positive_hits":
            return point_in_polygon_positive_hits_apple_rt(
                left_records,
                right_records,
                boundary_mode=str(options.get("boundary_mode", "inclusive")),
            )
        return point_in_polygon_full_matrix_apple_rt(
            left_records,
            right_records,
            boundary_mode=str(options.get("boundary_mode", "inclusive")),
        )
    if predicate_name == "point_nearest_segment" and all(
        isinstance(point, _CanonicalPoint2D) for point in left_records
    ) and all(isinstance(segment, _CanonicalSegment) for segment in right_records):
        return point_nearest_segment_apple_rt(left_records, right_records)
    if predicate_name == "overlay_compose" and all(
        isinstance(polygon, _CanonicalPolygon) for polygon in left_records
    ) and all(isinstance(polygon, _CanonicalPolygon) for polygon in right_records):
        return overlay_compose_apple_rt(left_records, right_records)
    if predicate_name == "polygon_pair_overlap_area_rows" and all(
        isinstance(polygon, _CanonicalPolygon) for polygon in left_records
    ) and all(isinstance(polygon, _CanonicalPolygon) for polygon in right_records):
        return polygon_pair_overlap_area_rows_apple_rt(left_records, right_records)
    if predicate_name == "polygon_set_jaccard" and all(
        isinstance(polygon, _CanonicalPolygon) for polygon in left_records
    ) and all(isinstance(polygon, _CanonicalPolygon) for polygon in right_records):
        return polygon_set_jaccard_apple_rt(left_records, right_records)
    if predicate_name == "segment_polygon_hitcount" and all(
        isinstance(segment, _CanonicalSegment) for segment in left_records
    ) and all(isinstance(polygon, _CanonicalPolygon) for polygon in right_records):
        return segment_polygon_hitcount_apple_rt(left_records, right_records)
    if predicate_name == "segment_polygon_anyhit_rows" and all(
        isinstance(segment, _CanonicalSegment) for segment in left_records
    ) and all(isinstance(polygon, _CanonicalPolygon) for polygon in right_records):
        return segment_polygon_anyhit_rows_apple_rt(left_records, right_records)
    if predicate_name == "segment_intersection":
        return tuple(segment_intersection_apple_rt(left_records, right_records))
    if predicate_name == "conjunctive_scan":
        return tuple(conjunctive_scan_apple_rt(right_records, left_records))
    if predicate_name == "grouped_count":
        return tuple(grouped_count_apple_rt(right_records, left_records))
    if predicate_name == "grouped_sum":
        return tuple(grouped_sum_apple_rt(right_records, left_records))
    if predicate_name == "bfs_discover":
        visited_name = str(compiled.refine_op.predicate.options["visited_input"])
        return tuple(
            bfs_discover_apple_rt(
                right_records,
                left_records,
                normalized[visited_name],
                dedupe=bool(compiled.refine_op.predicate.options.get("dedupe", True)),
            )
        )
    if predicate_name == "triangle_match":
        return tuple(
            triangle_match_apple_rt(
                right_records,
                left_records,
                order=str(compiled.refine_op.predicate.options.get("order", "id_ascending")),
                unique=bool(compiled.refine_op.predicate.options.get("unique", True)),
            )
        )
    if native_only:
        raise NotImplementedError(
            "Apple RT native MPS execution currently supports only 3D "
            "ray_triangle_closest_hit, 2D/3D ray_triangle_hit_count, "
            "2D/3D ray_triangle_any_hit through hit-count projection, 2D segment_intersection, "
            "2D/3D point-neighborhood workloads, point-in-polygon positive hits, "
            "2D point-nearest-segment, 2D segment-polygon workloads, "
            "bounded 2D polygon-pair area/Jaccard workloads, 2D overlay compose, "
            "numeric DB conjunctive_scan through Metal compute, and grouped DB "
            "aggregation through Metal predicate filtering plus CPU aggregation, "
            "BFS discovery through Metal frontier expansion, and triangle matching "
            "through Metal neighbor intersection; "
            f"`{predicate_name}` is available only through CPU reference compatibility dispatch"
        )
    return _run_cpu_python_reference_from_normalized(compiled, normalized)
