"""HIPRT backend probe utilities for RTDL.

This module intentionally exposes only a bounded bring-up surface:
version reporting and context creation. It does not claim RTDL workload
execution through HIPRT yet.
"""

from __future__ import annotations

import ctypes
import ctypes.util
from bisect import bisect_left
from bisect import bisect_right
import functools
import math
import os
import platform
from pathlib import Path

from .db_reference import PredicateClause
from .db_reference import normalize_grouped_query
from .db_reference import normalize_predicate_bundle
from .oracle_runtime import _decode_db_group_key
from .oracle_runtime import _RtdlDbClause
from .oracle_runtime import _RtdlDbField
from .oracle_runtime import _RtdlDbGroupedCountRow
from .oracle_runtime import _RtdlDbGroupedSumRow
from .oracle_runtime import _RtdlDbRowIdRow
from .oracle_runtime import _RtdlDbScalar
from .oracle_runtime import _encode_db_clauses
from .oracle_runtime import _encode_db_table
from .oracle_runtime import _encode_db_text_fields
from .graph_reference import CSRGraph as _CanonicalCSRGraph
from .graph_reference import EdgeSeed as _CanonicalEdgeSeed
from .graph_reference import FrontierVertex as _CanonicalFrontierVertex
from .ir import CompiledKernel
from .reference import Point3D as _CanonicalPoint3D
from .reference import Point as _CanonicalPoint
from .reference import Polygon as _CanonicalPolygon
from .reference import Ray2D as _CanonicalRay2D
from .reference import Ray3D as _CanonicalRay3D
from .reference import Segment as _CanonicalSegment
from .reference import Triangle as _CanonicalTriangle2D
from .reference import Triangle3D as _CanonicalTriangle3D
from .runtime import _normalize_records
from .runtime import _project_rows
from .runtime import _resolve_kernel
from .runtime import _validate_kernel_for_cpu

_HIPRT_PEER_PREDICATES = {
    "segment_intersection",
    "point_in_polygon",
    "point_nearest_segment",
    "overlay_compose",
    "ray_triangle_any_hit",
    "ray_triangle_hit_count",
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows",
    "fixed_radius_neighbors",
    "bounded_knn_rows",
    "knn_rows",
    "bfs_discover",
    "triangle_match",
    "conjunctive_scan",
    "grouped_count",
    "grouped_sum",
}

_HIPRT_IMPLEMENTED_PREDICATES = {
    "ray_triangle_hit_count",
    "ray_triangle_any_hit",
    "segment_intersection",
    "point_in_polygon",
    "point_nearest_segment",
    "overlay_compose",
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows",
    "fixed_radius_neighbors",
    "bounded_knn_rows",
    "knn_rows",
    "bfs_discover",
    "triangle_match",
    "conjunctive_scan",
    "grouped_count",
    "grouped_sum",
}

_HIPRT_GOAL_BY_PREDICATE = {
    "segment_intersection": "Goal 550 2D geometry expansion",
    "point_in_polygon": "Goal 550 2D geometry expansion",
    "overlay_compose": "Goal 550 2D geometry expansion",
    "ray_triangle_hit_count": "Goal 550 for 2D, Goal 548/542 for 3D",
    "ray_triangle_any_hit": "Goal 636 hit-count projection for 2D/3D",
    "segment_polygon_hitcount": "Goal 550 2D geometry expansion",
    "segment_polygon_anyhit_rows": "Goal 550 2D geometry expansion",
    "point_nearest_segment": "Goal 553 2D point-nearest-segment expansion",
    "fixed_radius_neighbors": "Goal 548 for 3D, Goal 550 for 2D",
    "bounded_knn_rows": "Goal 549 for 3D, Goal 550 for 2D",
    "knn_rows": "Goal 549 for 3D, Goal 550 for 2D",
    "bfs_discover": "Goal 550 graph expansion",
    "triangle_match": "Goal 550 graph expansion",
    "conjunctive_scan": "Goal 551 DB expansion",
    "grouped_count": "Goal 551 DB expansion",
    "grouped_sum": "Goal 551 DB expansion",
}


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


class _RtdlPointNearestSegmentRow(ctypes.Structure):
    _fields_ = [
        ("point_id", ctypes.c_uint32),
        ("segment_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
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


class _RtdlPoint3D(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double),
    ]


class _RtdlFixedRadiusNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
    ]


class _RtdlFrontierVertex(ctypes.Structure):
    _fields_ = [
        ("vertex_id", ctypes.c_uint32),
        ("level", ctypes.c_uint32),
    ]


class _RtdlBfsRow(ctypes.Structure):
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


def _library_name() -> str:
    return "librtdl_hiprt.dylib" if platform.system() == "Darwin" else "librtdl_hiprt.so"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _candidate_paths() -> list[Path]:
    candidates: list[Path] = []
    env = os.environ.get("RTDL_HIPRT_LIB")
    if env:
        candidates.append(Path(env))
    candidates.append(_repo_root() / "build" / _library_name())
    found = ctypes.util.find_library("rtdl_hiprt")
    if found:
        candidates.append(Path(found))
    return candidates


@functools.lru_cache(maxsize=1)
def _load_hiprt_library() -> ctypes.CDLL:
    errors: list[str] = []
    for path in _candidate_paths():
        try:
            return ctypes.CDLL(str(path))
        except OSError as exc:
            errors.append(f"{path}: {exc}")
    message = "RTDL HIPRT backend library not found; build it with `make build-hiprt` or set RTDL_HIPRT_LIB"
    if errors:
        message += " (" + "; ".join(errors) + ")"
    raise FileNotFoundError(message)


