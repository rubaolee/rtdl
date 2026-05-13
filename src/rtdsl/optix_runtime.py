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
import time
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
from .embree_runtime import _RtdlPayloadField
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
from .v1_5_1_collect_k_bounded import collect_native_i64_rows_with_backend_symbol
from .v1_5_1_collect_k_bounded import collect_k_bounded_rows
from .v1_5_1_collect_k_bounded import validate_collect_k_bounded_result
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
from . import partner as _partner


_PREPARED_CACHE_MAX_ENTRIES = 8
_prepared_optix_execution_cache: OrderedDict[tuple[object, ...], "PreparedOptixExecution"] = OrderedDict()
_DB_MAX_ROWS_PER_JOB = 1_000_000
OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL = "rtdl_optix_collect_k_bounded_i64_device"
OPTIX_COLLECT_K_BOUNDED_I64_HOST_SYMBOL = "rtdl_optix_collect_k_bounded_i64"


def collect_k_bounded_i64_device_optix(
    *,
    candidate_rows_device_ptr: int,
    candidate_count: int,
    row_width: int,
    rows_out_device_ptr: int,
    row_capacity: int,
    allow_experimental: bool = False,
) -> dict[str, object]:
    """Experimental Python entry point for the measured OptiX device-pointer ABI."""
    if row_width <= 0:
        raise ValueError("row_width must be positive")
    if candidate_count < 0 or row_capacity < 0:
        raise ValueError("candidate_count and row_capacity must be nonnegative")
    if candidate_count and int(candidate_rows_device_ptr) == 0:
        raise ValueError("candidate_rows_device_ptr must be nonzero when candidate_count is nonzero")
    if row_capacity and int(rows_out_device_ptr) == 0:
        raise ValueError("rows_out_device_ptr must be nonzero when row_capacity is nonzero")
    if not allow_experimental:
        raise RuntimeError(
            f"{OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL} is measured natively but remains experimental; "
            "pass allow_experimental=True only for controlled Goal1500-style device-buffer validation"
        )

    lib = _load_optix_library()
    symbol = _require_backend_symbol(lib, OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL)
    emitted_count = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    h2d_transfers = ctypes.c_uint64()
    d2h_transfers = ctypes.c_uint64()
    internal_device_transfers = ctypes.c_uint64()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        ctypes.c_uint64(int(candidate_rows_device_ptr)),
        ctypes.c_size_t(int(candidate_count)),
        ctypes.c_size_t(int(row_width)),
        ctypes.c_uint64(int(rows_out_device_ptr)),
        ctypes.c_size_t(int(row_capacity)),
        ctypes.byref(emitted_count),
        ctypes.byref(overflowed),
        ctypes.byref(h2d_transfers),
        ctypes.byref(d2h_transfers),
        ctypes.byref(internal_device_transfers),
        error,
        len(error),
    )
    _check_status(status, error)
    return {
        "valid_count": int(emitted_count.value),
        "overflowed": bool(overflowed.value),
        "transfer_accounting": {
            "host_to_device_transfers_before_backend_execution": int(h2d_transfers.value),
            "device_to_host_transfers_after_backend_execution": int(d2h_transfers.value),
            "internal_device_transfers_if_any": int(internal_device_transfers.value),
            "allocation_only_transfers_distinguished_from_content_transfers": True,
        },
        "claim_flags": {
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "stable_public_primitive_authorized": False,
            "partner_tensor_handoff_authorized": False,
            "release_action_authorized": False,
        },
    }


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


