"""vulkan_runtime.py — Vulkan KHR ray-tracing backend for rtdl.

Public API mirrors optix_runtime.py (just substitute "vulkan" for "optix"):
  run_vulkan(kernel_fn_or_compiled, **inputs)        → tuple[dict, ...]
  prepare_vulkan(kernel_fn_or_compiled)               → PreparedVulkanKernel
  vulkan_version()                                    → tuple[int, int, int]

Current Vulkan-native workload surface:
  segment_intersection, point_in_polygon, overlay_compose,
  ray_triangle_hit_count, segment_polygon_hitcount,
  segment_polygon_anyhit_rows, point_nearest_segment,
  fixed_radius_neighbors, bounded_knn_rows, knn_rows

Additional accepted public Vulkan surface:
  polygon_pair_overlap_area_rows, polygon_set_jaccard
  via documented native CPU/oracle fallback, not Vulkan-native kernels

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
from .runtime import _identity_cache_token
from .runtime import _normalize_records
from .runtime import _resolve_kernel
from .runtime import _validate_kernel_for_cpu
from .graph_reference import CSRGraph
from .graph_reference import EdgeSeed
from .graph_reference import FrontierVertex
from .graph_reference import normalize_edge_set
from .graph_reference import normalize_frontier
from .graph_reference import normalize_vertex_set


_PREPARED_CACHE_MAX_ENTRIES = 8
_prepared_vulkan_execution_cache: OrderedDict[tuple[object, ...], "PreparedVulkanExecution"] = OrderedDict()
_DB_MAX_ROWS_PER_JOB = 1_000_000


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


class _RtdlSegmentPolygonAnyHitRow(ctypes.Structure):
    _fields_ = [
        ("segment_id", ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
    ]


class _RtdlFixedRadiusNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id",    ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance",    ctypes.c_double),
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
    _free_on_close: bool = True
    _owner: object | None = None

    def close(self) -> None:
        if not self._closed:
            if self._free_on_close:
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
        if self.predicate_name in {"conjunctive_scan", "grouped_count", "grouped_sum"}:
            normalized_inputs = {
                name: _normalize_records(name, self.expected_inputs[name].geometry.name, payload)
                for name, payload in inputs.items()
            }
            return _prepare_db_vulkan_execution(self.compiled, normalized_inputs, self.library)
        packed = {
            name: _pack_for_geometry(self.expected_inputs[name], payload)
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
            "segment_polygon_anyhit_rows": _call_segment_polygon_anyhit_rows_vulkan_packed,
            "point_nearest_segment":  _call_point_nearest_segment_vulkan_packed,
            "fixed_radius_neighbors": _call_fixed_radius_neighbors_vulkan_packed,
            "bounded_knn_rows": _call_bounded_knn_rows_vulkan_packed,
            "knn_rows": _call_knn_rows_vulkan_packed,
            "bfs_discover": _call_bfs_expand_vulkan_packed,
            "triangle_match": _call_triangle_probe_vulkan_packed,
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


def clear_vulkan_prepared_cache() -> None:
    _prepared_vulkan_execution_cache.clear()


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

    if compiled.refine_op.predicate.name in {
        "conjunctive_scan",
        "grouped_count",
        "grouped_sum",
    }:
        normalized_inputs = {
            name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
            for name, payload in inputs.items()
        }
        return _run_db_vulkan(compiled, normalized_inputs, _load_vulkan_library(), result_mode=result_mode)

    # Current accepted honesty boundary:
    # segment_polygon_hitcount is a closed workload family, but not yet an
    # accepted Vulkan-native traversal path. The direct Vulkan implementation
    # is not relied on for release-grade correctness on county-derived cases, so
    # the public run path falls back to the native CPU oracle here.
    if compiled.refine_op.predicate.name == "segment_polygon_hitcount":
        if result_mode == "raw":
            raise ValueError(
                "Vulkan raw mode is not supported for segment_polygon_hitcount "
                "while the backend uses the native CPU oracle fallback"
            )
        from .runtime import run_cpu

        return run_cpu(compiled, **inputs)

    # Current accepted honesty boundary:
    # the Jaccard workloads are closed on Python/native CPU today, but not as
    # Vulkan-native kernels. The public Vulkan run surface accepts them through
    # the native CPU/oracle implementation so they can participate in Linux
    # consistency and scale audits without overclaiming backend maturity.
    if compiled.refine_op.predicate.name in {
        "polygon_pair_overlap_area_rows",
        "polygon_set_jaccard",
    }:
        if result_mode == "raw":
            raise ValueError(
                "Vulkan raw mode is not supported for the Jaccard workloads "
                "while the backend uses the native CPU oracle fallback"
            )
        from .runtime import run_cpu

        return run_cpu(compiled, **inputs)

    prepared = _get_or_bind_prepared_vulkan_execution(compiled, expected_inputs, inputs)
    return prepared.run_raw() if result_mode == "raw" else prepared.run()


def _run_db_vulkan(compiled: CompiledKernel, normalized_inputs, lib, *, result_mode: str):
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name == "conjunctive_scan":
        symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_conjunctive_scan")
        if symbol is None:
            raise ValueError("current Vulkan backend does not yet export DB conjunctive_scan support")
        predicates_name = compiled.candidates.left.name
        table_name = compiled.candidates.right.name
        table_rows = normalized_inputs[table_name]
        if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
            raise ValueError("first-wave Vulkan DB lowering supports at most 1000000 rows per RT job")
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
        rows = VulkanRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbRowIdRow,
            field_names=("row_id",),
        )
        if result_mode == "raw":
            return rows
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()

    query_name = compiled.candidates.left.name
    table_name = compiled.candidates.right.name
    table_rows = normalized_inputs[table_name]
    if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
        raise ValueError("first-wave Vulkan DB lowering supports at most 1000000 rows per RT job")
    query = normalized_inputs[query_name]
    group_keys = tuple(query.group_keys)
    if len(group_keys) != 1:
        raise ValueError("first-wave Vulkan DB lowering supports exactly one group key")
    encoded_rows, encoded_predicates, reverse_maps = _encode_db_text_fields(
        table_rows,
        query.predicates,
        extra_fields=group_keys,
    )
    fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
    clauses_array = _encode_db_clauses(encoded_predicates)
    group_key_field = group_keys[0].encode("utf-8")

    if predicate_name == "grouped_count":
        symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_grouped_count")
        if symbol is None:
            raise ValueError("current Vulkan backend does not yet export DB grouped_count support")
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
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
        rows = VulkanRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbGroupedCountRow,
            field_names=("group_key", "count"),
        )
        if result_mode == "raw":
            return rows
        try:
            decoded = []
            for row in rows.to_dict_rows():
                decoded.append({
                    group_keys[0]: _decode_db_group_key(reverse_maps[group_keys[0]], row["group_key"]),
                    "count": row["count"],
                })
            return tuple(decoded)
        finally:
            rows.close()

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_grouped_sum")
    if symbol is None:
        raise ValueError("current Vulkan backend does not yet export DB grouped_sum support")
    rows_ptr = ctypes.POINTER(_RtdlDbGroupedSumRow)()
    row_count_out = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
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
    rows = VulkanRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count_out.value,
        row_type=_RtdlDbGroupedSumRow,
        field_names=("group_key", "sum"),
    )
    if result_mode == "raw":
        return rows
    try:
        decoded = []
        for row in rows.to_dict_rows():
            decoded.append({
                group_keys[0]: _decode_db_group_key(reverse_maps[group_keys[0]], row["group_key"]),
                "sum": row["sum"],
            })
        return tuple(decoded)
    finally:
        rows.close()


@dataclass(frozen=True)
class PreparedVulkanDbExecution:
    compiled: CompiledKernel
    library: object
    predicate_name: str
    dataset: object
    clauses_array: object
    group_key_name: str | None = None
    group_key_field: bytes | None = None
    reverse_map: object | None = None
    value_field: bytes | None = None

    def run_raw(self) -> VulkanRowView:
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
                    "sum": rows.rows_ptr[index].sum,
                }
                for index in range(rows.row_count)
            )
        finally:
            rows.close()


class VulkanPreparedDbDataset:
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
            if not hasattr(self.library, "rtdl_vulkan_db_dataset_create_columnar"):
                raise RuntimeError(
                    "loaded Vulkan backend does not export rtdl_vulkan_db_dataset_create_columnar; "
                    "rebuild the Vulkan backend from the current checkout"
                )
            status = self.library.rtdl_vulkan_db_dataset_create_columnar(
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
            status = self.library.rtdl_vulkan_db_dataset_create(
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
            self.library.rtdl_vulkan_db_dataset_destroy(self.handle)
        self._closed = True

    def conjunctive_scan(self, clauses_array) -> VulkanRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbRowIdRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_vulkan_db_dataset_conjunctive_scan(
            self.handle,
            clauses_array,
            ctypes.c_size_t(len(clauses_array)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
        _check_status(status, error)
        return VulkanRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbRowIdRow,
            field_names=("row_id",),
        )

    def grouped_count(self, clauses_array, group_key_field: bytes) -> VulkanRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_vulkan_db_dataset_grouped_count(
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
        return VulkanRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count_out.value,
            row_type=_RtdlDbGroupedCountRow,
            field_names=("group_key", "count"),
        )

    def grouped_sum(self, clauses_array, group_key_field: bytes, value_field: bytes) -> VulkanRowView:
        rows_ptr = ctypes.POINTER(_RtdlDbGroupedSumRow)()
        row_count_out = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_vulkan_db_dataset_grouped_sum(
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
        return VulkanRowView(
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


class PreparedVulkanDbDataset:
    def __init__(self, table_rows, *, primary_fields=(), transfer: str = "row"):
        if transfer not in {"row", "columnar"}:
            raise ValueError("Vulkan DB dataset transfer must be 'row' or 'columnar'")
        rows = normalize_denorm_table(table_rows)
        if len(rows) > _DB_MAX_ROWS_PER_JOB:
            raise ValueError("first-wave Vulkan DB lowering supports at most 1000000 rows per RT job")
        encoded_rows, self._field_maps, self._reverse_maps = _encode_all_db_text_columns(rows)
        if transfer == "columnar":
            columns_array, row_count, keepalive = _encode_db_table_columnar(encoded_rows)
            fields_array = None
            row_values_array = None
        else:
            fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
            columns_array = None
            keepalive = ()
        self._dataset = VulkanPreparedDbDataset(
            _load_vulkan_library(),
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
            raise ValueError("first-wave Vulkan DB grouped kernels support exactly one group key")
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
            raise ValueError("first-wave Vulkan DB grouped kernels support exactly one group key")
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
            value = encode_map[clause.value]
            value_hi = encode_map[clause.value_hi] if clause.value_hi is not None else None
            encoded.append(PredicateClause(field=clause.field, op=clause.op, value=value, value_hi=value_hi))
        return tuple(encoded)

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def prepare_vulkan_db_dataset(table_rows, *, primary_fields=(), transfer: str = "row") -> PreparedVulkanDbDataset:
    return PreparedVulkanDbDataset(table_rows, primary_fields=primary_fields, transfer=transfer)


def _db_primary_fields_from_clauses(clauses) -> tuple[str, ...]:
    fields = []
    for clause in clauses:
        name = str(clause.field)
        if name not in fields:
            fields.append(name)
        if len(fields) == 3:
            break
    return tuple(fields)


def _prepare_db_vulkan_execution(compiled: CompiledKernel, normalized_inputs, lib) -> PreparedVulkanDbExecution:
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name == "conjunctive_scan":
        predicates_name = compiled.candidates.left.name
        table_name = compiled.candidates.right.name
        table_rows = normalized_inputs[table_name]
        if len(table_rows) > _DB_MAX_ROWS_PER_JOB:
            raise ValueError("first-wave Vulkan DB lowering supports at most 1000000 rows per RT job")
        predicates = normalized_inputs[predicates_name]
        columns_array, row_count, keepalive = _encode_db_table_columnar(table_rows)
        clauses_array = _encode_db_clauses(predicates.clauses)
        dataset = VulkanPreparedDbDataset(
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
        return PreparedVulkanDbExecution(
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
        raise ValueError("first-wave Vulkan DB lowering supports at most 1000000 rows per RT job")
    query = normalized_inputs[query_name]
    group_keys = tuple(query.group_keys)
    if len(group_keys) != 1:
        raise ValueError("first-wave Vulkan DB lowering supports exactly one group key")
    extra_fields = list(group_keys)
    if predicate_name == "grouped_sum" and query.value_field:
        extra_fields.append(query.value_field)
    encoded_rows, encoded_predicates, reverse_maps = _encode_db_text_fields(
        table_rows,
        query.predicates,
        extra_fields=tuple(extra_fields),
    )
    columns_array, row_count, keepalive = _encode_db_table_columnar(encoded_rows)
    clauses_array = _encode_db_clauses(encoded_predicates)
    dataset = VulkanPreparedDbDataset(
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
    return PreparedVulkanDbExecution(
        compiled=compiled,
        library=lib,
        predicate_name=predicate_name,
        dataset=dataset,
        clauses_array=clauses_array,
        group_key_name=group_keys[0],
        group_key_field=group_keys[0].encode("utf-8"),
        reverse_map=reverse_maps.get(group_keys[0]),
        value_field=query.value_field.encode("utf-8") if predicate_name == "grouped_sum" else None,
    )


def _get_or_bind_prepared_vulkan_execution(compiled: CompiledKernel, expected_inputs, inputs) -> PreparedVulkanExecution:
    cache_key = _prepared_execution_cache_key(compiled, expected_inputs, inputs)
    if cache_key is None:
        return prepare_vulkan(compiled).bind(**inputs)
    cached = _prepared_vulkan_execution_cache.get(cache_key)
    if cached is not None:
        _prepared_vulkan_execution_cache.move_to_end(cache_key)
        return cached
    prepared = prepare_vulkan(compiled).bind(**inputs)
    _prepared_vulkan_execution_cache[cache_key] = prepared
    if len(_prepared_vulkan_execution_cache) > _PREPARED_CACHE_MAX_ENTRIES:
        _prepared_vulkan_execution_cache.popitem(last=False)
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
    result_mode = compiled.refine_op.predicate.options.get("result_mode", "full_matrix")
    if result_mode not in {"full_matrix", "positive_hits"}:
        raise ValueError("the Vulkan PIP backend supports only result_mode='full_matrix' or 'positive_hits'")
    points   = packed[compiled.candidates.left.name]
    polygons = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlPipRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_vulkan_run_pip(
        points.records, points.count,
        polygons.refs, polygons.polygon_count,
        polygons.vertices_xy, polygons.vertex_xy_count,
        1 if result_mode == "positive_hits" else 0,
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
    if rays.dimension != triangles.dimension:
        raise ValueError("Vulkan ray_triangle_hit_count requires rays and triangles to have the same dimension")
    if rays.dimension == 3:
        symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_ray_hitcount_3d")
        if symbol is None:
            raise RuntimeError(
                "Loaded Vulkan backend library does not export rtdl_vulkan_run_ray_hitcount_3d. "
                "Rebuild it with 'make build-vulkan' from current main."
            )
        status = symbol(
            rays.records, rays.count,
            triangles.records, triangles.count,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    else:
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


def _call_segment_polygon_anyhit_rows_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    segments = packed[compiled.candidates.left.name]
    polygons = packed[compiled.candidates.right.name]
    rows_ptr  = ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    status = lib.rtdl_vulkan_run_segment_polygon_anyhit_rows(
        segments.records, segments.count,
        polygons.refs, polygons.polygon_count,
        polygons.vertices_xy, polygons.vertex_xy_count,
        ctypes.byref(rows_ptr), ctypes.byref(row_count),
        error, len(error))
    _check_status(status, error)
    return VulkanRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlSegmentPolygonAnyHitRow,
        field_names=("segment_id", "polygon_id"))


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


def _call_fixed_radius_neighbors_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    query_points  = packed[compiled.candidates.left.name]
    search_points = packed[compiled.candidates.right.name]
    radius = float(compiled.refine_op.predicate.options["radius"])
    k_max  = int(compiled.refine_op.predicate.options["k_max"])
    rows_ptr  = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
    row_count = ctypes.c_size_t()
    error     = ctypes.create_string_buffer(4096)
    if query_points.dimension == 3:
        symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_fixed_radius_neighbors_3d")
        if symbol is None:
            raise RuntimeError(
                "loaded Vulkan backend library does not export rtdl_vulkan_run_fixed_radius_neighbors_3d; "
                "rebuild the Vulkan backend from current main"
            )
        status = symbol(
            query_points.records, query_points.count,
            search_points.records, search_points.count,
            radius, k_max,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    else:
        status = lib.rtdl_vulkan_run_fixed_radius_neighbors(
            query_points.records, query_points.count,
            search_points.records, search_points.count,
            radius, k_max,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    _check_status(status, error)
    return VulkanRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlFixedRadiusNeighborRow,
        field_names=("query_id", "neighbor_id", "distance"))


def _call_bounded_knn_rows_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    fixed_radius_rows = _call_fixed_radius_neighbors_vulkan_packed(compiled, packed, lib)
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


def _call_knn_rows_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    query_points = packed[compiled.candidates.left.name]
    search_points = packed[compiled.candidates.right.name]
    k = int(compiled.refine_op.predicate.options["k"])
    rows_ptr = ctypes.POINTER(_RtdlKnnNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if query_points.dimension == 3:
        symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_knn_rows_3d")
        if symbol is None:
            raise RuntimeError(
                "loaded Vulkan backend library does not export rtdl_vulkan_run_knn_rows_3d; "
                "rebuild the Vulkan backend from current main"
            )
        status = symbol(
            query_points.records, query_points.count,
            search_points.records, search_points.count,
            k,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    else:
        status = lib.rtdl_vulkan_run_knn_rows(
            query_points.records, query_points.count,
            search_points.records, search_points.count,
            k,
            ctypes.byref(rows_ptr), ctypes.byref(row_count),
            error, len(error))
    _check_status(status, error)
    return VulkanRowView(
        library=lib, rows_ptr=rows_ptr,
        row_count=row_count.value, row_type=_RtdlKnnNeighborRow,
        field_names=("query_id", "neighbor_id", "distance", "neighbor_rank"))


def _call_bfs_expand_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    symbol = _require_vulkan_graph_symbol(lib, "rtdl_vulkan_run_bfs_expand")
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
    return VulkanRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlBfsExpandRow,
        field_names=("src_vertex", "dst_vertex", "level"),
    )


def _call_triangle_probe_vulkan_packed(compiled: CompiledKernel, packed, lib) -> VulkanRowView:
    symbol = _require_vulkan_graph_symbol(lib, "rtdl_vulkan_run_triangle_probe")
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
    return VulkanRowView(
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
def _load_vulkan_library():
    lib_path = _find_vulkan_library()
    lib = ctypes.CDLL(str(lib_path))
    lib._rtdl_library_path = str(lib_path)
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
    _require_backend_symbol(lib, "rtdl_vulkan_get_version").argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.rtdl_vulkan_get_version.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_vulkan_free_rows").argtypes = [ctypes.c_void_p]
    lib.rtdl_vulkan_free_rows.restype  = None

    _require_backend_symbol(lib, "rtdl_vulkan_run_lsi").argtypes = [
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_lsi.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_vulkan_run_pip").argtypes = [
        ctypes.POINTER(_RtdlPoint),      ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlPipRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_pip.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_vulkan_run_overlay").argtypes = [
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlOverlayRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_overlay.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_vulkan_run_ray_hitcount").argtypes = [
        ctypes.POINTER(_RtdlRay2D),      ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle),   ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_ray_hitcount.restype = ctypes.c_int
    optional_ray3d = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_ray_hitcount_3d")
    if optional_ray3d is not None:
        optional_ray3d.argtypes = [
            ctypes.POINTER(_RtdlRay3D), ctypes.c_size_t,
            ctypes.POINTER(_RtdlTriangle3D), ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_ray3d.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_vulkan_run_segment_polygon_hitcount").argtypes = [
        ctypes.POINTER(_RtdlSegment),    ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_segment_polygon_hitcount.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_vulkan_run_segment_polygon_anyhit_rows").argtypes = [
        ctypes.POINTER(_RtdlSegment),    ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_segment_polygon_anyhit_rows.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_vulkan_run_point_nearest_segment").argtypes = [
        ctypes.POINTER(_RtdlPoint),   ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPointNearestSegmentRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_point_nearest_segment.restype = ctypes.c_int

    _require_backend_symbol(lib, "rtdl_vulkan_run_fixed_radius_neighbors").argtypes = [
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_fixed_radius_neighbors.restype = ctypes.c_int
    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_fixed_radius_neighbors_3d")
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

    _require_backend_symbol(lib, "rtdl_vulkan_run_knn_rows").argtypes = [
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p, ctypes.c_size_t,
    ]
    lib.rtdl_vulkan_run_knn_rows.restype = ctypes.c_int
    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_knn_rows_3d")
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
    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_bfs_expand")
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
    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_triangle_probe")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_conjunctive_scan")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDbField), ctypes.c_size_t,
            ctypes.c_void_p, ctypes.c_size_t,
            ctypes.c_void_p, ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbRowIdRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_grouped_count")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDbField), ctypes.c_size_t,
            ctypes.c_void_p, ctypes.c_size_t,
            ctypes.c_void_p, ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_run_grouped_sum")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDbField), ctypes.c_size_t,
            ctypes.c_void_p, ctypes.c_size_t,
            ctypes.c_void_p, ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedSumRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_db_dataset_create")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_db_dataset_create_columnar")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_db_dataset_destroy")
    if symbol is not None:
        symbol.argtypes = [ctypes.c_void_p]
        symbol.restype = None

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_db_dataset_conjunctive_scan")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_db_dataset_grouped_count")
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

    symbol = _find_optional_backend_symbol(lib, "rtdl_vulkan_db_dataset_grouped_sum")
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
            f"Loaded Vulkan library {path!r} is missing required export {symbol_name!r}. "
            "This usually means the shared library is stale or was built from an older RTDL checkout. "
            "Rebuild it with 'make build-vulkan' or point RTDL_VULKAN_LIB at a rebuilt library."
        ) from exc


def _find_optional_backend_symbol(lib, symbol_name: str):
    try:
        return getattr(lib, symbol_name)
    except AttributeError:
        return None


def _require_vulkan_graph_symbol(lib, symbol_name: str):
    symbol = _find_optional_backend_symbol(lib, symbol_name)
    if symbol is None:
        path = getattr(lib, "_rtdl_library_path", "<unknown>")
        raise RuntimeError(
            f"Loaded Vulkan library {path!r} does not export {symbol_name!r}. "
            "Rebuild it with 'make build-vulkan' from the current checkout before running RT graph kernels on Vulkan."
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


def _geometry_layout_dimension(geometry_input) -> int:
    layout = geometry_input.layout
    field_names = set(layout.field_names())
    if layout.name.endswith("3D") or any(name in field_names for name in ("z0", "z1", "z2", "oz", "dz")):
        return 3
    return 2


def _pack_for_geometry(geometry_input, payload):
    from .embree_runtime import (
        pack_segments, pack_points, pack_polygons,
        pack_triangles, pack_rays,
    )
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
    raise ValueError(f"unsupported geometry type for Vulkan backend: {geometry_name!r}")


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
    raise ValueError(f"unsupported geometry type for Vulkan backend: {geometry_name!r}")


def _make_owned_row_view(row_type, rows, field_names: tuple[str, ...]) -> VulkanRowView:
    array = (row_type * len(rows))(*rows)
    rows_ptr = ctypes.cast(array, ctypes.POINTER(row_type))
    return VulkanRowView(
        library=None,
        rows_ptr=rows_ptr,
        row_count=len(rows),
        row_type=row_type,
        field_names=field_names,
        _free_on_close=False,
        _owner=array,
    )