@functools.lru_cache(maxsize=1)
def _hiprt_lib() -> ctypes.CDLL:
    lib = _load_hiprt_library()
    lib.rtdl_hiprt_get_version.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.rtdl_hiprt_get_version.restype = ctypes.c_int
    lib.rtdl_hiprt_context_probe.argtypes = [
        ctypes.c_char_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_context_probe.restype = ctypes.c_int
    lib.rtdl_hiprt_free_rows.argtypes = [ctypes.c_void_p]
    lib.rtdl_hiprt_free_rows.restype = None
    lib.rtdl_hiprt_run_ray_hitcount_3d.argtypes = [
        ctypes.POINTER(_RtdlRay3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle3D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_ray_hitcount_3d.restype = ctypes.c_int
    lib.rtdl_hiprt_run_ray_hitcount_2d.argtypes = [
        ctypes.POINTER(_RtdlRay2D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_ray_hitcount_2d.restype = ctypes.c_int
    lib.rtdl_hiprt_run_lsi.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_lsi.restype = ctypes.c_int
    lib.rtdl_hiprt_run_pip.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPipRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_pip.restype = ctypes.c_int
    lib.rtdl_hiprt_run_overlay.argtypes = [
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
    lib.rtdl_hiprt_run_overlay.restype = ctypes.c_int
    lib.rtdl_hiprt_run_point_nearest_segment.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPointNearestSegmentRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_point_nearest_segment.restype = ctypes.c_int
    lib.rtdl_hiprt_run_segment_polygon_hitcount.argtypes = [
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
    lib.rtdl_hiprt_run_segment_polygon_hitcount.restype = ctypes.c_int
    lib.rtdl_hiprt_run_segment_polygon_anyhit_rows.argtypes = [
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
    lib.rtdl_hiprt_run_segment_polygon_anyhit_rows.restype = ctypes.c_int
    lib.rtdl_hiprt_run_fixed_radius_neighbors_3d.argtypes = [
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_fixed_radius_neighbors_3d.restype = ctypes.c_int
    lib.rtdl_hiprt_prepare_fixed_radius_neighbors_3d.argtypes = [
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_prepare_fixed_radius_neighbors_3d.restype = ctypes.c_int
    lib.rtdl_hiprt_run_prepared_fixed_radius_neighbors_3d.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_prepared_fixed_radius_neighbors_3d.restype = ctypes.c_int
    lib.rtdl_hiprt_destroy_prepared_fixed_radius_neighbors_3d.argtypes = [ctypes.c_void_p]
    lib.rtdl_hiprt_destroy_prepared_fixed_radius_neighbors_3d.restype = None
    lib.rtdl_hiprt_run_fixed_radius_neighbors_2d.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_fixed_radius_neighbors_2d.restype = ctypes.c_int
    lib.rtdl_hiprt_run_bfs_expand.argtypes = [
        ctypes.POINTER(_RtdlFrontierVertex),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.c_int,
        ctypes.POINTER(ctypes.POINTER(_RtdlBfsRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_bfs_expand.restype = ctypes.c_int
    lib.rtdl_hiprt_prepare_graph_csr.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_prepare_graph_csr.restype = ctypes.c_int
    lib.rtdl_hiprt_run_prepared_bfs_expand.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_RtdlFrontierVertex),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.c_int,
        ctypes.POINTER(ctypes.POINTER(_RtdlBfsRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_prepared_bfs_expand.restype = ctypes.c_int
    lib.rtdl_hiprt_run_triangle_probe.argtypes = [
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
    lib.rtdl_hiprt_run_triangle_probe.restype = ctypes.c_int
    lib.rtdl_hiprt_run_prepared_triangle_probe.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_RtdlEdgeSeed),
        ctypes.c_size_t,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(ctypes.POINTER(_RtdlTriangleRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_prepared_triangle_probe.restype = ctypes.c_int
    lib.rtdl_hiprt_destroy_prepared_graph_csr.argtypes = [ctypes.c_void_p]
    lib.rtdl_hiprt_destroy_prepared_graph_csr.restype = None
    lib.rtdl_hiprt_run_conjunctive_scan.argtypes = [
        ctypes.POINTER(_RtdlDbField),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbScalar),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbClause),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlDbRowIdRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_conjunctive_scan.restype = ctypes.c_int
    lib.rtdl_hiprt_run_grouped_count.argtypes = [
        ctypes.POINTER(_RtdlDbField),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbScalar),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbClause),
        ctypes.c_size_t,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_grouped_count.restype = ctypes.c_int
    lib.rtdl_hiprt_run_grouped_sum.argtypes = [
        ctypes.POINTER(_RtdlDbField),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbScalar),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbClause),
        ctypes.c_size_t,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedSumRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_grouped_sum.restype = ctypes.c_int
    lib.rtdl_hiprt_prepare_db_table.argtypes = [
        ctypes.POINTER(_RtdlDbField),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbScalar),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_prepare_db_table.restype = ctypes.c_int
    lib.rtdl_hiprt_run_prepared_conjunctive_scan.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_RtdlDbClause),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlDbRowIdRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_prepared_conjunctive_scan.restype = ctypes.c_int
    lib.rtdl_hiprt_run_prepared_grouped_count.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_RtdlDbClause),
        ctypes.c_size_t,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_prepared_grouped_count.restype = ctypes.c_int
    lib.rtdl_hiprt_run_prepared_grouped_sum.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_RtdlDbClause),
        ctypes.c_size_t,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedSumRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_prepared_grouped_sum.restype = ctypes.c_int
    lib.rtdl_hiprt_destroy_prepared_db_table.argtypes = [ctypes.c_void_p]
    lib.rtdl_hiprt_destroy_prepared_db_table.restype = None
    lib.rtdl_hiprt_prepare_ray_hitcount_3d.argtypes = [
        ctypes.POINTER(_RtdlTriangle3D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_prepare_ray_hitcount_3d.restype = ctypes.c_int
    lib.rtdl_hiprt_run_prepared_ray_hitcount_3d.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_RtdlRay3D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_hiprt_run_prepared_ray_hitcount_3d.restype = ctypes.c_int
    lib.rtdl_hiprt_destroy_prepared_ray_hitcount_3d.argtypes = [ctypes.c_void_p]
    lib.rtdl_hiprt_destroy_prepared_ray_hitcount_3d.restype = None
    return lib


def hiprt_version() -> tuple[int, int, int]:
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    status = _hiprt_lib().rtdl_hiprt_get_version(
        ctypes.byref(major),
        ctypes.byref(minor),
        ctypes.byref(patch),
    )
    if status != 0:
        raise RuntimeError("rtdl_hiprt_get_version failed")
    return (major.value, minor.value, patch.value)


def hiprt_context_probe() -> dict[str, object]:
    device_name = ctypes.create_string_buffer(256)
    error = ctypes.create_string_buffer(1024)
    device_type = ctypes.c_int()
    api_version = ctypes.c_int()
    status = _hiprt_lib().rtdl_hiprt_context_probe(
        device_name,
        ctypes.sizeof(device_name),
        ctypes.byref(device_type),
        ctypes.byref(api_version),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_context_probe failed with status {status}: {detail}")
    return {
        "version": hiprt_version(),
        "api_version": api_version.value,
        "device_type": device_type.value,
        "device_name": device_name.value.decode("utf-8", errors="replace"),
    }


def ray_triangle_hit_count_hiprt(
    rays: tuple[_CanonicalRay3D, ...],
    triangles: tuple[_CanonicalTriangle3D, ...],
) -> tuple[dict[str, int], ...]:
    ray_records = tuple(rays)
    triangle_records = tuple(triangles)
    if any(not isinstance(ray, _CanonicalRay3D) for ray in ray_records):
        raise TypeError("ray_triangle_hit_count_hiprt currently supports only Ray3D inputs")
    if any(not isinstance(triangle, _CanonicalTriangle3D) for triangle in triangle_records):
        raise TypeError("ray_triangle_hit_count_hiprt currently supports only Triangle3D inputs")

    ray_array = (_RtdlRay3D * len(ray_records))(
        *[
            _RtdlRay3D(item.id, item.ox, item.oy, item.oz, item.dx, item.dy, item.dz, item.tmax)
            for item in ray_records
        ]
    )
    triangle_array = (_RtdlTriangle3D * len(triangle_records))(
        *[
            _RtdlTriangle3D(
                item.id,
                item.x0,
                item.y0,
                item.z0,
                item.x1,
                item.y1,
                item.z1,
                item.x2,
                item.y2,
                item.z2,
            )
            for item in triangle_records
        ]
    )
    rows_ptr = ctypes.POINTER(_RtdlRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_ray_hitcount_3d(
        ray_array,
        len(ray_records),
        triangle_array,
        len(triangle_records),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_ray_hitcount_3d failed with status {status}: {detail}")
    try:
        return tuple(
            {"ray_id": int(rows_ptr[index].ray_id), "hit_count": int(rows_ptr[index].hit_count)}
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def segment_intersection_hiprt(
    left: tuple[_CanonicalSegment, ...],
    right: tuple[_CanonicalSegment, ...],
) -> tuple[dict[str, int | float], ...]:
    left_records = tuple(left)
    right_records = tuple(right)
    if any(not isinstance(segment, _CanonicalSegment) for segment in left_records):
        raise TypeError("segment_intersection_hiprt currently supports only Segment left inputs")
    if any(not isinstance(segment, _CanonicalSegment) for segment in right_records):
        raise TypeError("segment_intersection_hiprt currently supports only Segment right inputs")

    left_array = (_RtdlSegment * len(left_records))(
        *[_RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in left_records]
    )
    right_array = (_RtdlSegment * len(right_records))(
        *[_RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in right_records]
    )
    rows_ptr = ctypes.POINTER(_RtdlLsiRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_lsi(
        left_array,
        len(left_records),
        right_array,
        len(right_records),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_lsi failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "left_id": int(rows_ptr[index].left_id),
                "right_id": int(rows_ptr[index].right_id),
                "intersection_point_x": float(rows_ptr[index].intersection_point_x),
                "intersection_point_y": float(rows_ptr[index].intersection_point_y),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def ray_triangle_hit_count_2d_hiprt(
    rays: tuple[_CanonicalRay2D, ...],
    triangles: tuple[_CanonicalTriangle2D, ...],
) -> tuple[dict[str, int], ...]:
    ray_records = tuple(rays)
    triangle_records = tuple(triangles)
    if any(not isinstance(ray, _CanonicalRay2D) for ray in ray_records):
        raise TypeError("ray_triangle_hit_count_2d_hiprt currently supports only Ray2D inputs")
    if any(not isinstance(triangle, _CanonicalTriangle2D) for triangle in triangle_records):
        raise TypeError("ray_triangle_hit_count_2d_hiprt currently supports only Triangle2D inputs")

    ray_array = (_RtdlRay2D * len(ray_records))(
        *[_RtdlRay2D(item.id, item.ox, item.oy, item.dx, item.dy, item.tmax) for item in ray_records]
    )
    triangle_array = (_RtdlTriangle * len(triangle_records))(
        *[
            _RtdlTriangle(item.id, item.x0, item.y0, item.x1, item.y1, item.x2, item.y2)
            for item in triangle_records
        ]
    )
    rows_ptr = ctypes.POINTER(_RtdlRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_ray_hitcount_2d(
        ray_array,
        len(ray_records),
        triangle_array,
        len(triangle_records),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_ray_hitcount_2d failed with status {status}: {detail}")
    try:
        return tuple(
            {"ray_id": int(rows_ptr[index].ray_id), "hit_count": int(rows_ptr[index].hit_count)}
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def _project_ray_hitcount_rows_to_anyhit(rows: tuple[dict[str, int], ...]) -> tuple[dict[str, int], ...]:
    return tuple(
        {"ray_id": int(row["ray_id"]), "any_hit": 1 if int(row["hit_count"]) else 0}
        for row in rows
    )


def _hiprt_ray_anyhit_symbol(dimension: int):
    name = f"rtdl_hiprt_run_ray_anyhit_{dimension}d"
    symbol = getattr(_hiprt_lib(), name, None)
    if symbol is None:
        return None
    if dimension == 2:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlRay2D),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlTriangle),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayAnyHitRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
    else:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlTriangle3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayAnyHitRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
    symbol.restype = ctypes.c_int
    return symbol


def ray_triangle_any_hit_2d_hiprt(
    rays: tuple[_CanonicalRay2D, ...],
    triangles: tuple[_CanonicalTriangle2D, ...],
) -> tuple[dict[str, int], ...]:
    symbol = _hiprt_ray_anyhit_symbol(2)
    if symbol is None:
        return _project_ray_hitcount_rows_to_anyhit(ray_triangle_hit_count_2d_hiprt(rays, triangles))
    ray_records = tuple(rays)
    triangle_records = tuple(triangles)
    if any(not isinstance(ray, _CanonicalRay2D) for ray in ray_records):
        raise TypeError("ray_triangle_any_hit_2d_hiprt currently supports only Ray2D inputs")
    if any(not isinstance(triangle, _CanonicalTriangle2D) for triangle in triangle_records):
        raise TypeError("ray_triangle_any_hit_2d_hiprt currently supports only Triangle2D inputs")

    ray_array = (_RtdlRay2D * len(ray_records))(
        *[_RtdlRay2D(item.id, item.ox, item.oy, item.dx, item.dy, item.tmax) for item in ray_records]
    )
    triangle_array = (_RtdlTriangle * len(triangle_records))(
        *[
            _RtdlTriangle(item.id, item.x0, item.y0, item.x1, item.y1, item.x2, item.y2)
            for item in triangle_records
        ]
    )
    rows_ptr = ctypes.POINTER(_RtdlRayAnyHitRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        ray_array,
        len(ray_records),
        triangle_array,
        len(triangle_records),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_ray_anyhit_2d failed with status {status}: {detail}")
    try:
        return tuple(
            {"ray_id": int(rows_ptr[index].ray_id), "any_hit": int(rows_ptr[index].any_hit)}
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def ray_triangle_any_hit_3d_hiprt(
    rays: tuple[_CanonicalRay3D, ...],
    triangles: tuple[_CanonicalTriangle3D, ...],
) -> tuple[dict[str, int], ...]:
    symbol = _hiprt_ray_anyhit_symbol(3)
    if symbol is None:
        return _project_ray_hitcount_rows_to_anyhit(ray_triangle_hit_count_hiprt(rays, triangles))
    ray_records = tuple(rays)
    triangle_records = tuple(triangles)
    if any(not isinstance(ray, _CanonicalRay3D) for ray in ray_records):
        raise TypeError("ray_triangle_any_hit_3d_hiprt currently supports only Ray3D inputs")
    if any(not isinstance(triangle, _CanonicalTriangle3D) for triangle in triangle_records):
        raise TypeError("ray_triangle_any_hit_3d_hiprt currently supports only Triangle3D inputs")

    ray_array = (_RtdlRay3D * len(ray_records))(
        *[
            _RtdlRay3D(item.id, item.ox, item.oy, item.oz, item.dx, item.dy, item.dz, item.tmax)
            for item in ray_records
        ]
    )
    triangle_array = (_RtdlTriangle3D * len(triangle_records))(
        *[
            _RtdlTriangle3D(
                item.id,
                item.x0,
                item.y0,
                item.z0,
                item.x1,
                item.y1,
                item.z1,
                item.x2,
                item.y2,
                item.z2,
            )
            for item in triangle_records
        ]
    )
    rows_ptr = ctypes.POINTER(_RtdlRayAnyHitRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        ray_array,
        len(ray_records),
        triangle_array,
        len(triangle_records),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_ray_anyhit_3d failed with status {status}: {detail}")
    try:
        return tuple(
            {"ray_id": int(rows_ptr[index].ray_id), "any_hit": int(rows_ptr[index].any_hit)}
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def ray_triangle_any_hit_hiprt(
    rays: tuple[_CanonicalRay2D | _CanonicalRay3D, ...],
    triangles: tuple[_CanonicalTriangle2D | _CanonicalTriangle3D, ...],
) -> tuple[dict[str, int], ...]:
    if all(isinstance(ray, _CanonicalRay2D) for ray in rays) and all(
        isinstance(triangle, _CanonicalTriangle2D) for triangle in triangles
    ):
        return ray_triangle_any_hit_2d_hiprt(rays, triangles)
    if all(isinstance(ray, _CanonicalRay3D) for ray in rays) and all(
        isinstance(triangle, _CanonicalTriangle3D) for triangle in triangles
    ):
        return ray_triangle_any_hit_3d_hiprt(rays, triangles)
    raise TypeError("ray_triangle_any_hit_hiprt requires matching Ray2D/Triangle2D or Ray3D/Triangle3D inputs")


def _encode_polygon_arrays(polygons: tuple[_CanonicalPolygon, ...]):
    refs = []
    vertices: list[float] = []
    offset = 0
    for polygon in polygons:
        refs.append(_RtdlPolygonRef(polygon.id, offset, len(polygon.vertices)))
        for x, y in polygon.vertices:
            vertices.extend([float(x), float(y)])
        offset += len(polygon.vertices)
    ref_array = (_RtdlPolygonRef * len(refs))(*refs)
    vertex_array = (ctypes.c_double * len(vertices))(*vertices)
    return ref_array, vertex_array


def point_in_polygon_hiprt(
    points: tuple[_CanonicalPoint, ...],
    polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, int], ...]:
    point_records = tuple(points)
    polygon_records = tuple(polygons)
    if any(not isinstance(point, _CanonicalPoint) for point in point_records):
        raise TypeError("point_in_polygon_hiprt currently supports only Point2D inputs")
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in polygon_records):
        raise TypeError("point_in_polygon_hiprt currently supports only Polygon inputs")
    point_array = (_RtdlPoint * len(point_records))(*[_RtdlPoint(item.id, item.x, item.y) for item in point_records])
    polygon_refs, vertex_array = _encode_polygon_arrays(polygon_records)
    rows_ptr = ctypes.POINTER(_RtdlPipRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_pip(
        point_array,
        len(point_records),
        polygon_refs,
        len(polygon_records),
        vertex_array,
        len(vertex_array),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_pip failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "point_id": int(rows_ptr[index].point_id),
                "polygon_id": int(rows_ptr[index].polygon_id),
                "contains": int(rows_ptr[index].contains),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def point_nearest_segment_hiprt(
    points: tuple[_CanonicalPoint, ...],
    segments: tuple[_CanonicalSegment, ...],
) -> tuple[dict[str, int | float], ...]:
    point_records = tuple(points)
    segment_records = tuple(segments)
    if any(not isinstance(point, _CanonicalPoint) for point in point_records):
        raise TypeError("point_nearest_segment_hiprt currently supports only Point2D inputs")
    if any(not isinstance(segment, _CanonicalSegment) for segment in segment_records):
        raise TypeError("point_nearest_segment_hiprt currently supports only Segment inputs")
    point_array = (_RtdlPoint * len(point_records))(*[_RtdlPoint(item.id, item.x, item.y) for item in point_records])
    segment_array = (_RtdlSegment * len(segment_records))(
        *[_RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in segment_records]
    )
    rows_ptr = ctypes.POINTER(_RtdlPointNearestSegmentRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_point_nearest_segment(
        point_array,
        len(point_records),
        segment_array,
        len(segment_records),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_point_nearest_segment failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "point_id": int(rows_ptr[index].point_id),
                "segment_id": int(rows_ptr[index].segment_id),
                "distance": float(rows_ptr[index].distance),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def overlay_compose_hiprt(
    left_polygons: tuple[_CanonicalPolygon, ...],
    right_polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, int], ...]:
    left_records = tuple(left_polygons)
    right_records = tuple(right_polygons)
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in left_records):
        raise TypeError("overlay_compose_hiprt currently supports only Polygon left inputs")
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in right_records):
        raise TypeError("overlay_compose_hiprt currently supports only Polygon right inputs")
    left_refs, left_vertices = _encode_polygon_arrays(left_records)
    right_refs, right_vertices = _encode_polygon_arrays(right_records)
    rows_ptr = ctypes.POINTER(_RtdlOverlayRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_overlay(
        left_refs,
        len(left_records),
        left_vertices,
        len(left_vertices),
        right_refs,
        len(right_records),
        right_vertices,
        len(right_vertices),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_overlay failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "left_polygon_id": int(rows_ptr[index].left_polygon_id),
                "right_polygon_id": int(rows_ptr[index].right_polygon_id),
                "requires_lsi": int(rows_ptr[index].requires_lsi),
                "requires_pip": int(rows_ptr[index].requires_pip),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def _encode_segment_array(segments: tuple[_CanonicalSegment, ...]):
    return (_RtdlSegment * len(segments))(
        *[_RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in segments]
    )


def segment_polygon_hitcount_hiprt(
    segments: tuple[_CanonicalSegment, ...],
    polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, int], ...]:
    segment_records = tuple(segments)
    polygon_records = tuple(polygons)
    if any(not isinstance(segment, _CanonicalSegment) for segment in segment_records):
        raise TypeError("segment_polygon_hitcount_hiprt currently supports only Segment inputs")
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in polygon_records):
        raise TypeError("segment_polygon_hitcount_hiprt currently supports only Polygon inputs")
    segment_array = _encode_segment_array(segment_records)
    polygon_refs, vertex_array = _encode_polygon_arrays(polygon_records)
    rows_ptr = ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_segment_polygon_hitcount(
        segment_array,
        len(segment_records),
        polygon_refs,
        len(polygon_records),
        vertex_array,
        len(vertex_array),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_segment_polygon_hitcount failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "segment_id": int(rows_ptr[index].segment_id),
                "hit_count": int(rows_ptr[index].hit_count),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def segment_polygon_anyhit_rows_hiprt(
    segments: tuple[_CanonicalSegment, ...],
    polygons: tuple[_CanonicalPolygon, ...],
) -> tuple[dict[str, int], ...]:
    segment_records = tuple(segments)
    polygon_records = tuple(polygons)
    if any(not isinstance(segment, _CanonicalSegment) for segment in segment_records):
        raise TypeError("segment_polygon_anyhit_rows_hiprt currently supports only Segment inputs")
    if any(not isinstance(polygon, _CanonicalPolygon) for polygon in polygon_records):
        raise TypeError("segment_polygon_anyhit_rows_hiprt currently supports only Polygon inputs")
    segment_array = _encode_segment_array(segment_records)
    polygon_refs, vertex_array = _encode_polygon_arrays(polygon_records)
    rows_ptr = ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_segment_polygon_anyhit_rows(
        segment_array,
        len(segment_records),
        polygon_refs,
        len(polygon_records),
        vertex_array,
        len(vertex_array),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_segment_polygon_anyhit_rows failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "segment_id": int(rows_ptr[index].segment_id),
                "polygon_id": int(rows_ptr[index].polygon_id),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def fixed_radius_neighbors_3d_hiprt(
    query_points: tuple[_CanonicalPoint3D, ...],
    search_points: tuple[_CanonicalPoint3D, ...],
    *,
    radius: float,
    k_max: int,
) -> tuple[dict[str, int | float], ...]:
    query_records = tuple(query_points)
    search_records = tuple(search_points)
    if any(not isinstance(point, _CanonicalPoint3D) for point in query_records):
        raise TypeError("fixed_radius_neighbors_3d_hiprt currently supports only Point3D query inputs")
    if any(not isinstance(point, _CanonicalPoint3D) for point in search_records):
        raise TypeError("fixed_radius_neighbors_3d_hiprt currently supports only Point3D search inputs")
    if k_max <= 0:
        raise ValueError("fixed_radius_neighbors_3d_hiprt k_max must be positive")
    if k_max > 64:
        raise ValueError("HIPRT fixed_radius_neighbors_3d currently supports k_max <= 64")

    query_array = (_RtdlPoint3D * len(query_records))(
        *[_RtdlPoint3D(item.id, item.x, item.y, item.z) for item in query_records]
    )
    search_array = (_RtdlPoint3D * len(search_records))(
        *[_RtdlPoint3D(item.id, item.x, item.y, item.z) for item in search_records]
    )
    rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_fixed_radius_neighbors_3d(
        query_array,
        len(query_records),
        search_array,
        len(search_records),
        float(radius),
        int(k_max),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_fixed_radius_neighbors_3d failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "query_id": int(rows_ptr[index].query_id),
                "neighbor_id": int(rows_ptr[index].neighbor_id),
                "distance": float(rows_ptr[index].distance),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def fixed_radius_neighbors_2d_hiprt(
    query_points: tuple[_CanonicalPoint, ...],
    search_points: tuple[_CanonicalPoint, ...],
    *,
    radius: float,
    k_max: int,
) -> tuple[dict[str, int | float], ...]:
    query_records = tuple(query_points)
    search_records = tuple(search_points)
    if any(not isinstance(point, _CanonicalPoint) for point in query_records):
        raise TypeError("fixed_radius_neighbors_2d_hiprt currently supports only Point2D query inputs")
    if any(not isinstance(point, _CanonicalPoint) for point in search_records):
        raise TypeError("fixed_radius_neighbors_2d_hiprt currently supports only Point2D search inputs")
    if k_max <= 0:
        raise ValueError("fixed_radius_neighbors_2d_hiprt k_max must be positive")
    if k_max > 64:
        raise ValueError("HIPRT fixed_radius_neighbors_2d currently supports k_max <= 64")

    query_array = (_RtdlPoint * len(query_records))(*[_RtdlPoint(item.id, item.x, item.y) for item in query_records])
    search_array = (_RtdlPoint * len(search_records))(*[_RtdlPoint(item.id, item.x, item.y) for item in search_records])
    rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_fixed_radius_neighbors_2d(
        query_array,
        len(query_records),
        search_array,
        len(search_records),
        float(radius),
        int(k_max),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_fixed_radius_neighbors_2d failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "query_id": int(rows_ptr[index].query_id),
                "neighbor_id": int(rows_ptr[index].neighbor_id),
                "distance": float(rows_ptr[index].distance),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def _global_radius_for_all_3d_candidates(
    query_points: tuple[_CanonicalPoint3D, ...],
    search_points: tuple[_CanonicalPoint3D, ...],
) -> float:
    if not query_points or not search_points:
        return 0.0
    xs = [point.x for point in (*query_points, *search_points)]
    ys = [point.y for point in (*query_points, *search_points)]
    zs = [point.z for point in (*query_points, *search_points)]
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    dz = max(zs) - min(zs)
    return math.sqrt(dx * dx + dy * dy + dz * dz) + 1.0e-6


def _global_radius_for_all_2d_candidates(
    query_points: tuple[_CanonicalPoint, ...],
    search_points: tuple[_CanonicalPoint, ...],
) -> float:
    if not query_points or not search_points:
        return 0.0
    xs = [point.x for point in (*query_points, *search_points)]
    ys = [point.y for point in (*query_points, *search_points)]
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    return math.sqrt(dx * dx + dy * dy) + 1.0e-6


def _add_neighbor_rank(rows: tuple[dict[str, int | float], ...], k: int) -> tuple[dict[str, int | float], ...]:
    ranked: list[dict[str, int | float]] = []
    current_query = None
    rank = 0
    for row in rows:
        query_id = int(row["query_id"])
        if query_id != current_query:
            current_query = query_id
            rank = 1
        if rank > k:
            continue
        ranked.append({**row, "neighbor_rank": rank})
        rank += 1
    return tuple(ranked)


def knn_rows_3d_hiprt(
    query_points: tuple[_CanonicalPoint3D, ...],
    search_points: tuple[_CanonicalPoint3D, ...],
    *,
    k: int,
) -> tuple[dict[str, int | float], ...]:
    if k <= 0:
        raise ValueError("knn_rows_3d_hiprt k must be positive")
    radius = _global_radius_for_all_3d_candidates(tuple(query_points), tuple(search_points))
    rows = fixed_radius_neighbors_3d_hiprt(
        query_points,
        search_points,
        radius=radius,
        k_max=k,
    )
    return _add_neighbor_rank(rows, k)


def knn_rows_2d_hiprt(
    query_points: tuple[_CanonicalPoint, ...],
    search_points: tuple[_CanonicalPoint, ...],
    *,
    k: int,
) -> tuple[dict[str, int | float], ...]:
    if k <= 0:
        raise ValueError("knn_rows_2d_hiprt k must be positive")
    radius = _global_radius_for_all_2d_candidates(tuple(query_points), tuple(search_points))
    rows = fixed_radius_neighbors_2d_hiprt(
        query_points,
        search_points,
        radius=radius,
        k_max=k,
    )
    return _add_neighbor_rank(rows, k)


def bounded_knn_rows_3d_hiprt(
    query_points: tuple[_CanonicalPoint3D, ...],
    search_points: tuple[_CanonicalPoint3D, ...],
    *,
    radius: float,
    k_max: int,
) -> tuple[dict[str, int | float], ...]:
    rows = fixed_radius_neighbors_3d_hiprt(
        query_points,
        search_points,
        radius=radius,
        k_max=k_max,
    )
    return _add_neighbor_rank(rows, k_max)


def bounded_knn_rows_2d_hiprt(
    query_points: tuple[_CanonicalPoint, ...],
    search_points: tuple[_CanonicalPoint, ...],
    *,
    radius: float,
    k_max: int,
) -> tuple[dict[str, int | float], ...]:
    rows = fixed_radius_neighbors_2d_hiprt(
        query_points,
        search_points,
        radius=radius,
        k_max=k_max,
    )
    return _add_neighbor_rank(rows, k_max)


def bfs_expand_hiprt(
    graph: _CanonicalCSRGraph,
    frontier: tuple[_CanonicalFrontierVertex, ...],
    visited: tuple[int, ...],
    *,
    dedupe: bool = True,
) -> tuple[dict[str, int], ...]:
    if not isinstance(graph, _CanonicalCSRGraph):
        raise TypeError("bfs_expand_hiprt currently supports only CSRGraph build inputs")
    frontier_records = tuple(frontier)
    if any(not isinstance(item, _CanonicalFrontierVertex) for item in frontier_records):
        raise TypeError("bfs_expand_hiprt currently supports only FrontierVertex probe inputs")
    visited_records = tuple(int(value) for value in visited)
    if graph.vertex_count < 0:
        raise ValueError("bfs_expand_hiprt graph vertex_count must be non-negative")
    if graph.vertex_count > (2**32 - 1):
        raise ValueError("HIPRT bfs_expand_hiprt currently supports vertex IDs <= 2^32-1")

    frontier_array = (_RtdlFrontierVertex * len(frontier_records))(
        *[_RtdlFrontierVertex(item.vertex_id, item.level) for item in frontier_records]
    )
    row_offsets_array = (ctypes.c_uint32 * len(graph.row_offsets))(*[int(value) for value in graph.row_offsets])
    column_indices_array = (ctypes.c_uint32 * len(graph.column_indices))(
        *[int(value) for value in graph.column_indices]
    )
    visited_array = (ctypes.c_uint32 * len(visited_records))(*visited_records)
    rows_ptr = ctypes.POINTER(_RtdlBfsRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_bfs_expand(
        frontier_array,
        len(frontier_records),
        row_offsets_array,
        len(graph.row_offsets),
        column_indices_array,
        len(graph.column_indices),
        int(graph.vertex_count),
        visited_array,
        len(visited_records),
        1 if dedupe else 0,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_bfs_expand failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "src_vertex": int(rows_ptr[index].src_vertex),
                "dst_vertex": int(rows_ptr[index].dst_vertex),
                "level": int(rows_ptr[index].level),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def triangle_match_hiprt(
    graph: _CanonicalCSRGraph,
    seeds: tuple[_CanonicalEdgeSeed, ...],
    *,
    order: str = "id_ascending",
    unique: bool = True,
) -> tuple[dict[str, int], ...]:
    if order != "id_ascending":
        raise ValueError("triangle_match_hiprt currently supports only order='id_ascending'")
    if not isinstance(graph, _CanonicalCSRGraph):
        raise TypeError("triangle_match_hiprt currently supports only CSRGraph build inputs")
    seed_records = tuple(seeds)
    if any(not isinstance(item, _CanonicalEdgeSeed) for item in seed_records):
        raise TypeError("triangle_match_hiprt currently supports only EdgeSeed probe inputs")
    if graph.vertex_count < 0:
        raise ValueError("triangle_match_hiprt graph vertex_count must be non-negative")
    if graph.vertex_count > (2**32 - 1):
        raise ValueError("HIPRT triangle_match_hiprt currently supports vertex IDs <= 2^32-1")

    row_offsets_array = (ctypes.c_uint32 * len(graph.row_offsets))(*[int(value) for value in graph.row_offsets])
    column_indices_array = (ctypes.c_uint32 * len(graph.column_indices))(
        *[int(value) for value in graph.column_indices]
    )
    seed_array = (_RtdlEdgeSeed * len(seed_records))(*[_RtdlEdgeSeed(item.u, item.v) for item in seed_records])
    rows_ptr = ctypes.POINTER(_RtdlTriangleRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_triangle_probe(
        row_offsets_array,
        len(graph.row_offsets),
        column_indices_array,
        len(graph.column_indices),
        seed_array,
        len(seed_records),
        1,
        1 if unique else 0,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_triangle_probe failed with status {status}: {detail}")
    try:
        return tuple(
            {
                "u": int(rows_ptr[index].u),
                "v": int(rows_ptr[index].v),
                "w": int(rows_ptr[index].w),
            }
            for index in range(row_count.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


class PreparedHiprtGraphCSR:
    def __init__(self, handle: ctypes.c_void_p, *, empty: bool = False) -> None:
        self._handle = handle
        self._empty = empty

    def close(self) -> None:
        if self._handle:
            _hiprt_lib().rtdl_hiprt_destroy_prepared_graph_csr(self._handle)
            self._handle = ctypes.c_void_p()

    def __enter__(self) -> "PreparedHiprtGraphCSR":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def bfs_expand(
        self,
        frontier: tuple[_CanonicalFrontierVertex, ...],
        visited: tuple[int, ...],
        *,
        dedupe: bool = True,
    ) -> tuple[dict[str, int], ...]:
        frontier_records = tuple(frontier)
        if any(not isinstance(item, _CanonicalFrontierVertex) for item in frontier_records):
            raise TypeError("Prepared HIPRT bfs_expand currently supports only FrontierVertex probe inputs")
        visited_records = tuple(int(value) for value in visited)
        if self._empty:
            return ()
        if not self._handle:
            raise RuntimeError("prepared HIPRT graph CSR handle is closed")

        frontier_array = (_RtdlFrontierVertex * len(frontier_records))(
            *[_RtdlFrontierVertex(item.vertex_id, item.level) for item in frontier_records]
        )
        visited_array = (ctypes.c_uint32 * len(visited_records))(*visited_records)
        rows_ptr = ctypes.POINTER(_RtdlBfsRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = _hiprt_lib().rtdl_hiprt_run_prepared_bfs_expand(
            self._handle,
            frontier_array,
            len(frontier_records),
            visited_array,
            len(visited_records),
            1 if dedupe else 0,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            ctypes.sizeof(error),
        )
        if status != 0:
            detail = error.value.decode("utf-8", errors="replace")
            raise RuntimeError(f"rtdl_hiprt_run_prepared_bfs_expand failed with status {status}: {detail}")
        try:
            return tuple(
                {
                    "src_vertex": int(rows_ptr[index].src_vertex),
                    "dst_vertex": int(rows_ptr[index].dst_vertex),
                    "level": int(rows_ptr[index].level),
                }
                for index in range(row_count.value)
            )
        finally:
            _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)

    def triangle_match(
        self,
        seeds: tuple[_CanonicalEdgeSeed, ...],
        *,
        order: str = "id_ascending",
        unique: bool = True,
    ) -> tuple[dict[str, int], ...]:
        if order != "id_ascending":
            raise ValueError("Prepared HIPRT triangle_match currently supports only order='id_ascending'")
        seed_records = tuple(seeds)
        if any(not isinstance(item, _CanonicalEdgeSeed) for item in seed_records):
            raise TypeError("Prepared HIPRT triangle_match currently supports only EdgeSeed probe inputs")
        if self._empty:
            return ()
        if not self._handle:
            raise RuntimeError("prepared HIPRT graph CSR handle is closed")

        seed_array = (_RtdlEdgeSeed * len(seed_records))(*[_RtdlEdgeSeed(item.u, item.v) for item in seed_records])
        rows_ptr = ctypes.POINTER(_RtdlTriangleRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = _hiprt_lib().rtdl_hiprt_run_prepared_triangle_probe(
            self._handle,
            seed_array,
            len(seed_records),
            1,
            1 if unique else 0,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            ctypes.sizeof(error),
        )
        if status != 0:
            detail = error.value.decode("utf-8", errors="replace")
            raise RuntimeError(f"rtdl_hiprt_run_prepared_triangle_probe failed with status {status}: {detail}")
        try:
            return tuple(
                {
                    "u": int(rows_ptr[index].u),
                    "v": int(rows_ptr[index].v),
                    "w": int(rows_ptr[index].w),
                }
                for index in range(row_count.value)
            )
        finally:
            _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def prepare_hiprt_graph_csr(graph: _CanonicalCSRGraph) -> PreparedHiprtGraphCSR:
    if not isinstance(graph, _CanonicalCSRGraph):
        raise TypeError("prepare_hiprt_graph_csr currently supports only CSRGraph build inputs")
    if graph.vertex_count < 0:
        raise ValueError("prepare_hiprt_graph_csr graph vertex_count must be non-negative")
    if graph.vertex_count > (2**32 - 1):
        raise ValueError("HIPRT prepare_hiprt_graph_csr currently supports vertex IDs <= 2^32-1")
    if not graph.column_indices:
        return PreparedHiprtGraphCSR(ctypes.c_void_p(), empty=True)
    row_offsets_array = (ctypes.c_uint32 * len(graph.row_offsets))(*[int(value) for value in graph.row_offsets])
    column_indices_array = (ctypes.c_uint32 * len(graph.column_indices))(
        *[int(value) for value in graph.column_indices]
    )
    handle = ctypes.c_void_p()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_prepare_graph_csr(
        row_offsets_array,
        len(graph.row_offsets),
        column_indices_array,
        len(graph.column_indices),
        int(graph.vertex_count),
        ctypes.byref(handle),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_prepare_graph_csr failed with status {status}: {detail}")
    return PreparedHiprtGraphCSR(handle)


def conjunctive_scan_hiprt(table_rows, predicates) -> tuple[dict[str, int], ...]:
    if not table_rows:
        return ()
    encoded_rows, encoded_predicates, _reverse_maps = _encode_db_text_fields(table_rows, predicates.clauses)
    fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
    clauses_array = _encode_db_clauses(encoded_predicates)
    rows_ptr = ctypes.POINTER(_RtdlDbRowIdRow)()
    row_count_out = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_conjunctive_scan(
        fields_array,
        len(fields_array),
        row_values_array,
        row_count,
        clauses_array,
        len(clauses_array),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_conjunctive_scan failed with status {status}: {detail}")
    try:
        return tuple({"row_id": int(rows_ptr[index].row_id)} for index in range(row_count_out.value))
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def grouped_count_hiprt(table_rows, query) -> tuple[dict[str, object], ...]:
    if len(query.group_keys) != 1:
        raise ValueError("HIPRT grouped_count currently supports exactly one group key")
    if not table_rows:
        return ()
    group_key = query.group_keys[0]
    encoded_rows, encoded_predicates, reverse_maps = _encode_db_text_fields(
        table_rows,
        query.predicates,
        extra_fields=(group_key,),
    )
    fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
    clauses_array = _encode_db_clauses(encoded_predicates)
    rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
    row_count_out = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_grouped_count(
        fields_array,
        len(fields_array),
        row_values_array,
        row_count,
        clauses_array,
        len(clauses_array),
        group_key.encode("utf-8"),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_grouped_count failed with status {status}: {detail}")
    try:
        reverse_map = reverse_maps.get(group_key)
        return tuple(
            {
                group_key: _decode_db_group_key(reverse_map, int(rows_ptr[index].group_key)),
                "count": int(rows_ptr[index].count),
            }
            for index in range(row_count_out.value)
        )
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def grouped_sum_hiprt(table_rows, query) -> tuple[dict[str, object], ...]:
    if len(query.group_keys) != 1:
        raise ValueError("HIPRT grouped_sum currently supports exactly one group key")
    if not query.value_field:
        raise ValueError("HIPRT grouped_sum requires a value_field")
    if not table_rows:
        return ()
    group_key = query.group_keys[0]
    encoded_rows, encoded_predicates, reverse_maps = _encode_db_text_fields(
        table_rows,
        query.predicates,
        extra_fields=(group_key, query.value_field),
    )
    fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
    clauses_array = _encode_db_clauses(encoded_predicates)
    rows_ptr = ctypes.POINTER(_RtdlDbGroupedSumRow)()
    row_count_out = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_run_grouped_sum(
        fields_array,
        len(fields_array),
        row_values_array,
        row_count,
        clauses_array,
        len(clauses_array),
        group_key.encode("utf-8"),
        query.value_field.encode("utf-8"),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_run_grouped_sum failed with status {status}: {detail}")
    try:
        reverse_map = reverse_maps.get(group_key)
        rows = []
        for index in range(row_count_out.value):
            total = float(rows_ptr[index].sum)
            rows.append(
                {
                    group_key: _decode_db_group_key(reverse_map, int(rows_ptr[index].group_key)),
                    "sum": int(total) if total.is_integer() else total,
                }
            )
        return tuple(rows)
    finally:
        _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def _encode_prepared_db_table(table_rows):
    text_fields = {
        str(field)
        for row in table_rows
        for field, value in row.items()
        if isinstance(value, str)
    }
    field_maps: dict[str, dict[object, int]] = {}
    reverse_maps: dict[str, dict[int, object]] = {}
    for field in sorted(text_fields):
        values = sorted({row[field] for row in table_rows})
        encode_map = {value: index + 1 for index, value in enumerate(values)}
        field_maps[field] = encode_map
        reverse_maps[field] = {code: value for value, code in encode_map.items()}
    encoded_rows = []
    for row in table_rows:
        encoded = dict(row)
        for field, encode_map in field_maps.items():
            encoded[field] = encode_map[row[field]]
        encoded_rows.append(encoded)
    return tuple(encoded_rows), field_maps, reverse_maps


def _encode_prepared_db_text_clause_values(clause: PredicateClause, encode_map: dict[object, int]) -> tuple[int, int | None]:
    values = sorted(encode_map)
    op = str(clause.op)
    if op == "eq":
        return int(encode_map.get(clause.value, 0)), None
    if op in {"lt", "ge"}:
        return bisect_left(values, clause.value) + 1, None
    if op in {"le", "gt"}:
        return bisect_right(values, clause.value), None
    if op == "between":
        return bisect_left(values, clause.value) + 1, bisect_right(values, clause.value_hi)
    raise ValueError(f"unsupported predicate operator: {clause.op}")


def _encode_prepared_db_clauses(clauses, field_maps):
    encoded = []
    for clause in clauses:
        field = str(clause.field)
        if field in field_maps:
            value, value_hi = _encode_prepared_db_text_clause_values(clause, field_maps[field])
            encoded.append(PredicateClause(field=field, op=clause.op, value=value, value_hi=value_hi))
        else:
            encoded.append(clause)
    return _encode_db_clauses(tuple(encoded))


class PreparedHiprtDbTable:
    def __init__(self, handle: ctypes.c_void_p, *, empty: bool = False, field_maps=None, reverse_maps=None) -> None:
        self._handle = handle
        self._empty = empty
        self._field_maps = dict(field_maps or {})
        self._reverse_maps = dict(reverse_maps or {})

    def close(self) -> None:
        if self._handle:
            _hiprt_lib().rtdl_hiprt_destroy_prepared_db_table(self._handle)
            self._handle = ctypes.c_void_p()

    def __enter__(self) -> "PreparedHiprtDbTable":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def conjunctive_scan(self, predicates) -> tuple[dict[str, int], ...]:
        predicate_bundle = normalize_predicate_bundle(predicates)
        if self._empty:
            return ()
        if not self._handle:
            raise RuntimeError("prepared HIPRT DB table handle is closed")
        clauses_array = _encode_prepared_db_clauses(predicate_bundle.clauses, self._field_maps)
        rows_ptr = ctypes.POINTER(_RtdlDbRowIdRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = _hiprt_lib().rtdl_hiprt_run_prepared_conjunctive_scan(
            self._handle,
            clauses_array,
            len(clauses_array),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            ctypes.sizeof(error),
        )
        if status != 0:
            detail = error.value.decode("utf-8", errors="replace")
            raise RuntimeError(f"rtdl_hiprt_run_prepared_conjunctive_scan failed with status {status}: {detail}")
        try:
            return tuple({"row_id": int(rows_ptr[index].row_id)} for index in range(row_count_out.value))
        finally:
            _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)

    def grouped_count(self, query) -> tuple[dict[str, object], ...]:
        grouped_query = normalize_grouped_query(query)
        if len(grouped_query.group_keys) != 1:
            raise ValueError("Prepared HIPRT grouped_count currently supports exactly one group key")
        if self._empty:
            return ()
        if not self._handle:
            raise RuntimeError("prepared HIPRT DB table handle is closed")
        group_key = grouped_query.group_keys[0]
        clauses_array = _encode_prepared_db_clauses(grouped_query.predicates, self._field_maps)
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = _hiprt_lib().rtdl_hiprt_run_prepared_grouped_count(
            self._handle,
            clauses_array,
            len(clauses_array),
            group_key.encode("utf-8"),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            ctypes.sizeof(error),
        )
        if status != 0:
            detail = error.value.decode("utf-8", errors="replace")
            raise RuntimeError(f"rtdl_hiprt_run_prepared_grouped_count failed with status {status}: {detail}")
        try:
            reverse_map = self._reverse_maps.get(group_key)
            return tuple(
                {
                    group_key: _decode_db_group_key(reverse_map, int(rows_ptr[index].group_key)),
                    "count": int(rows_ptr[index].count),
                }
                for index in range(row_count_out.value)
            )
        finally:
            _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)

    def grouped_sum(self, query) -> tuple[dict[str, object], ...]:
        grouped_query = normalize_grouped_query(query)
        if len(grouped_query.group_keys) != 1:
            raise ValueError("Prepared HIPRT grouped_sum currently supports exactly one group key")
        if not grouped_query.value_field:
            raise ValueError("Prepared HIPRT grouped_sum requires a value_field")
        if self._empty:
            return ()
        if not self._handle:
            raise RuntimeError("prepared HIPRT DB table handle is closed")
        group_key = grouped_query.group_keys[0]
        clauses_array = _encode_prepared_db_clauses(grouped_query.predicates, self._field_maps)
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedSumRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = _hiprt_lib().rtdl_hiprt_run_prepared_grouped_sum(
            self._handle,
            clauses_array,
            len(clauses_array),
            group_key.encode("utf-8"),
            grouped_query.value_field.encode("utf-8"),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            ctypes.sizeof(error),
        )
        if status != 0:
            detail = error.value.decode("utf-8", errors="replace")
            raise RuntimeError(f"rtdl_hiprt_run_prepared_grouped_sum failed with status {status}: {detail}")
        try:
            reverse_map = self._reverse_maps.get(group_key)
            rows = []
            for index in range(row_count_out.value):
                total = float(rows_ptr[index].sum)
                rows.append(
                    {
                        group_key: _decode_db_group_key(reverse_map, int(rows_ptr[index].group_key)),
                        "sum": int(total) if total.is_integer() else total,
                    }
                )
            return tuple(rows)
        finally:
            _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def prepare_hiprt_db_table(table_rows) -> PreparedHiprtDbTable:
    normalized_rows = _normalize_records("table", "denorm_table", table_rows)
    if not normalized_rows:
        return PreparedHiprtDbTable(ctypes.c_void_p(), empty=True)
    encoded_rows, field_maps, reverse_maps = _encode_prepared_db_table(normalized_rows)
    fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
    handle = ctypes.c_void_p()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_prepare_db_table(
        fields_array,
        len(fields_array),
        row_values_array,
        row_count,
        ctypes.byref(handle),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_prepare_db_table failed with status {status}: {detail}")
    return PreparedHiprtDbTable(handle, field_maps=field_maps, reverse_maps=reverse_maps)


def _encode_ray_array(ray_records: tuple[_CanonicalRay3D, ...]):
    return (_RtdlRay3D * len(ray_records))(
        *[
            _RtdlRay3D(item.id, item.ox, item.oy, item.oz, item.dx, item.dy, item.dz, item.tmax)
            for item in ray_records
        ]
    )


def _encode_triangle_array(triangle_records: tuple[_CanonicalTriangle3D, ...]):
    return (_RtdlTriangle3D * len(triangle_records))(
        *[
            _RtdlTriangle3D(
                item.id,
                item.x0,
                item.y0,
                item.z0,
                item.x1,
                item.y1,
                item.z1,
                item.x2,
                item.y2,
                item.z2,
            )
            for item in triangle_records
        ]
    )


def _encode_point3d_array(point_records: tuple[_CanonicalPoint3D, ...]):
    return (_RtdlPoint3D * len(point_records))(
        *[_RtdlPoint3D(item.id, item.x, item.y, item.z) for item in point_records]
    )


class PreparedHiprtRayTriangleHitCount3D:
    def __init__(self, handle: ctypes.c_void_p) -> None:
        self._handle = handle

    def close(self) -> None:
        if self._handle:
            _hiprt_lib().rtdl_hiprt_destroy_prepared_ray_hitcount_3d(self._handle)
            self._handle = ctypes.c_void_p()

    def __enter__(self) -> "PreparedHiprtRayTriangleHitCount3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def run(self, rays: tuple[_CanonicalRay3D, ...]) -> tuple[dict[str, int], ...]:
        if not self._handle:
            raise RuntimeError("prepared HIPRT ray-triangle hit-count handle is closed")
        ray_records = tuple(rays)
        if any(not isinstance(ray, _CanonicalRay3D) for ray in ray_records):
            raise TypeError("Prepared HIPRT ray-triangle hit-count currently supports only Ray3D inputs")

        ray_array = _encode_ray_array(ray_records)
        rows_ptr = ctypes.POINTER(_RtdlRayHitCountRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = _hiprt_lib().rtdl_hiprt_run_prepared_ray_hitcount_3d(
            self._handle,
            ray_array,
            len(ray_records),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            ctypes.sizeof(error),
        )
        if status != 0:
            detail = error.value.decode("utf-8", errors="replace")
            raise RuntimeError(f"rtdl_hiprt_run_prepared_ray_hitcount_3d failed with status {status}: {detail}")
        try:
            return tuple(
                {"ray_id": int(rows_ptr[index].ray_id), "hit_count": int(rows_ptr[index].hit_count)}
                for index in range(row_count.value)
            )
        finally:
            _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def prepare_hiprt_ray_triangle_hit_count(
    triangles: tuple[_CanonicalTriangle3D, ...],
) -> PreparedHiprtRayTriangleHitCount3D:
    triangle_records = tuple(triangles)
    if any(not isinstance(triangle, _CanonicalTriangle3D) for triangle in triangle_records):
        raise TypeError("prepare_hiprt_ray_triangle_hit_count currently supports only Triangle3D inputs")
    triangle_array = _encode_triangle_array(triangle_records)
    handle = ctypes.c_void_p()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_prepare_ray_hitcount_3d(
        triangle_array,
        len(triangle_records),
        ctypes.byref(handle),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_prepare_ray_hitcount_3d failed with status {status}: {detail}")
    return PreparedHiprtRayTriangleHitCount3D(handle)


class PreparedHiprtFixedRadiusNeighbors3D:
    def __init__(self, handle: ctypes.c_void_p, *, empty: bool = False) -> None:
        self._handle = handle
        self._empty = empty

    def close(self) -> None:
        if self._handle:
            _hiprt_lib().rtdl_hiprt_destroy_prepared_fixed_radius_neighbors_3d(self._handle)
            self._handle = ctypes.c_void_p()

    def __enter__(self) -> "PreparedHiprtFixedRadiusNeighbors3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def run(
        self,
        query_points: tuple[_CanonicalPoint3D, ...],
        *,
        k_max: int,
    ) -> tuple[dict[str, int | float], ...]:
        query_records = tuple(query_points)
        if any(not isinstance(point, _CanonicalPoint3D) for point in query_records):
            raise TypeError("Prepared HIPRT fixed_radius_neighbors_3d currently supports only Point3D query inputs")
        if k_max <= 0:
            raise ValueError("Prepared HIPRT fixed_radius_neighbors_3d k_max must be positive")
        if k_max > 64:
            raise ValueError("HIPRT fixed_radius_neighbors_3d currently supports k_max <= 64")
        if self._empty:
            return ()
        if not self._handle:
            raise RuntimeError("prepared HIPRT fixed_radius_neighbors_3d handle is closed")

        query_array = _encode_point3d_array(query_records)
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = _hiprt_lib().rtdl_hiprt_run_prepared_fixed_radius_neighbors_3d(
            self._handle,
            query_array,
            len(query_records),
            int(k_max),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            ctypes.sizeof(error),
        )
        if status != 0:
            detail = error.value.decode("utf-8", errors="replace")
            raise RuntimeError(f"rtdl_hiprt_run_prepared_fixed_radius_neighbors_3d failed with status {status}: {detail}")
        try:
            return tuple(
                {
                    "query_id": int(rows_ptr[index].query_id),
                    "neighbor_id": int(rows_ptr[index].neighbor_id),
                    "distance": float(rows_ptr[index].distance),
                }
                for index in range(row_count.value)
            )
        finally:
            _hiprt_lib().rtdl_hiprt_free_rows(rows_ptr)


def prepare_hiprt_fixed_radius_neighbors_3d(
    search_points: tuple[_CanonicalPoint3D, ...],
    *,
    radius: float,
) -> PreparedHiprtFixedRadiusNeighbors3D:
    search_records = tuple(search_points)
    if any(not isinstance(point, _CanonicalPoint3D) for point in search_records):
        raise TypeError("prepare_hiprt_fixed_radius_neighbors_3d currently supports only Point3D search inputs")
    if radius < 0.0:
        raise ValueError("fixed_radius_neighbors radius must be non-negative")
    if not search_records:
        return PreparedHiprtFixedRadiusNeighbors3D(ctypes.c_void_p(), empty=True)
    search_array = _encode_point3d_array(search_records)
    handle = ctypes.c_void_p()
    error = ctypes.create_string_buffer(4096)
    status = _hiprt_lib().rtdl_hiprt_prepare_fixed_radius_neighbors_3d(
        search_array,
        len(search_records),
        float(radius),
        ctypes.byref(handle),
        error,
        ctypes.sizeof(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_hiprt_prepare_fixed_radius_neighbors_3d failed with status {status}: {detail}")
    return PreparedHiprtFixedRadiusNeighbors3D(handle)


def _unsupported_hiprt_peer_workload(predicate_name: str, detail: str) -> NotImplementedError:
    goal = _HIPRT_GOAL_BY_PREDICATE.get(predicate_name, "the v0.9 HIPRT plan")
    return NotImplementedError(
        f"HIPRT v0.9 API skeleton recognizes `{predicate_name}`, but {detail}; "
        f"implementation is tracked under {goal}. No CPU fallback is used."
    )


def _validate_hiprt_kernel(compiled: CompiledKernel) -> tuple[str, tuple[str, str], dict[str, object]]:
    _validate_kernel_for_cpu(compiled)
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name not in _HIPRT_PEER_PREDICATES:
        raise ValueError(f"unsupported predicate for HIPRT backend: {predicate_name!r}")
    if predicate_name not in _HIPRT_IMPLEMENTED_PREDICATES:
        raise _unsupported_hiprt_peer_workload(
            predicate_name,
            "that workload family is not implemented yet",
        )
    if predicate_name == "segment_intersection":
        left_input = compiled.candidates.left
        right_input = compiled.candidates.right
        if left_input.geometry.name != "segments" or right_input.geometry.name != "segments":
            raise ValueError("HIPRT segment_intersection requires segment probe input followed by segment build input")
        if left_input.role != "probe" or right_input.role != "build":
            raise ValueError("HIPRT segment_intersection requires left role='probe' and right role='build'")
        if left_input.layout.name != "Segment2D" or right_input.layout.name != "Segment2D":
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only Segment2DLayout inputs are implemented today",
            )
        return predicate_name, (left_input.name, right_input.name), {}
    if predicate_name == "point_in_polygon":
        points_input = compiled.candidates.left
        polygons_input = compiled.candidates.right
        if points_input.geometry.name != "points" or polygons_input.geometry.name != "polygons":
            raise ValueError("HIPRT point_in_polygon requires point probe input followed by polygon build input")
        if points_input.role != "probe" or polygons_input.role != "build":
            raise ValueError("HIPRT point_in_polygon requires points role='probe' and polygons role='build'")
        if points_input.layout.name != "Point2D" or polygons_input.layout.name != "Polygon2DRef":
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only Point2DLayout and Polygon2DRef inputs are implemented today",
            )
        options = dict(compiled.refine_op.predicate.options)
        if options.get("boundary_mode", "inclusive") != "inclusive":
            raise ValueError("HIPRT point_in_polygon currently supports only boundary_mode='inclusive'")
        if options.get("result_mode", "full_matrix") != "full_matrix":
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only result_mode='full_matrix' is implemented today",
            )
        return predicate_name, (points_input.name, polygons_input.name), options
    if predicate_name == "overlay_compose":
        left_input = compiled.candidates.left
        right_input = compiled.candidates.right
        if left_input.geometry.name != "polygons" or right_input.geometry.name != "polygons":
            raise ValueError("HIPRT overlay_compose requires polygon probe input followed by polygon build input")
        if left_input.role != "probe" or right_input.role != "build":
            raise ValueError("HIPRT overlay_compose requires left polygons role='probe' and right polygons role='build'")
        if left_input.layout.name != "Polygon2DRef" or right_input.layout.name != "Polygon2DRef":
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only Polygon2DRef inputs are implemented today",
            )
        return predicate_name, (left_input.name, right_input.name), {}
    if predicate_name == "point_nearest_segment":
        points_input = compiled.candidates.left
        segments_input = compiled.candidates.right
        if points_input.geometry.name != "points" or segments_input.geometry.name != "segments":
            raise ValueError("HIPRT point_nearest_segment requires point probe input followed by segment build input")
        if points_input.role != "probe" or segments_input.role != "build":
            raise ValueError("HIPRT point_nearest_segment requires points role='probe' and segments role='build'")
        if points_input.layout.name != "Point2D" or segments_input.layout.name != "Segment2D":
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only Point2DLayout and Segment2DLayout inputs are implemented today",
            )
        return predicate_name, (points_input.name, segments_input.name), {}
    if predicate_name in {"segment_polygon_hitcount", "segment_polygon_anyhit_rows"}:
        segments_input = compiled.candidates.left
        polygons_input = compiled.candidates.right
        if segments_input.geometry.name != "segments" or polygons_input.geometry.name != "polygons":
            raise ValueError(f"HIPRT {predicate_name} requires segment probe input followed by polygon build input")
        if segments_input.role != "probe" or polygons_input.role != "build":
            raise ValueError(f"HIPRT {predicate_name} requires segments role='probe' and polygons role='build'")
        if segments_input.layout.name != "Segment2D" or polygons_input.layout.name != "Polygon2DRef":
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only Segment2DLayout and Polygon2DRef inputs are implemented today",
            )
        return predicate_name, (segments_input.name, polygons_input.name), {}
    if predicate_name == "fixed_radius_neighbors":
        query_input = compiled.candidates.left
        search_input = compiled.candidates.right
        if query_input.geometry.name != "points" or search_input.geometry.name != "points":
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only Point2D/Point3D fixed-radius inputs are implemented today",
            )
        if query_input.role != "probe" or search_input.role != "build":
            raise ValueError("HIPRT fixed_radius_neighbors requires query points role='probe' and search points role='build'")
        if (query_input.layout.name, search_input.layout.name) not in {
            ("Point2D", "Point2D"),
            ("Point3D", "Point3D"),
        }:
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only matching Point2DLayout or Point3DLayout fixed-radius inputs are implemented today",
            )
        options = dict(compiled.refine_op.predicate.options)
        options["layout_pair"] = (query_input.layout.name, search_input.layout.name)
        return predicate_name, (query_input.name, search_input.name), options
    if predicate_name in {"knn_rows", "bounded_knn_rows"}:
        query_input = compiled.candidates.left
        search_input = compiled.candidates.right
        if query_input.geometry.name != "points" or search_input.geometry.name != "points":
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only Point2D/Point3D nearest-neighbor inputs are implemented today",
            )
        if query_input.role != "probe" or search_input.role != "build":
            raise ValueError(f"HIPRT {predicate_name} requires query points role='probe' and search points role='build'")
        if (query_input.layout.name, search_input.layout.name) not in {
            ("Point2D", "Point2D"),
            ("Point3D", "Point3D"),
        }:
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only matching Point2DLayout or Point3DLayout nearest-neighbor inputs are implemented today",
            )
        options = dict(compiled.refine_op.predicate.options)
        options["layout_pair"] = (query_input.layout.name, search_input.layout.name)
        return predicate_name, (query_input.name, search_input.name), options
    if predicate_name == "bfs_discover":
        frontier_input = compiled.candidates.left
        graph_input = compiled.candidates.right
        if frontier_input.geometry.name != "vertex_frontier" or graph_input.geometry.name != "graph_csr":
            raise ValueError("HIPRT bfs_discover requires vertex frontier probe input followed by CSR graph build input")
        if frontier_input.role != "probe" or graph_input.role != "build":
            raise ValueError("HIPRT bfs_discover requires frontier role='probe' and graph role='build'")
        options = dict(compiled.refine_op.predicate.options)
        visited_input = str(options.get("visited_input", ""))
        if not visited_input:
            raise ValueError("HIPRT bfs_discover requires a visited input")
        return predicate_name, (frontier_input.name, graph_input.name), options
    if predicate_name == "triangle_match":
        seeds_input = compiled.candidates.left
        graph_input = compiled.candidates.right
        if seeds_input.geometry.name != "edge_set" or graph_input.geometry.name != "graph_csr":
            raise ValueError("HIPRT triangle_match requires edge seed probe input followed by CSR graph build input")
        if seeds_input.role != "probe" or graph_input.role != "build":
            raise ValueError("HIPRT triangle_match requires seeds role='probe' and graph role='build'")
        options = dict(compiled.refine_op.predicate.options)
        if options.get("order", "id_ascending") != "id_ascending":
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "only order='id_ascending' is implemented today",
            )
        return predicate_name, (seeds_input.name, graph_input.name), options
    if predicate_name == "conjunctive_scan":
        predicates_input = compiled.candidates.left
        table_input = compiled.candidates.right
        if predicates_input.geometry.name != "predicate_set" or table_input.geometry.name != "denorm_table":
            raise ValueError("HIPRT conjunctive_scan requires predicate probe input followed by denormalized table build input")
        if predicates_input.role != "probe" or table_input.role != "build":
            raise ValueError("HIPRT conjunctive_scan requires predicates role='probe' and table role='build'")
        return predicate_name, (predicates_input.name, table_input.name), dict(compiled.refine_op.predicate.options)
    if predicate_name in {"grouped_count", "grouped_sum"}:
        query_input = compiled.candidates.left
        table_input = compiled.candidates.right
        if query_input.geometry.name != "grouped_query" or table_input.geometry.name != "denorm_table":
            raise ValueError(f"HIPRT {predicate_name} requires grouped query probe input followed by denormalized table build input")
        if query_input.role != "probe" or table_input.role != "build":
            raise ValueError(f"HIPRT {predicate_name} requires query role='probe' and table role='build'")
        return predicate_name, (query_input.name, table_input.name), dict(compiled.refine_op.predicate.options)
    rays_input = compiled.candidates.left
    triangles_input = compiled.candidates.right
    if rays_input.geometry.name != "rays" or triangles_input.geometry.name != "triangles":
        raise ValueError(f"HIPRT {predicate_name} requires ray probe input followed by triangle build input")
    if rays_input.role != "probe" or triangles_input.role != "build":
        raise ValueError(f"HIPRT {predicate_name} requires rays role='probe' and triangles role='build'")
    if (rays_input.layout.name, triangles_input.layout.name) not in {
        ("Ray2D", "Triangle2D"),
        ("Ray3D", "Triangle3D"),
    }:
        raise _unsupported_hiprt_peer_workload(
            predicate_name,
            "only matching Ray2D/Triangle2D or Ray3D/Triangle3D layouts are implemented today",
        )
    return predicate_name, (rays_input.name, triangles_input.name), {
        "layout_pair": (rays_input.layout.name, triangles_input.layout.name)
    }


def _validate_inputs(compiled: CompiledKernel, inputs: dict[str, object]) -> dict[str, object]:
    expected_inputs = {item.name: item for item in compiled.inputs}
    missing = [name for name in expected_inputs if name not in inputs]
    unexpected = [name for name in inputs if name not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL HIPRT inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL HIPRT inputs: {', '.join(sorted(unexpected))}")
    return {
        name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
        for name, payload in inputs.items()
    }


def run_hiprt(kernel_fn_or_compiled, *, result_mode: str = "dict", **inputs):
    if result_mode != "dict":
        raise ValueError("HIPRT result_mode currently supports only 'dict'")
    compiled = _resolve_kernel(kernel_fn_or_compiled)
    predicate_name, input_names, options = _validate_hiprt_kernel(compiled)
    normalized_inputs = _validate_inputs(compiled, inputs)
    if predicate_name in {"ray_triangle_hit_count", "ray_triangle_any_hit"}:
        ray_rows = normalized_inputs[input_names[0]]
        triangle_rows = normalized_inputs[input_names[1]]
        if predicate_name == "ray_triangle_any_hit":
            rows = ray_triangle_any_hit_hiprt(ray_rows, triangle_rows)
        elif options.get("layout_pair") == ("Ray2D", "Triangle2D"):
            rows = ray_triangle_hit_count_2d_hiprt(ray_rows, triangle_rows)
        else:
            rows = ray_triangle_hit_count_hiprt(ray_rows, triangle_rows)
    elif predicate_name == "segment_intersection":
        rows = segment_intersection_hiprt(
            normalized_inputs[input_names[0]],
            normalized_inputs[input_names[1]],
        )
    elif predicate_name == "point_in_polygon":
        rows = point_in_polygon_hiprt(
            normalized_inputs[input_names[0]],
            normalized_inputs[input_names[1]],
        )
    elif predicate_name == "overlay_compose":
        rows = overlay_compose_hiprt(
            normalized_inputs[input_names[0]],
            normalized_inputs[input_names[1]],
        )
    elif predicate_name == "point_nearest_segment":
        rows = point_nearest_segment_hiprt(
            normalized_inputs[input_names[0]],
            normalized_inputs[input_names[1]],
        )
    elif predicate_name == "segment_polygon_hitcount":
        rows = segment_polygon_hitcount_hiprt(
            normalized_inputs[input_names[0]],
            normalized_inputs[input_names[1]],
        )
    elif predicate_name == "segment_polygon_anyhit_rows":
        rows = segment_polygon_anyhit_rows_hiprt(
            normalized_inputs[input_names[0]],
            normalized_inputs[input_names[1]],
        )
    elif predicate_name == "fixed_radius_neighbors":
        if options.get("layout_pair") == ("Point2D", "Point2D"):
            rows = fixed_radius_neighbors_2d_hiprt(
                normalized_inputs[input_names[0]],
                normalized_inputs[input_names[1]],
                radius=float(options["radius"]),
                k_max=int(options["k_max"]),
            )
        else:
            rows = fixed_radius_neighbors_3d_hiprt(
                normalized_inputs[input_names[0]],
                normalized_inputs[input_names[1]],
                radius=float(options["radius"]),
                k_max=int(options["k_max"]),
            )
    elif predicate_name == "bounded_knn_rows":
        if options.get("layout_pair") == ("Point2D", "Point2D"):
            rows = bounded_knn_rows_2d_hiprt(
                normalized_inputs[input_names[0]],
                normalized_inputs[input_names[1]],
                radius=float(options["radius"]),
                k_max=int(options["k_max"]),
            )
        else:
            rows = bounded_knn_rows_3d_hiprt(
                normalized_inputs[input_names[0]],
                normalized_inputs[input_names[1]],
                radius=float(options["radius"]),
                k_max=int(options["k_max"]),
            )
    elif predicate_name == "knn_rows":
        if options.get("layout_pair") == ("Point2D", "Point2D"):
            rows = knn_rows_2d_hiprt(
                normalized_inputs[input_names[0]],
                normalized_inputs[input_names[1]],
                k=int(options["k"]),
            )
        else:
            rows = knn_rows_3d_hiprt(
                normalized_inputs[input_names[0]],
                normalized_inputs[input_names[1]],
                k=int(options["k"]),
            )
    elif predicate_name == "bfs_discover":
        visited_input = str(options["visited_input"])
        if visited_input not in normalized_inputs:
            raise ValueError(f"HIPRT bfs_discover visited input {visited_input!r} was not provided")
        rows = bfs_expand_hiprt(
            normalized_inputs[input_names[1]],
            normalized_inputs[input_names[0]],
            normalized_inputs[visited_input],
            dedupe=bool(options.get("dedupe", True)),
        )
    elif predicate_name == "triangle_match":
        rows = triangle_match_hiprt(
            normalized_inputs[input_names[1]],
            normalized_inputs[input_names[0]],
            order=str(options.get("order", "id_ascending")),
            unique=bool(options.get("unique", True)),
        )
    elif predicate_name == "conjunctive_scan":
        rows = conjunctive_scan_hiprt(
            normalized_inputs[input_names[1]],
            normalized_inputs[input_names[0]],
        )
    elif predicate_name == "grouped_count":
        rows = grouped_count_hiprt(
            normalized_inputs[input_names[1]],
            normalized_inputs[input_names[0]],
        )
    elif predicate_name == "grouped_sum":
        rows = grouped_sum_hiprt(
            normalized_inputs[input_names[1]],
            normalized_inputs[input_names[0]],
        )
    else:  # defensive: _validate_hiprt_kernel should have rejected this.
        raise _unsupported_hiprt_peer_workload(predicate_name, "that workload family is not implemented yet")
    return _project_rows(compiled, rows)


class PreparedHiprtKernel:
    def __init__(
        self,
        compiled: CompiledKernel,
        rays_name: str,
        triangles_name: str,
        prepared: PreparedHiprtRayTriangleHitCount3D,
    ) -> None:
        self.compiled = compiled
        self.rays_name = rays_name
        self.triangles_name = triangles_name
        self.prepared = prepared

    def close(self) -> None:
        self.prepared.close()

    def __enter__(self) -> "PreparedHiprtKernel":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def run(self, **inputs) -> tuple[dict[str, object], ...]:
        missing = [self.rays_name] if self.rays_name not in inputs else []
        unexpected = [name for name in inputs if name != self.rays_name]
        if missing:
            raise ValueError(f"missing RTDL HIPRT prepared query inputs: {', '.join(missing)}")
        if unexpected:
            raise ValueError(f"unexpected RTDL HIPRT prepared query inputs: {', '.join(sorted(unexpected))}")
        rays = _normalize_records(self.rays_name, "rays", inputs[self.rays_name])
        rows = self.prepared.run(rays)
        return _project_rows(self.compiled, rows)


class PreparedHiprtFixedRadiusKernel:
    def __init__(
        self,
        compiled: CompiledKernel,
        query_name: str,
        search_name: str,
        k_max: int,
        prepared: PreparedHiprtFixedRadiusNeighbors3D,
    ) -> None:
        self.compiled = compiled
        self.query_name = query_name
        self.search_name = search_name
        self.k_max = k_max
        self.prepared = prepared

    def close(self) -> None:
        self.prepared.close()

    def __enter__(self) -> "PreparedHiprtFixedRadiusKernel":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def run(self, **inputs) -> tuple[dict[str, object], ...]:
        missing = [self.query_name] if self.query_name not in inputs else []
        unexpected = [name for name in inputs if name != self.query_name]
        if missing:
            raise ValueError(f"missing RTDL HIPRT prepared query inputs: {', '.join(missing)}")
        if unexpected:
            raise ValueError(f"unexpected RTDL HIPRT prepared query inputs: {', '.join(sorted(unexpected))}")
        queries = _normalize_records(self.query_name, "points", inputs[self.query_name])
        rows = self.prepared.run(queries, k_max=self.k_max)
        return _project_rows(self.compiled, rows)


class PreparedHiprtGraphKernel:
    def __init__(
        self,
        compiled: CompiledKernel,
        predicate_name: str,
        probe_name: str,
        graph_name: str,
        prepared: PreparedHiprtGraphCSR,
        *,
        visited_name: str | None = None,
        dedupe: bool = True,
        unique: bool = True,
    ) -> None:
        self.compiled = compiled
        self.predicate_name = predicate_name
        self.probe_name = probe_name
        self.graph_name = graph_name
        self.prepared = prepared
        self.visited_name = visited_name
        self.dedupe = dedupe
        self.unique = unique

    def close(self) -> None:
        self.prepared.close()

    def __enter__(self) -> "PreparedHiprtGraphKernel":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def run(self, **inputs) -> tuple[dict[str, object], ...]:
        expected = {self.probe_name}
        if self.visited_name is not None:
            expected.add(self.visited_name)
        missing = [name for name in expected if name not in inputs]
        unexpected = [name for name in inputs if name not in expected]
        if missing:
            raise ValueError(f"missing RTDL HIPRT prepared query inputs: {', '.join(sorted(missing))}")
        if unexpected:
            raise ValueError(f"unexpected RTDL HIPRT prepared query inputs: {', '.join(sorted(unexpected))}")
        if self.predicate_name == "bfs_discover":
            frontier = _normalize_records(self.probe_name, "vertex_frontier", inputs[self.probe_name])
            visited = _normalize_records(self.visited_name or "visited", "vertex_set", inputs[self.visited_name or "visited"])
            rows = self.prepared.bfs_expand(frontier, visited, dedupe=self.dedupe)
        elif self.predicate_name == "triangle_match":
            seeds = _normalize_records(self.probe_name, "edge_set", inputs[self.probe_name])
            rows = self.prepared.triangle_match(seeds, order="id_ascending", unique=self.unique)
        else:
            raise _unsupported_hiprt_peer_workload(self.predicate_name, "prepared graph execution is not implemented")
        return _project_rows(self.compiled, rows)


class PreparedHiprtDbKernel:
    def __init__(
        self,
        compiled: CompiledKernel,
        predicate_name: str,
        probe_name: str,
        table_name: str,
        prepared: PreparedHiprtDbTable,
    ) -> None:
        self.compiled = compiled
        self.predicate_name = predicate_name
        self.probe_name = probe_name
        self.table_name = table_name
        self.prepared = prepared

    def close(self) -> None:
        self.prepared.close()

    def __enter__(self) -> "PreparedHiprtDbKernel":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def run(self, **inputs) -> tuple[dict[str, object], ...]:
        missing = [self.probe_name] if self.probe_name not in inputs else []
        unexpected = [name for name in inputs if name != self.probe_name]
        if missing:
            raise ValueError(f"missing RTDL HIPRT prepared query inputs: {', '.join(missing)}")
        if unexpected:
            raise ValueError(f"unexpected RTDL HIPRT prepared query inputs: {', '.join(sorted(unexpected))}")
        if self.predicate_name == "conjunctive_scan":
            predicates = _normalize_records(self.probe_name, "predicate_set", inputs[self.probe_name])
            rows = self.prepared.conjunctive_scan(predicates)
        elif self.predicate_name == "grouped_count":
            query = _normalize_records(self.probe_name, "grouped_query", inputs[self.probe_name])
            rows = self.prepared.grouped_count(query)
        elif self.predicate_name == "grouped_sum":
            query = _normalize_records(self.probe_name, "grouped_query", inputs[self.probe_name])
            rows = self.prepared.grouped_sum(query)
        else:
            raise _unsupported_hiprt_peer_workload(self.predicate_name, "prepared DB execution is not implemented")
        return _project_rows(self.compiled, rows)


def prepare_hiprt(kernel_fn_or_compiled, **inputs):
    compiled = _resolve_kernel(kernel_fn_or_compiled)
    predicate_name, input_names, options = _validate_hiprt_kernel(compiled)
    if predicate_name == "fixed_radius_neighbors":
        if options.get("layout_pair") != ("Point3D", "Point3D"):
            raise _unsupported_hiprt_peer_workload(
                predicate_name,
                "prepared execution currently supports only Point3D fixed-radius neighbors",
            )
        query_name, search_name = input_names
        expected_build_inputs = {search_name}
        missing = [name for name in expected_build_inputs if name not in inputs]
        unexpected = [name for name in inputs if name not in expected_build_inputs]
        if missing:
            raise ValueError(f"missing RTDL HIPRT prepare inputs: {', '.join(sorted(missing))}")
        if unexpected:
            raise ValueError(
                "unexpected RTDL HIPRT prepare inputs: "
                + ", ".join(sorted(unexpected))
                + f"; pass query points later to prepared.run({query_name}=...)"
            )
        search_points = _normalize_records(search_name, "points", inputs[search_name])
        prepared = prepare_hiprt_fixed_radius_neighbors_3d(search_points, radius=float(options["radius"]))
        return PreparedHiprtFixedRadiusKernel(
            compiled,
            query_name,
            search_name,
            int(options["k_max"]),
            prepared,
        )
    if predicate_name in {"bfs_discover", "triangle_match"}:
        probe_name, graph_name = input_names
        expected_build_inputs = {graph_name}
        missing = [name for name in expected_build_inputs if name not in inputs]
        unexpected = [name for name in inputs if name not in expected_build_inputs]
        if missing:
            raise ValueError(f"missing RTDL HIPRT prepare inputs: {', '.join(sorted(missing))}")
        if unexpected:
            raise ValueError(
                "unexpected RTDL HIPRT prepare inputs: "
                + ", ".join(sorted(unexpected))
                + f"; pass query inputs later to prepared.run({probe_name}=...)"
            )
        graph = _normalize_records(graph_name, "graph_csr", inputs[graph_name])
        prepared = prepare_hiprt_graph_csr(graph)
        if predicate_name == "bfs_discover":
            visited_name = str(options["visited_input"])
            return PreparedHiprtGraphKernel(
                compiled,
                predicate_name,
                probe_name,
                graph_name,
                prepared,
                visited_name=visited_name,
                dedupe=bool(options.get("dedupe", True)),
            )
        return PreparedHiprtGraphKernel(
            compiled,
            predicate_name,
            probe_name,
            graph_name,
            prepared,
            unique=bool(options.get("unique", True)),
        )
    if predicate_name in {"conjunctive_scan", "grouped_count", "grouped_sum"}:
        probe_name, table_name = input_names
        expected_build_inputs = {table_name}
        missing = [name for name in expected_build_inputs if name not in inputs]
        unexpected = [name for name in inputs if name not in expected_build_inputs]
        if missing:
            raise ValueError(f"missing RTDL HIPRT prepare inputs: {', '.join(sorted(missing))}")
        if unexpected:
            raise ValueError(
                "unexpected RTDL HIPRT prepare inputs: "
                + ", ".join(sorted(unexpected))
                + f"; pass query inputs later to prepared.run({probe_name}=...)"
            )
        prepared = prepare_hiprt_db_table(inputs[table_name])
        return PreparedHiprtDbKernel(compiled, predicate_name, probe_name, table_name, prepared)
    if predicate_name != "ray_triangle_hit_count":
        raise _unsupported_hiprt_peer_workload(
            predicate_name,
            "prepared execution is not implemented for this workload yet",
        )
    rays_name, triangles_name = input_names
    expected_build_inputs = {triangles_name}
    missing = [name for name in expected_build_inputs if name not in inputs]
    unexpected = [name for name in inputs if name not in expected_build_inputs]
    if missing:
        raise ValueError(f"missing RTDL HIPRT prepare inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(
            "unexpected RTDL HIPRT prepare inputs: "
            + ", ".join(sorted(unexpected))
            + f"; pass query rays later to prepared.run({rays_name}=...)"
        )
    triangles = _normalize_records(triangles_name, "triangles", inputs[triangles_name])
    prepared = prepare_hiprt_ray_triangle_hit_count(triangles)
    return PreparedHiprtKernel(compiled, rays_name, triangles_name, prepared)
