"""optix_runtime.py — NVIDIA/OptiX backend for rtdl.

Public API mirrors embree_runtime.py:
  run_optix(kernel_fn_or_compiled, **inputs)       → tuple[dict, ...]
  prepare_optix(kernel_fn_or_compiled)              → PreparedOptixKernel
  optix_version()                                   → tuple[int, int, int]

Current OptiX-native workload surface:
  segment_intersection, point_in_polygon, overlay_compose,
  ray_triangle_hit_count, segment_polygon_hitcount,
  segment_polygon_anyhit_rows, point_nearest_segment,
  fixed_radius_neighbors, bounded_knn_rows, knn_rows

Additional accepted public OptiX surface:
  polygon_pair_overlap_area_rows, polygon_set_jaccard
  via documented native CPU/oracle fallback, not OptiX-native kernels

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
from .embree_runtime import _RtdlPoint3D
from .embree_runtime import _RtdlPolygonRef
from .embree_runtime import _RtdlTriangle
from .embree_runtime import _RtdlTriangle3D
from .embree_runtime import _RtdlRay2D
from .embree_runtime import _RtdlRay3D
from .embree_runtime import _RtdlFrontierVertex
from .embree_runtime import _RtdlBfsExpandRow
from .embree_runtime import _RtdlEdgeSeed
from .embree_runtime import _RtdlTriangleRow
from .embree_runtime import _RtdlDbColumn
from .embree_runtime import _encode_db_table_columnar
from .oracle_runtime import _decode_db_group_key
from .oracle_runtime import _RtdlDbField
from .oracle_runtime import _RtdlDbGroupedCountRow
from .oracle_runtime import _RtdlDbRowIdRow
from .oracle_runtime import _encode_db_clauses
from .oracle_runtime import _encode_db_table
from .oracle_runtime import _encode_db_text_clause_values
from .oracle_runtime import _encode_db_text_fields
from .embree_runtime import PackedPoints
from .embree_runtime import PackedPolygons
from .embree_runtime import PackedRays
from .embree_runtime import PackedSegments
from .embree_runtime import PackedTriangles
from .embree_runtime import PackedGraphCSR
from .embree_runtime import PackedVertexFrontier
from .embree_runtime import PackedVertexSet
from .embree_runtime import PackedEdgeSet
from .embree_runtime import _encode_all_db_text_columns
from .db_reference import PredicateClause
from .db_reference import normalize_denorm_table
from .db_reference import normalize_grouped_query
from .db_reference import normalize_predicate_bundle
from .ir import CompiledKernel
from .runtime import _normalize_records
from .runtime import _resolve_kernel
from .runtime import _validate_kernel_for_cpu
from .runtime import _identity_cache_token
from .reference import Segment as _CanonicalSegment
from .reference import Point as _CanonicalPoint
from .reference import Point3D as _CanonicalPoint3D
from .reference import Polygon as _CanonicalPolygon
from .reference import Triangle as _CanonicalTriangle
from .reference import Triangle3D as _CanonicalTriangle3D
from .reference import Ray2D as _CanonicalRay2D
from .reference import Ray3D as _CanonicalRay3D
from .graph_reference import CSRGraph
from .graph_reference import EdgeSeed
from .graph_reference import FrontierVertex
from .graph_reference import normalize_edge_set
from .graph_reference import normalize_frontier
from .graph_reference import normalize_vertex_set


_PREPARED_CACHE_MAX_ENTRIES = 8
_prepared_optix_execution_cache: OrderedDict[tuple[object, ...], "PreparedOptixExecution"] = OrderedDict()
_DB_MAX_ROWS_PER_JOB = 1_000_000


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


class _RtdlRayAnyHitRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("any_hit", ctypes.c_uint32),
    ]


class _RtdlSegmentPolygonHitCountRow(ctypes.Structure):
    _fields_ = [
        ("segment_id", ctypes.c_uint32),
        ("hit_count",  ctypes.c_uint32),
    ]


class _RtdlSegmentPolygonAnyHitRow(ctypes.Structure):
    _fields_ = [
        ("segment_id", ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
    ]


class _RtdlFixedRadiusNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
    ]


class _RtdlFixedRadiusCountRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_count", ctypes.c_uint32),
        ("threshold_reached", ctypes.c_uint32),
    ]


class _RtdlKnnNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
        ("neighbor_rank", ctypes.c_uint32),
    ]


class _RtdlPointNearestSegmentRow(ctypes.Structure):
    _fields_ = [
        ("point_id",   ctypes.c_uint32),
        ("segment_id", ctypes.c_uint32),
        ("distance",   ctypes.c_double),
    ]


class _RtdlDbGroupedSumRow(ctypes.Structure):
    _fields_ = [
        ("group_key", ctypes.c_int64),
        ("sum", ctypes.c_int64),
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
    _free_on_close: bool = True
    _owner: object = None
    _closed: bool = False

    def close(self) -> None:
        if not self._closed:
            if self._free_on_close:
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


def _project_ray_hitcount_view_to_anyhit(rows: OptixRowView) -> tuple[dict[str, int], ...]:
    return tuple(
        {
            "ray_id": int(rows.rows_ptr[index].ray_id),
            "any_hit": 1 if int(rows.rows_ptr[index].hit_count) else 0,
        }
        for index in range(rows.row_count)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Prepared-kernel API
# ─────────────────────────────────────────────────────────────────────────────

class PreparedOptixKernel:
    """Compiled-once handle for the OptiX backend.  Mirrors PreparedEmbreeKernel."""

    _SUPPORTED_PREDICATES = {
        "segment_intersection",
        "point_in_polygon",
        "overlay_compose",
        "ray_triangle_any_hit",
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
        if self.predicate_name in {"conjunctive_scan", "grouped_count", "grouped_sum"}:
            normalized_inputs = {
                name: _normalize_records(name, self.expected_inputs[name].geometry.name, payload)
                for name, payload in inputs.items()
            }
            return _prepare_db_optix_execution(self.compiled, normalized_inputs, self.library)
        packed = {
            name: _pack_for_geometry(self.expected_inputs[name], payload)
            for name, payload in inputs.items()
        }
        execution = PreparedOptixExecution(self.compiled, self.library, packed)
        predicate = self.compiled.refine_op.predicate
        if (
            predicate.name == "point_in_polygon"
            and predicate.options.get("result_mode", "full_matrix") == "positive_hits"
        ):
            execution.warmup()
        return execution

    def run(self, **inputs) -> tuple:
        return self.bind(**inputs).run()


@dataclass
class PreparedOptixExecution:
    compiled: CompiledKernel
    library: object
    packed_inputs: dict
    _warmed: bool = False

    def warmup(self) -> None:
        if self._warmed:
            return
        rows = self.run_raw()
        try:
            rows.close()
        finally:
            self._warmed = True

    def run_raw(self) -> OptixRowView:
        pred = self.compiled.refine_op.predicate.name
        if pred == "ray_triangle_any_hit":
            native = _find_optional_backend_symbol(self.library, "rtdl_optix_run_ray_anyhit")
            if native is not None:
                return _call_ray_anyhit_optix_packed(self.compiled, self.packed_inputs, self.library)
            raise ValueError(
                "OptiX raw mode requires a backend library exporting "
                "rtdl_optix_run_ray_anyhit; rebuild with 'make build-optix'."
            )
        dispatch = {
            "segment_intersection":   _call_lsi_optix_packed,
            "point_in_polygon":       _call_pip_optix_packed,
            "overlay_compose":        _call_overlay_optix_packed,
            "ray_triangle_hit_count": _call_ray_hitcount_optix_packed,
            "segment_polygon_hitcount": _call_segment_polygon_hitcount_optix_packed,
            "segment_polygon_anyhit_rows": _call_segment_polygon_anyhit_rows_optix_packed,
            "point_nearest_segment":  _call_point_nearest_segment_optix_packed,
            "fixed_radius_neighbors": _call_fixed_radius_neighbors_optix_packed,
            "bounded_knn_rows": _call_bounded_knn_rows_optix_packed,
            "knn_rows": _call_knn_rows_optix_packed,
            "bfs_discover": _call_bfs_expand_optix_packed,
            "triangle_match": _call_triangle_probe_optix_packed,
        }
        fn = dispatch.get(pred)
        if fn is None:
            raise ValueError(f"unsupported prepared OptiX predicate: {pred!r}")
        return fn(self.compiled, self.packed_inputs, self.library)

    def run(self) -> tuple:
        pred = self.compiled.refine_op.predicate.name
        if pred == "ray_triangle_any_hit":
            if _find_optional_backend_symbol(self.library, "rtdl_optix_run_ray_anyhit") is not None:
                rows = _call_ray_anyhit_optix_packed(self.compiled, self.packed_inputs, self.library)
            else:
                rows = _call_ray_hitcount_optix_packed(self.compiled, self.packed_inputs, self.library)
                try:
                    return _project_ray_hitcount_view_to_anyhit(rows)
                finally:
                    rows.close()
            try:
                return rows.to_dict_rows()
            finally:
                rows.close()
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

    # Current accepted honesty boundary:
    # the Jaccard workloads are closed on Python/native CPU today, but not as
    # OptiX-native kernels. The public OptiX run surface accepts them through
    # the native CPU/oracle implementation so they can participate in Linux
    # consistency and scale audits without overclaiming backend maturity.
    if compiled.refine_op.predicate.name in {
        "polygon_pair_overlap_area_rows",
        "polygon_set_jaccard",
    }:
        if result_mode == "raw":
            raise ValueError(
                "OptiX raw mode is not supported for the Jaccard workloads "
                "while the backend uses the native CPU oracle fallback"
            )
        from .runtime import run_cpu

        return run_cpu(compiled, **inputs)

    if compiled.refine_op.predicate.name in {
        "conjunctive_scan",
        "grouped_count",
        "grouped_sum",
    }:
        normalized_inputs = {
            name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
            for name, payload in inputs.items()
        }
        return _run_db_optix(compiled, normalized_inputs, _load_optix_library(), result_mode=result_mode)

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
    prepared = prepare_optix(compiled).bind(**inputs)
    _prepared_optix_execution_cache[cache_key] = prepared
    if len(_prepared_optix_execution_cache) > _PREPARED_CACHE_MAX_ENTRIES:
        _prepared_optix_execution_cache.popitem(last=False)
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


def fixed_radius_count_threshold_2d_optix(
    query_points,
    search_points=None,
    *,
    radius: float,
    threshold: int = 0,
) -> tuple[dict[str, int], ...]:
    """Run the experimental OptiX RT-traversal fixed-radius count primitive.

    This is intentionally narrower than ``fixed_radius_neighbors``: it emits
    one summary row per query with ``neighbor_count`` counted up to
    ``threshold``. A threshold of ``0`` requests full counts; a positive
    threshold allows the OptiX any-hit program to terminate each ray once the
    threshold is reached. The current implementation is 2-D only and is meant
    for outlier/DBSCAN core-flag prototypes, not KNN or Hausdorff.
    """
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    packed_queries = pack_points(records=query_points, dimension=2)
    packed_search = packed_queries if search_points is None else pack_points(records=search_points, dimension=2)
    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_fixed_radius_count_threshold")
    if symbol is None:
        raise RuntimeError(
            "loaded OptiX backend library does not export rtdl_optix_run_fixed_radius_count_threshold; "
            "rebuild the OptiX backend from current main"
        )
    rows_ptr = ctypes.POINTER(_RtdlFixedRadiusCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        packed_queries.records,
        packed_queries.count,
        packed_search.records,
        packed_search.count,
        ctypes.c_double(float(radius)),
        ctypes.c_size_t(int(threshold)),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    view = OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlFixedRadiusCountRow,
        field_names=("query_id", "neighbor_count", "threshold_reached"),
    )
    try:
        return tuple(
            {
                "query_id": int(row["query_id"]),
                "neighbor_count": int(row["neighbor_count"]),
                "threshold_reached": int(row["threshold_reached"]),
            }
            for row in view.to_dict_rows()
        )
    finally:
        view.close()


class PreparedOptixFixedRadiusCountThreshold2D:
    """Prepared OptiX 2-D fixed-radius count-threshold scene.

    ``max_radius`` is part of preparation because the OptiX custom-primitive
    AABBs must be wide enough for every later query radius.
    """

    def __init__(self, search_points, *, max_radius: float):
        if max_radius < 0:
            raise ValueError("max_radius must be non-negative")
        packed = search_points if isinstance(search_points, PackedPoints) else pack_points(records=search_points, dimension=2)
        if packed.dimension != 2:
            raise ValueError("prepare_optix_fixed_radius_count_threshold_2d requires 2-D points")
        self._packed_search = packed
        self._max_radius = float(max_radius)
        self._handle = ctypes.c_void_p()
        self._closed = False
        if packed.count == 0:
            return

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_fixed_radius_count_threshold_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_fixed_radius_count_threshold_2d; rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(
            packed.records,
            packed.count,
            ctypes.c_double(self._max_radius),
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)

    @property
    def max_radius(self) -> float:
        return self._max_radius

    @property
    def closed(self) -> bool:
        return self._closed

    def run(self, query_points, *, radius: float, threshold: int = 0) -> tuple[dict[str, int], ...]:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius count handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=2)
        if packed_queries.dimension != 2:
            raise ValueError("PreparedOptixFixedRadiusCountThreshold2D.run requires 2-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0:
            return ()

        lib = _load_optix_library()
        run_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_fixed_radius_count_threshold_2d")
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_fixed_radius_count_threshold_2d; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusCountRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(threshold)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        view = OptixRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlFixedRadiusCountRow,
            field_names=("query_id", "neighbor_count", "threshold_reached"),
        )
        try:
            return tuple(
                {
                    "query_id": int(row["query_id"]),
                    "neighbor_count": int(row["neighbor_count"]),
                    "threshold_reached": int(row["threshold_reached"]),
                }
                for row in view.to_dict_rows()
            )
        finally:
            view.close()

    def count_threshold_reached(self, query_points, *, radius: float, threshold: int = 0) -> int:
        """Return only the number of query points that reached ``threshold``.

        This is the scalar-summary path for app profilers that need counts
        rather than one Python row per query point.
        """
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius count handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=2)
        if packed_queries.dimension != 2:
            raise ValueError("PreparedOptixFixedRadiusCountThreshold2D.count_threshold_reached requires 2-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0:
            return 0

        lib = _load_optix_library()
        count_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d")
        if count_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d; rebuild the OptiX backend from current main"
            )
        threshold_reached_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(threshold)),
            ctypes.byref(threshold_reached_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(threshold_reached_count.value)

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixFixedRadiusCountThreshold2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_fixed_radius_count_threshold_2d(
    search_points,
    *,
    max_radius: float,
) -> PreparedOptixFixedRadiusCountThreshold2D:
    return PreparedOptixFixedRadiusCountThreshold2D(search_points, max_radius=max_radius)


class PreparedOptixSegmentPolygonHitcount2D:
    """Prepared OptiX segment/polygon hit-count scene.

    The polygon set and its custom-primitive BVH are prepared once.  Each
    ``run`` call uploads only the probe segments, launches the native OptiX
    traversal kernel, and returns one hit-count row per segment.
    """

    def __init__(self, polygons):
        packed = polygons if isinstance(polygons, PackedPolygons) else pack_polygons(records=polygons)
        self._packed_polygons = packed
        self._handle = ctypes.c_void_p()
        self._closed = False
        if packed.polygon_count == 0:
            return

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_segment_polygon_hitcount_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_segment_polygon_hitcount_2d; rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(
            packed.refs,
            packed.polygon_count,
            packed.vertices_xy,
            packed.vertex_xy_count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)

    @property
    def closed(self) -> bool:
        return self._closed

    def run(self, segments) -> tuple[dict[str, int], ...]:
        if self._closed:
            raise RuntimeError("prepared OptiX segment/polygon hit-count handle is closed")
        packed_segments = segments if isinstance(segments, PackedSegments) else pack_segments(records=segments)
        if packed_segments.count == 0:
            return ()
        if self._packed_polygons.polygon_count == 0:
            return tuple(
                {"segment_id": int(packed_segments.records[index].id), "hit_count": 0}
                for index in range(packed_segments.count)
            )

        lib = _load_optix_library()
        run_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_segment_polygon_hitcount_2d")
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_segment_polygon_hitcount_2d; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_segments.records,
            packed_segments.count,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        view = OptixRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlSegmentPolygonHitCountRow,
            field_names=("segment_id", "hit_count"),
        )
        try:
            return tuple(
                {
                    "segment_id": int(row["segment_id"]),
                    "hit_count": int(row["hit_count"]),
                }
                for row in view.to_dict_rows()
            )
        finally:
            view.close()

    def count_at_least(self, segments, *, threshold: int) -> int:
        if self._closed:
            raise RuntimeError("prepared OptiX segment/polygon hit-count handle is closed")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        if threshold > 0xFFFFFFFF:
            raise ValueError("threshold exceeds uint32 range")
        packed_segments = segments if isinstance(segments, PackedSegments) else pack_segments(records=segments)
        if packed_segments.count == 0:
            return 0
        if self._packed_polygons.polygon_count == 0:
            return packed_segments.count if threshold == 0 else 0

        lib = _load_optix_library()
        count_symbol = _find_optional_backend_symbol(
            lib,
            "rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d",
        )
        if count_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d; rebuild the OptiX backend from current main"
            )
        count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self._handle,
            packed_segments.records,
            packed_segments.count,
            ctypes.c_uint32(threshold),
            ctypes.byref(count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(count.value)

    def aggregate(self, segments, *, positive_threshold: int = 1) -> dict[str, int]:
        if self._closed:
            raise RuntimeError("prepared OptiX segment/polygon hit-count handle is closed")
        if positive_threshold < 0:
            raise ValueError("positive_threshold must be non-negative")
        if positive_threshold > 0xFFFFFFFF:
            raise ValueError("positive_threshold exceeds uint32 range")
        packed_segments = segments if isinstance(segments, PackedSegments) else pack_segments(records=segments)
        if packed_segments.count == 0:
            return {"row_count": 0, "hit_sum": 0, "positive_count": 0}
        if self._packed_polygons.polygon_count == 0:
            return {
                "row_count": packed_segments.count,
                "hit_sum": 0,
                "positive_count": packed_segments.count if positive_threshold == 0 else 0,
            }

        lib = _load_optix_library()
        aggregate_symbol = _find_optional_backend_symbol(
            lib,
            "rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d",
        )
        if aggregate_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d; rebuild the OptiX backend from current main"
            )
        row_count = ctypes.c_size_t()
        hit_sum = ctypes.c_uint64()
        positive_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = aggregate_symbol(
            self._handle,
            packed_segments.records,
            packed_segments.count,
            ctypes.c_uint32(positive_threshold),
            ctypes.byref(row_count),
            ctypes.byref(hit_sum),
            ctypes.byref(positive_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return {
            "row_count": int(row_count.value),
            "hit_sum": int(hit_sum.value),
            "positive_count": int(positive_count.value),
        }

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_segment_polygon_hitcount_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixSegmentPolygonHitcount2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_segment_polygon_hitcount_2d(polygons) -> PreparedOptixSegmentPolygonHitcount2D:
    return PreparedOptixSegmentPolygonHitcount2D(polygons)


class PreparedOptixSegmentPolygonAnyHitRows2D:
    """Prepared OptiX segment/polygon pair-row scene with bounded output."""

    def __init__(self, polygons):
        packed = polygons if isinstance(polygons, PackedPolygons) else pack_polygons(records=polygons)
        self._packed_polygons = packed
        self._handle = ctypes.c_void_p()
        self._closed = False
        if packed.polygon_count == 0:
            return

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_segment_polygon_anyhit_rows_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_segment_polygon_anyhit_rows_2d; rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(
            packed.refs,
            packed.polygon_count,
            packed.vertices_xy,
            packed.vertex_xy_count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)

    @property
    def closed(self) -> bool:
        return self._closed

    def run_with_metadata(self, segments, *, output_capacity: int) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX segment/polygon pair-row handle is closed")
        if output_capacity <= 0:
            raise ValueError("output_capacity must be positive")
        packed_segments = segments if isinstance(segments, PackedSegments) else pack_segments(records=segments)
        if packed_segments.count == 0 or self._packed_polygons.polygon_count == 0:
            return {
                "rows": (),
                "emitted_count": 0,
                "copied_count": 0,
                "overflowed": False,
            }

        lib = _load_optix_library()
        run_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d")
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d; rebuild the OptiX backend from current main"
            )
        row_array = (_RtdlSegmentPolygonAnyHitRow * output_capacity)()
        emitted_count = ctypes.c_size_t()
        overflowed = ctypes.c_uint32()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_segments.records,
            packed_segments.count,
            row_array,
            output_capacity,
            ctypes.byref(emitted_count),
            ctypes.byref(overflowed),
            error,
            len(error),
        )
        _check_status(status, error)
        copied_count = min(int(emitted_count.value), int(output_capacity))
        rows = tuple(
            {
                "segment_id": int(row_array[index].segment_id),
                "polygon_id": int(row_array[index].polygon_id),
            }
            for index in range(copied_count)
        )
        return {
            "rows": rows,
            "emitted_count": int(emitted_count.value),
            "copied_count": copied_count,
            "overflowed": bool(overflowed.value),
        }

    def run(self, segments, *, output_capacity: int) -> tuple[dict[str, int], ...]:
        result = self.run_with_metadata(segments, output_capacity=output_capacity)
        if result["overflowed"]:
            raise RuntimeError(
                "prepared native OptiX segment/polygon pair-row output overflowed "
                f"capacity {output_capacity}; emitted {result['emitted_count']}"
            )
        return result["rows"]

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_segment_polygon_anyhit_rows_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixSegmentPolygonAnyHitRows2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_segment_polygon_anyhit_rows_2d(polygons) -> PreparedOptixSegmentPolygonAnyHitRows2D:
    return PreparedOptixSegmentPolygonAnyHitRows2D(polygons)


def get_last_phase_timings() -> dict[str, float] | None:
    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_get_last_phase_timings")
    if symbol is None:
        return None
    symbol.argtypes = (
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
    )
    symbol.restype = ctypes.c_int
    bvh = ctypes.c_double(0.0)
    trav = ctypes.c_double(0.0)
    copy = ctypes.c_double(0.0)
    status = symbol(ctypes.byref(bvh), ctypes.byref(trav), ctypes.byref(copy))
    if status != 0:
        return None
    return {
        "bvh_build": float(bvh.value),
        "traversal": float(trav.value),
        "copyback": float(copy.value),
    }


def get_last_db_phase_timings() -> dict[str, float | int] | None:
    return _get_last_db_phase_timings_from_library(_load_optix_library())


def _get_last_db_phase_timings_from_library(lib) -> dict[str, float | int] | None:
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_db_get_last_phase_timings")
    if symbol is None:
        return None
    symbol.argtypes = (
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_size_t),
    )
    symbol.restype = ctypes.c_int
    traversal = ctypes.c_double(0.0)
    bitset_copy = ctypes.c_double(0.0)
    exact_filter = ctypes.c_double(0.0)
    output_pack = ctypes.c_double(0.0)
    raw_candidates = ctypes.c_size_t(0)
    emitted = ctypes.c_size_t(0)
    status = symbol(
        ctypes.byref(traversal),
        ctypes.byref(bitset_copy),
        ctypes.byref(exact_filter),
        ctypes.byref(output_pack),
        ctypes.byref(raw_candidates),
        ctypes.byref(emitted),
    )
    if status != 0:
        return None
    return {
        "traversal": float(traversal.value),
        "bitset_copyback": float(bitset_copy.value),
        "exact_filter": float(exact_filter.value),
        "output_pack": float(output_pack.value),
        "raw_candidate_count": int(raw_candidates.value),
        "emitted_count": int(emitted.value),
    }


def _run_db_optix(compiled: CompiledKernel, normalized_inputs, lib, *, result_mode: str):
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name == "conjunctive_scan":
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_conjunctive_scan")
        if symbol is None:
            raise ValueError("current OptiX backend does not yet export DB conjunctive_scan support")
        predicates_name = compiled.candidates.left.name
        table_name = compiled.candidates.right.name
        table_rows = normalized_inputs[table_name]
        if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
            raise ValueError("first-wave OptiX DB lowering supports at most 1000000 rows per RT job")
        predicates = normalized_inputs[predicates_name]
        fields_array, row_values_array, row_count = _encode_db_table(table_rows)
        clauses_array = _encode_db_clauses(predicates.clauses)
        rows_ptr = ctypes.POINTER(_RtdlDbRowIdRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = symbol(
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
        row_view = OptixRowView(
            library=lib,
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
        raise ValueError("first-wave OptiX DB lowering supports at most 1000000 rows per RT job")
    query = normalized_inputs[query_name]
    if len(query.group_keys) != 1:
        raise ValueError("first-wave OptiX DB grouped kernels support exactly one group key")
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
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_grouped_count")
        if symbol is None:
            raise ValueError("current OptiX backend does not yet export DB grouped_count support")
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
        row_count_out = ctypes.c_size_t()
        status = symbol(
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
        row_view = OptixRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbGroupedCountRow,
            field_names=("group_key", "count"),
        )
        if result_mode == "raw":
            return row_view
        try:
            reverse_map = reverse_maps.get(query.group_keys[0])
            return tuple(
                {
                    query.group_keys[0]: _decode_db_group_key(reverse_map, row_view.rows_ptr[index].group_key),
                    "count": row_view.rows_ptr[index].count,
                }
                for index in range(row_view.row_count)
            )
        finally:
            row_view.close()

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_grouped_sum")
    if symbol is None:
        raise ValueError("current OptiX backend does not yet export DB grouped_sum support")
    rows_ptr = ctypes.POINTER(_RtdlDbGroupedSumRow)()
    row_count_out = ctypes.c_size_t()
    status = symbol(
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
    row_view = OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count_out.value,
        row_type=_RtdlDbGroupedSumRow,
        field_names=("group_key", "sum"),
    )
    if result_mode == "raw":
        return row_view
    try:
        reverse_map = reverse_maps.get(query.group_keys[0])
        return tuple(
            {
                query.group_keys[0]: _decode_db_group_key(reverse_map, row_view.rows_ptr[index].group_key),
                "sum": int(row_view.rows_ptr[index].sum),
            }
            for index in range(row_view.row_count)
        )
    finally:
        row_view.close()


@dataclass(frozen=True)
class PreparedOptixDbExecution:
    compiled: CompiledKernel
    library: object
    predicate_name: str
    dataset: object
    clauses_array: object
    group_key_name: str | None = None
    group_key_field: bytes | None = None
    reverse_map: object | None = None
    value_field: bytes | None = None

    def run_raw(self) -> OptixRowView:
        if self.predicate_name == "conjunctive_scan":
            return self.dataset.conjunctive_scan(self.clauses_array)

        if self.predicate_name == "grouped_count":
            return self.dataset.grouped_count(self.clauses_array, self.group_key_field)

        return self.dataset.grouped_sum(self.clauses_array, self.group_key_field, self.value_field)

    def run(self) -> tuple:
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


class OptixPreparedDbDataset:
    def __init__(
        self,
        lib,
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
        self.library = lib
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
            if not hasattr(self.library, "rtdl_optix_db_dataset_create_columnar"):
                raise RuntimeError(
                    "loaded OptiX backend does not export rtdl_optix_db_dataset_create_columnar; "
                    "rebuild the OptiX backend from the current checkout"
                )
            status = self.library.rtdl_optix_db_dataset_create_columnar(
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
            status = self.library.rtdl_optix_db_dataset_create(
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
            self.library.rtdl_optix_db_dataset_destroy(self.handle)
        self._closed = True

    def conjunctive_scan(self, clauses_array) -> OptixRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbRowIdRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_optix_db_dataset_conjunctive_scan(
            self.handle,
            clauses_array,
            ctypes.c_size_t(len(clauses_array)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbRowIdRow,
            field_names=("row_id",),
        )

    def conjunctive_scan_count(self, clauses_array) -> int:
        symbol = getattr(self.library, "rtdl_optix_db_dataset_conjunctive_scan_count", None)
        if symbol is None:
            rows = self.conjunctive_scan(clauses_array)
            try:
                return int(rows.row_count)
            finally:
                rows.close()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = symbol(
            self.handle,
            clauses_array,
            ctypes.c_size_t(len(clauses_array)),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(row_count_out.value)

    def last_phase_timings(self) -> dict[str, float | int] | None:
        return _get_last_db_phase_timings_from_library(self.library)

    def grouped_count(self, clauses_array, group_key_field: bytes) -> OptixRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_optix_db_dataset_grouped_count(
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
        return OptixRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbGroupedCountRow,
            field_names=("group_key", "count"),
        )

    def grouped_sum(self, clauses_array, group_key_field: bytes, value_field: bytes) -> OptixRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedSumRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_optix_db_dataset_grouped_sum(
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
        return OptixRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbGroupedSumRow,
            field_names=("group_key", "sum"),
        )

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


class PreparedOptixDbDataset:
    def __init__(self, table_rows, *, primary_fields=(), transfer: str = "row"):
        if transfer not in {"row", "columnar"}:
            raise ValueError("OptiX DB dataset transfer must be 'row' or 'columnar'")
        rows = normalize_denorm_table(table_rows)
        if len(rows) > _DB_MAX_ROWS_PER_JOB:
            raise ValueError("first-wave OptiX DB lowering supports at most 1000000 rows per RT job")
        encoded_rows, self._field_maps, self._reverse_maps = _encode_all_db_text_columns(rows)
        if transfer == "columnar":
            columns_array, row_count, keepalive = _encode_db_table_columnar(encoded_rows)
            fields_array = None
            row_values_array = None
        else:
            fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
            columns_array = None
            keepalive = ()
        self._dataset = OptixPreparedDbDataset(
            _load_optix_library(),
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

    def conjunctive_scan_count(self, predicates) -> int:
        bundle = normalize_predicate_bundle(predicates)
        clauses_array = _encode_db_clauses(self._encode_clauses(bundle.clauses))
        return self._dataset.conjunctive_scan_count(clauses_array)

    def last_phase_timings(self) -> dict[str, float | int] | None:
        return self._dataset.last_phase_timings()

    def grouped_count(self, query) -> tuple[dict[str, object], ...]:
        normalized_query = normalize_grouped_query(query)
        if len(normalized_query.group_keys) != 1:
            raise ValueError("first-wave OptiX DB grouped kernels support exactly one group key")
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

    def grouped_count_summary(self, query) -> dict[str, int]:
        normalized_query = normalize_grouped_query(query)
        if len(normalized_query.group_keys) != 1:
            raise ValueError("first-wave OptiX DB grouped kernels support exactly one group key")
        group_key = normalized_query.group_keys[0]
        clauses_array = _encode_db_clauses(self._encode_clauses(normalized_query.predicates))
        rows = self._dataset.grouped_count(clauses_array, group_key.encode("utf-8"))
        try:
            reverse_map = self._reverse_maps.get(group_key)
            return {
                str(_decode_db_group_key(reverse_map, rows.rows_ptr[index].group_key)): int(rows.rows_ptr[index].count)
                for index in range(rows.row_count)
            }
        finally:
            rows.close()

    def grouped_sum(self, query) -> tuple[dict[str, object], ...]:
        normalized_query = normalize_grouped_query(query)
        if len(normalized_query.group_keys) != 1:
            raise ValueError("first-wave OptiX DB grouped kernels support exactly one group key")
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

    def grouped_sum_summary(self, query) -> dict[str, int]:
        normalized_query = normalize_grouped_query(query)
        if len(normalized_query.group_keys) != 1:
            raise ValueError("first-wave OptiX DB grouped kernels support exactly one group key")
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
            return {
                str(_decode_db_group_key(reverse_map, rows.rows_ptr[index].group_key)): int(rows.rows_ptr[index].sum)
                for index in range(rows.row_count)
            }
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


def prepare_optix_db_dataset(table_rows, *, primary_fields=(), transfer: str = "row") -> PreparedOptixDbDataset:
    return PreparedOptixDbDataset(table_rows, primary_fields=primary_fields, transfer=transfer)


def _db_primary_fields_from_clauses(clauses) -> tuple[str, ...]:
    fields = []
    for clause in clauses:
        name = str(clause.field)
        if name not in fields:
            fields.append(name)
        if len(fields) == 3:
            break
    return tuple(fields)


def _prepare_db_optix_execution(compiled: CompiledKernel, normalized_inputs, lib) -> PreparedOptixDbExecution:
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name == "conjunctive_scan":
        predicates_name = compiled.candidates.left.name
        table_name = compiled.candidates.right.name
        table_rows = normalized_inputs[table_name]
        if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
            raise ValueError("first-wave OptiX DB lowering supports at most 1000000 rows per RT job")
        predicates = normalized_inputs[predicates_name]
        columns_array, row_count, keepalive = _encode_db_table_columnar(table_rows)
        clauses_array = _encode_db_clauses(predicates.clauses)
        dataset = OptixPreparedDbDataset(
            lib,
            None,
            None,
            row_count,
            primary_fields=_db_primary_fields_from_clauses(predicates.clauses),
            columns_array=columns_array,
            column_count=len(columns_array),
            transfer="columnar",
            keepalive=keepalive,
        )
        return PreparedOptixDbExecution(
            compiled=compiled,
            library=lib,
            predicate_name=predicate_name,
            dataset=dataset,
            clauses_array=clauses_array,
        )

    query_name = compiled.candidates.left.name
    table_name = compiled.candidates.right.name
    table_rows = normalized_inputs[table_name]
    if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
        raise ValueError("first-wave OptiX DB lowering supports at most 1000000 rows per RT job")
    query = normalized_inputs[query_name]
    if len(query.group_keys) != 1:
        raise ValueError("first-wave OptiX DB grouped kernels support exactly one group key")
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
    dataset = OptixPreparedDbDataset(
        lib,
        None,
        None,
        row_count,
        primary_fields=_db_primary_fields_from_clauses(encoded_predicates),
        columns_array=columns_array,
        column_count=len(columns_array),
        transfer="columnar",
        keepalive=keepalive,
    )
    return PreparedOptixDbExecution(
        compiled=compiled,
        library=lib,
        predicate_name=predicate_name,
        dataset=dataset,
        clauses_array=clauses_array,
        group_key_name=query.group_keys[0],
        group_key_field=query.group_keys[0].encode("utf-8"),
        reverse_map=reverse_maps.get(query.group_keys[0]),
        value_field=query.value_field.encode("utf-8") if predicate_name == "grouped_sum" else None,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Packing helpers  (same interface as embree_runtime.py)
# ─────────────────────────────────────────────────────────────────────────────

def pack_segments(records=None, *, ids=None, x0=None, y0=None, x1=None, y1=None) -> PackedSegments:
    if records is not None:
        norm = records if isinstance(records, tuple) and all(isinstance(item, _CanonicalSegment) for item in records) else _normalize_records("segments", "segments", records)
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


def pack_points(records=None, *, ids=None, x=None, y=None, z=None, dimension: int | None = None) -> PackedPoints:
    if records is not None:
        norm = (
            records
            if isinstance(records, tuple) and all(isinstance(item, (_CanonicalPoint, _CanonicalPoint3D)) for item in records)
            else _normalize_records("points", "points", records)
        )
        if dimension not in {None, 2, 3}:
            raise ValueError("points dimension must be one of: 2, 3")
        inferred_dimension = dimension
        if inferred_dimension is None:
            inferred_dimension = 3 if norm and all(isinstance(item, _CanonicalPoint3D) for item in norm) else 2
        if inferred_dimension == 3:
            if any(not isinstance(item, _CanonicalPoint3D) for item in norm):
                if norm:
                    raise ValueError("points packed for a 3D layout must provide 3D point records")
            arr = (_RtdlPoint3D * len(norm))(*[_RtdlPoint3D(r.id, r.x, r.y, r.z) for r in norm])
            return PackedPoints(records=arr, count=len(norm), dimension=3)
        if any(isinstance(item, _CanonicalPoint3D) for item in norm):
            if norm:
                raise ValueError("points packed for a 2D layout must provide 2D point records")
        arr = (_RtdlPoint * len(norm))(*[_RtdlPoint(r.id, r.x, r.y) for r in norm])
        return PackedPoints(records=arr, count=len(norm), dimension=2)
    ids_l = _coerce_list("ids", ids)
    x_l = _coerce_list("x", x)
    y_l = _coerce_list("y", y)
    if dimension not in {None, 2, 3}:
        raise ValueError("points dimension must be one of: 2, 3")
    if dimension == 3 or z is not None:
        z_l = _coerce_list("z", z)
        n = _validate_equal_lengths("points", ids_l, x_l, y_l, z_l)
        arr = (_RtdlPoint3D * n)(*[
            _RtdlPoint3D(int(ids_l[i]), float(x_l[i]), float(y_l[i]), float(z_l[i]))
            for i in range(n)
        ])
        return PackedPoints(records=arr, count=n, dimension=3)
    n = _validate_equal_lengths("points", ids_l, x_l, y_l)
    arr = (_RtdlPoint * n)(*[
        _RtdlPoint(int(ids_l[i]), float(x_l[i]), float(y_l[i]))
        for i in range(n)
    ])
    return PackedPoints(records=arr, count=n, dimension=2)


def pack_polygons(records=None, *, ids=None, vertex_offsets=None,
                  vertex_counts=None, vertices_xy=None) -> PackedPolygons:
    if records is not None:
        norm = records if isinstance(records, tuple) and all(isinstance(item, _CanonicalPolygon) for item in records) else _normalize_records("polygons", "polygons", records)
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
        norm = records if isinstance(records, tuple) and all(isinstance(item, (_CanonicalTriangle, _CanonicalTriangle3D)) for item in records) else _normalize_records("triangles", "triangles", records)
        if dimension not in {None, 2, 3}:
            raise ValueError("triangles dimension must be one of: 2, 3")
        inferred_dimension = dimension
        if inferred_dimension is None:
            inferred_dimension = 3 if norm and all(isinstance(item, _CanonicalTriangle3D) for item in norm) else 2
        if inferred_dimension == 3:
            if any(not isinstance(item, _CanonicalTriangle3D) for item in norm):
                if norm:
                    raise ValueError("triangles packed for a 3D layout must provide 3D triangle records")
            arr = (_RtdlTriangle3D * len(norm))(*[
                _RtdlTriangle3D(r.id, r.x0, r.y0, r.z0, r.x1, r.y1, r.z1, r.x2, r.y2, r.z2) for r in norm
            ])
            return PackedTriangles(records=arr, count=len(norm), dimension=3)
        if any(isinstance(item, _CanonicalTriangle3D) for item in norm):
            if norm:
                raise ValueError("triangles packed for a 2D layout must provide 2D triangle records")
        arr = (_RtdlTriangle * len(norm))(*[
            _RtdlTriangle(r.id, r.x0, r.y0, r.x1, r.y1, r.x2, r.y2) for r in norm
        ])
        return PackedTriangles(records=arr, count=len(norm), dimension=2)
    if dimension == 3:
        raise ValueError("triangles packed from explicit coordinate columns currently support only 2D records")
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
    return PackedTriangles(records=arr, count=n, dimension=2)


def pack_rays_3d_from_arrays(
    ids,
    ox,
    oy,
    oz,
    dx,
    dy,
    dz,
    tmax,
) -> PackedRays:
    """Fast bulk packing of 3-D rays from array-like inputs (numpy arrays preferred).

    Bypasses per-element Python object creation so it scales to millions of rays
    without the overhead of building a tuple[rt.Ray3D, ...] first.  Field order
    and dtype exactly match the C _RtdlRay3D packed struct (uint32 id + 7×float64).
    """
    try:
        import numpy as _np
    except ImportError:  # pragma: no cover
        raise RuntimeError("pack_rays_3d_from_arrays requires numpy")

    ids_a  = _np.asarray(ids,  dtype=_np.uint32)
    ox_a   = _np.asarray(ox,   dtype=_np.float64)
    oy_a   = _np.asarray(oy,   dtype=_np.float64)
    oz_a   = _np.asarray(oz,   dtype=_np.float64)
    dx_a   = _np.asarray(dx,   dtype=_np.float64)
    dy_a   = _np.asarray(dy,   dtype=_np.float64)
    dz_a   = _np.asarray(dz,   dtype=_np.float64)
    tmax_a = _np.asarray(tmax, dtype=_np.float64)

    n = len(ids_a)
    # Numpy structured dtype that mirrors _RtdlRay3D with _pack_=1:
    #   id(u4,@0), ox(f8,@4), oy(f8,@12), oz(f8,@20),
    #   dx(f8,@28), dy(f8,@36), dz(f8,@44), tmax(f8,@52)  → itemsize 60
    _dtype = _np.dtype({
        "names":   ["id", "ox", "oy", "oz", "dx", "dy", "dz", "tmax"],
        "formats": [_np.uint32, _np.float64, _np.float64, _np.float64,
                    _np.float64, _np.float64, _np.float64, _np.float64],
        "offsets": [0, 4, 12, 20, 28, 36, 44, 52],
        "itemsize": 60,
    })
    buf = _np.empty(n, dtype=_dtype)
    buf["id"]   = ids_a
    buf["ox"]   = ox_a;  buf["oy"] = oy_a;  buf["oz"] = oz_a
    buf["dx"]   = dx_a;  buf["dy"] = dy_a;  buf["dz"] = dz_a
    buf["tmax"] = tmax_a

    arr = (_RtdlRay3D * n).from_buffer_copy(buf)
    return PackedRays(records=arr, count=n, dimension=3)


def pack_rays_2d_from_arrays(
    ids,
    ox,
    oy,
    dx,
    dy,
    tmax,
) -> PackedRays:
    """Fast bulk packing of 2-D rays from array-like inputs.

    This bypasses per-ray ``Ray2D`` object construction for generated workloads
    such as robot pose sweeps.  The structured dtype mirrors the packed C ABI:
    ``uint32 id`` followed by five float64 fields.
    """
    try:
        import numpy as _np
    except ImportError:  # pragma: no cover
        raise RuntimeError("pack_rays_2d_from_arrays requires numpy")

    ids_a = _np.asarray(ids, dtype=_np.uint32)
    ox_a = _np.asarray(ox, dtype=_np.float64)
    oy_a = _np.asarray(oy, dtype=_np.float64)
    dx_a = _np.asarray(dx, dtype=_np.float64)
    dy_a = _np.asarray(dy, dtype=_np.float64)
    tmax_a = _np.asarray(tmax, dtype=_np.float64)

    n = len(ids_a)
    if any(len(field) != n for field in (ox_a, oy_a, dx_a, dy_a, tmax_a)):
        raise ValueError("rays arrays must have equal lengths")

    _dtype = _np.dtype({
        "names": ["id", "ox", "oy", "dx", "dy", "tmax"],
        "formats": [_np.uint32, _np.float64, _np.float64, _np.float64, _np.float64, _np.float64],
        "offsets": [0, 4, 12, 20, 28, 36],
        "itemsize": 44,
    })
    buf = _np.empty(n, dtype=_dtype)
    buf["id"] = ids_a
    buf["ox"] = ox_a
    buf["oy"] = oy_a
    buf["dx"] = dx_a
    buf["dy"] = dy_a
    buf["tmax"] = tmax_a

    arr = (_RtdlRay2D * n).from_buffer_copy(buf)
    return PackedRays(records=arr, count=n, dimension=2)


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
        norm = records if isinstance(records, tuple) and all(isinstance(item, (_CanonicalRay2D, _CanonicalRay3D)) for item in records) else _normalize_records("rays", "rays", records)
        if dimension not in {None, 2, 3}:
            raise ValueError("rays dimension must be one of: 2, 3")
        inferred_dimension = dimension
        if inferred_dimension is None:
            inferred_dimension = 3 if norm and all(isinstance(item, _CanonicalRay3D) for item in norm) else 2
        if inferred_dimension == 3:
            if any(not isinstance(item, _CanonicalRay3D) for item in norm):
                if norm:
                    raise ValueError("rays packed for a 3D layout must provide 3D ray records")
            arr = (_RtdlRay3D * len(norm))(*[
                _RtdlRay3D(r.id, r.ox, r.oy, r.oz, r.dx, r.dy, r.dz, r.tmax) for r in norm
            ])
            return PackedRays(records=arr, count=len(norm), dimension=3)
        if any(isinstance(item, _CanonicalRay3D) for item in norm):
            if norm:
                raise ValueError("rays packed for a 2D layout must provide 2D ray records")
        arr  = (_RtdlRay2D * len(norm))(*[
            _RtdlRay2D(r.id, r.ox, r.oy, r.dx, r.dy, r.tmax) for r in norm
        ])
        return PackedRays(records=arr, count=len(norm), dimension=2)
    if dimension == 3:
        raise ValueError("rays packed from explicit coordinate columns currently support only 2D records")
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
    return PackedRays(records=arr, count=n, dimension=2)


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
    if rays.dimension != triangles.dimension:
        raise ValueError("OptiX ray_triangle_hit_count requires rays and triangles to have the same dimension")
    if rays.dimension == 3:
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_ray_hitcount_3d")
        if symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_run_ray_hitcount_3d. "
                "Rebuild it with 'make build-optix' from current main."
            )
        status = symbol(
            rays.records, rays.count,
            triangles.records, triangles.count,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    else:
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


def _call_ray_anyhit_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    rays      = packed[compiled.candidates.left.name]
    triangles = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlRayAnyHitRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    if rays.dimension != triangles.dimension:
        raise ValueError("OptiX ray_triangle_any_hit requires rays and triangles to have the same dimension")
    if rays.dimension == 3:
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_ray_anyhit_3d")
        if symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_run_ray_anyhit_3d. "
                "Rebuild it with 'make build-optix' from current main."
            )
        status = symbol(
            rays.records, rays.count,
            triangles.records, triangles.count,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    else:
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_ray_anyhit")
        if symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_run_ray_anyhit. "
                "Rebuild it with 'make build-optix' from current main."
            )
        status = symbol(
            rays.records, rays.count,
            triangles.records, triangles.count,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlRayAnyHitRow,
        field_names=("ray_id", "any_hit"))


class PreparedOptixRayTriangleAnyHit2D:
    """Prepared OptiX 2-D any-hit scene with scalar hit-count query output."""

    def __init__(self, triangles):
        packed = triangles if isinstance(triangles, PackedTriangles) else pack_triangles(triangles, dimension=2)
        if packed.dimension != 2:
            raise ValueError("prepare_optix_ray_triangle_any_hit_2d requires 2-D triangles")
        self._packed_triangles = packed
        self._handle = ctypes.c_void_p()
        self._closed = False
        if packed.count == 0:
            return

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_ray_anyhit_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_prepare_ray_anyhit_2d. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(
            packed.records,
            packed.count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)

    def count(self, rays) -> int:
        if self._closed:
            raise RuntimeError("prepared OptiX any-hit handle is closed")
        if isinstance(rays, OptixRay2DBuffer):
            return self.count_packed(rays)
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=2)
        if packed_rays.dimension != 2:
            raise ValueError("PreparedOptixRayTriangleAnyHit2D.count requires 2-D rays")
        if packed_rays.count == 0 or self._packed_triangles.count == 0:
            return 0

        lib = _load_optix_library()
        count_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_ray_anyhit_2d")
        if count_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_count_prepared_ray_anyhit_2d. "
                "Rebuild it with 'make build-optix' from current main."
            )
        hit_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self._handle,
            packed_rays.records,
            packed_rays.count,
            ctypes.byref(hit_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(hit_count.value)

    def count_packed(self, rays: "OptixRay2DBuffer") -> int:
        if self._closed:
            raise RuntimeError("prepared OptiX any-hit handle is closed")
        if not isinstance(rays, OptixRay2DBuffer):
            raise ValueError("count_packed requires an OptixRay2DBuffer")
        if rays.closed:
            raise RuntimeError("prepared OptiX ray buffer is closed")
        if rays.count == 0 or self._packed_triangles.count == 0:
            return 0

        lib = _load_optix_library()
        count_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_ray_anyhit_2d_packed")
        if count_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_count_prepared_ray_anyhit_2d_packed. "
                "Rebuild it with 'make build-optix' from current main."
            )
        hit_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self._handle,
            rays.handle,
            ctypes.byref(hit_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(hit_count.value)

    def pose_flags_packed(self, rays: "OptixRay2DBuffer", pose_indices, *, pose_count: int) -> tuple[bool, ...]:
        """Return one native collision flag per pose index for packed 2-D rays."""
        if self._closed:
            raise RuntimeError("prepared OptiX any-hit handle is closed")
        if not isinstance(rays, OptixRay2DBuffer):
            raise ValueError("pose_flags_packed requires an OptixRay2DBuffer")
        if rays.closed:
            raise RuntimeError("prepared OptiX ray buffer is closed")
        if pose_count < 0:
            raise ValueError("pose_count must be non-negative")
        pose_index_ptr: ctypes.c_void_p | ctypes.POINTER(ctypes.c_uint32)
        pose_index_count: int
        pose_index_owner = None
        if hasattr(pose_indices, "ctypes"):
            try:
                import numpy as _np
            except ImportError:  # pragma: no cover
                _np = None
            if _np is None:
                raise RuntimeError("numpy pose-index buffers require numpy")
            pose_index_owner = _np.ascontiguousarray(pose_indices, dtype=_np.uint32)
            pose_index_count = int(pose_index_owner.size)
            if pose_index_count and (
                int(pose_index_owner.min()) < 0 or int(pose_index_owner.max()) >= pose_count
            ):
                raise ValueError("pose_indices entries must be within [0, pose_count)")
            pose_index_ptr = pose_index_owner.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
        else:
            normalized_pose_indices = tuple(int(index) for index in pose_indices)
            pose_index_count = len(normalized_pose_indices)
            if any(index < 0 or index >= pose_count for index in normalized_pose_indices):
                raise ValueError("pose_indices entries must be within [0, pose_count)")
            PoseIndexArray = ctypes.c_uint32 * pose_index_count
            pose_index_owner = PoseIndexArray(*normalized_pose_indices)
            pose_index_ptr = pose_index_owner

        if pose_index_count != rays.count:
            raise ValueError("pose_indices length must match prepared ray count")
        if rays.count == 0 or self._packed_triangles.count == 0 or pose_count == 0:
            return tuple(False for _ in range(pose_count))

        lib = _load_optix_library()
        pose_flags_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed")
        if pose_flags_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed. "
                "Rebuild it with 'make build-optix' from current main."
            )
        PoseFlagArray = ctypes.c_uint32 * pose_count
        pose_flag_buffer = PoseFlagArray()
        error = ctypes.create_string_buffer(4096)
        status = pose_flags_symbol(
            self._handle,
            rays.handle,
            pose_index_ptr,
            pose_index_count,
            pose_flag_buffer,
            pose_count,
            error,
            len(error),
        )
        _check_status(status, error)
        return tuple(bool(pose_flag_buffer[index]) for index in range(pose_count))

    def pose_flags_prepared_indices(
        self,
        rays: "OptixRay2DBuffer",
        pose_indices: "OptixPoseIndexBuffer",
        *,
        pose_count: int,
    ) -> tuple[bool, ...]:
        """Return pose flags using GPU-resident prepared pose indices."""
        if self._closed:
            raise RuntimeError("prepared OptiX any-hit handle is closed")
        if not isinstance(rays, OptixRay2DBuffer):
            raise ValueError("pose_flags_prepared_indices requires an OptixRay2DBuffer")
        if not isinstance(pose_indices, OptixPoseIndexBuffer):
            raise ValueError("pose_flags_prepared_indices requires an OptixPoseIndexBuffer")
        if rays.closed:
            raise RuntimeError("prepared OptiX ray buffer is closed")
        if pose_indices.closed:
            raise RuntimeError("prepared OptiX pose-index buffer is closed")
        if pose_count < 0:
            raise ValueError("pose_count must be non-negative")
        if pose_indices.count != rays.count:
            raise ValueError("prepared pose-index count must match prepared ray count")
        if rays.count == 0 or self._packed_triangles.count == 0 or pose_count == 0:
            return tuple(False for _ in range(pose_count))

        lib = _load_optix_library()
        pose_flags_symbol = _find_optional_backend_symbol(
            lib,
            "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_prepared_indices",
        )
        if pose_flags_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_prepared_indices. "
                "Rebuild it with 'make build-optix' from current main."
            )
        PoseFlagArray = ctypes.c_uint32 * pose_count
        pose_flag_buffer = PoseFlagArray()
        error = ctypes.create_string_buffer(4096)
        status = pose_flags_symbol(
            self._handle,
            rays.handle,
            pose_indices.handle,
            pose_flag_buffer,
            pose_count,
            error,
            len(error),
        )
        _check_status(status, error)
        return tuple(bool(pose_flag_buffer[index]) for index in range(pose_count))

    def pose_count_prepared_indices(
        self,
        rays: "OptixRay2DBuffer",
        pose_indices: "OptixPoseIndexBuffer",
        *,
        pose_count: int,
    ) -> int:
        """Return only the number of colliding poses using prepared buffers."""
        if self._closed:
            raise RuntimeError("prepared OptiX any-hit handle is closed")
        if not isinstance(rays, OptixRay2DBuffer):
            raise ValueError("pose_count_prepared_indices requires an OptixRay2DBuffer")
        if not isinstance(pose_indices, OptixPoseIndexBuffer):
            raise ValueError("pose_count_prepared_indices requires an OptixPoseIndexBuffer")
        if rays.closed:
            raise RuntimeError("prepared OptiX ray buffer is closed")
        if pose_indices.closed:
            raise RuntimeError("prepared OptiX pose-index buffer is closed")
        if pose_count < 0:
            raise ValueError("pose_count must be non-negative")
        if pose_indices.count != rays.count:
            raise ValueError("prepared pose-index count must match prepared ray count")
        if rays.count == 0 or self._packed_triangles.count == 0 or pose_count == 0:
            return 0

        lib = _load_optix_library()
        count_symbol = _find_optional_backend_symbol(
            lib,
            "rtdl_optix_count_poses_prepared_ray_anyhit_2d_prepared_indices",
        )
        if count_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_count_poses_prepared_ray_anyhit_2d_prepared_indices. "
                "Rebuild it with 'make build-optix' from current main."
            )
        colliding_pose_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self._handle,
            rays.handle,
            pose_indices.handle,
            pose_count,
            ctypes.byref(colliding_pose_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(colliding_pose_count.value)

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_ray_anyhit_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixRayTriangleAnyHit2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_ray_triangle_any_hit_2d(triangles) -> PreparedOptixRayTriangleAnyHit2D:
    return PreparedOptixRayTriangleAnyHit2D(triangles)


class OptixRay2DBuffer:
    """Prepared OptiX 2-D ray batch for repeated scalar any-hit counts."""

    def __init__(self, rays):
        packed = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=2)
        if packed.dimension != 2:
            raise ValueError("prepare_optix_rays_2d requires 2-D rays")
        self._packed_rays = packed
        self._handle = ctypes.c_void_p()
        self._closed = False
        if packed.count == 0:
            return

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_rays_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_prepare_rays_2d. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(
            packed.records,
            packed.count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)

    @property
    def count(self) -> int:
        return int(self._packed_rays.count)

    @property
    def handle(self):
        return self._handle

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_rays_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "OptixRay2DBuffer":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_rays_2d(rays) -> OptixRay2DBuffer:
    return OptixRay2DBuffer(rays)


class OptixPoseIndexBuffer:
    """Prepared GPU-resident pose-index batch for repeated pose-flag queries."""

    def __init__(self, pose_indices):
        self._closed = False
        self._handle = ctypes.c_void_p()
        self._owner = None
        self._count = 0

        if hasattr(pose_indices, "ctypes"):
            try:
                import numpy as _np
            except ImportError:  # pragma: no cover
                _np = None
            if _np is None:
                raise RuntimeError("numpy pose-index buffers require numpy")
            self._owner = _np.ascontiguousarray(pose_indices, dtype=_np.uint32)
            self._count = int(self._owner.size)
            ptr = self._owner.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
        else:
            normalized = tuple(int(index) for index in pose_indices)
            if any(index < 0 for index in normalized):
                raise ValueError("pose_indices entries must be non-negative")
            self._count = len(normalized)
            PoseIndexArray = ctypes.c_uint32 * self._count
            self._owner = PoseIndexArray(*normalized)
            ptr = self._owner

        if self._count == 0:
            return

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_pose_indices_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_prepare_pose_indices_2d. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(
            ptr,
            self._count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)

    @property
    def count(self) -> int:
        return self._count

    @property
    def handle(self):
        return self._handle

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_pose_indices_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "OptixPoseIndexBuffer":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_pose_indices_2d(pose_indices) -> OptixPoseIndexBuffer:
    return OptixPoseIndexBuffer(pose_indices)


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


def _call_segment_polygon_anyhit_rows_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    segments = packed[compiled.candidates.left.name]
    polygons = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_optix_run_segment_polygon_anyhit_rows(
        segments.records, segments.count,
        polygons.refs, polygons.polygon_count,
        polygons.vertices_xy, polygons.vertex_xy_count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlSegmentPolygonAnyHitRow,
        field_names=("segment_id", "polygon_id"))


def segment_polygon_anyhit_rows_native_bounded_optix(
    segments,
    polygons,
    *,
    output_capacity: int,
) -> tuple[dict[str, int], ...]:
    """Run the native bounded OptiX segment/polygon pair-row emitter.

    This is intentionally explicit and bounded: callers must size the output
    buffer and overflow is reported as an error instead of silently truncating
    pair rows.
    """
    if output_capacity <= 0:
        raise ValueError("output_capacity must be positive")
    packed_segments = pack_segments(records=segments)
    packed_polygons = pack_polygons(records=polygons)
    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded",
    )
    if symbol is None:
        raise ValueError(
            "loaded OptiX backend does not export "
            "rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded; "
            "rebuild the OptiX backend from current main"
        )
    row_array = (_RtdlSegmentPolygonAnyHitRow * output_capacity)()
    emitted_count = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        packed_segments.records,
        packed_segments.count,
        packed_polygons.refs,
        packed_polygons.polygon_count,
        packed_polygons.vertices_xy,
        packed_polygons.vertex_xy_count,
        row_array,
        output_capacity,
        ctypes.byref(emitted_count),
        ctypes.byref(overflowed),
        error,
        len(error),
    )
    _check_status(status, error)
    if int(overflowed.value) != 0:
        raise RuntimeError(
            "native bounded OptiX segment/polygon pair-row output overflowed "
            f"capacity {output_capacity}; emitted at least {int(emitted_count.value)} rows"
        )
    return tuple(
        {"segment_id": int(row_array[index].segment_id), "polygon_id": int(row_array[index].polygon_id)}
        for index in range(int(emitted_count.value))
    )


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


def _call_fixed_radius_neighbors_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    query_points = packed[compiled.candidates.left.name]
    search_points = packed[compiled.candidates.right.name]
    radius = float(compiled.refine_op.predicate.options["radius"])
    k_max = int(compiled.refine_op.predicate.options["k_max"])
    rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if query_points.dimension == 3:
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_fixed_radius_neighbors_3d")
        if symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export rtdl_optix_run_fixed_radius_neighbors_3d; "
                "rebuild the OptiX backend from current main"
            )
        status = symbol(
            query_points.records, query_points.count,
            search_points.records, search_points.count,
            radius, k_max,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    else:
        status = lib.rtdl_optix_run_fixed_radius_neighbors(
            query_points.records, query_points.count,
            search_points.records, search_points.count,
            radius, k_max,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlFixedRadiusNeighborRow,
        field_names=("query_id", "neighbor_id", "distance"))


def _call_bounded_knn_rows_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    fixed_radius_rows = _call_fixed_radius_neighbors_optix_packed(compiled, packed, lib)
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


def _call_knn_rows_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    query_points = packed[compiled.candidates.left.name]
    search_points = packed[compiled.candidates.right.name]
    k = int(compiled.refine_op.predicate.options["k"])
    rows_ptr = ctypes.POINTER(_RtdlKnnNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if query_points.dimension == 3:
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_knn_rows_3d")
        if symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export rtdl_optix_run_knn_rows_3d; "
                "rebuild the OptiX backend from current main"
            )
        status = symbol(
            query_points.records, query_points.count,
            search_points.records, search_points.count,
            k,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    else:
        status = lib.rtdl_optix_run_knn_rows(
            query_points.records, query_points.count,
            search_points.records, search_points.count,
            k,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    _check_status(status, error)
    return OptixRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlKnnNeighborRow,
        field_names=("query_id", "neighbor_id", "distance", "neighbor_rank"))


def _call_bfs_expand_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    symbol = _require_optix_graph_symbol(lib, "rtdl_optix_run_bfs_expand")
    frontier = packed[compiled.candidates.left.name]
    graph = packed[compiled.candidates.right.name]
    visited_name = str(compiled.refine_op.predicate.options["visited_input"])
    visited = packed[visited_name]
    rows_ptr = ctypes.POINTER(_RtdlBfsExpandRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        graph.row_offsets, graph.row_offset_count,
        graph.column_indices, graph.column_index_count,
        frontier.records, frontier.count,
        visited.records, visited.count,
        ctypes.c_uint32(1 if compiled.refine_op.predicate.options.get("dedupe", True) else 0),
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error),
    )
    _check_status(status, error)
    return OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlBfsExpandRow,
        field_names=("src_vertex", "dst_vertex", "level"),
    )


def _call_triangle_probe_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    symbol = _require_optix_graph_symbol(lib, "rtdl_optix_run_triangle_probe")
    seeds = packed[compiled.candidates.left.name]
    graph = packed[compiled.candidates.right.name]
    rows_ptr = ctypes.POINTER(_RtdlTriangleRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        graph.row_offsets, graph.row_offset_count,
        graph.column_indices, graph.column_index_count,
        seeds.records, seeds.count,
        ctypes.c_uint32(1 if compiled.refine_op.predicate.options.get("order") == "id_ascending" else 0),
        ctypes.c_uint32(1 if compiled.refine_op.predicate.options.get("unique", True) else 0),
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error),
    )
    _check_status(status, error)
    return OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlTriangleRow,
        field_names=("u", "v", "w"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Library loading
# ─────────────────────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _load_optix_library():
    lib_path = _find_optix_library()
    lib = ctypes.CDLL(str(lib_path))
    lib._rtdl_library_path = str(lib_path)
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
    _require_backend_symbol(lib, "rtdl_optix_get_version").argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.rtdl_optix_get_version.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_optix_free_rows").argtypes = [ctypes.c_void_p]
    lib.rtdl_optix_free_rows.restype  = None

    _require_backend_symbol(lib, "rtdl_optix_run_lsi").argtypes = [
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_lsi.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_optix_run_pip").argtypes = [
        ctypes.POINTER(_RtdlPoint),      ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlPipRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_pip.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_optix_run_overlay").argtypes = [
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlOverlayRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_overlay.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_optix_run_ray_hitcount").argtypes = [
        ctypes.POINTER(_RtdlRay2D),      ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle),   ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_ray_hitcount.restype = ctypes.c_int
    optional_ray3d = _find_optional_backend_symbol(lib, "rtdl_optix_run_ray_hitcount_3d")
    if optional_ray3d is not None:
        optional_ray3d.argtypes = [
            ctypes.POINTER(_RtdlRay3D), ctypes.c_size_t,
            ctypes.POINTER(_RtdlTriangle3D), ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_ray3d.restype = ctypes.c_int
    optional_anyhit = _find_optional_backend_symbol(lib, "rtdl_optix_run_ray_anyhit")
    if optional_anyhit is not None:
        optional_anyhit.argtypes = [
            ctypes.POINTER(_RtdlRay2D), ctypes.c_size_t,
            ctypes.POINTER(_RtdlTriangle), ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayAnyHitRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_anyhit.restype = ctypes.c_int
    optional_anyhit3d = _find_optional_backend_symbol(lib, "rtdl_optix_run_ray_anyhit_3d")
    if optional_anyhit3d is not None:
        optional_anyhit3d.argtypes = [
            ctypes.POINTER(_RtdlRay3D), ctypes.c_size_t,
            ctypes.POINTER(_RtdlTriangle3D), ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayAnyHitRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_anyhit3d.restype = ctypes.c_int
    optional_prepare_anyhit2d = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_ray_anyhit_2d")
    if optional_prepare_anyhit2d is not None:
        optional_prepare_anyhit2d.argtypes = [
            ctypes.POINTER(_RtdlTriangle),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_anyhit2d.restype = ctypes.c_int
    optional_count_anyhit2d = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_ray_anyhit_2d")
    if optional_count_anyhit2d is not None:
        optional_count_anyhit2d.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay2D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_count_anyhit2d.restype = ctypes.c_int
    optional_destroy_anyhit2d = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_ray_anyhit_2d")
    if optional_destroy_anyhit2d is not None:
        optional_destroy_anyhit2d.argtypes = [ctypes.c_void_p]
        optional_destroy_anyhit2d.restype = None
    optional_prepare_rays2d = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_rays_2d")
    if optional_prepare_rays2d is not None:
        optional_prepare_rays2d.argtypes = [
            ctypes.POINTER(_RtdlRay2D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_rays2d.restype = ctypes.c_int
    optional_count_anyhit2d_packed = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_ray_anyhit_2d_packed")
    if optional_count_anyhit2d_packed is not None:
        optional_count_anyhit2d_packed.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_count_anyhit2d_packed.restype = ctypes.c_int
    optional_pose_flags_anyhit2d_packed = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed",
    )
    if optional_pose_flags_anyhit2d_packed is not None:
        optional_pose_flags_anyhit2d_packed.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_pose_flags_anyhit2d_packed.restype = ctypes.c_int
    optional_prepare_pose_indices2d = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_pose_indices_2d")
    if optional_prepare_pose_indices2d is not None:
        optional_prepare_pose_indices2d.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_pose_indices2d.restype = ctypes.c_int
    optional_pose_flags_anyhit2d_prepared_indices = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_prepared_indices",
    )
    if optional_pose_flags_anyhit2d_prepared_indices is not None:
        optional_pose_flags_anyhit2d_prepared_indices.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_pose_flags_anyhit2d_prepared_indices.restype = ctypes.c_int
    optional_pose_count_anyhit2d_prepared_indices = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_count_poses_prepared_ray_anyhit_2d_prepared_indices",
    )
    if optional_pose_count_anyhit2d_prepared_indices is not None:
        optional_pose_count_anyhit2d_prepared_indices.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_pose_count_anyhit2d_prepared_indices.restype = ctypes.c_int
    optional_destroy_pose_indices2d = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_pose_indices_2d")
    if optional_destroy_pose_indices2d is not None:
        optional_destroy_pose_indices2d.argtypes = [ctypes.c_void_p]
        optional_destroy_pose_indices2d.restype = None
    optional_destroy_rays2d = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_rays_2d")
    if optional_destroy_rays2d is not None:
        optional_destroy_rays2d.argtypes = [ctypes.c_void_p]
        optional_destroy_rays2d.restype = None

    _require_backend_symbol(lib, "rtdl_optix_run_segment_polygon_hitcount").argtypes = [
        ctypes.POINTER(_RtdlSegment),    ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_segment_polygon_hitcount.restype = ctypes.c_int

    optional_prepare_segpoly_hitcount = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_segment_polygon_hitcount_2d",
    )
    if optional_prepare_segpoly_hitcount is not None:
        optional_prepare_segpoly_hitcount.argtypes = [
            ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_prepare_segpoly_hitcount.restype = ctypes.c_int
    optional_run_prepared_segpoly_hitcount = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_prepared_segment_polygon_hitcount_2d",
    )
    if optional_run_prepared_segpoly_hitcount is not None:
        optional_run_prepared_segpoly_hitcount.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_run_prepared_segpoly_hitcount.restype = ctypes.c_int
    optional_count_prepared_segpoly_hitcount_at_least = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d",
    )
    if optional_count_prepared_segpoly_hitcount_at_least is not None:
        optional_count_prepared_segpoly_hitcount_at_least.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_count_prepared_segpoly_hitcount_at_least.restype = ctypes.c_int
    optional_aggregate_prepared_segpoly_hitcount = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d",
    )
    if optional_aggregate_prepared_segpoly_hitcount is not None:
        optional_aggregate_prepared_segpoly_hitcount.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_aggregate_prepared_segpoly_hitcount.restype = ctypes.c_int
    optional_destroy_prepared_segpoly_hitcount = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_destroy_prepared_segment_polygon_hitcount_2d",
    )
    if optional_destroy_prepared_segpoly_hitcount is not None:
        optional_destroy_prepared_segpoly_hitcount.argtypes = [ctypes.c_void_p]
        optional_destroy_prepared_segpoly_hitcount.restype = None

    _require_backend_symbol(lib, "rtdl_optix_run_segment_polygon_anyhit_rows").argtypes = [
        ctypes.POINTER(_RtdlSegment),    ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_segment_polygon_anyhit_rows.restype = ctypes.c_int

    optional_segment_polygon_anyhit_rows_native_bounded = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded",
    )
    if optional_segment_polygon_anyhit_rows_native_bounded is not None:
        optional_segment_polygon_anyhit_rows_native_bounded.argtypes = [
            ctypes.POINTER(_RtdlSegment),    ctypes.c_size_t,
            ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
            ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_segment_polygon_anyhit_rows_native_bounded.restype = ctypes.c_int

    optional_prepare_segment_polygon_anyhit_rows = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_segment_polygon_anyhit_rows_2d",
    )
    if optional_prepare_segment_polygon_anyhit_rows is not None:
        optional_prepare_segment_polygon_anyhit_rows.argtypes = [
            ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_prepare_segment_polygon_anyhit_rows.restype = ctypes.c_int
    optional_run_prepared_segment_polygon_anyhit_rows = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d",
    )
    if optional_run_prepared_segment_polygon_anyhit_rows is not None:
        optional_run_prepared_segment_polygon_anyhit_rows.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
            ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_run_prepared_segment_polygon_anyhit_rows.restype = ctypes.c_int
    optional_destroy_prepared_segment_polygon_anyhit_rows = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_destroy_prepared_segment_polygon_anyhit_rows_2d",
    )
    if optional_destroy_prepared_segment_polygon_anyhit_rows is not None:
        optional_destroy_prepared_segment_polygon_anyhit_rows.argtypes = [ctypes.c_void_p]
        optional_destroy_prepared_segment_polygon_anyhit_rows.restype = None

    _require_backend_symbol(lib, "rtdl_optix_run_point_nearest_segment").argtypes = [
        ctypes.POINTER(_RtdlPoint),   ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPointNearestSegmentRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_point_nearest_segment.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_optix_run_fixed_radius_neighbors").argtypes = [
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_fixed_radius_neighbors.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_fixed_radius_neighbors_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    optional_frn_count = _find_optional_backend_symbol(lib, "rtdl_optix_run_fixed_radius_count_threshold")
    if optional_frn_count is not None:
        optional_frn_count.argtypes = [
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_frn_count.restype = ctypes.c_int

    optional_prepare_frn_count = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_fixed_radius_count_threshold_2d")
    if optional_prepare_frn_count is not None:
        optional_prepare_frn_count.argtypes = [
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_prepare_frn_count.restype = ctypes.c_int

    optional_run_prepared_frn_count = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_fixed_radius_count_threshold_2d")
    if optional_run_prepared_frn_count is not None:
        optional_run_prepared_frn_count.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_run_prepared_frn_count.restype = ctypes.c_int

    optional_count_prepared_frn_threshold = _find_optional_backend_symbol(
        lib, "rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d"
    )
    if optional_count_prepared_frn_threshold is not None:
        optional_count_prepared_frn_threshold.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_count_prepared_frn_threshold.restype = ctypes.c_int

    optional_destroy_prepared_frn_count = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d")
    if optional_destroy_prepared_frn_count is not None:
        optional_destroy_prepared_frn_count.argtypes = [ctypes.c_void_p]
        optional_destroy_prepared_frn_count.restype = None

    _require_backend_symbol(lib, "rtdl_optix_run_knn_rows").argtypes = [
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_knn_rows.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_knn_rows_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_bfs_expand")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
            ctypes.POINTER(_RtdlFrontierVertex), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.POINTER(_RtdlBfsExpandRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_triangle_probe")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
            ctypes.POINTER(_RtdlEdgeSeed), ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.POINTER(_RtdlTriangleRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_conjunctive_scan")
    if symbol is not None:
        symbol.argtypes = [
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
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_grouped_count")
    if symbol is not None:
        symbol.argtypes = [
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
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_grouped_sum")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDbField),
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedSumRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_db_dataset_create")
    if symbol is not None:
        symbol.argtypes = [
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
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_db_dataset_create_columnar")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDbColumn),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_db_dataset_destroy")
    if symbol is not None:
        symbol.argtypes = [ctypes.c_void_p]
        symbol.restype = None

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_db_dataset_conjunctive_scan")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbRowIdRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_db_dataset_conjunctive_scan_count")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_db_dataset_grouped_count")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_db_dataset_grouped_sum")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedSumRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int


def _require_backend_symbol(lib, symbol_name: str):
    try:
        return getattr(lib, symbol_name)
    except AttributeError as exc:
        path = getattr(lib, "_rtdl_library_path", "<unknown>")
        raise RuntimeError(
            f"Loaded OptiX library {path!r} is missing required export {symbol_name!r}. "
            "This usually means the shared library is stale or was built from an older RTDL checkout. "
            "Rebuild it with 'make build-optix' or point RTDL_OPTIX_LIB at a rebuilt library."
        ) from exc


def _find_optional_backend_symbol(lib, symbol_name: str):
    try:
        return getattr(lib, symbol_name)
    except AttributeError:
        return None


def _require_optix_graph_symbol(lib, symbol_name: str):
    symbol = _find_optional_backend_symbol(lib, symbol_name)
    if symbol is None:
        path = getattr(lib, "_rtdl_library_path", "<unknown>")
        raise RuntimeError(
            f"Loaded OptiX library {path!r} does not export {symbol_name!r}. "
            "Rebuild it with 'make build-optix' from the current checkout before running RT graph kernels on OptiX."
        )
    return symbol


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


def _geometry_layout_dimension(geometry_input) -> int:
    layout = geometry_input.layout
    field_names = set(layout.field_names())
    if layout.name.endswith("3D") or any(name in field_names for name in ("z0", "z1", "z2", "oz", "dz")):
        return 3
    return 2


def _pack_for_geometry(geometry_input, payload):
    if isinstance(geometry_input, str):
        geometry_name = geometry_input
        expected_dimension = None
    else:
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
        return payload if isinstance(payload, PackedSegments)  else pack_segments(records=payload)
    if geometry_name == "points":
        cached = getattr(payload, "_rtdl_packed_points", None)
        if isinstance(cached, PackedPoints):
            if expected_dimension is not None and cached.dimension != expected_dimension:
                raise ValueError(
                    "cached packed points payload dimension does not match the kernel input layout"
                )
            return cached
        if isinstance(payload, PackedPoints):
            if expected_dimension is not None and payload.dimension != expected_dimension:
                raise ValueError(
                    "packed points payload dimension does not match the kernel input layout"
                )
            return payload
        return pack_points(records=payload, dimension=expected_dimension)
    if geometry_name == "polygons":
        cached = getattr(payload, "_rtdl_packed_polygons", None)
        if isinstance(cached, PackedPolygons):
            return cached
        return payload if isinstance(payload, PackedPolygons)  else pack_polygons(records=payload)
    if geometry_name == "triangles":
        if isinstance(payload, PackedTriangles):
            if expected_dimension is not None and payload.dimension != expected_dimension:
                raise ValueError(
                    "packed triangles payload dimension does not match the kernel input layout"
                )
            return payload
        return pack_triangles(records=payload, dimension=expected_dimension)
    if geometry_name == "rays":
        if isinstance(payload, PackedRays):
            if expected_dimension is not None and payload.dimension != expected_dimension:
                raise ValueError(
                    "packed rays payload dimension does not match the kernel input layout"
                )
            return payload
        return pack_rays(records=payload, dimension=expected_dimension)
    raise ValueError(f"unsupported geometry type for OptiX backend: {geometry_name!r}")


def _make_owned_row_view(row_type, rows, field_names: tuple[str, ...]) -> OptixRowView:
    array = (row_type * len(rows))(*rows)
    rows_ptr = ctypes.cast(array, ctypes.POINTER(row_type))
    view = OptixRowView(
        library=None,
        rows_ptr=rows_ptr,
        row_count=len(rows),
        row_type=row_type,
        field_names=field_names,
        _free_on_close=False,
        _owner=array,
    )
    return view


def _is_packed_for_geometry(geometry_name: str, payload) -> bool:
    if geometry_name == "graph_csr":
        return isinstance(payload, PackedGraphCSR)
    if geometry_name == "vertex_frontier":
        return isinstance(payload, PackedVertexFrontier)
    if geometry_name == "vertex_set":
        return isinstance(payload, PackedVertexSet)
    if geometry_name == "edge_set":
        return isinstance(payload, PackedEdgeSet)
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