class _RtdlPolygonPairCandidate(ctypes.Structure):
    _fields_ = [
        ("left_polygon_id", ctypes.c_uint32),
        ("right_polygon_id", ctypes.c_uint32),
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


_DB_COMPACT_SUMMARY_OP_SCAN_COUNT = 1
_DB_COMPACT_SUMMARY_OP_GROUPED_COUNT = 2
_DB_COMPACT_SUMMARY_OP_GROUPED_SUM = 3


class _RtdlDbCompactSummaryRequest(ctypes.Structure):
    _fields_ = [
        ("operation", ctypes.c_uint32),
        ("clauses", ctypes.c_void_p),
        ("clause_count", ctypes.c_size_t),
        ("group_key_field", ctypes.c_char_p),
        ("value_field", ctypes.c_char_p),
    ]


class _RtdlDbCompactSummaryResult(ctypes.Structure):
    _fields_ = [
        ("operation", ctypes.c_uint32),
        ("scalar_value", ctypes.c_size_t),
        ("count_rows", ctypes.POINTER(_RtdlDbGroupedCountRow)),
        ("count_row_count", ctypes.c_size_t),
        ("sum_rows", ctypes.POINTER(_RtdlDbGroupedSumRow)),
        ("sum_row_count", ctypes.c_size_t),
        ("traversal", ctypes.c_double),
        ("bitset_copyback", ctypes.c_double),
        ("exact_filter", ctypes.c_double),
        ("output_pack", ctypes.c_double),
        ("raw_candidate_count", ctypes.c_size_t),
        ("emitted_count", ctypes.c_size_t),
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
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_segment_shape_hitcount_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_segment_shape_hitcount_2d; rebuild the OptiX backend from current main"
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
        run_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_segment_shape_hitcount_2d")
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_segment_shape_hitcount_2d; rebuild the OptiX backend from current main"
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
            "rtdl_optix_count_prepared_segment_shape_hitcount_at_least_2d",
        )
        if count_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_count_prepared_segment_shape_hitcount_at_least_2d; rebuild the OptiX backend from current main"
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
            "rtdl_optix_aggregate_prepared_segment_shape_hitcount_2d",
        )
        if aggregate_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_aggregate_prepared_segment_shape_hitcount_2d; rebuild the OptiX backend from current main"
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
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_segment_shape_hitcount_2d")
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
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_segment_shape_anyhit_rows_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_segment_shape_anyhit_rows_2d; rebuild the OptiX backend from current main"
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
        run_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_segment_shape_anyhit_rows_2d")
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_segment_shape_anyhit_rows_2d; rebuild the OptiX backend from current main"
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
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_segment_shape_anyhit_rows_2d")
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
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_get_last_phase_timings")
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
        field_count: int | None = None,
        transfer: str = "row",
        keepalive=(),
    ):
        self.library = lib
        self.fields_array = fields_array
        self.row_values_array = row_values_array
        self.columns_array = columns_array
        self.field_count = int(field_count or 0)
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
            if not hasattr(self.library, "rtdl_optix_columnar_payload_create_from_columns"):
                raise RuntimeError(
                    "loaded OptiX backend does not export rtdl_optix_columnar_payload_create_from_columns; "
                    "rebuild the OptiX backend from the current checkout"
                )
            status = self.library.rtdl_optix_columnar_payload_create_from_columns(
                self.columns_array,
                ctypes.c_size_t(self.field_count),
                ctypes.c_size_t(self.row_count),
                primary_fields_array,
                ctypes.c_size_t(len(primary_field_bytes)),
                ctypes.byref(handle),
                error,
                len(error),
            )
        else:
            status = self.library.rtdl_optix_columnar_payload_create(
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
            self.library.rtdl_optix_columnar_payload_destroy(self.handle)
        self._closed = True

    def conjunctive_scan(self, clauses_array) -> OptixRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbRowIdRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_optix_columnar_payload_multi_predicate_scan(
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
        symbol = getattr(self.library, "rtdl_optix_columnar_payload_multi_predicate_scan_count", None)
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

    def compact_summary_batch_native(self, requests_array, request_count):
        symbol = getattr(self.library, "rtdl_optix_columnar_payload_compact_summary_batch", None)
        if symbol is None:
            return None
        results_ptr = ctypes.POINTER(_RtdlDbCompactSummaryResult)()
        result_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = symbol(
            self.handle,
            requests_array,
            ctypes.c_size_t(request_count),
            ctypes.byref(results_ptr),
            ctypes.byref(result_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return results_ptr, int(result_count.value)

    def destroy_compact_summary_batch_results(self, results_ptr, result_count: int) -> None:
        symbol = getattr(self.library, "rtdl_optix_columnar_compact_summary_results_destroy", None)
        if symbol is not None:
            symbol(results_ptr, ctypes.c_size_t(result_count))

    def grouped_count(self, clauses_array, group_key_field: bytes) -> OptixRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_optix_columnar_payload_grouped_reduction_count(
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
        status = self.library.rtdl_optix_columnar_payload_grouped_reduction_sum(
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
            field_count=len(columns_array) if columns_array is not None else None,
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

    def compact_summary_batch(self, requests) -> dict[str, object]:
        native = self._compact_summary_batch_native(requests)
        if native is not None:
            return native
        results: dict[str, object] = {}
        phases: dict[str, object] = {}
        for request in requests:
            name = str(request["name"])
            operation = str(request["operation"])
            if operation == "conjunctive_scan_count":
                results[name] = self.conjunctive_scan_count(request["predicates"])
            elif operation == "grouped_count_summary":
                results[name] = self.grouped_count_summary(request["query"])
            elif operation == "grouped_sum_summary":
                results[name] = self.grouped_sum_summary(request["query"])
            else:
                raise ValueError(f"unsupported DB compact-summary batch operation: {operation}")
            phases[name] = self.last_phase_timings()
        self._last_compact_summary_batch_phase_timings = phases
        return results

    def last_compact_summary_batch_phase_timings(self) -> dict[str, object]:
        return dict(getattr(self, "_last_compact_summary_batch_phase_timings", {}))

    def _compact_summary_batch_native(self, requests) -> dict[str, object] | None:
        if not hasattr(self, "_dataset"):
            return None
        if getattr(self._dataset.library, "rtdl_optix_columnar_payload_compact_summary_batch", None) is None:
            return None

        encoded_requests: list[_RtdlDbCompactSummaryRequest] = []
        request_meta: list[dict[str, object]] = []
        keepalive: list[object] = []
        for request in requests:
            operation = str(request["operation"])
            if operation == "conjunctive_scan_count":
                bundle = normalize_predicate_bundle(request["predicates"])
                clauses_array = _encode_db_clauses(self._encode_clauses(bundle.clauses))
                keepalive.append(clauses_array)
                encoded_requests.append(
                    _RtdlDbCompactSummaryRequest(
                        _DB_COMPACT_SUMMARY_OP_SCAN_COUNT,
                        ctypes.cast(clauses_array, ctypes.c_void_p),
                        len(clauses_array),
                        None,
                        None,
                    )
                )
                request_meta.append({"name": str(request["name"]), "operation": operation})
            elif operation in {"grouped_count_summary", "grouped_sum_summary"}:
                normalized_query = normalize_grouped_query(request["query"])
                if len(normalized_query.group_keys) != 1:
                    raise ValueError("first-wave OptiX DB compact summary batch supports exactly one group key")
                group_key = normalized_query.group_keys[0]
                if operation == "grouped_sum_summary" and not normalized_query.value_field:
                    raise ValueError("grouped_sum_summary requires a value_field")
                clauses_array = _encode_db_clauses(self._encode_clauses(normalized_query.predicates))
                group_key_field = group_key.encode("utf-8")
                value_field = (
                    normalized_query.value_field.encode("utf-8")
                    if operation == "grouped_sum_summary"
                    else None
                )
                keepalive.extend(item for item in (clauses_array, group_key_field, value_field) if item is not None)
                encoded_requests.append(
                    _RtdlDbCompactSummaryRequest(
                        _DB_COMPACT_SUMMARY_OP_GROUPED_SUM
                        if operation == "grouped_sum_summary"
                        else _DB_COMPACT_SUMMARY_OP_GROUPED_COUNT,
                        ctypes.cast(clauses_array, ctypes.c_void_p),
                        len(clauses_array),
                        group_key_field,
                        value_field,
                    )
                )
                request_meta.append({"name": str(request["name"]), "operation": operation, "group_key": group_key})
            else:
                raise ValueError(f"unsupported DB compact-summary batch operation: {operation}")

        requests_array = (_RtdlDbCompactSummaryRequest * len(encoded_requests))(*encoded_requests)
        native_result = self._dataset.compact_summary_batch_native(requests_array, len(encoded_requests))
        if native_result is None:
            return None
        results_ptr, result_count = native_result
        try:
            if result_count != len(request_meta):
                raise RuntimeError("OptiX compact-summary batch returned an unexpected result count")
            results: dict[str, object] = {}
            phases: dict[str, object] = {}
            for index, meta in enumerate(request_meta):
                result = results_ptr[index]
                name = str(meta["name"])
                operation = str(meta["operation"])
                phases[name] = {
                    "traversal": float(result.traversal),
                    "bitset_copyback": float(result.bitset_copyback),
                    "exact_filter": float(result.exact_filter),
                    "output_pack": float(result.output_pack),
                    "raw_candidate_count": int(result.raw_candidate_count),
                    "emitted_count": int(result.emitted_count),
                }
                if operation == "conjunctive_scan_count":
                    results[name] = int(result.scalar_value)
                elif operation == "grouped_count_summary":
                    group_key = str(meta["group_key"])
                    reverse_map = self._reverse_maps.get(group_key)
                    results[name] = {
                        str(_decode_db_group_key(reverse_map, result.count_rows[row_index].group_key)): int(
                            result.count_rows[row_index].count
                        )
                        for row_index in range(int(result.count_row_count))
                    }
                elif operation == "grouped_sum_summary":
                    group_key = str(meta["group_key"])
                    reverse_map = self._reverse_maps.get(group_key)
                    results[name] = {
                        str(_decode_db_group_key(reverse_map, result.sum_rows[row_index].group_key)): int(
                            result.sum_rows[row_index].sum
                        )
                        for row_index in range(int(result.sum_row_count))
                    }
            self._last_compact_summary_batch_phase_timings = phases
            keepalive.append(requests_array)
            return results
        finally:
            self._dataset.destroy_compact_summary_batch_results(results_ptr, result_count)

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
            field_count=len(columns_array),
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
        field_count=len(columns_array),
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


def pack_triangles_2d_from_arrays(
    ids,
    x0,
    y0,
    x1,
    y1,
    x2,
    y2,
) -> PackedTriangles:
    """Fast bulk packing of 2-D triangles from array-like inputs."""
    try:
        import numpy as _np
    except ImportError:  # pragma: no cover
        raise RuntimeError("pack_triangles_2d_from_arrays requires numpy")

    ids_a = _np.asarray(ids, dtype=_np.uint32)
    x0_a = _np.asarray(x0, dtype=_np.float64)
    y0_a = _np.asarray(y0, dtype=_np.float64)
    x1_a = _np.asarray(x1, dtype=_np.float64)
    y1_a = _np.asarray(y1, dtype=_np.float64)
    x2_a = _np.asarray(x2, dtype=_np.float64)
    y2_a = _np.asarray(y2, dtype=_np.float64)

    n = len(ids_a)
    if any(len(field) != n for field in (x0_a, y0_a, x1_a, y1_a, x2_a, y2_a)):
        raise ValueError("triangle arrays must have equal lengths")

    _dtype = _np.dtype({
        "names": ["id", "x0", "y0", "x1", "y1", "x2", "y2"],
        "formats": [_np.uint32, _np.float64, _np.float64, _np.float64, _np.float64, _np.float64, _np.float64],
        "offsets": [
            _RtdlTriangle.id.offset,
            _RtdlTriangle.x0.offset,
            _RtdlTriangle.y0.offset,
            _RtdlTriangle.x1.offset,
            _RtdlTriangle.y1.offset,
            _RtdlTriangle.x2.offset,
            _RtdlTriangle.y2.offset,
        ],
        "itemsize": ctypes.sizeof(_RtdlTriangle),
    })
    buf = _np.empty(n, dtype=_dtype)
    buf["id"] = ids_a
    buf["x0"] = x0_a
    buf["y0"] = y0_a
    buf["x1"] = x1_a
    buf["y1"] = y1_a
    buf["x2"] = x2_a
    buf["y2"] = y2_a

    arr = (_RtdlTriangle * n).from_buffer_copy(buf)
    return PackedTriangles(records=arr, count=n, dimension=2)


_PARTNER_RAY_2D_COLUMNS = ("ids", "ox", "oy", "dx", "dy", "tmax")
_PARTNER_TRIANGLE_2D_COLUMNS = ("ids", "x0", "y0", "x1", "y1", "x2", "y2")
_OPTIX_PARTNER_DEVICE_ANYHIT_SYMBOL = "rtdl_optix_count_ray_primitive_anyhit_2d_device_columns"
_OPTIX_PARTNER_PREPARED_DEVICE_RAYS_SYMBOL = "rtdl_optix_count_prepared_ray_anyhit_2d_device_rays"
_OPTIX_PARTNER_PREPARED_DEVICE_OUTPUT_FLAGS_SYMBOL = "rtdl_optix_write_prepared_ray_anyhit_2d_device_flags"
_OPTIX_PARTNER_PREPARED_DEVICE_WITNESSES_SYMBOL = "rtdl_optix_write_prepared_ray_anyhit_2d_device_witnesses"
_OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLES_SYMBOL = "rtdl_optix_prepare_ray_anyhit_2d_device_triangles"
_OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLE_COLUMNS_AABBS_SYMBOL = (
    "rtdl_optix_prepare_ray_anyhit_2d_device_triangle_columns_aabbs"
)


def _partner_dtype_token(dtype) -> str:
    token = str(dtype).lower()
    if "." in token:
        token = token.rsplit(".", 1)[-1]
    return token


def _partner_dtype_itemsize(dtype_token: str) -> int:
    if dtype_token in {"uint32", "float32", "float"}:
        return 4
    if dtype_token in {"float64", "double"}:
        return 8
    raise ValueError(f"unsupported partner dtype for stride validation: {dtype_token!r}")


def _partner_contiguous_column_strides(strides, *, itemsize: int) -> bool:
    return strides in (None, (1,), (itemsize,))


def _partner_contiguous_aabb_strides(strides) -> bool:
    return strides in (None, (6, 1), (24, 4))


def _require_partner_device_ray_column_layout(handoffs: dict) -> None:
    expected_dtypes = {
        "ids": {"uint32"},
        "ox": {"float64", "double"},
        "oy": {"float64", "double"},
        "dx": {"float64", "double"},
        "dy": {"float64", "double"},
        "tmax": {"float64", "double"},
    }
    expected_count = None
    expected_device = None
    for name in _PARTNER_RAY_2D_COLUMNS:
        handoff = handoffs[name]
        dtype = _partner_dtype_token(handoff.dtype)
        if dtype not in expected_dtypes[name]:
            allowed = ", ".join(sorted(expected_dtypes[name]))
            raise ValueError(f"partner device ray column {name!r} must use dtype {allowed}")
        if not _partner_contiguous_column_strides(
            handoff.strides,
            itemsize=_partner_dtype_itemsize(dtype),
        ):
            raise ValueError(f"partner device ray column {name!r} must be contiguous")
        count = int(handoff.shape[0])
        if expected_count is None:
            expected_count = count
        elif count != expected_count:
            raise ValueError("partner device ray columns must have matching lengths")
        device = (handoff.device_type, handoff.device_id)
        if expected_device is None:
            expected_device = device
        elif device != expected_device:
            raise ValueError("partner device ray columns must live on the same CUDA device")


def _require_partner_device_triangle_column_layout(handoffs: dict) -> None:
    expected_dtypes = {
        "ids": {"uint32"},
        "x0": {"float64", "double"},
        "y0": {"float64", "double"},
        "x1": {"float64", "double"},
        "y1": {"float64", "double"},
        "x2": {"float64", "double"},
        "y2": {"float64", "double"},
    }
    expected_count = None
    expected_device = None
    for name in _PARTNER_TRIANGLE_2D_COLUMNS:
        handoff = handoffs[name]
        dtype = _partner_dtype_token(handoff.dtype)
        if dtype not in expected_dtypes[name]:
            allowed = ", ".join(sorted(expected_dtypes[name]))
            raise ValueError(f"partner device triangle column {name!r} must use dtype {allowed}")
        if not _partner_contiguous_column_strides(
            handoff.strides,
            itemsize=_partner_dtype_itemsize(dtype),
        ):
            raise ValueError(f"partner device triangle column {name!r} must be contiguous")
        count = int(handoff.shape[0])
        if expected_count is None:
            expected_count = count
        elif count != expected_count:
            raise ValueError("partner device triangle columns must have matching lengths")
        device = (handoff.device_type, handoff.device_id)
        if expected_device is None:
            expected_device = device
        elif device != expected_device:
            raise ValueError("partner device triangle columns must live on the same CUDA device")


def _require_partner_device_triangle_aabb_layout(handoff, *, triangle_count: int, expected_device: tuple[str, int]) -> None:
    dtype = _partner_dtype_token(handoff.dtype)
    if dtype not in {"float32", "float"}:
        raise ValueError("partner device triangle AABB buffer must use dtype float32")
    if tuple(handoff.shape) != (triangle_count, 6):
        raise ValueError("partner device triangle AABB buffer must have shape (triangle_count, 6)")
    if not _partner_contiguous_aabb_strides(handoff.strides):
        raise ValueError(
            "partner device triangle AABB buffer must be contiguous with element strides (6, 1) "
            "or byte strides (24, 4)"
        )
    if (handoff.device_type, handoff.device_id) != expected_device:
        raise ValueError("partner device triangle AABB buffer must live on the same CUDA device as triangle columns")


def _require_partner_device_any_hit_output_layout(
    handoff,
    *,
    ray_count: int,
    expected_device: tuple[str, int],
) -> None:
    dtype = _partner_dtype_token(handoff.dtype)
    if dtype != "uint32":
        raise ValueError("partner device any-hit output buffer must use dtype uint32")
    if tuple(handoff.shape) != (ray_count,):
        raise ValueError("partner device any-hit output buffer must have shape (ray_count,)")
    if not _partner_contiguous_column_strides(
        handoff.strides,
        itemsize=_partner_dtype_itemsize(dtype),
    ):
        raise ValueError("partner device any-hit output buffer must be contiguous")
    if (handoff.device_type, handoff.device_id) != expected_device:
        raise ValueError("partner device any-hit output buffer must live on the same CUDA device as ray columns")


def _partner_column_to_host_array(value, *, column_name: str):
    try:
        import numpy as _np
    except ImportError:  # pragma: no cover
        raise RuntimeError("partner OptiX host staging requires numpy")

    descriptor_start = time.perf_counter()
    ctx = _partner.auto(value)
    descriptor = ctx.tensor(value, access="read")
    if len(descriptor.shape) != 1:
        raise ValueError(f"partner column {column_name!r} must be one-dimensional")
    descriptor_seconds = time.perf_counter() - descriptor_start

    staging_start = time.perf_counter()
    if descriptor.source_protocol == "torch":
        tensor = value.detach() if callable(getattr(value, "detach", None)) else value
        tensor = tensor.cpu() if callable(getattr(tensor, "cpu", None)) else tensor
        if not callable(getattr(tensor, "numpy", None)):
            raise TypeError(f"PyTorch partner column {column_name!r} cannot be converted to a host NumPy array")
        host_array = tensor.numpy()
    elif descriptor.source_protocol == "cupy":
        cupy = __import__("cupy")
        host_array = cupy.asnumpy(value)
    else:
        if descriptor.device_type != "cpu":
            raise TypeError(
                f"partner column {column_name!r} uses device {descriptor.device_type}:{descriptor.device_id}; "
                "only torch/cupy CUDA columns have a defined first-wave host staging path"
            )
        host_array = _np.asarray(value)
    staging_seconds = time.perf_counter() - staging_start
    return host_array, descriptor, {
        "descriptor_validation_s": descriptor_seconds,
        "framework_to_host_staging_s": staging_seconds,
    }


def _partner_host_stage_columns(columns: dict, required: tuple[str, ...], *, label: str):
    missing = [name for name in required if name not in columns]
    unexpected = [name for name in columns if name not in required]
    if missing:
        raise ValueError(f"missing {label} partner columns: {', '.join(missing)}")
    if unexpected:
        raise ValueError(f"unexpected {label} partner columns: {', '.join(unexpected)}")
    arrays = {}
    descriptors = {}
    timings = {
        "descriptor_validation_s": 0.0,
        "framework_to_host_staging_s": 0.0,
    }
    for name in required:
        arrays[name], descriptors[name], column_timings = _partner_column_to_host_array(
            columns[name],
            column_name=f"{label}.{name}",
        )
        for timing_name, seconds in column_timings.items():
            timings[timing_name] += float(seconds)
    return arrays, descriptors, timings


def _partner_device_descriptor_columns(columns: dict, required: tuple[str, ...], *, label: str):
    missing = [name for name in required if name not in columns]
    unexpected = [name for name in columns if name not in required]
    if missing:
        raise ValueError(f"missing {label} partner device columns: {', '.join(missing)}")
    if unexpected:
        raise ValueError(f"unexpected {label} partner device columns: {', '.join(unexpected)}")
    handoffs = {}
    validation_start = time.perf_counter()
    for name in required:
        handoff = _partner.prepare_direct_device_pointer_handoff(columns[name], access="read")
        if len(handoff.shape) != 1:
            raise ValueError(f"partner device column {label}.{name!r} must be one-dimensional")
        handoffs[name] = handoff
    validation_seconds = time.perf_counter() - validation_start
    return handoffs, {"descriptor_validation_s": validation_seconds}


def pack_optix_ray_any_hit_2d_device_ray_inputs(ray_columns: dict) -> dict[str, object]:
    """Validate partner-owned CUDA ray columns for a prepared OptiX scene.

    This is a ray-side true zero-copy path: the OptiX raygen reads these
    partner-owned columns directly. The prepared triangle scene is a separate
    native handle and may still have been built through RTDL-owned layout
    construction, so whole-primitive zero-copy is not implied.
    """
    ray_handoffs, timings = _partner_device_descriptor_columns(
        ray_columns,
        _PARTNER_RAY_2D_COLUMNS,
        label="ray",
    )
    _require_partner_device_ray_column_layout(ray_handoffs)
    descriptors = tuple(ray_handoffs[name] for name in _PARTNER_RAY_2D_COLUMNS)
    return {
        "rays": ray_handoffs,
        "metadata": {
            "backend": "optix",
            "transfer_mode": "device_ray_columns_zero_copy",
            "native_symbol": _OPTIX_PARTNER_PREPARED_DEVICE_RAYS_SYMBOL,
            "source_protocols": tuple(sorted({handoff.source_protocol for handoff in descriptors})),
            "source_devices": tuple(sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in descriptors})),
            "ray_count": int(ray_handoffs["ids"].shape[0]),
            "triangle_scene_transfer_mode": "prepared_scene_existing_path",
            "direct_device_pointer_observed": True,
            "direct_device_handoff_authorized": True,
            "ray_columns_true_zero_copy_authorized": True,
            "triangle_scene_true_zero_copy_authorized": False,
            "true_zero_copy_authorized": False,
            "partner_tensor_handoff_authorized": True,
            "rt_core_speedup_claim_authorized": False,
            "partner_phase_timings_s": timings,
        },
    }


def pack_optix_ray_any_hit_2d_device_triangle_inputs(triangle_columns: dict) -> dict[str, object]:
    """Validate partner-owned CUDA triangle columns for a prepared OptiX scene.

    The columns stay device-resident and are packed on GPU into RTDL's internal
    triangle and AABB layouts before OptiX GAS construction.
    """
    triangle_handoffs, timings = _partner_device_descriptor_columns(
        triangle_columns,
        _PARTNER_TRIANGLE_2D_COLUMNS,
        label="triangle",
    )
    _require_partner_device_triangle_column_layout(triangle_handoffs)
    descriptors = tuple(triangle_handoffs[name] for name in _PARTNER_TRIANGLE_2D_COLUMNS)
    return {
        "triangles": triangle_handoffs,
        "metadata": {
            "backend": "optix",
            "transfer_mode": "device_columns_gpu_pack_gas_build",
            "native_symbol": _OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLES_SYMBOL,
            "source_protocols": tuple(sorted({handoff.source_protocol for handoff in descriptors})),
            "source_devices": tuple(sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in descriptors})),
            "triangle_count": int(triangle_handoffs["ids"].shape[0]),
            "direct_device_pointer_observed": True,
            "direct_device_handoff_authorized": True,
            "true_zero_copy_authorized": False,
            "partner_tensor_handoff_authorized": True,
            "rt_core_speedup_claim_authorized": False,
            "partner_phase_timings_s": timings,
        },
    }


def pack_optix_ray_any_hit_2d_device_triangle_zero_copy_scene_inputs(
    triangle_columns: dict,
    triangle_aabbs,
) -> dict[str, object]:
    """Validate partner-owned CUDA triangle columns plus OptiX AABBs.

    This scene-preparation packet lets OptiX build its GAS directly from a
    partner-owned contiguous `float32[:, 6]` AABB buffer and lets the any-hit
    intersection shader read partner-owned triangle columns directly. The OptiX
    GAS output is still native acceleration state, so this authorizes
    triangle-scene zero-copy only, not a no-native-state claim.
    """
    triangle_handoffs, timings = _partner_device_descriptor_columns(
        triangle_columns,
        _PARTNER_TRIANGLE_2D_COLUMNS,
        label="triangle",
    )
    _require_partner_device_triangle_column_layout(triangle_handoffs)
    triangle_count = int(triangle_handoffs["ids"].shape[0])
    expected_device = (triangle_handoffs["ids"].device_type, triangle_handoffs["ids"].device_id)
    aabb_start = time.perf_counter()
    aabb_handoff = _partner.prepare_direct_device_pointer_handoff(triangle_aabbs, access="read")
    _require_partner_device_triangle_aabb_layout(
        aabb_handoff,
        triangle_count=triangle_count,
        expected_device=expected_device,
    )
    timings["aabb_descriptor_validation_s"] = time.perf_counter() - aabb_start
    descriptors = tuple(triangle_handoffs[name] for name in _PARTNER_TRIANGLE_2D_COLUMNS)
    all_descriptors = (*descriptors, aabb_handoff)
    return {
        "triangles": triangle_handoffs,
        "aabbs": aabb_handoff,
        "metadata": {
            "backend": "optix",
            "transfer_mode": "device_triangle_columns_aabb_zero_copy_gas_build",
            "native_symbol": _OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLE_COLUMNS_AABBS_SYMBOL,
            "source_protocols": tuple(sorted({handoff.source_protocol for handoff in all_descriptors})),
            "source_devices": tuple(sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in all_descriptors})),
            "triangle_count": triangle_count,
            "direct_device_pointer_observed": True,
            "direct_device_handoff_authorized": True,
            "triangle_scene_true_zero_copy_authorized": True,
            "true_zero_copy_authorized": False,
            "partner_tensor_handoff_authorized": True,
            "rt_core_speedup_claim_authorized": False,
            "native_acceleration_structure_required": True,
            "partner_phase_timings_s": timings,
        },
    }


def pack_optix_ray_any_hit_2d_device_output_flags(ray_columns: dict, output_flags) -> dict[str, object]:
    """Validate partner-owned CUDA rays plus a writable any-hit output vector."""
    ray_packet = pack_optix_ray_any_hit_2d_device_ray_inputs(ray_columns)
    ray_handoffs = ray_packet["rays"]
    ray_count = int(ray_packet["metadata"]["ray_count"])
    expected_device = (ray_handoffs["ids"].device_type, ray_handoffs["ids"].device_id)
    output_handoff = _partner.prepare_direct_device_pointer_handoff(output_flags, access="write")
    _require_partner_device_any_hit_output_layout(
        output_handoff,
        ray_count=ray_count,
        expected_device=expected_device,
    )
    return {
        "rays": ray_handoffs,
        "output": output_handoff,
        "metadata": {
            "backend": "optix",
            "transfer_mode": "device_ray_triangle_columns_output_flags_zero_copy",
            "native_symbol": _OPTIX_PARTNER_PREPARED_DEVICE_OUTPUT_FLAGS_SYMBOL,
            "source_protocols": tuple(
                sorted({handoff.source_protocol for handoff in (*ray_handoffs.values(), output_handoff)})
            ),
            "source_devices": tuple(
                sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in (*ray_handoffs.values(), output_handoff)})
            ),
            "ray_count": ray_count,
            "direct_device_pointer_observed": True,
            "direct_device_handoff_authorized": True,
            "ray_columns_true_zero_copy_authorized": True,
            "output_flags_true_zero_copy_authorized": True,
            "partner_tensor_handoff_authorized": True,
            "rt_core_speedup_claim_authorized": False,
        },
    }


def pack_optix_ray_any_hit_2d_device_witness_outputs(
    ray_columns: dict,
    witness_ray_ids,
    witness_primitive_ids,
) -> dict[str, object]:
    """Validate partner-owned CUDA output columns for first any-hit witnesses."""
    ray_packet = pack_optix_ray_any_hit_2d_device_ray_inputs(ray_columns)
    ray_handoffs = ray_packet["rays"]
    ray_count = int(ray_packet["metadata"]["ray_count"])
    expected_device = (ray_handoffs["ids"].device_type, ray_handoffs["ids"].device_id)
    witness_ray_handoff = _partner.prepare_direct_device_pointer_handoff(witness_ray_ids, access="write")
    witness_primitive_handoff = _partner.prepare_direct_device_pointer_handoff(witness_primitive_ids, access="write")
    _require_partner_device_any_hit_output_layout(
        witness_ray_handoff,
        ray_count=ray_count,
        expected_device=expected_device,
    )
    _require_partner_device_any_hit_output_layout(
        witness_primitive_handoff,
        ray_count=ray_count,
        expected_device=expected_device,
    )
    descriptors = (*ray_handoffs.values(), witness_ray_handoff, witness_primitive_handoff)
    return {
        "rays": ray_handoffs,
        "witness_ray_ids": witness_ray_handoff,
        "witness_primitive_ids": witness_primitive_handoff,
        "metadata": {
            "backend": "optix",
            "transfer_mode": "device_ray_triangle_columns_witness_rows_zero_copy",
            "native_symbol": _OPTIX_PARTNER_PREPARED_DEVICE_WITNESSES_SYMBOL,
            "source_protocols": tuple(sorted({handoff.source_protocol for handoff in descriptors})),
            "source_devices": tuple(
                sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in descriptors})
            ),
            "ray_count": ray_count,
            "witness_row_capacity": ray_count,
            "witness_no_hit_primitive_id": 0xFFFFFFFF,
            "witness_contract": "one first-hit witness row per ray; not all-hit collection",
            "direct_device_pointer_observed": True,
            "direct_device_handoff_authorized": True,
            "ray_columns_true_zero_copy_authorized": True,
            "witness_outputs_true_zero_copy_authorized": True,
            "partner_tensor_handoff_authorized": True,
            "rt_core_speedup_claim_authorized": False,
        },
    }


def pack_optix_ray_triangle_any_hit_2d_device_descriptor_inputs(
    ray_columns: dict,
    triangle_columns: dict,
) -> dict[str, object]:
    """Validate partner-owned CUDA columns for future direct OptiX execution.

    This packet contains device pointer descriptors only. It does not host-stage
    data, does not execute native code, and does not authorize zero-copy claims.
    """
    ray_handoffs, ray_timings = _partner_device_descriptor_columns(
        ray_columns,
        _PARTNER_RAY_2D_COLUMNS,
        label="rays",
    )
    triangle_handoffs, triangle_timings = _partner_device_descriptor_columns(
        triangle_columns,
        _PARTNER_TRIANGLE_2D_COLUMNS,
        label="triangles",
    )
    descriptors = (*ray_handoffs.values(), *triangle_handoffs.values())
    return {
        "rays": ray_handoffs,
        "triangles": triangle_handoffs,
        "metadata": {
            "backend": "optix",
            "transfer_mode": "device_descriptor_only",
            "native_symbol": _OPTIX_PARTNER_DEVICE_ANYHIT_SYMBOL,
            "source_protocols": tuple(sorted({handoff.source_protocol for handoff in descriptors})),
            "source_devices": tuple(sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in descriptors})),
            "ray_count": int(ray_handoffs["ids"].shape[0]),
            "triangle_count": int(triangle_handoffs["ids"].shape[0]),
            "direct_device_pointer_observed": True,
            "direct_device_handoff_authorized": False,
            "true_zero_copy_authorized": False,
            "partner_tensor_handoff_authorized": True,
            "rt_core_speedup_claim_authorized": False,
            "partner_phase_timings_s": {
                "descriptor_validation": float(
                    ray_timings["descriptor_validation_s"] + triangle_timings["descriptor_validation_s"]
                ),
            },
        },
    }


def run_optix_partner_ray_triangle_any_hit_2d_device_descriptors(
    ray_columns: dict,
    triangle_columns: dict,
) -> dict[str, object]:
    """Fail-closed direct-device OptiX partner entrypoint.

    The Python contract is now explicit, but the native backend must provide the
    matching device-column ABI before this function may execute. There is no
    silent host-stage fallback from this path.
    """
    packet = pack_optix_ray_triangle_any_hit_2d_device_descriptor_inputs(ray_columns, triangle_columns)
    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(lib, _OPTIX_PARTNER_DEVICE_ANYHIT_SYMBOL)
    if symbol is None:
        raise RuntimeError(
            "Loaded OptiX backend library does not export "
            f"{_OPTIX_PARTNER_DEVICE_ANYHIT_SYMBOL}. "
            "Direct device-pointer partner execution remains blocked; use the "
            "host-stage partner path or rebuild after the native device-column ABI lands."
        )
    raise RuntimeError(
        "Direct device-pointer partner execution ABI is detected but not yet wired "
        "through the Python safety contract."
    )


def pack_optix_ray_triangle_any_hit_2d_partner_inputs(ray_columns: dict, triangle_columns: dict) -> dict[str, object]:
    """Host-stage partner-owned ray/triangle columns into existing OptiX packets.

    This is the first v2.0 partner execution bridge. It intentionally reports
    `host_stage` transfer behavior and does not claim zero-copy.
    """
    ray_arrays, ray_descriptors, ray_timings = _partner_host_stage_columns(
        ray_columns,
        _PARTNER_RAY_2D_COLUMNS,
        label="rays",
    )
    triangle_arrays, triangle_descriptors, triangle_timings = _partner_host_stage_columns(
        triangle_columns,
        _PARTNER_TRIANGLE_2D_COLUMNS,
        label="triangles",
    )
    packet_start = time.perf_counter()
    packed_rays = pack_rays_2d_from_arrays(
        ray_arrays["ids"],
        ray_arrays["ox"],
        ray_arrays["oy"],
        ray_arrays["dx"],
        ray_arrays["dy"],
        ray_arrays["tmax"],
    )
    packed_triangles = pack_triangles_2d_from_arrays(
        triangle_arrays["ids"],
        triangle_arrays["x0"],
        triangle_arrays["y0"],
        triangle_arrays["x1"],
        triangle_arrays["y1"],
        triangle_arrays["x2"],
        triangle_arrays["y2"],
    )
    packet_packing_seconds = time.perf_counter() - packet_start
    source_protocols = tuple(
        sorted(
            {
                descriptor.source_protocol
                for descriptor in (*ray_descriptors.values(), *triangle_descriptors.values())
            }
        )
    )
    source_devices = tuple(
        sorted(
            {
                f"{descriptor.device_type}:{descriptor.device_id}"
                for descriptor in (*ray_descriptors.values(), *triangle_descriptors.values())
            }
        )
    )
    return {
        "rays": packed_rays,
        "triangles": packed_triangles,
        "metadata": {
            "transfer_mode": "host_stage",
            "source_protocols": source_protocols,
            "source_devices": source_devices,
            "ray_count": int(packed_rays.count),
            "triangle_count": int(packed_triangles.count),
            "true_zero_copy_authorized": False,
            "partner_tensor_handoff_authorized": True,
            "rt_core_speedup_claim_authorized": False,
            "partner_phase_timings_s": {
                "descriptor_validation": float(
                    ray_timings["descriptor_validation_s"] + triangle_timings["descriptor_validation_s"]
                ),
                "framework_to_host_staging": float(
                    ray_timings["framework_to_host_staging_s"] + triangle_timings["framework_to_host_staging_s"]
                ),
                "packet_packing": float(packet_packing_seconds),
            },
        },
    }


def run_optix_partner_ray_triangle_any_hit_2d(ray_columns: dict, triangle_columns: dict) -> dict[str, object]:
    """Run prepared OptiX any-hit count from partner-owned 2-D column tensors.

    First-wave v2.0 behavior is explicit host staging: partner tensors are
    validated through `RtdlTensorDescriptor`, copied to host arrays as needed,
    packed through the existing app-agnostic OptiX ABI, and then executed.
    """
    prepared_inputs = pack_optix_ray_triangle_any_hit_2d_partner_inputs(ray_columns, triangle_columns)
    prepare_start = time.perf_counter()
    scene = prepare_optix_ray_triangle_any_hit_2d(prepared_inputs["triangles"])
    optix_prepare_seconds = time.perf_counter() - prepare_start
    optix_count_seconds = 0.0
    try:
        count_start = time.perf_counter()
        hit_count = scene.count(prepared_inputs["rays"])
        optix_count_seconds = time.perf_counter() - count_start
    finally:
        scene.close()
    timings = get_last_phase_timings()
    partner_timings = dict(prepared_inputs["metadata"]["partner_phase_timings_s"])
    partner_timings.update({
        "optix_prepare": float(optix_prepare_seconds),
        "optix_count_and_scalar_copyback": float(optix_count_seconds),
    })
    return {
        **prepared_inputs["metadata"],
        "hit_count": int(hit_count),
        "partner_phase_timings_s": partner_timings,
        "phase_timings": timings,
    }


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
    status = lib.rtdl_optix_run_segment_pair_intersection(
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
    status = lib.rtdl_optix_run_point_primitive_anyhit_packet(
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
    status = lib.rtdl_optix_run_shape_pair_relation_flags(
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


@dataclass(frozen=True)
class _DeviceTriangleScene2D:
    count: int
    dimension: int = 2


class PreparedOptixRayTriangleAnyHit2D:
    """Prepared OptiX 2-D any-hit scene with scalar hit-count query output."""

    def __init__(self, triangles):
        packed = triangles if isinstance(triangles, PackedTriangles) else pack_triangles(triangles, dimension=2)
        if packed.dimension != 2:
            raise ValueError("prepare_optix_ray_triangle_any_hit_2d requires 2-D triangles")
        self._packed_triangles = packed
        self._handle = ctypes.c_void_p()
        self._closed = False
        self._triangle_scene_true_zero_copy = False
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

    def count_device_rays(self, ray_columns: dict) -> int:
        """Count any-hit intersections from partner-owned CUDA ray columns.

        The ray columns are read directly by the OptiX raygen from partner
        device pointers. The prepared triangle scene is still the existing OptiX
        prepared-scene path, so this method authorizes ray-column true zero-copy
        wording only, not whole-primitive true zero-copy.
        """
        if self._closed:
            raise RuntimeError("prepared OptiX any-hit handle is closed")
        packet = pack_optix_ray_any_hit_2d_device_ray_inputs(ray_columns)
        if packet["metadata"]["ray_count"] == 0 or self._packed_triangles.count == 0:
            return 0

        lib = _load_optix_library()
        count_symbol = _find_optional_backend_symbol(lib, _OPTIX_PARTNER_PREPARED_DEVICE_RAYS_SYMBOL)
        if count_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{_OPTIX_PARTNER_PREPARED_DEVICE_RAYS_SYMBOL}. "
                "Direct device-ray partner execution remains blocked; rebuild the "
                "OptiX backend after the native device-ray ABI lands."
            )
        hit_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        rays = packet["rays"]
        status = count_symbol(
            self._handle,
            ctypes.c_void_p(rays["ids"].data_ptr),
            ctypes.c_void_p(rays["ox"].data_ptr),
            ctypes.c_void_p(rays["oy"].data_ptr),
            ctypes.c_void_p(rays["dx"].data_ptr),
            ctypes.c_void_p(rays["dy"].data_ptr),
            ctypes.c_void_p(rays["tmax"].data_ptr),
            packet["metadata"]["ray_count"],
            ctypes.byref(hit_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(hit_count.value)

    def write_device_any_hit_flags(self, ray_columns: dict, output_flags) -> dict[str, object]:
        """Write one any-hit flag per partner-owned CUDA ray into partner output."""
        if self._closed:
            raise RuntimeError("prepared OptiX any-hit handle is closed")
        if not getattr(self, "_triangle_scene_true_zero_copy", False):
            raise RuntimeError(
                "write_device_any_hit_flags requires a triangle-column zero-copy prepared scene"
            )
        packet = pack_optix_ray_any_hit_2d_device_output_flags(ray_columns, output_flags)

        lib = _load_optix_library()
        write_symbol = _find_optional_backend_symbol(lib, _OPTIX_PARTNER_PREPARED_DEVICE_OUTPUT_FLAGS_SYMBOL)
        if write_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{_OPTIX_PARTNER_PREPARED_DEVICE_OUTPUT_FLAGS_SYMBOL}. "
                "Partner-owned any-hit output remains blocked; rebuild the "
                "OptiX backend after the native output ABI lands."
            )
        rays = packet["rays"]
        error = ctypes.create_string_buffer(4096)
        status = write_symbol(
            self._handle,
            ctypes.c_void_p(rays["ids"].data_ptr),
            ctypes.c_void_p(rays["ox"].data_ptr),
            ctypes.c_void_p(rays["oy"].data_ptr),
            ctypes.c_void_p(rays["dx"].data_ptr),
            ctypes.c_void_p(rays["dy"].data_ptr),
            ctypes.c_void_p(rays["tmax"].data_ptr),
            packet["metadata"]["ray_count"],
            ctypes.c_void_p(packet["output"].data_ptr),
            error,
            len(error),
        )
        _check_status(status, error)
        metadata = dict(packet["metadata"])
        metadata["triangle_scene_true_zero_copy_authorized"] = bool(
            getattr(self, "_triangle_scene_true_zero_copy", False)
        )
        metadata["true_zero_copy_authorized"] = bool(
            metadata["ray_columns_true_zero_copy_authorized"]
            and metadata["output_flags_true_zero_copy_authorized"]
            and metadata["triangle_scene_true_zero_copy_authorized"]
        )
        metadata["v2_0_release_authorized"] = False
        return {"metadata": metadata}

    def write_device_any_hit_witnesses(
        self,
        ray_columns: dict,
        witness_ray_ids,
        witness_primitive_ids,
    ) -> dict[str, object]:
        """Write one first-hit witness row per partner-owned CUDA ray."""
        if self._closed:
            raise RuntimeError("prepared OptiX any-hit handle is closed")
        if not getattr(self, "_triangle_scene_true_zero_copy", False):
            raise RuntimeError(
                "write_device_any_hit_witnesses requires a triangle-column zero-copy prepared scene"
            )
        packet = pack_optix_ray_any_hit_2d_device_witness_outputs(
            ray_columns,
            witness_ray_ids,
            witness_primitive_ids,
        )

        lib = _load_optix_library()
        write_symbol = _find_optional_backend_symbol(lib, _OPTIX_PARTNER_PREPARED_DEVICE_WITNESSES_SYMBOL)
        if write_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{_OPTIX_PARTNER_PREPARED_DEVICE_WITNESSES_SYMBOL}. "
                "Partner-owned any-hit witness output remains blocked; rebuild the "
                "OptiX backend after the native witness ABI lands."
            )
        rays = packet["rays"]
        error = ctypes.create_string_buffer(4096)
        status = write_symbol(
            self._handle,
            ctypes.c_void_p(rays["ids"].data_ptr),
            ctypes.c_void_p(rays["ox"].data_ptr),
            ctypes.c_void_p(rays["oy"].data_ptr),
            ctypes.c_void_p(rays["dx"].data_ptr),
            ctypes.c_void_p(rays["dy"].data_ptr),
            ctypes.c_void_p(rays["tmax"].data_ptr),
            packet["metadata"]["ray_count"],
            ctypes.c_void_p(packet["witness_ray_ids"].data_ptr),
            ctypes.c_void_p(packet["witness_primitive_ids"].data_ptr),
            error,
            len(error),
        )
        _check_status(status, error)
        metadata = dict(packet["metadata"])
        metadata["triangle_scene_true_zero_copy_authorized"] = bool(
            getattr(self, "_triangle_scene_true_zero_copy", False)
        )
        metadata["true_zero_copy_authorized"] = bool(
            metadata["ray_columns_true_zero_copy_authorized"]
            and metadata["witness_outputs_true_zero_copy_authorized"]
            and metadata["triangle_scene_true_zero_copy_authorized"]
        )
        metadata["v2_0_release_authorized"] = False
        return {"metadata": metadata}

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
        pose_flags_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed")
        if pose_flags_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed. "
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

    def group_flags_packed(self, rays: "OptixRay2DBuffer", group_indices, *, group_count: int) -> tuple[bool, ...]:
        try:
            return self.pose_flags_packed(rays, group_indices, pose_count=group_count)
        except (RuntimeError, ValueError) as exc:
            _raise_group_index_error(exc)

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
            "rtdl_optix_group_flags_prepared_ray_anyhit_2d_prepared_indices",
        )
        if pose_flags_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_group_flags_prepared_ray_anyhit_2d_prepared_indices. "
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

    def group_flags_prepared_indices(
        self,
        rays: "OptixRay2DBuffer",
        group_indices: "OptixGroupIndexBuffer",
        *,
        group_count: int,
    ) -> tuple[bool, ...]:
        try:
            return self.pose_flags_prepared_indices(rays, group_indices, pose_count=group_count)
        except (RuntimeError, ValueError) as exc:
            _raise_group_index_error(exc)

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
            "rtdl_optix_count_groups_prepared_ray_anyhit_2d_prepared_indices",
        )
        if count_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_count_groups_prepared_ray_anyhit_2d_prepared_indices. "
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

    def group_count_prepared_indices(
        self,
        rays: "OptixRay2DBuffer",
        group_indices: "OptixGroupIndexBuffer",
        *,
        group_count: int,
    ) -> int:
        try:
            return self.pose_count_prepared_indices(rays, group_indices, pose_count=group_count)
        except (RuntimeError, ValueError) as exc:
            _raise_group_index_error(exc)

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


def prepare_optix_ray_triangle_any_hit_2d_device_triangles(
    triangle_columns: dict,
) -> PreparedOptixRayTriangleAnyHit2D:
    packet = pack_optix_ray_any_hit_2d_device_triangle_inputs(triangle_columns)
    prepared = PreparedOptixRayTriangleAnyHit2D.__new__(PreparedOptixRayTriangleAnyHit2D)
    prepared._packed_triangles = _DeviceTriangleScene2D(packet["metadata"]["triangle_count"])
    prepared._handle = ctypes.c_void_p()
    prepared._closed = False
    prepared._triangle_scene_true_zero_copy = False
    if packet["metadata"]["triangle_count"] == 0:
        return prepared

    lib = _load_optix_library()
    prepare_symbol = _find_optional_backend_symbol(lib, _OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLES_SYMBOL)
    if prepare_symbol is None:
        raise RuntimeError(
            "Loaded OptiX backend library does not export "
            f"{_OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLES_SYMBOL}. "
            "Direct device-triangle partner scene preparation remains blocked; "
            "rebuild the OptiX backend after the native device-triangle ABI lands."
        )
    triangles = packet["triangles"]
    error = ctypes.create_string_buffer(4096)
    status = prepare_symbol(
        ctypes.c_void_p(triangles["ids"].data_ptr),
        ctypes.c_void_p(triangles["x0"].data_ptr),
        ctypes.c_void_p(triangles["y0"].data_ptr),
        ctypes.c_void_p(triangles["x1"].data_ptr),
        ctypes.c_void_p(triangles["y1"].data_ptr),
        ctypes.c_void_p(triangles["x2"].data_ptr),
        ctypes.c_void_p(triangles["y2"].data_ptr),
        packet["metadata"]["triangle_count"],
        ctypes.byref(prepared._handle),
        error,
        len(error),
    )
    _check_status(status, error)
    return prepared


def prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
    triangle_columns: dict,
    triangle_aabbs,
) -> PreparedOptixRayTriangleAnyHit2D:
    packet = pack_optix_ray_any_hit_2d_device_triangle_zero_copy_scene_inputs(
        triangle_columns,
        triangle_aabbs,
    )
    prepared = PreparedOptixRayTriangleAnyHit2D.__new__(PreparedOptixRayTriangleAnyHit2D)
    prepared._packed_triangles = _DeviceTriangleScene2D(packet["metadata"]["triangle_count"])
    prepared._handle = ctypes.c_void_p()
    prepared._closed = False
    prepared._triangle_scene_true_zero_copy = bool(packet["metadata"]["triangle_scene_true_zero_copy_authorized"])
    if packet["metadata"]["triangle_count"] == 0:
        return prepared

    lib = _load_optix_library()
    prepare_symbol = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLE_COLUMNS_AABBS_SYMBOL,
    )
    if prepare_symbol is None:
        raise RuntimeError(
            "Loaded OptiX backend library does not export "
            f"{_OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLE_COLUMNS_AABBS_SYMBOL}. "
            "Triangle-scene zero-copy partner preparation remains blocked; "
            "rebuild the OptiX backend after the native borrowed-AABB ABI lands."
        )
    triangles = packet["triangles"]
    error = ctypes.create_string_buffer(4096)
    status = prepare_symbol(
        ctypes.c_void_p(triangles["ids"].data_ptr),
        ctypes.c_void_p(triangles["x0"].data_ptr),
        ctypes.c_void_p(triangles["y0"].data_ptr),
        ctypes.c_void_p(triangles["x1"].data_ptr),
        ctypes.c_void_p(triangles["y1"].data_ptr),
        ctypes.c_void_p(triangles["x2"].data_ptr),
        ctypes.c_void_p(triangles["y2"].data_ptr),
        ctypes.c_void_p(packet["aabbs"].data_ptr),
        packet["metadata"]["triangle_count"],
        ctypes.byref(prepared._handle),
        error,
        len(error),
    )
    _check_status(status, error)
    return prepared


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
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_group_indices_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_prepare_group_indices_2d. "
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
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_group_indices_2d")
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


OptixGroupIndexBuffer = OptixPoseIndexBuffer


def prepare_optix_group_indices_2d(group_indices) -> OptixGroupIndexBuffer:
    return OptixGroupIndexBuffer(group_indices)


def _raise_group_index_error(exc: Exception):
    message = str(exc)
    message = message.replace("pose_indices", "group_indices")
    message = message.replace("pose-index", "group-index")
    message = message.replace("pose index", "group index")
    message = message.replace("pose_count", "group_count")
    message = message.replace("poses", "groups")
    raise type(exc)(message) from exc


def _call_segment_polygon_hitcount_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    segments = packed[compiled.candidates.left.name]
    polygons = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_optix_run_segment_shape_hitcount(
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
    status = lib.rtdl_optix_run_segment_shape_anyhit_rows(
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
        "rtdl_optix_run_segment_shape_anyhit_rows_native_bounded",
    )
    if symbol is None:
        raise ValueError(
            "loaded OptiX backend does not export "
            "rtdl_optix_run_segment_shape_anyhit_rows_native_bounded; "
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


def collect_polygon_pair_candidates_bounded_optix(
    left_polygons,
    right_polygons,
    *,
    candidate_capacity: int,
) -> dict[str, object]:
    """Collect bounded polygon-pair candidates through the native OptiX ABI.

    The ABI is intentionally app-name-free: it returns normalized candidate
    pair ids plus fail-closed overflow metadata. Score reduction remains a
    separate primitive and must only run when complete coverage is true.
    """
    if candidate_capacity < 0:
        raise ValueError("candidate_capacity must be non-negative")
    packed_left = pack_polygons(records=left_polygons)
    packed_right = pack_polygons(records=right_polygons)
    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_collect_shape_pair_candidates_bounded",
    )
    if symbol is None:
        raise ValueError(
            "loaded OptiX backend does not export "
            "rtdl_optix_collect_shape_pair_candidates_bounded; "
            "rebuild the OptiX backend from current main"
        )

    candidate_array = (
        (_RtdlPolygonPairCandidate * candidate_capacity)()
        if candidate_capacity
        else None
    )
    emitted_count = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        packed_left.refs,
        packed_left.polygon_count,
        packed_left.vertices_xy,
        packed_left.vertex_xy_count,
        packed_right.refs,
        packed_right.polygon_count,
        packed_right.vertices_xy,
        packed_right.vertex_xy_count,
        candidate_array,
        candidate_capacity,
        ctypes.byref(emitted_count),
        ctypes.byref(overflowed),
        error,
        len(error),
    )
    _check_status(status, error)

    emitted = int(emitted_count.value)
    if int(overflowed.value) != 0:
        raise RuntimeError(
            "native bounded OptiX polygon-pair candidate collection overflowed "
            f"capacity {candidate_capacity}; emitted at least {emitted}; "
            "failure_mode=fail_closed_overflow"
        )
    if emitted > int(candidate_capacity):
        raise RuntimeError(
            "native bounded OptiX polygon-pair candidate collection reported "
            f"emitted_count {emitted} beyond capacity {candidate_capacity}; "
            "failure_mode=fail_closed_overflow"
        )

    native_candidate_pairs = tuple(
        (
            int(candidate_array[index].left_polygon_id),
            int(candidate_array[index].right_polygon_id),
        )
        for index in range(emitted)
    )
    row_buffer = collect_native_i64_rows_with_backend_symbol(
        native_candidate_pairs,
        capacity=int(candidate_capacity),
        row_width=2,
        backend="optix",
        library=lib,
        symbol_name="rtdl_optix_collect_k_bounded_i64",
        candidate_source_symbol="rtdl_optix_collect_shape_pair_candidates_bounded",
    )
    result = {
        "primitive": "COLLECT_K_BOUNDED",
        "backend": "optix",
        "app_generic": row_buffer["app_generic"],
        "native_i64_adapter": row_buffer["native_i64_adapter"],
        "native_source_symbol": row_buffer["native_source_symbol"],
        "source_rows_are_row_major_i64": row_buffer["source_rows_are_row_major_i64"],
        "binary_symbol_validation_present": row_buffer["binary_symbol_validation_present"],
        "native_generic_symbol": row_buffer["native_generic_symbol"],
        "native_candidate_source_symbol": row_buffer["native_candidate_source_symbol"],
        "candidate_pairs": row_buffer["candidate_id_rows"],
        "candidate_id_rows": row_buffer["candidate_id_rows"],
        "capacity": int(candidate_capacity),
        "valid_count": row_buffer["valid_count"],
        "emitted_count": row_buffer["emitted_count"],
        "native_emitted_count": emitted,
        "overflowed": False,
        "complete_candidate_coverage": True,
        "failure_mode": "fail_closed_overflow",
        "overflow_policy": row_buffer["overflow_policy"],
        "result_layout": "bounded_candidate_pair_ids",
        "generic_result_layout": row_buffer["result_layout"],
        "ordering_policy": row_buffer["ordering_policy"],
        "duplicate_policy": row_buffer["duplicate_policy"],
        "partial_result_on_overflow_allowed": row_buffer[
            "partial_result_on_overflow_allowed"
        ],
        "score_or_reduction_after_overflow_allowed": row_buffer[
            "score_or_reduction_after_overflow_allowed"
        ],
        "claim_boundary": (
            "native OptiX bounded polygon-pair candidate collection only; "
            "candidate rows route through the built generic native i64 symbol; "
            "Jaccard score reduction, "
            "stable promotion, and whole-app speedup require separate evidence"
        ),
    }
    return validate_collect_k_bounded_result(result, row_width=2, backend="optix")


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
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_k_closest_hits_3d")
        if symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export rtdl_optix_run_k_closest_hits_3d; "
                "rebuild the OptiX backend from current main"
            )
        status = symbol(
            query_points.records, query_points.count,
            search_points.records, search_points.count,
            k,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    else:
        status = lib.rtdl_optix_run_k_closest_hits(
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
    symbol = _require_optix_graph_symbol(lib, "rtdl_optix_run_frontier_edge_traversal_packet")
    frontier = packed[compiled.candidates.left.name]
    graph = packed[compiled.candidates.right.name]
    visited_name = str(compiled.refine_op.predicate.options["visited_input"])
    visited = packed[visited_name]
    rows_ptr = ctypes.POINTER(_RtdlBfsExpandRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        graph.row_offsets, graph.row_offset_count,
        graph.column_indices, graph.field_index_count,
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
    symbol = _require_optix_graph_symbol(lib, "rtdl_optix_run_edge_neighbor_intersection_packet")
    seeds = packed[compiled.candidates.left.name]
    graph = packed[compiled.candidates.right.name]
    rows_ptr = ctypes.POINTER(_RtdlTriangleRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        graph.row_offsets, graph.row_offset_count,
        graph.column_indices, graph.field_index_count,
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

    _require_backend_symbol(lib, "rtdl_optix_run_segment_pair_intersection").argtypes = [
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_segment_pair_intersection.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_optix_run_point_primitive_anyhit_packet").argtypes = [
        ctypes.POINTER(_RtdlPoint),      ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlPipRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_point_primitive_anyhit_packet.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_optix_run_shape_pair_relation_flags").argtypes = [
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlOverlayRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_shape_pair_relation_flags.restype = ctypes.c_int

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
    optional_prepare_anyhit2d_device_triangles = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLES_SYMBOL,
    )
    if optional_prepare_anyhit2d_device_triangles is not None:
        optional_prepare_anyhit2d_device_triangles.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_anyhit2d_device_triangles.restype = ctypes.c_int
    optional_prepare_anyhit2d_device_triangle_columns_aabbs = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLE_COLUMNS_AABBS_SYMBOL,
    )
    if optional_prepare_anyhit2d_device_triangle_columns_aabbs is not None:
        optional_prepare_anyhit2d_device_triangle_columns_aabbs.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_anyhit2d_device_triangle_columns_aabbs.restype = ctypes.c_int
    optional_count_anyhit2d_device_rays = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_DEVICE_RAYS_SYMBOL,
    )
    if optional_count_anyhit2d_device_rays is not None:
        optional_count_anyhit2d_device_rays.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_count_anyhit2d_device_rays.restype = ctypes.c_int
    optional_write_anyhit2d_device_flags = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_DEVICE_OUTPUT_FLAGS_SYMBOL,
    )
    if optional_write_anyhit2d_device_flags is not None:
        optional_write_anyhit2d_device_flags.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_write_anyhit2d_device_flags.restype = ctypes.c_int
    optional_write_anyhit2d_device_witnesses = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_DEVICE_WITNESSES_SYMBOL,
    )
    if optional_write_anyhit2d_device_witnesses is not None:
        optional_write_anyhit2d_device_witnesses.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_write_anyhit2d_device_witnesses.restype = ctypes.c_int
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
        "rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed",
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
    optional_prepare_pose_indices2d = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_group_indices_2d")
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
        "rtdl_optix_group_flags_prepared_ray_anyhit_2d_prepared_indices",
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
        "rtdl_optix_count_groups_prepared_ray_anyhit_2d_prepared_indices",
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
    optional_destroy_pose_indices2d = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_group_indices_2d")
    if optional_destroy_pose_indices2d is not None:
        optional_destroy_pose_indices2d.argtypes = [ctypes.c_void_p]
        optional_destroy_pose_indices2d.restype = None
    optional_destroy_rays2d = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_rays_2d")
    if optional_destroy_rays2d is not None:
        optional_destroy_rays2d.argtypes = [ctypes.c_void_p]
        optional_destroy_rays2d.restype = None

    _require_backend_symbol(lib, "rtdl_optix_run_segment_shape_hitcount").argtypes = [
        ctypes.POINTER(_RtdlSegment),    ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_segment_shape_hitcount.restype = ctypes.c_int

    optional_prepare_segpoly_hitcount = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_segment_shape_hitcount_2d",
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
        "rtdl_optix_run_prepared_segment_shape_hitcount_2d",
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
        "rtdl_optix_count_prepared_segment_shape_hitcount_at_least_2d",
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
        "rtdl_optix_aggregate_prepared_segment_shape_hitcount_2d",
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
        "rtdl_optix_destroy_prepared_segment_shape_hitcount_2d",
    )
    if optional_destroy_prepared_segpoly_hitcount is not None:
        optional_destroy_prepared_segpoly_hitcount.argtypes = [ctypes.c_void_p]
        optional_destroy_prepared_segpoly_hitcount.restype = None

    _require_backend_symbol(lib, "rtdl_optix_run_segment_shape_anyhit_rows").argtypes = [
        ctypes.POINTER(_RtdlSegment),    ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_segment_shape_anyhit_rows.restype = ctypes.c_int

    optional_segment_polygon_anyhit_rows_native_bounded = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_segment_shape_anyhit_rows_native_bounded",
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

    optional_polygon_pair_candidates_bounded = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_collect_shape_pair_candidates_bounded",
    )
    if optional_polygon_pair_candidates_bounded is not None:
        optional_polygon_pair_candidates_bounded.argtypes = [
            ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
            ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
            ctypes.POINTER(_RtdlPolygonPairCandidate),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_polygon_pair_candidates_bounded.restype = ctypes.c_int

    optional_prepare_segment_polygon_anyhit_rows = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_segment_shape_anyhit_rows_2d",
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
        "rtdl_optix_run_prepared_segment_shape_anyhit_rows_2d",
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
        "rtdl_optix_destroy_prepared_segment_shape_anyhit_rows_2d",
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

    _require_backend_symbol(lib, "rtdl_optix_run_k_closest_hits").argtypes = [
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_optix_run_k_closest_hits.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_k_closest_hits_3d")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_frontier_edge_traversal_packet")
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
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_edge_neighbor_intersection_packet")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_create")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_create_from_columns")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlPayloadField),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_destroy")
    if symbol is not None:
        symbol.argtypes = [ctypes.c_void_p]
        symbol.restype = None

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_multi_predicate_scan")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_multi_predicate_scan_count")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_grouped_reduction_count")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_grouped_reduction_sum")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_compact_summary_batch")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlDbCompactSummaryRequest),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbCompactSummaryResult)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_compact_summary_results_destroy")
    if symbol is not None:
        symbol.argtypes = [ctypes.POINTER(_RtdlDbCompactSummaryResult), ctypes.c_size_t]
        symbol.restype = None

    symbol = _find_optional_backend_symbol(lib, OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL)
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_uint64,
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_uint64,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
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
    if "unsupported toolchain" in msg:
        msg += (
            " RTDL could not load generated PTX with the installed CUDA driver. "
            "Check that the CUDA toolkit/NVRTC used to build/run RTDL is supported by the driver; "
            "if using a newer toolkit with an older datacenter driver, put the CUDA compat library path first in "
            "LD_LIBRARY_PATH or rebuild/run with a compatible CUDA toolkit. You may also set "
            "RTDL_OPTIX_PTX_ARCH=compute_XX to target the GPU architecture explicitly."
        )
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
            field_index_count=len(normalized.column_indices),
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
