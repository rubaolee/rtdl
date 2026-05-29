"""optix_runtime.py — NVIDIA/OptiX backend for rtdl.

Public API mirrors embree_runtime.py:
  run_optix(kernel_fn_or_compiled, **inputs)       → tuple[dict, ...]
  prepare_optix(kernel_fn_or_compiled)              → PreparedOptixKernel
  optix_version()                                   → tuple[int, int, int]

Current OptiX-native workload surface:
  segment_intersection, point_in_polygon, overlay_compose,
  ray_triangle_hit_count, segment_polygon_hitcount,
  segment_polygon_anyhit_rows, point_nearest_segment,
  ray_segment_group_count_2d,
  fixed_radius_neighbors, point_group_nearest_witness,
  point_group_nearest_max_distance_reduction,
  bounded_knn_rows, knn_rows

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
from typing import Iterable, Mapping

from .embree_runtime import _RtdlSegment
from .embree_runtime import _RtdlPoint
from .embree_runtime import _RtdlPoint3D
from .embree_runtime import _RtdlPolygonRef
from .embree_runtime import _RtdlTriangle
from .embree_runtime import _RtdlTriangle3D
from .embree_runtime import _RtdlRay2D
from .embree_runtime import _RtdlRay3D
from .embree_runtime import _RtdlRayTriangleHitStreamRow
from .embree_runtime import _RtdlSegment3D
from .embree_runtime import _RtdlFrontierVertex
from .embree_runtime import _RtdlBfsExpandRow
from .embree_runtime import _RtdlEdgeSeed
from .embree_runtime import _RtdlTriangleRow
from .embree_runtime import _RtdlPayloadField
from .embree_runtime import _RtdlAggregateFrontierSource2D
from .embree_runtime import _RtdlAggregateFrontierNode2D
from .embree_runtime import _UINT64_MAX
from .embree_runtime import _aggregate_frontier_capacity_upper_bound
from .embree_runtime import _encode_db_table_columnar
from .embree_runtime import _encode_db_column_mapping_columnar_with_metadata
from .embree_runtime import _encode_all_db_text_column_mapping
from .embree_runtime import _columnar_record_set_to_column_mapping
from .oracle_runtime import _decode_db_group_key
from .oracle_runtime import _DB_KIND_FLOAT64
from .oracle_runtime import _DB_KIND_INT64
from .oracle_runtime import _RtdlColumnField
from .oracle_runtime import _RtdlGroupedCountRow
from .oracle_runtime import _RtdlColumnRowIdRow
from .oracle_runtime import _RtdlDbField  # legacy compatibility marker
from .oracle_runtime import _RtdlDbGroupedCountRow  # legacy compatibility marker
from .oracle_runtime import _RtdlDbRowIdRow  # legacy compatibility marker
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
from .embree_runtime import PreparedGroupedSegmentQuery3D
from .embree_runtime import _pack_group_offsets_u32
from .embree_runtime import _pack_segments_3d_from_endpoints
from .embree_runtime import _pack_static_triangles_3d
from .embree_runtime import _encode_all_db_text_columns
from .embree_runtime import _pack_points_columns_numpy
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
from .columnar_partner import DeviceColumnDescriptor
from .columnar_partner import PartnerResidentColumnarRecordSet
from .columnar_partner import PARTNER_RESIDENT_COLUMNAR_NATIVE_EXECUTION_STATUS
from .columnar_partner import PARTNER_RESIDENT_COLUMNAR_REQUIRED_OPTIX_SYMBOL
from .columnar_partner import plan_partner_resident_columnar_native_execution
from .columnar_partner import prepare_partner_resident_columnar_record_set
from .grouped_reduction import GroupedReductionCapacityStatus
from .grouped_reduction import GroupedReductionSpec
from .aggregate_tree_reference import AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT
from .aggregate_tree_reference import AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT
from .aggregate_tree_reference import AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE
from .aggregate_tree_reference import AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA
from .aggregate_tree_reference import AGGREGATE_FRONTIER_COLLECT_OVERFLOW_POLICY
from .aggregate_tree_reference import AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE
from .aggregate_tree_reference import AggregateFrontierOverflowError
from .aggregate_tree_reference import _tree_node_rows
from .aggregate_tree_reference import normalize_weighted_point_rows


_PREPARED_CACHE_MAX_ENTRIES = 8
_prepared_optix_execution_cache: OrderedDict[tuple[object, ...], "PreparedOptixExecution"] = OrderedDict()
_DB_MAX_ROWS_PER_JOB = 1_000_000
OPTIX_PARTNER_RESIDENT_COLUMNAR_DEVICE_SYMBOL = PARTNER_RESIDENT_COLUMNAR_REQUIRED_OPTIX_SYMBOL
OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_SYMBOL = "rtdl_optix_columnar_device_payload_grouped_count_i64"
OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_SYMBOL = "rtdl_optix_columnar_device_payload_grouped_sum_i64"
OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_WITH_CAPACITY_SYMBOL = (
    "rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity"
)
OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_WITH_CAPACITY_SYMBOL = (
    "rtdl_optix_columnar_device_payload_grouped_sum_i64_with_capacity"
)
OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MIN_I64_WITH_CAPACITY_SYMBOL = (
    "rtdl_optix_columnar_device_payload_grouped_min_i64_with_capacity"
)
OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MAX_I64_WITH_CAPACITY_SYMBOL = (
    "rtdl_optix_columnar_device_payload_grouped_max_i64_with_capacity"
)
OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL = (
    "rtdl_optix_columnar_device_payload_grouped_sum_count_i64_with_capacity"
)
OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_STATS_I64_WITH_CAPACITY_SYMBOL = (
    "rtdl_optix_columnar_device_payload_grouped_stats_i64_with_capacity"
)
OPTIX_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL = (
    "rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction"
)
OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_SYMBOL = "rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream"
OPTIX_PRIMITIVE_GROUPED_I64_PAYLOAD_3D_CREATE_SYMBOL = (
    "rtdl_optix_primitive_grouped_i64_payload_3d_create"
)
OPTIX_PREPARED_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL = (
    "rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction"
)
OPTIX_RAY_BATCH_3D_CREATE_DEVICE_RAYS_SYMBOL = "rtdl_optix_ray_batch_3d_create_device_rays"
OPTIX_RAY_BATCH_PREPARED_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL = (
    "rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction"
)
OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTIONS = (
    "count",
    "sum",
    "min",
    "max",
    "sum_count",
    "stats",
)
_OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTION_OPERATIONS = {
    "count": "group_count",
    "sum": "group_sum_i64",
    "min": "group_min_i64",
    "max": "group_max_i64",
    "sum_count": "group_sum_count_i64",
    "stats": "group_stats_i64",
}
_OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTION_SYMBOLS = {
    "count": OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_WITH_CAPACITY_SYMBOL,
    "sum": OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_WITH_CAPACITY_SYMBOL,
    "min": OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MIN_I64_WITH_CAPACITY_SYMBOL,
    "max": OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MAX_I64_WITH_CAPACITY_SYMBOL,
    "sum_count": OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL,
    "stats": OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_STATS_I64_WITH_CAPACITY_SYMBOL,
}
OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL = "rtdl_optix_collect_k_bounded_i64_device"
OPTIX_COLLECT_K_BOUNDED_I64_HOST_SYMBOL = "rtdl_optix_collect_k_bounded_i64"
OPTIX_AABB_INDEX_POINT_CONTAINS = 1
OPTIX_AABB_INDEX_RANGE_CONTAINS = 2
OPTIX_AABB_INDEX_RANGE_INTERSECTS = 3
OPTIX_AABB_INDEX_SUPPORTED_OPERATIONS = ("point_contains", "range_contains", "range_intersects")
_OPTIX_AABB_INDEX_OPERATION_CODES = {
    "point_contains": OPTIX_AABB_INDEX_POINT_CONTAINS,
    "range_contains": OPTIX_AABB_INDEX_RANGE_CONTAINS,
    "range_intersects": OPTIX_AABB_INDEX_RANGE_INTERSECTS,
}


class _RtdlAabb2D(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("min_x", ctypes.c_double),
        ("min_y", ctypes.c_double),
        ("max_x", ctypes.c_double),
        ("max_y", ctypes.c_double),
    ]


class _RtdlAabbPairRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("indexed_id", ctypes.c_uint32),
    ]


@dataclass(frozen=True)
class PackedAabbs2D:
    records: object
    count: int


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


def collect_aggregate_frontier_2d_optix(
    source_points: Iterable[object],
    tree_nodes: Iterable[object],
    *,
    theta: float,
    max_rows_per_source: int | None = None,
    max_total_rows: int | None = None,
    deduplicate_fallback_targets: bool = True,
) -> dict[str, object]:
    """Collect aggregate-frontier rows through the app-name-free OptiX ABI."""

    if max_rows_per_source is not None and int(max_rows_per_source) < 0:
        raise ValueError("max_rows_per_source must be non-negative when provided")
    if max_total_rows is not None and int(max_total_rows) < 0:
        raise ValueError("max_total_rows must be non-negative when provided")
    theta_value = float(theta)
    if theta_value <= 0.0:
        raise ValueError("theta must be positive")

    sources = normalize_weighted_point_rows(source_points)
    nodes = _tree_node_rows(tree_nodes)
    row_width = len(AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA)
    row_capacity = (
        _aggregate_frontier_capacity_upper_bound(len(sources), len(nodes))
        if max_total_rows is None
        else int(max_total_rows)
    )
    per_source_capacity = _UINT64_MAX if max_rows_per_source is None else int(max_rows_per_source)

    source_array = (_RtdlAggregateFrontierSource2D * len(sources))(
        *(_RtdlAggregateFrontierSource2D(int(source.id), float(source.x), float(source.y)) for source in sources)
    )
    node_array = (_RtdlAggregateFrontierNode2D * len(nodes))(
        *(
            _RtdlAggregateFrontierNode2D(
                int(node.id),
                float(node.cx),
                float(node.cy),
                float(node.half_size),
                int(node.depth),
                int(node.dfs_index),
                -1 if node.resume_index is None else int(node.resume_index),
                1 if node.is_leaf else 0,
            )
            for node in nodes
        )
    )
    child_offsets = [0]
    child_ids: list[int] = []
    member_offsets = [0]
    member_ids: list[int] = []
    for node in nodes:
        child_ids.extend(int(child_id) for child_id in node.child_ids)
        child_offsets.append(len(child_ids))
        member_ids.extend(int(member_id) for member_id in node.member_ids)
        member_offsets.append(len(member_ids))

    child_offsets_array = (ctypes.c_uint64 * len(child_offsets))(*child_offsets)
    child_ids_array = (ctypes.c_int64 * len(child_ids))(*child_ids) if child_ids else None
    member_offsets_array = (ctypes.c_uint64 * len(member_offsets))(*member_offsets)
    member_ids_array = (ctypes.c_int64 * len(member_ids))(*member_ids) if member_ids else None
    row_offsets_array = (ctypes.c_uint64 * (len(sources) + 1))()
    frontier_array = (
        (ctypes.c_int64 * (int(row_capacity) * row_width))()
        if int(row_capacity) > 0
        else None
    )
    emitted_count = ctypes.c_uint64()
    attempted_count = ctypes.c_uint64()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)

    library = _load_optix_library()
    symbol = _find_optional_backend_symbol(library, "rtdl_optix_collect_aggregate_frontier_2d")
    if symbol is None:
        raise ValueError(
            "loaded OptiX backend does not export "
            "rtdl_optix_collect_aggregate_frontier_2d; "
            "rebuild the OptiX backend from current main"
        )
    status = symbol(
        source_array,
        len(sources),
        node_array,
        len(nodes),
        child_offsets_array,
        child_ids_array,
        member_offsets_array,
        member_ids_array,
        ctypes.c_double(theta_value),
        ctypes.c_uint64(per_source_capacity),
        ctypes.c_uint64(row_capacity),
        ctypes.c_uint32(1 if deduplicate_fallback_targets else 0),
        frontier_array,
        row_offsets_array,
        ctypes.byref(emitted_count),
        ctypes.byref(attempted_count),
        ctypes.byref(overflowed),
        error,
        len(error),
    )
    _check_status(status, error)
    if int(overflowed.value) != 0:
        raise AggregateFrontierOverflowError(
            "AGGREGATE_FRONTIER_COLLECT_2D OptiX native overflowed capacity; "
            f"attempted {int(attempted_count.value)}; "
            "failure_mode=fail_closed_overflow; partial_result_returned=False"
        )

    emitted = int(emitted_count.value)
    if emitted > row_capacity:
        raise RuntimeError("OptiX aggregate-frontier emitted_count exceeded row capacity")
    flat_rows = [int(frontier_array[index]) for index in range(emitted * row_width)] if emitted else []
    frontier_i64_rows = tuple(
        tuple(flat_rows[index:index + row_width])
        for index in range(0, len(flat_rows), row_width)
    )
    row_offsets = tuple(int(row_offsets_array[index]) for index in range(len(sources) + 1))
    frontier_rows = []
    aggregate_count = 0
    exact_count = 0
    for row in frontier_i64_rows:
        source_id, kind_code, item_id, owner_aggregate_id, dfs_index, resume_index, metadata_flags = row
        if kind_code == 1:
            aggregate_count += 1
            frontier_kind = "aggregate"
            aggregate_id = item_id
            target_id = None
        elif kind_code == 2:
            exact_count += 1
            frontier_kind = "exact"
            aggregate_id = owner_aggregate_id
            target_id = item_id
        else:
            raise RuntimeError(f"OptiX aggregate-frontier returned unknown kind code {kind_code}")
        frontier_rows.append(
            {
                "source_id": source_id,
                "frontier_kind": frontier_kind,
                "frontier_kind_code": kind_code,
                "item_id": item_id,
                "aggregate_id": aggregate_id,
                "target_id": target_id,
                "owner_aggregate_id": owner_aggregate_id,
                "dfs_index": dfs_index,
                "resume_index": None if resume_index < 0 else resume_index,
                "metadata_flags": metadata_flags,
            }
        )
    return {
        "frontier_rows": tuple(frontier_rows),
        "frontier_i64_rows": frontier_i64_rows,
        "source_ids": tuple(int(source.id) for source in sources),
        "row_offsets": row_offsets,
        "row_schema": AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA,
        "summary": {
            "source_count": len(sources),
            "tree_node_count": len(nodes),
            "frontier_row_count": emitted,
            "accepted_aggregate_row_count": aggregate_count,
            "fallback_exact_row_count": exact_count,
            "max_rows_per_source": None if max_rows_per_source is None else int(max_rows_per_source),
            "max_total_rows": None if max_total_rows is None else int(max_total_rows),
            "overflowed": False,
            "partial_result_returned": False,
            "app_math_embedded": False,
        },
        "metadata": {
            "primitive": AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE,
            "contract": AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
            "native_abi_contract": AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT,
            "backend": "optix",
            "native_symbol": "rtdl_optix_collect_aggregate_frontier_2d",
            "native_execution": True,
            "native_engine_app_specific": False,
            "app_math_embedded": False,
            "force_law_embedded": False,
            "row_schema": AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA,
            "metadata_flags_semantics": {
                AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE: "no flags set",
            },
            "overflow_policy": AGGREGATE_FRONTIER_COLLECT_OVERFLOW_POLICY,
            "claim_boundary": (
                "OptiX native aggregate-frontier row collection only. This is "
                "not an RT-core timing claim and not app math."
            ),
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


class _RtdlSegmentFirstHitRow(ctypes.Structure):
    _fields_ = [
        ("probe_id",     ctypes.c_uint32),
        ("primitive_id", ctypes.c_uint32),
        ("hit_x",        ctypes.c_double),
        ("hit_y",        ctypes.c_double),
        ("hit_t",        ctypes.c_double),
    ]


class _RtdlPipRow(ctypes.Structure):
    _fields_ = [
        ("point_id",   ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
        ("contains",   ctypes.c_uint32),
    ]


class _RtdlClosedShapeRef(ctypes.Structure):
    _fields_ = [
        ("id",            ctypes.c_uint32),
        ("vertex_offset", ctypes.c_uint32),
        ("vertex_count",  ctypes.c_uint32),
    ]


class _RtdlPointClosedShapeMembershipRow(ctypes.Structure):
    _fields_ = [
        ("point_id",   ctypes.c_uint32),
        ("shape_id",   ctypes.c_uint32),
        ("membership", ctypes.c_uint32),
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


class _RtdlRayClosestHitRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("triangle_id", ctypes.c_uint32),
        ("t", ctypes.c_double),
    ]


class _RtdlRaySegmentGroupCountRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("group_id", ctypes.c_uint32),
        ("hit_count", ctypes.c_uint32),
        ("parity", ctypes.c_uint32),
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


class _RtdlFixedRadiusNeighborSummary(ctypes.Structure):
    _fields_ = [
        ("count", ctypes.c_size_t),
        ("min_distance", ctypes.c_double),
        ("max_distance", ctypes.c_double),
        ("sum_distance", ctypes.c_double),
    ]


class _RtdlFixedRadiusCountRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_count", ctypes.c_uint32),
        ("threshold_reached", ctypes.c_uint32),
    ]


class _RtdlPointGroupBounds2D(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("point_offset", ctypes.c_uint32),
        ("point_count", ctypes.c_uint32),
        ("min_x", ctypes.c_double),
        ("min_y", ctypes.c_double),
        ("max_x", ctypes.c_double),
        ("max_y", ctypes.c_double),
    ]


class _RtdlKnnNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
        ("neighbor_rank", ctypes.c_uint32),
    ]


class _RtdlFixedRadiusRankedNeighborSummary(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_count", ctypes.c_uint32),
        ("nearest_neighbor_id", ctypes.c_uint32),
        ("kth_neighbor_id", ctypes.c_uint32),
        ("nearest_distance", ctypes.c_double),
        ("kth_distance", ctypes.c_double),
        ("sum_distance", ctypes.c_double),
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


class _RtdlDbGroupedSumCountRow(ctypes.Structure):
    _fields_ = [
        ("group_key", ctypes.c_int64),
        ("sum", ctypes.c_int64),
        ("count", ctypes.c_int64),
    ]


class _RtdlDbGroupedStatsRow(ctypes.Structure):
    _fields_ = [
        ("group_key", ctypes.c_int64),
        ("count", ctypes.c_int64),
        ("sum", ctypes.c_int64),
        ("min", ctypes.c_int64),
        ("max", ctypes.c_int64),
    ]


_RtdlGroupedSumRow = _RtdlDbGroupedSumRow
_RtdlGroupedSumCountRow = _RtdlDbGroupedSumCountRow
_RtdlGroupedStatsRow = _RtdlDbGroupedStatsRow


class _RtdlDevicePayloadField(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("kind", ctypes.c_uint32),
        ("dtype", ctypes.c_uint32),
        ("device_type", ctypes.c_uint32),
        ("device_id", ctypes.c_uint32),
        ("element_count", ctypes.c_size_t),
        ("stride_bytes", ctypes.c_size_t),
        ("device_ptr", ctypes.c_uint64),
    ]


_DB_COMPACT_SUMMARY_OP_SCAN_COUNT = 1
_DB_COMPACT_SUMMARY_OP_GROUPED_COUNT = 2
_DB_COMPACT_SUMMARY_OP_GROUPED_SUM = 3
_COLUMN_COMPACT_SUMMARY_OP_SCAN_COUNT = _DB_COMPACT_SUMMARY_OP_SCAN_COUNT
_COLUMN_COMPACT_SUMMARY_OP_GROUPED_COUNT = _DB_COMPACT_SUMMARY_OP_GROUPED_COUNT
_COLUMN_COMPACT_SUMMARY_OP_GROUPED_SUM = _DB_COMPACT_SUMMARY_OP_GROUPED_SUM
_DEVICE_PAYLOAD_DEVICE_CUDA = 1
_DEVICE_PAYLOAD_DTYPE_INT64 = 1
_DEVICE_PAYLOAD_DTYPE_UINT32 = 2
_DEVICE_PAYLOAD_DTYPE_FLOAT64 = 3


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
        ("count_rows", ctypes.POINTER(_RtdlGroupedCountRow)),
        ("count_row_count", ctypes.c_size_t),
        ("sum_rows", ctypes.POINTER(_RtdlGroupedSumRow)),
        ("sum_row_count", ctypes.c_size_t),
        ("traversal", ctypes.c_double),
        ("bitset_copyback", ctypes.c_double),
        ("exact_filter", ctypes.c_double),
        ("output_pack", ctypes.c_double),
        ("raw_candidate_count", ctypes.c_size_t),
        ("emitted_count", ctypes.c_size_t),
    ]


_RtdlColumnCompactSummaryRequest = _RtdlDbCompactSummaryRequest
_RtdlColumnCompactSummaryResult = _RtdlDbCompactSummaryResult


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
        "ray_triangle_closest_hit",
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
            return _prepare_columnar_optix_execution(self.compiled, normalized_inputs, self.library)
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
            "ray_triangle_closest_hit": _call_ray_closest_hit_optix_packed,
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


@dataclass
class PreparedOptixSegmentPairIntersection:
    library: object
    prepared_handle: ctypes.c_void_p
    _closed: bool = False

    def run_raw(self, left_segments) -> OptixRowView:
        if self._closed:
            raise RuntimeError("prepared OptiX segment-pair handle is closed")
        left = _pack_for_geometry("segments", left_segments)
        rows_ptr = ctypes.POINTER(_RtdlLsiRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_optix_run_prepared_segment_pair_intersection(
            self.prepared_handle,
            left.records,
            left.count,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlLsiRow,
            field_names=("left_id", "right_id", "intersection_point_x", "intersection_point_y"),
        )

    def run(self, left_segments) -> tuple:
        rows = self.run_raw(left_segments)
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()

    def count(self, left_segments) -> int:
        if self._closed:
            raise RuntimeError("prepared OptiX segment-pair handle is closed")
        left = _pack_for_geometry("segments", left_segments)
        count_symbol = _find_optional_backend_symbol(
            self.library,
            "rtdl_optix_count_prepared_segment_pair_intersection",
        )
        if count_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_count_prepared_segment_pair_intersection; rebuild the OptiX backend from current main"
            )
        count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self.prepared_handle,
            left.records,
            left.count,
            ctypes.byref(count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(count.value)

    def first_hit_raw(self, probe_segments) -> OptixRowView:
        if self._closed:
            raise RuntimeError("prepared OptiX segment first-hit handle is closed")
        probes = _pack_for_geometry("segments", probe_segments)
        run_symbol = _find_optional_backend_symbol(
            self.library,
            "rtdl_optix_run_prepared_segment_first_hit",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_segment_first_hit; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlSegmentFirstHitRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self.prepared_handle,
            probes.records,
            probes.count,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlSegmentFirstHitRow,
            field_names=("probe_id", "primitive_id", "hit_x", "hit_y", "hit_t"),
        )

    def first_hit(self, probe_segments) -> tuple:
        rows = self.first_hit_raw(probe_segments)
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()

    def first_hit_count(self, probe_segments) -> int:
        if self._closed:
            raise RuntimeError("prepared OptiX segment first-hit handle is closed")
        probes = _pack_for_geometry("segments", probe_segments)
        count_symbol = _find_optional_backend_symbol(
            self.library,
            "rtdl_optix_count_prepared_segment_first_hit",
        )
        if count_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_count_prepared_segment_first_hit; rebuild the OptiX backend from current main"
            )
        count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self.prepared_handle,
            probes.records,
            probes.count,
            ctypes.byref(count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(count.value)

    def last_phase_timings(self) -> dict[str, float | int | str] | None:
        return _get_last_segment_pair_phase_timings_from_library(self.library)

    def close(self) -> None:
        if not self._closed:
            destroy = _find_optional_backend_symbol(
                self.library,
                "rtdl_optix_destroy_prepared_segment_pair_intersection",
            )
            if destroy is not None:
                destroy(self.prepared_handle)
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def prepare_segment_pair_intersection_optix(right_segments) -> PreparedOptixSegmentPairIntersection:
    lib = _load_optix_library()
    prepare_symbol = _require_backend_symbol(lib, "rtdl_optix_prepare_segment_pair_intersection")
    _require_backend_symbol(lib, "rtdl_optix_run_prepared_segment_pair_intersection")
    right = _pack_for_geometry("segments", right_segments)
    prepared = ctypes.c_void_p()
    error = ctypes.create_string_buffer(4096)
    status = prepare_symbol(
        right.records,
        right.count,
        ctypes.byref(prepared),
        error,
        len(error),
    )
    _check_status(status, error)
    return PreparedOptixSegmentPairIntersection(
        library=lib,
        prepared_handle=prepared,
    )


@dataclass
class PreparedOptixShapePairRelation:
    library: object
    prepared_handle: ctypes.c_void_p
    _closed: bool = False

    def run_raw(self, left_polygons) -> OptixRowView:
        if self._closed:
            raise RuntimeError("prepared OptiX shape-pair relation handle is closed")
        left = left_polygons if isinstance(left_polygons, PackedPolygons) else pack_polygons(records=left_polygons)
        rows_ptr = ctypes.POINTER(_RtdlOverlayRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = self.library.rtdl_optix_run_prepared_shape_pair_relation_flags(
            self.prepared_handle,
            left.refs,
            left.polygon_count,
            left.vertices_xy,
            left.vertex_xy_count,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=self.library,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlOverlayRow,
            field_names=("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"),
        )

    def run(self, left_polygons) -> tuple:
        rows = self.run_raw(left_polygons)
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()

    def close(self) -> None:
        if not self._closed:
            destroy = _find_optional_backend_symbol(
                self.library,
                "rtdl_optix_destroy_prepared_shape_pair_relation_flags",
            )
            if destroy is not None:
                destroy(self.prepared_handle)
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def prepare_shape_pair_relation_flags_optix(right_polygons) -> PreparedOptixShapePairRelation:
    lib = _load_optix_library()
    prepare_symbol = _require_backend_symbol(lib, "rtdl_optix_prepare_shape_pair_relation_flags")
    _require_backend_symbol(lib, "rtdl_optix_run_prepared_shape_pair_relation_flags")
    right = right_polygons if isinstance(right_polygons, PackedPolygons) else pack_polygons(records=right_polygons)
    prepared = ctypes.c_void_p()
    error = ctypes.create_string_buffer(4096)
    status = prepare_symbol(
        right.refs,
        right.polygon_count,
        right.vertices_xy,
        right.vertex_xy_count,
        ctypes.byref(prepared),
        error,
        len(error),
    )
    _check_status(status, error)
    return PreparedOptixShapePairRelation(
        library=lib,
        prepared_handle=prepared,
    )


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
        self._search_scene_true_zero_copy = False
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

    def nearest_witness_rows(self, query_points, *, radius: float) -> tuple[dict[str, object], ...]:
        """Return one nearest in-radius witness row per query point.

        This is the generic RT traversal primitive needed by user-level exact
        Hausdorff-style reductions: OptiX finds in-radius candidate point AABBs,
        the shader carries the nearest witness payload, and Python/partner code
        can reduce the per-query nearest distances.
        """
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius count handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=2)
        if packed_queries.dimension != 2:
            raise ValueError("PreparedOptixFixedRadiusCountThreshold2D.nearest_witness_rows requires 2-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0:
            return ()

        lib = _load_optix_library()
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_fixed_radius_nearest_witness_2d")
        if symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_fixed_radius_nearest_witness_2d; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
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
            row_type=_RtdlFixedRadiusNeighborRow,
            field_names=("query_id", "neighbor_id", "distance"),
        )
        try:
            return tuple(
                {
                    "query_id": int(row["query_id"]),
                    "neighbor_id": int(row["neighbor_id"]),
                    "distance": float(row["distance"]),
                }
                for row in view.to_dict_rows()
            )
        finally:
            view.close()

    def write_device_count_threshold_columns(
        self,
        query_point_columns: dict,
        *,
        radius: float,
        threshold: int,
        query_ids_out,
        neighbor_counts_out,
        threshold_flags_out,
    ) -> dict[str, object]:
        """Write fixed-radius count-threshold columns into partner-owned CUDA buffers."""
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius count handle is closed")
        if not getattr(self, "_search_scene_true_zero_copy", False):
            raise RuntimeError(
                "write_device_count_threshold_columns requires a device-search-column prepared scene"
            )
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        query_packet = pack_optix_fixed_radius_count_threshold_2d_device_point_inputs(
            query_point_columns,
            label="query",
            native_symbol=_OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_QUERY_OUTPUT_SYMBOL,
        )
        query_handoffs = query_packet["points"]
        query_count = int(query_packet["metadata"]["point_count"])
        expected_device = (query_handoffs["ids"].device_type, query_handoffs["ids"].device_id)
        outputs = {}
        for name, value in {
            "query_ids": query_ids_out,
            "neighbor_counts": neighbor_counts_out,
            "threshold_flags": threshold_flags_out,
        }.items():
            handoff = _partner.prepare_direct_device_pointer_handoff(value, access="write")
            _require_partner_device_any_hit_output_layout(
                handoff,
                ray_count=query_count,
                expected_device=expected_device,
            )
            outputs[name] = handoff
        if query_count == 0:
            return {
                "metadata": {
                    "backend": "optix",
                    "transfer_mode": "device_fixed_radius_point_columns_output_columns_zero_copy",
                    "native_symbol": _OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_QUERY_OUTPUT_SYMBOL,
                    "query_count": 0,
                    "direct_device_handoff_authorized": True,
                    "true_zero_copy_authorized": bool(getattr(self, "_search_scene_true_zero_copy", False)),
                    "rt_core_speedup_claim_authorized": False,
                    "v2_0_release_authorized": False,
                }
            }

        lib = _load_optix_library()
        write_symbol = _find_optional_backend_symbol(
            lib,
            _OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_QUERY_OUTPUT_SYMBOL,
        )
        if write_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{_OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_QUERY_OUTPUT_SYMBOL}. "
                "Fixed-radius partner output remains blocked; rebuild the OptiX backend."
            )
        error = ctypes.create_string_buffer(4096)
        status = write_symbol(
            self._handle,
            ctypes.c_void_p(query_handoffs["ids"].data_ptr),
            ctypes.c_void_p(query_handoffs["x"].data_ptr),
            ctypes.c_void_p(query_handoffs["y"].data_ptr),
            query_count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(threshold)),
            ctypes.c_void_p(outputs["query_ids"].data_ptr),
            ctypes.c_void_p(outputs["neighbor_counts"].data_ptr),
            ctypes.c_void_p(outputs["threshold_flags"].data_ptr),
            error,
            len(error),
        )
        _check_status(status, error)
        metadata = {
            "backend": "optix",
            "transfer_mode": "device_fixed_radius_point_columns_output_columns_zero_copy",
            "native_symbol": _OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_QUERY_OUTPUT_SYMBOL,
            "source_protocols": tuple(
                sorted({handoff.source_protocol for handoff in (*query_handoffs.values(), *outputs.values())})
            ),
            "source_devices": tuple(
                sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in (*query_handoffs.values(), *outputs.values())})
            ),
            "query_count": query_count,
            "radius": float(radius),
            "threshold": int(threshold),
            "direct_device_pointer_observed": True,
            "direct_device_handoff_authorized": True,
            "query_point_columns_true_zero_copy_authorized": True,
            "search_point_columns_true_zero_copy_authorized": bool(getattr(self, "_search_scene_true_zero_copy", False)),
            "output_columns_true_zero_copy_authorized": True,
            "native_acceleration_structure_required": True,
            "true_zero_copy_authorized": bool(getattr(self, "_search_scene_true_zero_copy", False)),
            "rt_core_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
        }
        return {"metadata": metadata}

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


class PreparedOptixFixedRadiusNeighbors3D:
    """Prepared OptiX 3-D fixed-radius neighbor scene.

    The prepared handle is generic bounded-neighbor search state: it uploads
    and retains the search-side uniform-cell structure once, then later runs
    only upload query points and write neighbor rows.
    """

    def __init__(self, search_points, *, max_radius: float):
        if max_radius <= 0:
            raise ValueError("max_radius must be positive")
        packed = search_points if isinstance(search_points, PackedPoints) else pack_points(records=search_points, dimension=3)
        if packed.dimension != 3:
            raise ValueError("prepare_optix_fixed_radius_neighbors_3d requires 3-D points")
        self._packed_search = packed
        self._max_radius = float(max_radius)
        self._handle = ctypes.c_void_p()
        self._closed = False
        if packed.count == 0:
            return

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_fixed_radius_neighbors_3d")
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_fixed_radius_neighbors_3d; rebuild the OptiX backend from current main"
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

    def run_raw(self, query_points, *, radius: float, k_max: int) -> OptixRowView:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius-neighbor 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if k_max <= 0:
            raise ValueError("k_max must be positive")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=3)
        if packed_queries.dimension != 3:
            raise ValueError("PreparedOptixFixedRadiusNeighbors3D.run_raw requires 3-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0:
            return OptixRowView(
                library=_load_optix_library(),
                rows_ptr=ctypes.POINTER(_RtdlFixedRadiusNeighborRow)(),
                row_count=0,
                row_type=_RtdlFixedRadiusNeighborRow,
                field_names=("query_id", "neighbor_id", "distance"),
                _free_on_close=False,
            )

        lib = _load_optix_library()
        run_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_fixed_radius_neighbors_3d")
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_fixed_radius_neighbors_3d; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(k_max)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlFixedRadiusNeighborRow,
            field_names=("query_id", "neighbor_id", "distance"),
        )

    def run(self, query_points, *, radius: float, k_max: int) -> tuple[dict[str, object], ...]:
        rows = self.run_raw(query_points, radius=radius, k_max=k_max)
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()

    def run_exact_raw(self, query_points, *, radius: float, k_max: int) -> OptixRowView:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius-neighbor 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if k_max <= 0:
            raise ValueError("k_max must be positive")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=3)
        if packed_queries.dimension != 3:
            raise ValueError("PreparedOptixFixedRadiusNeighbors3D.run_exact_raw requires 3-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0:
            return OptixRowView(
                library=_load_optix_library(),
                rows_ptr=ctypes.POINTER(_RtdlFixedRadiusNeighborRow)(),
                row_count=0,
                row_type=_RtdlFixedRadiusNeighborRow,
                field_names=("query_id", "neighbor_id", "distance"),
                _free_on_close=False,
            )

        lib = _load_optix_library()
        run_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_exact_fixed_radius_neighbors_3d")
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_exact_fixed_radius_neighbors_3d; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(k_max)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlFixedRadiusNeighborRow,
            field_names=("query_id", "neighbor_id", "distance"),
        )

    def run_exact(self, query_points, *, radius: float, k_max: int) -> tuple[dict[str, object], ...]:
        rows = self.run_exact_raw(query_points, radius=radius, k_max=k_max)
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()

    def run_ranked_raw(self, query_points, *, radius: float, k_max: int) -> OptixRowView:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius-neighbor 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if k_max <= 0:
            raise ValueError("k_max must be positive")
        if k_max > 64:
            raise ValueError("PreparedOptixFixedRadiusNeighbors3D.run_ranked_raw currently supports k_max <= 64")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=3)
        if packed_queries.dimension != 3:
            raise ValueError("PreparedOptixFixedRadiusNeighbors3D.run_ranked_raw requires 3-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0:
            return OptixRowView(
                library=_load_optix_library(),
                rows_ptr=ctypes.POINTER(_RtdlKnnNeighborRow)(),
                row_count=0,
                row_type=_RtdlKnnNeighborRow,
                field_names=("query_id", "neighbor_id", "distance", "neighbor_rank"),
                _free_on_close=False,
            )

        lib = _load_optix_library()
        run_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d")
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlKnnNeighborRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(k_max)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlKnnNeighborRow,
            field_names=("query_id", "neighbor_id", "distance", "neighbor_rank"),
        )

    def run_ranked(self, query_points, *, radius: float, k_max: int) -> tuple[dict[str, object], ...]:
        rows = self.run_ranked_raw(query_points, radius=radius, k_max=k_max)
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()

    def run_ranked_summary_raw(self, query_points, *, radius: float, k_max: int) -> OptixRowView:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius-neighbor 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if k_max <= 0:
            raise ValueError("k_max must be positive")
        if k_max > 64:
            raise ValueError("PreparedOptixFixedRadiusNeighbors3D.run_ranked_summary_raw currently supports k_max <= 64")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=3)
        if packed_queries.dimension != 3:
            raise ValueError("PreparedOptixFixedRadiusNeighbors3D.run_ranked_summary_raw requires 3-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0:
            return OptixRowView(
                library=_load_optix_library(),
                rows_ptr=ctypes.POINTER(_RtdlFixedRadiusRankedNeighborSummary)(),
                row_count=0,
                row_type=_RtdlFixedRadiusRankedNeighborSummary,
                field_names=(
                    "query_id",
                    "neighbor_count",
                    "nearest_neighbor_id",
                    "kth_neighbor_id",
                    "nearest_distance",
                    "kth_distance",
                    "sum_distance",
                ),
                _free_on_close=False,
            )

        lib = _load_optix_library()
        run_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d")
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusRankedNeighborSummary)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(k_max)),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlFixedRadiusRankedNeighborSummary,
            field_names=(
                "query_id",
                "neighbor_count",
                "nearest_neighbor_id",
                "kth_neighbor_id",
                "nearest_distance",
                "kth_distance",
                "sum_distance",
            ),
        )

    def run_ranked_summary(self, query_points, *, radius: float, k_max: int) -> tuple[dict[str, object], ...]:
        rows = self.run_ranked_summary_raw(query_points, radius=radius, k_max=k_max)
        try:
            return rows.to_dict_rows()
        finally:
            rows.close()

    def count(self, query_points, *, radius: float, k_max: int) -> int:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius-neighbor 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if k_max <= 0:
            raise ValueError("k_max must be positive")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=3)
        if packed_queries.dimension != 3:
            raise ValueError("PreparedOptixFixedRadiusNeighbors3D.count requires 3-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0:
            return 0

        lib = _load_optix_library()
        count_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_fixed_radius_neighbors_3d")
        if count_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_count_prepared_fixed_radius_neighbors_3d; rebuild the OptiX backend from current main"
            )
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(k_max)),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(row_count.value)

    def summary(self, query_points, *, radius: float, k_max: int) -> dict[str, float | int]:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius-neighbor 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if k_max <= 0:
            raise ValueError("k_max must be positive")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=3)
        if packed_queries.dimension != 3:
            raise ValueError("PreparedOptixFixedRadiusNeighbors3D.summary requires 3-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0:
            return {"count": 0, "min_distance": 0.0, "max_distance": 0.0, "sum_distance": 0.0}

        lib = _load_optix_library()
        summary_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_summarize_prepared_fixed_radius_neighbors_3d")
        if summary_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_summarize_prepared_fixed_radius_neighbors_3d; rebuild the OptiX backend from current main"
            )
        summary = _RtdlFixedRadiusNeighborSummary()
        error = ctypes.create_string_buffer(4096)
        status = summary_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(k_max)),
            ctypes.byref(summary),
            error,
            len(error),
        )
        _check_status(status, error)
        return {
            "count": int(summary.count),
            "min_distance": float(summary.min_distance),
            "max_distance": float(summary.max_distance),
            "sum_distance": float(summary.sum_distance),
        }

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixFixedRadiusNeighbors3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_fixed_radius_neighbors_3d(
    search_points,
    *,
    max_radius: float,
) -> PreparedOptixFixedRadiusNeighbors3D:
    return PreparedOptixFixedRadiusNeighbors3D(search_points, max_radius=max_radius)


class PreparedOptixFixedRadiusCountThreshold3D:
    """Prepared OptiX RT 3-D fixed-radius count-threshold scene.

    The native contract is generic: a prepared search scene accepts host query
    points and writes query ids, threshold-capped neighbor counts, and threshold
    flags into caller-owned CUDA columns.
    """

    def __init__(self, search_points, *, max_radius: float):
        if max_radius <= 0:
            raise ValueError("max_radius must be positive")
        packed = search_points if isinstance(search_points, PackedPoints) else pack_points(records=search_points, dimension=3)
        if packed.dimension != 3:
            raise ValueError("prepare_optix_fixed_radius_count_threshold_3d requires 3-D points")
        self._packed_search = packed
        self._max_radius = float(max_radius)
        self._handle = ctypes.c_void_p()
        self._closed = False

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_fixed_radius_count_threshold_3d")
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_fixed_radius_count_threshold_3d; rebuild the OptiX backend from current main"
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

    def write_device_count_threshold_columns(
        self,
        query_points,
        *,
        radius: float,
        threshold: int,
        query_ids_out,
        neighbor_counts_out,
        threshold_flags_out,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius count-threshold 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=3)
        if packed_queries.dimension != 3:
            raise ValueError("write_device_count_threshold_columns requires 3-D query points")

        outputs = {}
        expected_device = None
        for name, value in {
            "query_ids": query_ids_out,
            "neighbor_counts": neighbor_counts_out,
            "threshold_flags": threshold_flags_out,
        }.items():
            handoff = _partner.prepare_direct_device_pointer_handoff(value, access="write")
            if expected_device is None:
                expected_device = (handoff.device_type, handoff.device_id)
            _require_partner_device_any_hit_output_layout(
                handoff,
                ray_count=packed_queries.count,
                expected_device=expected_device,
            )
            outputs[name] = handoff

        if packed_queries.count == 0:
            return {
                "metadata": {
                    "backend": "optix",
                    "native_symbol": _OPTIX_PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_3D_DEVICE_OUTPUT_SYMBOL,
                    "query_count": 0,
                    "transfer_mode": "host_query_points_to_device_threshold_columns_empty_shortcut",
                    "rt_core_accelerated": True,
                    "materializes_neighbor_rows": False,
                    "direct_device_handoff_authorized": True,
                    "true_zero_copy_authorized": False,
                }
            }

        lib = _load_optix_library()
        write_symbol = _find_optional_backend_symbol(
            lib,
            _OPTIX_PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_3D_DEVICE_OUTPUT_SYMBOL,
        )
        if write_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                f"{_OPTIX_PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_3D_DEVICE_OUTPUT_SYMBOL}; "
                "rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        start = time.perf_counter()
        status = write_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(threshold)),
            ctypes.c_void_p(outputs["query_ids"].data_ptr),
            ctypes.c_void_p(outputs["neighbor_counts"].data_ptr),
            ctypes.c_void_p(outputs["threshold_flags"].data_ptr),
            error,
            len(error),
        )
        _check_status(status, error)
        elapsed = time.perf_counter() - start
        return {
            "metadata": {
                "backend": "optix",
                "native_symbol": _OPTIX_PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_3D_DEVICE_OUTPUT_SYMBOL,
                "native_engine_row_contract": "generic_fixed_radius_count_threshold_3d_device_columns",
                "native_execution_path": "prepared_rt_core_count_threshold_3d",
                "query_count": packed_queries.count,
                "search_count": self._packed_search.count,
                "radius": float(radius),
                "threshold": int(threshold),
                "native_elapsed_sec": elapsed,
                "transfer_mode": "host_query_points_to_device_threshold_columns",
                "source_protocols": tuple(sorted({handoff.source_protocol for handoff in outputs.values()})),
                "source_devices": tuple(sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in outputs.values()})),
                "rt_core_accelerated": True,
                "materializes_neighbor_rows": False,
                "direct_device_handoff_authorized": True,
                "output_columns_true_zero_copy_authorized": True,
                "true_zero_copy_authorized": False,
                "v2_0_release_authorized": False,
                "paper_speedup_claim_authorized": False,
            }
        }

    def write_device_adjacency_columns(
        self,
        query_points,
        *,
        radius: float,
        edge_offsets,
        neighbor_indices_out,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius adjacency 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=3)
        if packed_queries.dimension != 3:
            raise ValueError("write_device_adjacency_columns requires 3-D query points")

        edge_offsets_handoff = _partner.prepare_direct_device_pointer_handoff(edge_offsets, access="read")
        neighbor_indices_handoff = _partner.prepare_direct_device_pointer_handoff(neighbor_indices_out, access="write")
        expected_device = (edge_offsets_handoff.device_type, edge_offsets_handoff.device_id)
        if (neighbor_indices_handoff.device_type, neighbor_indices_handoff.device_id) != expected_device:
            raise ValueError("edge_offsets and neighbor_indices_out must live on the same CUDA device")
        if _partner_dtype_token(edge_offsets_handoff.dtype) != "int64":
            raise ValueError("edge_offsets must use dtype int64")
        if _partner_dtype_token(neighbor_indices_handoff.dtype) != "int32":
            raise ValueError("neighbor_indices_out must use dtype int32")
        if tuple(edge_offsets_handoff.shape) != (packed_queries.count + 1,):
            raise ValueError("edge_offsets must have shape (query_count + 1,)")
        if len(tuple(neighbor_indices_handoff.shape)) != 1:
            raise ValueError("neighbor_indices_out must be one-dimensional")
        if not _partner_contiguous_column_strides(edge_offsets_handoff.strides, itemsize=8):
            raise ValueError("edge_offsets must be contiguous")
        if not _partner_contiguous_column_strides(neighbor_indices_handoff.strides, itemsize=4):
            raise ValueError("neighbor_indices_out must be contiguous")

        if packed_queries.count == 0:
            return {
                "metadata": {
                    "backend": "optix",
                    "native_symbol": _OPTIX_PREPARED_FIXED_RADIUS_ADJACENCY_3D_DEVICE_OUTPUT_SYMBOL,
                    "query_count": 0,
                    "neighbor_index_capacity": 0,
                    "transfer_mode": "host_query_points_to_device_adjacency_empty_shortcut",
                    "rt_core_accelerated": True,
                    "materializes_neighbor_rows": False,
                    "direct_device_handoff_authorized": True,
                    "true_zero_copy_authorized": False,
                }
            }

        lib = _load_optix_library()
        write_symbol = _find_optional_backend_symbol(
            lib,
            _OPTIX_PREPARED_FIXED_RADIUS_ADJACENCY_3D_DEVICE_OUTPUT_SYMBOL,
        )
        if write_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                f"{_OPTIX_PREPARED_FIXED_RADIUS_ADJACENCY_3D_DEVICE_OUTPUT_SYMBOL}; "
                "rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        start = time.perf_counter()
        status = write_symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_void_p(edge_offsets_handoff.data_ptr),
            ctypes.c_void_p(neighbor_indices_handoff.data_ptr),
            ctypes.c_size_t(int(neighbor_indices_handoff.shape[0])),
            error,
            len(error),
        )
        _check_status(status, error)
        elapsed = time.perf_counter() - start
        return {
            "metadata": {
                "backend": "optix",
                "native_symbol": _OPTIX_PREPARED_FIXED_RADIUS_ADJACENCY_3D_DEVICE_OUTPUT_SYMBOL,
                "native_engine_row_contract": "generic_fixed_radius_adjacency_3d_device_columns",
                "native_execution_path": "prepared_rt_core_adjacency_3d",
                "query_count": packed_queries.count,
                "search_count": self._packed_search.count,
                "radius": float(radius),
                "neighbor_index_capacity": int(neighbor_indices_handoff.shape[0]),
                "native_elapsed_sec": elapsed,
                "transfer_mode": "host_query_points_to_device_adjacency_columns",
                "source_protocols": tuple(sorted({
                    edge_offsets_handoff.source_protocol,
                    neighbor_indices_handoff.source_protocol,
                })),
                "source_devices": (f"{expected_device[0]}:{expected_device[1]}",),
                "rt_core_accelerated": True,
                "materializes_neighbor_rows": False,
                "direct_device_handoff_authorized": True,
                "output_columns_true_zero_copy_authorized": True,
                "true_zero_copy_authorized": False,
                "v2_0_release_authorized": False,
                "paper_speedup_claim_authorized": False,
            }
        }

    def apply_device_grouped_union(
        self,
        query_points,
        *,
        radius: float,
        query_index_offset: int,
        predicate_flags,
        parent_out,
        fallback_candidate_out,
        same_root_culling: bool = True,
        direct_side_effect: bool = False,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius grouped-union 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        same_root_culling = _require_bool(same_root_culling, name="same_root_culling")
        direct_side_effect = _require_bool(direct_side_effect, name="direct_side_effect")
        query_index_offset = int(query_index_offset)
        if query_index_offset < 0:
            raise ValueError("query_index_offset must be non-negative")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=3)
        if packed_queries.dimension != 3:
            raise ValueError("apply_device_grouped_union requires 3-D query points")

        predicate_handoff = _partner.prepare_direct_device_pointer_handoff(predicate_flags, access="read")
        parent_handoff = _partner.prepare_direct_device_pointer_handoff(parent_out, access="readwrite")
        fallback_handoff = _partner.prepare_direct_device_pointer_handoff(fallback_candidate_out, access="readwrite")
        expected_device = (predicate_handoff.device_type, predicate_handoff.device_id)
        if (parent_handoff.device_type, parent_handoff.device_id) != expected_device:
            raise ValueError("predicate_flags and parent_out must live on the same CUDA device")
        if (fallback_handoff.device_type, fallback_handoff.device_id) != expected_device:
            raise ValueError("predicate_flags and fallback_candidate_out must live on the same CUDA device")
        if _partner_dtype_token(predicate_handoff.dtype) != "uint32":
            raise ValueError("predicate_flags must use dtype uint32")
        if _partner_dtype_token(parent_handoff.dtype) != "int32":
            raise ValueError("parent_out must use dtype int32")
        if _partner_dtype_token(fallback_handoff.dtype) != "int32":
            raise ValueError("fallback_candidate_out must use dtype int32")
        if len(tuple(predicate_handoff.shape)) != 1:
            raise ValueError("predicate_flags must be one-dimensional")
        if tuple(parent_handoff.shape) != tuple(predicate_handoff.shape):
            raise ValueError("parent_out must have the same shape as predicate_flags")
        if tuple(fallback_handoff.shape) != tuple(predicate_handoff.shape):
            raise ValueError("fallback_candidate_out must have the same shape as predicate_flags")
        if query_index_offset + packed_queries.count > int(predicate_handoff.shape[0]):
            raise ValueError("query_index_offset + query_count must not exceed predicate flag length")
        if int(predicate_handoff.shape[0]) < self._packed_search.count:
            raise ValueError("grouped-union workspaces must cover every prepared search item")
        if not _partner_contiguous_column_strides(predicate_handoff.strides, itemsize=4):
            raise ValueError("predicate_flags must be contiguous")
        if not _partner_contiguous_column_strides(parent_handoff.strides, itemsize=4):
            raise ValueError("parent_out must be contiguous")
        if not _partner_contiguous_column_strides(fallback_handoff.strides, itemsize=4):
            raise ValueError("fallback_candidate_out must be contiguous")

        if packed_queries.count == 0:
            return {
                "metadata": {
                    "backend": "optix",
                    "native_symbol": (
                        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL
                        if direct_side_effect
                        else
                        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_SYMBOL
                        if same_root_culling
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_OPTIONS_SYMBOL
                    ),
                    "query_count": 0,
                    "query_index_offset": query_index_offset,
                    "item_count": int(predicate_handoff.shape[0]),
                    "transfer_mode": "host_query_points_to_device_grouped_union_empty_shortcut",
                    "rt_core_accelerated": True,
                    "materializes_neighbor_rows": False,
                    "materializes_directed_adjacency_stream": False,
                    "grouped_union_same_root_culling_enabled": same_root_culling,
                    "grouped_union_same_root_culling_policy": (
                        "parent_union_same_root_before_anyhit"
                        if same_root_culling
                        else "disabled_by_caller"
                    ),
                    "grouped_union_direct_side_effect_enabled": direct_side_effect,
                    "grouped_union_direct_side_effect_policy": (
                        _grouped_union_direct_side_effect_policy(direct_side_effect)
                    ),
                    "direct_device_handoff_authorized": True,
                    "true_zero_copy_authorized": False,
                }
            }

        lib = _load_optix_library()
        symbol_name = (
            _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL
            if direct_side_effect
            else
            _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_SYMBOL
            if same_root_culling
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_OPTIONS_SYMBOL
        )
        apply_symbol = _find_optional_backend_symbol(
            lib,
            symbol_name,
        )
        if apply_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                f"{symbol_name}; "
                "rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        start = time.perf_counter()
        if direct_side_effect:
            status = apply_symbol(
                self._handle,
                packed_queries.records,
                packed_queries.count,
                ctypes.c_size_t(query_index_offset),
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(fallback_handoff.data_ptr),
                ctypes.c_uint32(1 if same_root_culling else 0),
                ctypes.c_uint32(1),
                ctypes.c_size_t(int(predicate_handoff.shape[0])),
                error,
                len(error),
            )
        elif same_root_culling:
            status = apply_symbol(
                self._handle,
                packed_queries.records,
                packed_queries.count,
                ctypes.c_size_t(query_index_offset),
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(fallback_handoff.data_ptr),
                ctypes.c_size_t(int(predicate_handoff.shape[0])),
                error,
                len(error),
            )
        else:
            status = apply_symbol(
                self._handle,
                packed_queries.records,
                packed_queries.count,
                ctypes.c_size_t(query_index_offset),
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(fallback_handoff.data_ptr),
                ctypes.c_uint32(0),
                ctypes.c_size_t(int(predicate_handoff.shape[0])),
                error,
                len(error),
            )
        _check_status(status, error)
        elapsed = time.perf_counter() - start
        return {
            "metadata": {
                "backend": "optix",
                "native_symbol": symbol_name,
                "native_engine_row_contract": "generic_prepared_fixed_radius_grouped_union_3d_device_workspaces",
                "native_execution_path": "prepared_rt_core_grouped_union_3d",
                "query_count": packed_queries.count,
                "query_index_offset": query_index_offset,
                "search_count": self._packed_search.count,
                "item_count": int(predicate_handoff.shape[0]),
                "radius": float(radius),
                "native_elapsed_sec": elapsed,
                "transfer_mode": "host_query_points_to_device_grouped_union_workspaces",
                "source_protocols": tuple(sorted({
                    predicate_handoff.source_protocol,
                    parent_handoff.source_protocol,
                    fallback_handoff.source_protocol,
                })),
                "source_devices": (f"{expected_device[0]}:{expected_device[1]}",),
                "rt_core_accelerated": True,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
                "grouped_union_same_root_culling_enabled": same_root_culling,
                "grouped_union_same_root_culling_policy": (
                    "parent_union_same_root_before_anyhit"
                    if same_root_culling
                    else "disabled_by_caller"
                ),
                "grouped_union_direct_side_effect_enabled": direct_side_effect,
                "grouped_union_direct_side_effect_policy": (
                    _grouped_union_direct_side_effect_policy(direct_side_effect)
                ),
                "direct_device_handoff_authorized": True,
                "output_columns_true_zero_copy_authorized": True,
                "true_zero_copy_authorized": False,
                "v2_0_release_authorized": False,
                "paper_speedup_claim_authorized": False,
            }
        }

    def apply_device_grouped_union_self(
        self,
        *,
        radius: float,
        predicate_flags,
        parent_out,
        fallback_candidate_out,
        telemetry_out=None,
        same_root_culling: bool = True,
        direct_side_effect: bool = False,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius grouped-union self 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        same_root_culling = _require_bool(same_root_culling, name="same_root_culling")
        direct_side_effect = _require_bool(direct_side_effect, name="direct_side_effect")

        predicate_handoff = _partner.prepare_direct_device_pointer_handoff(predicate_flags, access="read")
        parent_handoff = _partner.prepare_direct_device_pointer_handoff(parent_out, access="readwrite")
        fallback_handoff = _partner.prepare_direct_device_pointer_handoff(fallback_candidate_out, access="readwrite")
        expected_device = (predicate_handoff.device_type, predicate_handoff.device_id)
        if (parent_handoff.device_type, parent_handoff.device_id) != expected_device:
            raise ValueError("predicate_flags and parent_out must live on the same CUDA device")
        if (fallback_handoff.device_type, fallback_handoff.device_id) != expected_device:
            raise ValueError("predicate_flags and fallback_candidate_out must live on the same CUDA device")
        if _partner_dtype_token(predicate_handoff.dtype) != "uint32":
            raise ValueError("predicate_flags must use dtype uint32")
        if _partner_dtype_token(parent_handoff.dtype) != "int32":
            raise ValueError("parent_out must use dtype int32")
        if _partner_dtype_token(fallback_handoff.dtype) != "int32":
            raise ValueError("fallback_candidate_out must use dtype int32")
        if len(tuple(predicate_handoff.shape)) != 1:
            raise ValueError("predicate_flags must be one-dimensional")
        if tuple(parent_handoff.shape) != tuple(predicate_handoff.shape):
            raise ValueError("parent_out must have the same shape as predicate_flags")
        if tuple(fallback_handoff.shape) != tuple(predicate_handoff.shape):
            raise ValueError("fallback_candidate_out must have the same shape as predicate_flags")
        if int(predicate_handoff.shape[0]) < self._packed_search.count:
            raise ValueError("grouped-union self workspaces must cover every prepared search item")
        if not _partner_contiguous_column_strides(predicate_handoff.strides, itemsize=4):
            raise ValueError("predicate_flags must be contiguous")
        if not _partner_contiguous_column_strides(parent_handoff.strides, itemsize=4):
            raise ValueError("parent_out must be contiguous")
        if not _partner_contiguous_column_strides(fallback_handoff.strides, itemsize=4):
            raise ValueError("fallback_candidate_out must be contiguous")
        telemetry_handoff = None
        if telemetry_out is not None:
            telemetry_handoff = _partner.prepare_direct_device_pointer_handoff(telemetry_out, access="readwrite")
            if (telemetry_handoff.device_type, telemetry_handoff.device_id) != expected_device:
                raise ValueError("grouped-union telemetry_out must live on the same CUDA device")
            if _partner_dtype_token(telemetry_handoff.dtype) != "uint64":
                raise ValueError("grouped-union telemetry_out must use dtype uint64")
            if len(tuple(telemetry_handoff.shape)) != 1:
                raise ValueError("grouped-union telemetry_out must be one-dimensional")
            if int(telemetry_handoff.shape[0]) < 4:
                raise ValueError("grouped-union telemetry_out must contain at least four counters")
            if not _partner_contiguous_column_strides(telemetry_handoff.strides, itemsize=8):
                raise ValueError("grouped-union telemetry_out must be contiguous")

        query_count = self._packed_search.count
        if query_count == 0:
            return {
                "metadata": {
                    "backend": "optix",
                    "native_symbol": (
                        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_EXECUTION_OPTIONS_SYMBOL
                        if telemetry_handoff is not None and direct_side_effect
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL
                        if direct_side_effect
                        else
                        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_SYMBOL
                        if telemetry_handoff is not None and same_root_culling
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_OPTIONS_SYMBOL
                        if telemetry_handoff is not None
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_SYMBOL
                        if same_root_culling
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_OPTIONS_SYMBOL
                    ),
                    "query_count": 0,
                    "query_index_offset": 0,
                    "search_count": self._packed_search.count,
                    "item_count": int(predicate_handoff.shape[0]),
                    "query_source": "prepared_search_points_self_query_device",
                    "transfer_mode": "prepared_device_search_points_self_grouped_union_empty_shortcut",
                    "rt_core_accelerated": True,
                    "materializes_neighbor_rows": False,
                    "materializes_directed_adjacency_stream": False,
                    "grouped_union_same_root_culling_enabled": same_root_culling,
                    "grouped_union_same_root_culling_policy": (
                        "parent_union_same_root_before_anyhit"
                        if same_root_culling
                        else "disabled_by_caller"
                    ),
                    "grouped_union_direct_side_effect_enabled": direct_side_effect,
                    "grouped_union_direct_side_effect_policy": (
                        _grouped_union_direct_side_effect_policy(direct_side_effect)
                    ),
                    "direct_device_handoff_authorized": True,
                    "true_zero_copy_authorized": False,
                    "grouped_union_telemetry_requested": telemetry_handoff is not None,
                }
            }

        lib = _load_optix_library()
        symbol_name = (
            _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_EXECUTION_OPTIONS_SYMBOL
            if telemetry_handoff is not None and direct_side_effect
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL
            if direct_side_effect
            else
            _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_SYMBOL
            if telemetry_handoff is not None and same_root_culling
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_OPTIONS_SYMBOL
            if telemetry_handoff is not None
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_SYMBOL
            if same_root_culling
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_OPTIONS_SYMBOL
        )
        apply_symbol = _find_optional_backend_symbol(lib, symbol_name)
        if apply_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                f"{symbol_name}; "
                "rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        start = time.perf_counter()
        if telemetry_handoff is not None and direct_side_effect:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(fallback_handoff.data_ptr),
                ctypes.c_void_p(telemetry_handoff.data_ptr),
                ctypes.c_uint32(1 if same_root_culling else 0),
                ctypes.c_uint32(1),
                ctypes.c_size_t(int(predicate_handoff.shape[0])),
                error,
                len(error),
            )
        elif direct_side_effect:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(fallback_handoff.data_ptr),
                ctypes.c_uint32(1 if same_root_culling else 0),
                ctypes.c_uint32(1),
                ctypes.c_size_t(int(predicate_handoff.shape[0])),
                error,
                len(error),
            )
        elif telemetry_handoff is not None and same_root_culling:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(fallback_handoff.data_ptr),
                ctypes.c_void_p(telemetry_handoff.data_ptr),
                ctypes.c_size_t(int(predicate_handoff.shape[0])),
                error,
                len(error),
            )
        elif telemetry_handoff is not None:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(fallback_handoff.data_ptr),
                ctypes.c_void_p(telemetry_handoff.data_ptr),
                ctypes.c_uint32(0),
                ctypes.c_size_t(int(predicate_handoff.shape[0])),
                error,
                len(error),
            )
        elif same_root_culling:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(fallback_handoff.data_ptr),
                ctypes.c_size_t(int(predicate_handoff.shape[0])),
                error,
                len(error),
            )
        else:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(fallback_handoff.data_ptr),
                ctypes.c_uint32(0),
                ctypes.c_size_t(int(predicate_handoff.shape[0])),
                error,
                len(error),
            )
        _check_status(status, error)
        elapsed = time.perf_counter() - start
        return {
            "metadata": {
                "backend": "optix",
                "native_symbol": symbol_name,
                "native_engine_row_contract": "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces",
                "native_execution_path": "prepared_rt_core_grouped_union_3d_self_query",
                "query_source": "prepared_search_points_self_query_device",
                "query_count": query_count,
                "query_index_offset": 0,
                "search_count": self._packed_search.count,
                "item_count": int(predicate_handoff.shape[0]),
                "radius": float(radius),
                "native_elapsed_sec": elapsed,
                "transfer_mode": "prepared_device_search_points_self_grouped_union_workspaces",
                "source_protocols": tuple(sorted({
                    predicate_handoff.source_protocol,
                    parent_handoff.source_protocol,
                    fallback_handoff.source_protocol,
                })),
                "source_devices": (f"{expected_device[0]}:{expected_device[1]}",),
                "rt_core_accelerated": True,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
                "grouped_union_intersection_culling_policy": (
                    "predicate_aware_connectivity_and_fallback_before_anyhit"
                ),
                "grouped_union_same_root_culling_enabled": same_root_culling,
                "grouped_union_same_root_culling_policy": (
                    "parent_union_same_root_before_anyhit"
                    if same_root_culling
                    else "disabled_by_caller"
                ),
                "grouped_union_direct_side_effect_enabled": direct_side_effect,
                "grouped_union_direct_side_effect_policy": (
                    _grouped_union_direct_side_effect_policy(direct_side_effect)
                ),
                "grouped_union_telemetry_requested": telemetry_handoff is not None,
                "grouped_union_telemetry_contract": (
                    "uint64[0]=parent_atomic_attempts,uint64[1]=parent_atomic_successes,"
                    "uint64[2]=fallback_atomic_attempts,uint64[3]=fallback_atomic_successes"
                    if telemetry_handoff is not None
                    else None
                ),
                "direct_device_handoff_authorized": True,
                "output_columns_true_zero_copy_authorized": True,
                "true_zero_copy_authorized": False,
                "v2_0_release_authorized": False,
                "paper_speedup_claim_authorized": False,
            }
        }

    def apply_device_grouped_union_all_self(
        self,
        *,
        radius: float,
        parent_out,
        telemetry_out=None,
        same_root_culling: bool = True,
        direct_side_effect: bool = False,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius grouped-union all-items self 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        same_root_culling = _require_bool(same_root_culling, name="same_root_culling")
        direct_side_effect = _require_bool(direct_side_effect, name="direct_side_effect")

        parent_handoff = _partner.prepare_direct_device_pointer_handoff(parent_out, access="readwrite")
        if _partner_dtype_token(parent_handoff.dtype) != "int32":
            raise ValueError("parent_out must use dtype int32")
        if len(tuple(parent_handoff.shape)) != 1:
            raise ValueError("parent_out must be one-dimensional")
        if int(parent_handoff.shape[0]) < self._packed_search.count:
            raise ValueError("grouped-union all-items self workspace must cover every prepared search item")
        if not _partner_contiguous_column_strides(parent_handoff.strides, itemsize=4):
            raise ValueError("parent_out must be contiguous")
        telemetry_handoff = None
        if telemetry_out is not None:
            telemetry_handoff = _partner.prepare_direct_device_pointer_handoff(telemetry_out, access="readwrite")
            if (telemetry_handoff.device_type, telemetry_handoff.device_id) != (
                parent_handoff.device_type,
                parent_handoff.device_id,
            ):
                raise ValueError("grouped-union telemetry_out must live on the same CUDA device")
            if _partner_dtype_token(telemetry_handoff.dtype) != "uint64":
                raise ValueError("grouped-union telemetry_out must use dtype uint64")
            if len(tuple(telemetry_handoff.shape)) != 1:
                raise ValueError("grouped-union telemetry_out must be one-dimensional")
            if int(telemetry_handoff.shape[0]) < 4:
                raise ValueError("grouped-union telemetry_out must contain at least four counters")
            if not _partner_contiguous_column_strides(telemetry_handoff.strides, itemsize=8):
                raise ValueError("grouped-union telemetry_out must be contiguous")

        query_count = self._packed_search.count
        if query_count == 0:
            return {
                "metadata": {
                    "backend": "optix",
                    "native_symbol": (
                        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_EXECUTION_OPTIONS_SYMBOL
                        if telemetry_handoff is not None and direct_side_effect
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL
                        if direct_side_effect
                        else
                        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_SYMBOL
                        if telemetry_handoff is not None and same_root_culling
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_OPTIONS_SYMBOL
                        if telemetry_handoff is not None
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_SYMBOL
                        if same_root_culling
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_OPTIONS_SYMBOL
                    ),
                    "query_count": 0,
                    "query_index_offset": 0,
                    "search_count": self._packed_search.count,
                    "item_count": int(parent_handoff.shape[0]),
                    "query_source": "prepared_search_points_self_query_device",
                    "predicate_mode": "all_items_true_no_fallback_candidates",
                    "transfer_mode": "prepared_device_search_points_self_grouped_union_all_items_empty_shortcut",
                    "rt_core_accelerated": True,
                    "materializes_neighbor_rows": False,
                    "materializes_directed_adjacency_stream": False,
                    "grouped_union_same_root_culling_enabled": same_root_culling,
                    "grouped_union_same_root_culling_policy": (
                        "parent_union_same_root_before_anyhit"
                        if same_root_culling
                        else "disabled_by_caller"
                    ),
                    "grouped_union_direct_side_effect_enabled": direct_side_effect,
                    "grouped_union_direct_side_effect_policy": (
                        _grouped_union_direct_side_effect_policy(direct_side_effect)
                    ),
                    "direct_device_handoff_authorized": True,
                    "true_zero_copy_authorized": False,
                    "grouped_union_telemetry_requested": telemetry_handoff is not None,
                }
            }

        lib = _load_optix_library()
        symbol_name = (
            _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_EXECUTION_OPTIONS_SYMBOL
            if telemetry_handoff is not None and direct_side_effect
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL
            if direct_side_effect
            else
            _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_SYMBOL
            if telemetry_handoff is not None and same_root_culling
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_OPTIONS_SYMBOL
            if telemetry_handoff is not None
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_SYMBOL
            if same_root_culling
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_OPTIONS_SYMBOL
        )
        apply_symbol = _find_optional_backend_symbol(lib, symbol_name)
        if apply_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                f"{symbol_name}; "
                "rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        start = time.perf_counter()
        if telemetry_handoff is not None and direct_side_effect:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(0),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(0),
                ctypes.c_void_p(telemetry_handoff.data_ptr),
                ctypes.c_uint32(1 if same_root_culling else 0),
                ctypes.c_uint32(1),
                ctypes.c_size_t(int(parent_handoff.shape[0])),
                error,
                len(error),
            )
        elif direct_side_effect:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(0),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(0),
                ctypes.c_uint32(1 if same_root_culling else 0),
                ctypes.c_uint32(1),
                ctypes.c_size_t(int(parent_handoff.shape[0])),
                error,
                len(error),
            )
        elif telemetry_handoff is not None and same_root_culling:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(0),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(0),
                ctypes.c_void_p(telemetry_handoff.data_ptr),
                ctypes.c_size_t(int(parent_handoff.shape[0])),
                error,
                len(error),
            )
        elif telemetry_handoff is not None:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(0),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(0),
                ctypes.c_void_p(telemetry_handoff.data_ptr),
                ctypes.c_uint32(0),
                ctypes.c_size_t(int(parent_handoff.shape[0])),
                error,
                len(error),
            )
        elif same_root_culling:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(0),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(0),
                ctypes.c_size_t(int(parent_handoff.shape[0])),
                error,
                len(error),
            )
        else:
            status = apply_symbol(
                self._handle,
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(0),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(0),
                ctypes.c_uint32(0),
                ctypes.c_size_t(int(parent_handoff.shape[0])),
                error,
                len(error),
            )
        _check_status(status, error)
        elapsed = time.perf_counter() - start
        return {
            "metadata": {
                "backend": "optix",
                "native_symbol": symbol_name,
                "native_engine_row_contract": "generic_prepared_fixed_radius_grouped_union_3d_all_items_self_device_parent_workspace",
                "native_execution_path": "prepared_rt_core_grouped_union_3d_all_items_self_query",
                "query_source": "prepared_search_points_self_query_device",
                "predicate_mode": "all_items_true_no_fallback_candidates",
                "query_count": query_count,
                "query_index_offset": 0,
                "search_count": self._packed_search.count,
                "item_count": int(parent_handoff.shape[0]),
                "radius": float(radius),
                "native_elapsed_sec": elapsed,
                "transfer_mode": "prepared_device_search_points_self_grouped_union_all_items_parent_workspace",
                "source_protocols": (parent_handoff.source_protocol,),
                "source_devices": (f"{parent_handoff.device_type}:{parent_handoff.device_id}",),
                "rt_core_accelerated": True,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
                "grouped_union_intersection_culling_policy": "all_items_target_gt_source_before_anyhit",
                "grouped_union_same_root_culling_enabled": same_root_culling,
                "grouped_union_same_root_culling_policy": (
                    "parent_union_same_root_before_anyhit"
                    if same_root_culling
                    else "disabled_by_caller"
                ),
                "grouped_union_direct_side_effect_enabled": direct_side_effect,
                "grouped_union_direct_side_effect_policy": (
                    _grouped_union_direct_side_effect_policy(direct_side_effect)
                ),
                "grouped_union_telemetry_requested": telemetry_handoff is not None,
                "grouped_union_telemetry_contract": (
                    "uint64[0]=parent_atomic_attempts,uint64[1]=parent_atomic_successes,"
                    "uint64[2]=fallback_atomic_attempts,uint64[3]=fallback_atomic_successes"
                    if telemetry_handoff is not None
                    else None
                ),
                "direct_device_handoff_authorized": True,
                "output_columns_true_zero_copy_authorized": True,
                "true_zero_copy_authorized": False,
                "v2_0_release_authorized": False,
                "paper_speedup_claim_authorized": False,
            }
        }

    def apply_device_grouped_union_self_range(
        self,
        *,
        query_start: int,
        query_count: int,
        radius: float,
        parent_out,
        predicate_flags=None,
        fallback_candidate_out=None,
        telemetry_out=None,
        same_root_culling: bool = True,
        direct_side_effect: bool = False,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX fixed-radius grouped-union self-range 3D handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        same_root_culling = _require_bool(same_root_culling, name="same_root_culling")
        direct_side_effect = _require_bool(direct_side_effect, name="direct_side_effect")
        query_start = int(query_start)
        query_count = int(query_count)
        prepared_count = int(self._packed_search.count)
        if query_start < 0 or query_count < 0:
            raise ValueError("query_start and query_count must be non-negative")
        if query_start > prepared_count or query_count > prepared_count - query_start:
            raise ValueError("grouped-union self-range query window must be inside prepared search items")

        all_predicate = predicate_flags is None and fallback_candidate_out is None
        if not all_predicate and (predicate_flags is None or fallback_candidate_out is None):
            raise ValueError(
                "predicate_flags and fallback_candidate_out must both be omitted only for all-items mode"
            )

        parent_handoff = _partner.prepare_direct_device_pointer_handoff(parent_out, access="readwrite")
        if _partner_dtype_token(parent_handoff.dtype) != "int32":
            raise ValueError("parent_out must use dtype int32")
        if len(tuple(parent_handoff.shape)) != 1:
            raise ValueError("parent_out must be one-dimensional")
        if int(parent_handoff.shape[0]) < prepared_count:
            raise ValueError("grouped-union self-range parent workspace must cover every prepared search item")
        if not _partner_contiguous_column_strides(parent_handoff.strides, itemsize=4):
            raise ValueError("parent_out must be contiguous")

        predicate_handoff = None
        fallback_handoff = None
        expected_device = (parent_handoff.device_type, parent_handoff.device_id)
        if not all_predicate:
            predicate_handoff = _partner.prepare_direct_device_pointer_handoff(predicate_flags, access="read")
            fallback_handoff = _partner.prepare_direct_device_pointer_handoff(
                fallback_candidate_out,
                access="readwrite",
            )
            expected_device = (predicate_handoff.device_type, predicate_handoff.device_id)
            if (parent_handoff.device_type, parent_handoff.device_id) != expected_device:
                raise ValueError("predicate_flags and parent_out must live on the same CUDA device")
            if (fallback_handoff.device_type, fallback_handoff.device_id) != expected_device:
                raise ValueError("predicate_flags and fallback_candidate_out must live on the same CUDA device")
            if _partner_dtype_token(predicate_handoff.dtype) != "uint32":
                raise ValueError("predicate_flags must use dtype uint32")
            if _partner_dtype_token(fallback_handoff.dtype) != "int32":
                raise ValueError("fallback_candidate_out must use dtype int32")
            if len(tuple(predicate_handoff.shape)) != 1:
                raise ValueError("predicate_flags must be one-dimensional")
            if tuple(parent_handoff.shape) != tuple(predicate_handoff.shape):
                raise ValueError("parent_out must have the same shape as predicate_flags")
            if tuple(fallback_handoff.shape) != tuple(predicate_handoff.shape):
                raise ValueError("fallback_candidate_out must have the same shape as predicate_flags")
            if int(predicate_handoff.shape[0]) < prepared_count:
                raise ValueError("grouped-union self-range workspaces must cover every prepared search item")
            if not _partner_contiguous_column_strides(predicate_handoff.strides, itemsize=4):
                raise ValueError("predicate_flags must be contiguous")
            if not _partner_contiguous_column_strides(fallback_handoff.strides, itemsize=4):
                raise ValueError("fallback_candidate_out must be contiguous")

        telemetry_handoff = None
        if telemetry_out is not None:
            telemetry_handoff = _partner.prepare_direct_device_pointer_handoff(telemetry_out, access="readwrite")
            if (telemetry_handoff.device_type, telemetry_handoff.device_id) != expected_device:
                raise ValueError("grouped-union telemetry_out must live on the same CUDA device")
            if _partner_dtype_token(telemetry_handoff.dtype) != "uint64":
                raise ValueError("grouped-union telemetry_out must use dtype uint64")
            if len(tuple(telemetry_handoff.shape)) != 1:
                raise ValueError("grouped-union telemetry_out must be one-dimensional")
            if int(telemetry_handoff.shape[0]) < 4:
                raise ValueError("grouped-union telemetry_out must contain at least four counters")
            if not _partner_contiguous_column_strides(telemetry_handoff.strides, itemsize=8):
                raise ValueError("grouped-union telemetry_out must be contiguous")

        item_count = int(parent_handoff.shape[0])
        if query_count == 0:
            return {
                "metadata": {
                    "backend": "optix",
                    "native_symbol": (
                        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL
                        if direct_side_effect
                        else
                        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_SYMBOL
                        if same_root_culling
                        else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_OPTIONS_SYMBOL
                    ),
                    "query_count": 0,
                    "query_index_offset": query_start,
                    "search_count": prepared_count,
                    "item_count": item_count,
                    "query_source": "prepared_search_points_self_query_device_range",
                    "predicate_mode": "all_items_true_no_fallback_candidates" if all_predicate else "predicate_flags",
                    "transfer_mode": "prepared_device_search_points_self_range_grouped_union_empty_shortcut",
                    "rt_core_accelerated": True,
                    "materializes_neighbor_rows": False,
                    "materializes_directed_adjacency_stream": False,
                    "grouped_union_query_range_requested": True,
                    "grouped_union_telemetry_requested": telemetry_handoff is not None,
                    "grouped_union_same_root_culling_enabled": same_root_culling,
                    "grouped_union_same_root_culling_policy": (
                        "parent_union_same_root_before_anyhit"
                        if same_root_culling
                        else "disabled_by_caller"
                    ),
                    "grouped_union_direct_side_effect_enabled": direct_side_effect,
                    "grouped_union_direct_side_effect_policy": (
                        _grouped_union_direct_side_effect_policy(direct_side_effect)
                    ),
                    "direct_device_handoff_authorized": True,
                    "true_zero_copy_authorized": False,
                }
            }

        lib = _load_optix_library()
        symbol_name = (
            _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL
            if direct_side_effect
            else
            _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_SYMBOL
            if same_root_culling
            else _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_OPTIONS_SYMBOL
        )
        apply_symbol = _find_optional_backend_symbol(
            lib,
            symbol_name,
        )
        if apply_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                f"{symbol_name}; "
                "rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        start = time.perf_counter()
        if direct_side_effect:
            status = apply_symbol(
                self._handle,
                ctypes.c_size_t(query_start),
                ctypes.c_size_t(query_count),
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(0 if predicate_handoff is None else predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(0 if fallback_handoff is None else fallback_handoff.data_ptr),
                ctypes.c_void_p(0 if telemetry_handoff is None else telemetry_handoff.data_ptr),
                ctypes.c_uint32(1 if same_root_culling else 0),
                ctypes.c_uint32(1),
                ctypes.c_size_t(item_count),
                error,
                len(error),
            )
        elif same_root_culling:
            status = apply_symbol(
                self._handle,
                ctypes.c_size_t(query_start),
                ctypes.c_size_t(query_count),
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(0 if predicate_handoff is None else predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(0 if fallback_handoff is None else fallback_handoff.data_ptr),
                ctypes.c_void_p(0 if telemetry_handoff is None else telemetry_handoff.data_ptr),
                ctypes.c_size_t(item_count),
                error,
                len(error),
            )
        else:
            status = apply_symbol(
                self._handle,
                ctypes.c_size_t(query_start),
                ctypes.c_size_t(query_count),
                ctypes.c_double(float(radius)),
                ctypes.c_void_p(0 if predicate_handoff is None else predicate_handoff.data_ptr),
                ctypes.c_void_p(parent_handoff.data_ptr),
                ctypes.c_void_p(0 if fallback_handoff is None else fallback_handoff.data_ptr),
                ctypes.c_void_p(0 if telemetry_handoff is None else telemetry_handoff.data_ptr),
                ctypes.c_uint32(0),
                ctypes.c_size_t(item_count),
                error,
                len(error),
            )
        _check_status(status, error)
        elapsed = time.perf_counter() - start
        protocols = [parent_handoff.source_protocol]
        if predicate_handoff is not None:
            protocols.append(predicate_handoff.source_protocol)
        if fallback_handoff is not None:
            protocols.append(fallback_handoff.source_protocol)
        return {
            "metadata": {
                "backend": "optix",
                "native_symbol": symbol_name,
                "native_engine_row_contract": (
                    "generic_prepared_fixed_radius_grouped_union_3d_all_items_self_range_device_parent_workspace"
                    if all_predicate
                    else "generic_prepared_fixed_radius_grouped_union_3d_self_range_device_workspaces"
                ),
                "native_execution_path": "prepared_rt_core_grouped_union_3d_self_query_range",
                "query_source": "prepared_search_points_self_query_device_range",
                "predicate_mode": "all_items_true_no_fallback_candidates" if all_predicate else "predicate_flags",
                "query_count": query_count,
                "query_index_offset": query_start,
                "query_range_end": query_start + query_count,
                "search_count": prepared_count,
                "item_count": item_count,
                "radius": float(radius),
                "native_elapsed_sec": elapsed,
                "transfer_mode": "prepared_device_search_points_self_range_grouped_union_workspaces",
                "query_range_policy": "explicit_contiguous_prepared_search_range",
                "grouped_union_query_range_requested": True,
                "grouped_union_blocked_candidate": True,
                "source_protocols": tuple(sorted(set(protocols))),
                "source_devices": (f"{expected_device[0]}:{expected_device[1]}",),
                "rt_core_accelerated": True,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
                "grouped_union_intersection_culling_policy": (
                    "all_items_target_gt_source_before_anyhit"
                    if all_predicate
                    else "predicate_aware_connectivity_and_fallback_before_anyhit"
                ),
                "grouped_union_same_root_culling_enabled": same_root_culling,
                "grouped_union_same_root_culling_policy": (
                    "parent_union_same_root_before_anyhit"
                    if same_root_culling
                    else "disabled_by_caller"
                ),
                "grouped_union_direct_side_effect_enabled": direct_side_effect,
                "grouped_union_direct_side_effect_policy": (
                    _grouped_union_direct_side_effect_policy(direct_side_effect)
                ),
                "grouped_union_telemetry_requested": telemetry_handoff is not None,
                "grouped_union_telemetry_contract": (
                    "uint64[0]=parent_atomic_attempts,uint64[1]=parent_atomic_successes,"
                    "uint64[2]=fallback_atomic_attempts,uint64[3]=fallback_atomic_successes"
                    if telemetry_handoff is not None
                    else None
                ),
                "direct_device_handoff_authorized": True,
                "output_columns_true_zero_copy_authorized": True,
                "true_zero_copy_authorized": False,
                "v2_0_release_authorized": False,
                "paper_speedup_claim_authorized": False,
            }
        }

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_3d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixFixedRadiusCountThreshold3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_fixed_radius_count_threshold_3d(
    search_points,
    *,
    max_radius: float,
) -> PreparedOptixFixedRadiusCountThreshold3D:
    return PreparedOptixFixedRadiusCountThreshold3D(search_points, max_radius=max_radius)


def prepare_optix_fixed_radius_count_threshold_2d_device_search_columns(
    search_point_columns: dict,
    *,
    max_radius: float,
) -> PreparedOptixFixedRadiusCountThreshold2D:
    """Prepare an OptiX fixed-radius scene from caller-owned CUDA point columns."""
    if max_radius < 0:
        raise ValueError("max_radius must be non-negative")
    packet = pack_optix_fixed_radius_count_threshold_2d_device_point_inputs(
        search_point_columns,
        label="search",
        native_symbol=_OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_SEARCH_SYMBOL,
    )
    prepared = PreparedOptixFixedRadiusCountThreshold2D.__new__(PreparedOptixFixedRadiusCountThreshold2D)
    prepared._packed_search = _DevicePointScene2D(packet["metadata"]["point_count"])
    prepared._max_radius = float(max_radius)
    prepared._handle = ctypes.c_void_p()
    prepared._closed = False
    prepared._search_scene_true_zero_copy = True
    if packet["metadata"]["point_count"] == 0:
        return prepared

    lib = _load_optix_library()
    prepare_symbol = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_SEARCH_SYMBOL,
    )
    if prepare_symbol is None:
        raise RuntimeError(
            "Loaded OptiX backend library does not export "
            f"{_OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_SEARCH_SYMBOL}. "
            "Direct device-search fixed-radius preparation remains blocked; rebuild the OptiX backend."
        )
    points = packet["points"]
    error = ctypes.create_string_buffer(4096)
    status = prepare_symbol(
        ctypes.c_void_p(points["ids"].data_ptr),
        ctypes.c_void_p(points["x"].data_ptr),
        ctypes.c_void_p(points["y"].data_ptr),
        packet["metadata"]["point_count"],
        ctypes.c_double(float(max_radius)),
        ctypes.byref(prepared._handle),
        error,
        len(error),
    )
    _check_status(status, error)
    return prepared


def _point_group_value(group, key: str):
    if isinstance(group, dict):
        return group[key]
    return getattr(group, key)


def _pack_point_group_bounds_2d(groups) -> tuple[ctypes.Array, int]:
    rows = tuple(groups)
    packed = (_RtdlPointGroupBounds2D * len(rows))()
    for index, group in enumerate(rows):
        packed[index].id = int(_point_group_value(group, "id"))
        packed[index].point_offset = int(_point_group_value(group, "point_offset"))
        packed[index].point_count = int(_point_group_value(group, "point_count"))
        packed[index].min_x = float(_point_group_value(group, "min_x"))
        packed[index].min_y = float(_point_group_value(group, "min_y"))
        packed[index].max_x = float(_point_group_value(group, "max_x"))
        packed[index].max_y = float(_point_group_value(group, "max_y"))
    return packed, len(rows)


class PreparedOptixPointGroupNearestWitness2D:
    """Prepared OptiX 2-D point-group nearest-witness scene.

    The primitive is app-agnostic: the caller supplies a point array and a set
    of group MBRs whose spans reference contiguous ranges inside that point
    array. OptiX builds a BVH over the group bounds, then query calls can ask
    for threshold coverage or one nearest in-radius witness per query point.
    """

    def __init__(self, search_points, groups, *, max_radius: float):
        if max_radius < 0:
            raise ValueError("max_radius must be non-negative")
        packed = search_points if isinstance(search_points, PackedPoints) else pack_points(records=search_points, dimension=2)
        if packed.dimension != 2:
            raise ValueError("prepare_optix_point_group_nearest_witness_2d requires 2-D points")
        packed_groups, group_count = _pack_point_group_bounds_2d(groups)
        self._packed_search = packed
        self._packed_groups = packed_groups
        self._group_count = group_count
        self._max_radius = float(max_radius)
        self._handle = ctypes.c_void_p()
        self._closed = False
        if packed.count == 0 or group_count == 0:
            return

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_point_group_nearest_witness_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_point_group_nearest_witness_2d; rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(
            packed.records,
            packed.count,
            packed_groups,
            group_count,
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

    def count_threshold_reached(self, query_points, *, radius: float, threshold: int = 0) -> int:
        if self._closed:
            raise RuntimeError("prepared OptiX point-group handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=2)
        if packed_queries.dimension != 2:
            raise ValueError("PreparedOptixPointGroupNearestWitness2D.count_threshold_reached requires 2-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0 or self._group_count == 0:
            return 0

        lib = _load_optix_library()
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_point_group_threshold_reached_2d")
        if symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_count_prepared_point_group_threshold_reached_2d; rebuild the OptiX backend from current main"
            )
        threshold_reached_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = symbol(
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

    def threshold_flags(self, query_points, *, radius: float, threshold: int = 0):
        """Return one uint32 threshold-reached flag per query point.

        This is the per-query form of ``count_threshold_reached``. It remains
        app-agnostic: callers provide points, group bounds, a radius, and a
        threshold; higher-level code decides how to use the safe/unsafe mask.
        """
        if self._closed:
            raise RuntimeError("prepared OptiX point-group handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=2)
        if packed_queries.dimension != 2:
            raise ValueError("PreparedOptixPointGroupNearestWitness2D.threshold_flags requires 2-D points")

        import numpy as _np

        if packed_queries.count == 0:
            return _np.asarray([], dtype=_np.uint32)
        if self._packed_search.count == 0 or self._group_count == 0:
            value = 1 if int(threshold) == 0 else 0
            return _np.full(packed_queries.count, value, dtype=_np.uint32)

        lib = _load_optix_library()
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_write_prepared_point_group_threshold_flags_2d")
        if symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_write_prepared_point_group_threshold_flags_2d; rebuild the OptiX backend from current main"
            )
        flags = (ctypes.c_uint32 * packed_queries.count)()
        error = ctypes.create_string_buffer(4096)
        status = symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.c_size_t(int(threshold)),
            flags,
            error,
            len(error),
        )
        _check_status(status, error)
        return _np.ctypeslib.as_array(flags).copy()

    def nearest_witness_rows(self, query_points, *, radius: float) -> tuple[dict[str, object], ...]:
        if self._closed:
            raise RuntimeError("prepared OptiX point-group handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=2)
        if packed_queries.dimension != 2:
            raise ValueError("PreparedOptixPointGroupNearestWitness2D.nearest_witness_rows requires 2-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0 or self._group_count == 0:
            return ()

        lib = _load_optix_library()
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_point_group_nearest_witness_2d")
        if symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_point_group_nearest_witness_2d; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
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
            row_type=_RtdlFixedRadiusNeighborRow,
            field_names=("query_id", "neighbor_id", "distance"),
        )
        try:
            return tuple(
                {
                    "query_id": int(row["query_id"]),
                    "neighbor_id": int(row["neighbor_id"]),
                    "distance": float(row["distance"]),
                }
                for row in view.to_dict_rows()
            )
        finally:
            view.close()

    def nearest_max_distance_row(self, query_points, *, radius: float) -> dict[str, object]:
        """Return the max-distance row after reducing nearest witnesses on device."""
        if self._closed:
            raise RuntimeError("prepared OptiX point-group handle is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self._max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        packed_queries = query_points if isinstance(query_points, PackedPoints) else pack_points(records=query_points, dimension=2)
        if packed_queries.dimension != 2:
            raise ValueError("PreparedOptixPointGroupNearestWitness2D.nearest_max_distance_row requires 2-D points")
        if packed_queries.count == 0 or self._packed_search.count == 0 or self._group_count == 0:
            return {"query_id": 0xFFFFFFFF, "neighbor_id": 0xFFFFFFFF, "distance": float("inf")}

        lib = _load_optix_library()
        symbol = _find_optional_backend_symbol(
            lib, "rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d"
        )
        if symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d; "
                "rebuild the OptiX backend from current main"
            )
        row = _RtdlFixedRadiusNeighborRow()
        error = ctypes.create_string_buffer(4096)
        status = symbol(
            self._handle,
            packed_queries.records,
            packed_queries.count,
            ctypes.c_double(float(radius)),
            ctypes.byref(row),
            error,
            len(error),
        )
        _check_status(status, error)
        return {
            "query_id": int(row.query_id),
            "neighbor_id": int(row.neighbor_id),
            "distance": float(row.distance),
        }

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_point_group_nearest_witness_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixPointGroupNearestWitness2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_point_group_nearest_witness_2d(
    search_points,
    groups,
    *,
    max_radius: float,
) -> PreparedOptixPointGroupNearestWitness2D:
    return PreparedOptixPointGroupNearestWitness2D(search_points, groups, max_radius=max_radius)


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


def get_last_segment_pair_phase_timings() -> dict[str, float | int | str] | None:
    return _get_last_segment_pair_phase_timings_from_library(_load_optix_library())


def get_last_closed_shape_membership_phase_timings() -> dict[str, float | int | str] | None:
    return _get_last_closed_shape_membership_phase_timings_from_library(_load_optix_library())


def get_last_fixed_radius_neighbors_3d_phase_timings() -> dict[str, float | int | str] | None:
    return _get_last_fixed_radius_neighbors_3d_phase_timings_from_library(_load_optix_library())


def _get_last_segment_pair_phase_timings_from_library(lib) -> dict[str, float | int | str] | None:
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_segment_pair_intersection_get_last_phase_timings")
    if symbol is None:
        return None
    symbol.argtypes = (
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_uint32),
    )
    symbol.restype = ctypes.c_int
    left_upload = ctypes.c_double(0.0)
    candidate_count = ctypes.c_double(0.0)
    candidate_write = ctypes.c_double(0.0)
    candidate_download = ctypes.c_double(0.0)
    exact_refine = ctypes.c_double(0.0)
    raw_candidates = ctypes.c_size_t(0)
    emitted = ctypes.c_size_t(0)
    mode = ctypes.c_uint32(0)
    status = symbol(
        ctypes.byref(left_upload),
        ctypes.byref(candidate_count),
        ctypes.byref(candidate_write),
        ctypes.byref(candidate_download),
        ctypes.byref(exact_refine),
        ctypes.byref(raw_candidates),
        ctypes.byref(emitted),
        ctypes.byref(mode),
    )
    if status != 0:
        return None
    mode_value = int(mode.value)
    mode_name = {
        1: "rows",
        2: "count",
        3: "first_hit_rows",
        4: "first_hit_count",
    }.get(mode_value, "none")
    result = {
        "mode": mode_name,
        "left_upload": float(left_upload.value),
        "candidate_count_pass": float(candidate_count.value),
        "candidate_write_pass": float(candidate_write.value),
        "candidate_download": float(candidate_download.value),
        "exact_refine": float(exact_refine.value),
        "raw_candidate_count": int(raw_candidates.value),
        "emitted_count": int(emitted.value),
    }
    if mode_name.startswith("first_hit"):
        result["device_witness_materialize"] = float(exact_refine.value)
    return result


def _get_last_closed_shape_membership_phase_timings_from_library(lib) -> dict[str, float | int | str] | None:
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_closed_shape_membership_get_last_phase_timings")
    if symbol is None:
        return None
    symbol.argtypes = (
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_uint32),
    )
    symbol.restype = ctypes.c_int
    point_pack = ctypes.c_double(0.0)
    point_upload = ctypes.c_double(0.0)
    candidate_count = ctypes.c_double(0.0)
    candidate_write = ctypes.c_double(0.0)
    candidate_download = ctypes.c_double(0.0)
    exact_refine = ctypes.c_double(0.0)
    raw_candidates = ctypes.c_size_t(0)
    emitted = ctypes.c_size_t(0)
    mode = ctypes.c_uint32(0)
    status = symbol(
        ctypes.byref(point_pack),
        ctypes.byref(point_upload),
        ctypes.byref(candidate_count),
        ctypes.byref(candidate_write),
        ctypes.byref(candidate_download),
        ctypes.byref(exact_refine),
        ctypes.byref(raw_candidates),
        ctypes.byref(emitted),
        ctypes.byref(mode),
    )
    if status != 0:
        return None
    mode_value = int(mode.value)
    return {
        "mode": "rows" if mode_value == 1 else "count" if mode_value == 2 else "none",
        "point_pack": float(point_pack.value),
        "point_upload": float(point_upload.value),
        "candidate_count_pass": float(candidate_count.value),
        "candidate_write_pass": float(candidate_write.value),
        "candidate_download": float(candidate_download.value),
        "exact_refine": float(exact_refine.value),
        "raw_candidate_count": int(raw_candidates.value),
        "emitted_count": int(emitted.value),
    }


def _get_last_fixed_radius_neighbors_3d_phase_timings_from_library(lib) -> dict[str, float | int | str] | None:
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_fixed_radius_neighbors_3d_get_last_phase_timings")
    if symbol is None:
        return None
    symbol.argtypes = (
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_uint32),
    )
    symbol.restype = ctypes.c_int
    prepare = ctypes.c_double(0.0)
    upload = ctypes.c_double(0.0)
    candidate_count = ctypes.c_double(0.0)
    count_download = ctypes.c_double(0.0)
    row_offset_upload = ctypes.c_double(0.0)
    candidate_write = ctypes.c_double(0.0)
    row_download = ctypes.c_double(0.0)
    exact_refine = ctypes.c_double(0.0)
    raw_candidates = ctypes.c_size_t(0)
    emitted = ctypes.c_size_t(0)
    mode = ctypes.c_uint32(0)
    status = symbol(
        ctypes.byref(prepare),
        ctypes.byref(upload),
        ctypes.byref(candidate_count),
        ctypes.byref(count_download),
        ctypes.byref(row_offset_upload),
        ctypes.byref(candidate_write),
        ctypes.byref(row_download),
        ctypes.byref(exact_refine),
        ctypes.byref(raw_candidates),
        ctypes.byref(emitted),
        ctypes.byref(mode),
    )
    if status != 0:
        return None
    mode_value = int(mode.value)
    return {
        "mode": {
            1: "all_pairs_cuda",
            2: "uniform_cell_compact",
            3: "simple_rt_traversal",
            4: "prepared_uniform_cell_compact",
            5: "prepared_uniform_cell_exact_count_summary",
            6: "prepared_uniform_cell_exact_distance_summary",
            7: "prepared_uniform_cell_exact_rows",
            8: "prepared_uniform_cell_ranked_rows",
            9: "prepared_uniform_cell_ranked_summary_rows",
        }.get(mode_value, "none"),
        "prepare": float(prepare.value),
        "upload": float(upload.value),
        "candidate_count_pass": float(candidate_count.value),
        "count_download_and_prefix": float(count_download.value),
        "row_offset_upload": float(row_offset_upload.value),
        "candidate_write_pass": float(candidate_write.value),
        "row_download": float(row_download.value),
        "exact_refine": float(exact_refine.value),
        "raw_candidate_count": int(raw_candidates.value),
        "emitted_count": int(emitted.value),
    }


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
        rows_ptr = ctypes.POINTER(_RtdlColumnRowIdRow)()
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
            row_type=_RtdlColumnRowIdRow,
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
        rows_ptr = ctypes.POINTER(_RtdlGroupedCountRow)()
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
            row_type=_RtdlGroupedCountRow,
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
    rows_ptr = ctypes.POINTER(_RtdlGroupedSumRow)()
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
        row_type=_RtdlGroupedSumRow,
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
class PreparedOptixColumnarExecution:
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


PreparedOptixDbExecution = PreparedOptixColumnarExecution


class OptixPreparedColumnarPayload:
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
        rows_ptr = ctypes.POINTER(_RtdlColumnRowIdRow)()
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
            row_type=_RtdlColumnRowIdRow,
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
        results_ptr = ctypes.POINTER(_RtdlColumnCompactSummaryResult)()
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
        rows_ptr = ctypes.POINTER(_RtdlGroupedCountRow)()
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
            row_type=_RtdlGroupedCountRow,
            field_names=("group_key", "count"),
        )

    def grouped_sum(self, clauses_array, group_key_field: bytes, value_field: bytes) -> OptixRowView:
        rows_ptr = ctypes.POINTER(_RtdlGroupedSumRow)()
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
            row_type=_RtdlGroupedSumRow,
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
        self._dataset = OptixPreparedColumnarPayload(
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

    @classmethod
    def from_columnar_record_set(cls, record_set, *, primary_fields=()) -> "PreparedOptixDbDataset":
        columns, field_maps, reverse_maps = _encode_all_db_text_column_mapping(
            _columnar_record_set_to_column_mapping(record_set)
        )
        columns_array, row_count, keepalive, columnar_metadata = _encode_db_column_mapping_columnar_with_metadata(
            columns,
            error_prefix="OptiX direct columnar record-set path",
        )
        prepared = cls.__new__(cls)
        prepared._field_maps = field_maps
        prepared._reverse_maps = reverse_maps
        prepared._dataset = OptixPreparedColumnarPayload(
            _load_optix_library(),
            None,
            None,
            row_count,
            primary_fields=primary_fields,
            columns_array=columns_array,
            field_count=len(columns_array),
            transfer="columnar",
            keepalive=keepalive,
        )
        prepared._fields_array = None
        prepared._row_values_array = None
        prepared._columns_array = columns_array
        prepared._transfer = "columnar_record_set"
        prepared._columnar_preparation_metadata = columnar_metadata
        prepared.row_count = row_count
        return prepared

    def close(self) -> None:
        self._dataset.close()

    def columnar_preparation_metadata(self) -> dict[str, object]:
        return dict(getattr(self, "_columnar_preparation_metadata", {}))

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

        encoded_requests: list[_RtdlColumnCompactSummaryRequest] = []
        request_meta: list[dict[str, object]] = []
        keepalive: list[object] = []
        for request in requests:
            operation = str(request["operation"])
            if operation == "conjunctive_scan_count":
                bundle = normalize_predicate_bundle(request["predicates"])
                clauses_array = _encode_db_clauses(self._encode_clauses(bundle.clauses))
                keepalive.append(clauses_array)
                encoded_requests.append(
                    _RtdlColumnCompactSummaryRequest(
                        _COLUMN_COMPACT_SUMMARY_OP_SCAN_COUNT,
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
                    _RtdlColumnCompactSummaryRequest(
                        _COLUMN_COMPACT_SUMMARY_OP_GROUPED_SUM
                        if operation == "grouped_sum_summary"
                        else _COLUMN_COMPACT_SUMMARY_OP_GROUPED_COUNT,
                        ctypes.cast(clauses_array, ctypes.c_void_p),
                        len(clauses_array),
                        group_key_field,
                        value_field,
                    )
                )
                request_meta.append({"name": str(request["name"]), "operation": operation, "group_key": group_key})
            else:
                raise ValueError(f"unsupported DB compact-summary batch operation: {operation}")

        requests_array = (_RtdlColumnCompactSummaryRequest * len(encoded_requests))(*encoded_requests)
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


class PreparedOptixColumnarPayload(PreparedOptixDbDataset):
    """Generic prepared columnar payload API; `PreparedOptixDbDataset` is legacy."""


def prepare_optix_columnar_payload(
    table_rows,
    *,
    primary_fields=(),
    transfer: str = "row",
) -> PreparedOptixColumnarPayload:
    return PreparedOptixColumnarPayload(table_rows, primary_fields=primary_fields, transfer=transfer)


def prepare_optix_columnar_record_set(record_set, *, primary_fields=()) -> PreparedOptixColumnarPayload:
    return PreparedOptixColumnarPayload.from_columnar_record_set(record_set, primary_fields=primary_fields)


def prepare_optix_partner_resident_columnar_record_set(
    descriptor,
    *,
    primary_fields=(),
    allow_scaffold_probe: bool = False,
):
    prepared_descriptor = (
        descriptor
        if isinstance(descriptor, PartnerResidentColumnarRecordSet)
        else prepare_partner_resident_columnar_record_set(descriptor, backend="optix")
    )
    plan = plan_partner_resident_columnar_native_execution(prepared_descriptor)
    if not allow_scaffold_probe:
        raise RuntimeError(
            f"{OPTIX_PARTNER_RESIDENT_COLUMNAR_DEVICE_SYMBOL} is scaffolded but not executable; "
            f"native_execution_allowed={plan['native_execution_allowed']} "
            f"status={PARTNER_RESIDENT_COLUMNAR_NATIVE_EXECUTION_STATUS}. "
            "Pass allow_scaffold_probe=True only to verify the native fail-closed symbol."
        )

    fields_array, keepalive = _encode_partner_resident_device_payload_fields(prepared_descriptor)
    primary_field_bytes = tuple(str(name).encode("utf-8") for name in primary_fields)
    primary_fields_array = (
        (ctypes.c_char_p * len(primary_field_bytes))(*primary_field_bytes)
        if primary_field_bytes
        else None
    )
    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(lib, OPTIX_PARTNER_RESIDENT_COLUMNAR_DEVICE_SYMBOL)
    if symbol is None:
        raise RuntimeError(
            "loaded OptiX backend library does not export "
            f"{OPTIX_PARTNER_RESIDENT_COLUMNAR_DEVICE_SYMBOL}; rebuild the OptiX backend from current main"
        )
    handle = ctypes.c_void_p()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        ctypes.c_size_t(prepared_descriptor.row_count),
        primary_fields_array,
        ctypes.c_size_t(len(primary_field_bytes)),
        ctypes.byref(handle),
        error,
        len(error),
    )
    keepalive = (keepalive, primary_field_bytes, primary_fields_array)
    _check_status(status, error)
    if handle:
        destroy = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_destroy")
        if destroy is not None:
            destroy(handle)
    raise RuntimeError("OptiX partner-resident columnar scaffold unexpectedly returned success")


def _raise_on_partner_resident_grouped_capacity_overflow(
    overflowed: ctypes.c_uint32,
    *,
    operation: str,
    group_capacity: int,
) -> None:
    if int(overflowed.value) == 0:
        return
    raise RuntimeError(
        "OptiX partner-resident grouped "
        f"{operation} overflowed explicit group_capacity={group_capacity}; "
        "increase group_capacity or remap group keys before using exact rows"
    )


def run_optix_partner_resident_columnar_grouped_count_i64(
    descriptor,
    query,
    *,
    allow_experimental_native: bool = False,
    group_capacity: int | None = None,
) -> tuple[dict[str, object], ...]:
    if not allow_experimental_native:
        raise RuntimeError(
            f"{OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_SYMBOL} is experimental; "
            "pass allow_experimental_native=True only for controlled partner-resident CUDA validation"
        )
    prepared_descriptor = (
        descriptor
        if isinstance(descriptor, PartnerResidentColumnarRecordSet)
        else prepare_partner_resident_columnar_record_set(descriptor, backend="optix")
    )
    normalized_query = normalize_grouped_query(query)
    if len(normalized_query.group_keys) != 1:
        raise ValueError("experimental partner-resident grouped_count supports exactly one group key")
    group_key = normalized_query.group_keys[0]
    resolved_group_capacity = _resolve_partner_resident_group_capacity(query, group_capacity)
    fields_array, keepalive = _encode_partner_resident_device_payload_fields(prepared_descriptor)
    clauses_array = _encode_db_clauses(normalized_query.predicates)
    group_key_field = group_key.encode("utf-8")
    keepalive = (keepalive, clauses_array, group_key_field)
    lib = _load_optix_library()
    symbol_name = (
        OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_WITH_CAPACITY_SYMBOL
        if resolved_group_capacity is not None
        else OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_SYMBOL
    )
    symbol = _find_optional_backend_symbol(lib, symbol_name)
    if symbol is None:
        raise RuntimeError(
            "loaded OptiX backend library does not export "
            f"{symbol_name}; rebuild the OptiX backend from current main"
        )
    rows_ptr = ctypes.POINTER(_RtdlGroupedCountRow)()
    row_count_out = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    common_args = (
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        ctypes.c_size_t(prepared_descriptor.row_count),
        clauses_array,
        ctypes.c_size_t(len(clauses_array)),
        group_key_field,
    )
    status = (
        symbol(
            *common_args,
            ctypes.c_size_t(resolved_group_capacity),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            ctypes.byref(overflowed),
            error,
            len(error),
        )
        if resolved_group_capacity is not None
        else symbol(
            *common_args,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
    )
    _check_status(status, error)
    if resolved_group_capacity is not None:
        _raise_on_partner_resident_grouped_capacity_overflow(
            overflowed,
            operation="count",
            group_capacity=resolved_group_capacity,
        )
    rows = OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count_out.value,
        row_type=_RtdlGroupedCountRow,
        field_names=("group_key", "count"),
    )
    try:
        return tuple(
            {group_key: int(rows.rows_ptr[index].group_key), "count": int(rows.rows_ptr[index].count)}
            for index in range(rows.row_count)
        )
    finally:
        rows.close()


def run_optix_partner_resident_columnar_grouped_sum_i64(
    descriptor,
    query,
    *,
    allow_experimental_native: bool = False,
    group_capacity: int | None = None,
) -> tuple[dict[str, object], ...]:
    if not allow_experimental_native:
        raise RuntimeError(
            f"{OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_SYMBOL} is experimental; "
            "pass allow_experimental_native=True only for controlled partner-resident CUDA validation"
        )
    prepared_descriptor = (
        descriptor
        if isinstance(descriptor, PartnerResidentColumnarRecordSet)
        else prepare_partner_resident_columnar_record_set(descriptor, backend="optix")
    )
    normalized_query = normalize_grouped_query(query)
    if len(normalized_query.group_keys) != 1:
        raise ValueError("experimental partner-resident grouped_sum supports exactly one group key")
    if not normalized_query.value_field:
        raise ValueError("experimental partner-resident grouped_sum requires a value_field")
    group_key = normalized_query.group_keys[0]
    resolved_group_capacity = _resolve_partner_resident_group_capacity(query, group_capacity)
    fields_array, keepalive = _encode_partner_resident_device_payload_fields(prepared_descriptor)
    clauses_array = _encode_db_clauses(normalized_query.predicates)
    group_key_field = group_key.encode("utf-8")
    value_field = normalized_query.value_field.encode("utf-8")
    keepalive = (keepalive, clauses_array, group_key_field, value_field)
    lib = _load_optix_library()
    symbol_name = (
        OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_WITH_CAPACITY_SYMBOL
        if resolved_group_capacity is not None
        else OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_SYMBOL
    )
    symbol = _find_optional_backend_symbol(lib, symbol_name)
    if symbol is None:
        raise RuntimeError(
            "loaded OptiX backend library does not export "
            f"{symbol_name}; rebuild the OptiX backend from current main"
        )
    rows_ptr = ctypes.POINTER(_RtdlGroupedSumRow)()
    row_count_out = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    common_args = (
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        ctypes.c_size_t(prepared_descriptor.row_count),
        clauses_array,
        ctypes.c_size_t(len(clauses_array)),
        group_key_field,
        value_field,
    )
    status = (
        symbol(
            *common_args,
            ctypes.c_size_t(resolved_group_capacity),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            ctypes.byref(overflowed),
            error,
            len(error),
        )
        if resolved_group_capacity is not None
        else symbol(
            *common_args,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count_out),
            error,
            len(error),
        )
    )
    _check_status(status, error)
    if resolved_group_capacity is not None:
        _raise_on_partner_resident_grouped_capacity_overflow(
            overflowed,
            operation="sum",
            group_capacity=resolved_group_capacity,
        )
    rows = OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count_out.value,
        row_type=_RtdlGroupedSumRow,
        field_names=("group_key", "sum"),
    )
    try:
        return tuple(
            {group_key: int(rows.rows_ptr[index].group_key), "sum": int(rows.rows_ptr[index].sum)}
            for index in range(rows.row_count)
        )
    finally:
        rows.close()


def run_optix_partner_resident_columnar_grouped_min_i64(
    descriptor,
    query,
    *,
    allow_experimental_native: bool = False,
    group_capacity: int | None = None,
) -> tuple[dict[str, object], ...]:
    return _run_optix_partner_resident_columnar_grouped_value_i64(
        descriptor,
        query,
        operation="min",
        symbol_name=OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MIN_I64_WITH_CAPACITY_SYMBOL,
        allow_experimental_native=allow_experimental_native,
        group_capacity=group_capacity,
    )


def run_optix_partner_resident_columnar_grouped_max_i64(
    descriptor,
    query,
    *,
    allow_experimental_native: bool = False,
    group_capacity: int | None = None,
) -> tuple[dict[str, object], ...]:
    return _run_optix_partner_resident_columnar_grouped_value_i64(
        descriptor,
        query,
        operation="max",
        symbol_name=OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MAX_I64_WITH_CAPACITY_SYMBOL,
        allow_experimental_native=allow_experimental_native,
        group_capacity=group_capacity,
    )


def run_optix_partner_resident_columnar_grouped_sum_count_i64(
    descriptor,
    query,
    *,
    allow_experimental_native: bool = False,
    group_capacity: int | None = None,
) -> tuple[dict[str, object], ...]:
    if not allow_experimental_native:
        raise RuntimeError(
            f"{OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL} is experimental; "
            "pass allow_experimental_native=True only for controlled partner-resident CUDA validation"
        )
    prepared_descriptor = (
        descriptor
        if isinstance(descriptor, PartnerResidentColumnarRecordSet)
        else prepare_partner_resident_columnar_record_set(descriptor, backend="optix")
    )
    normalized_query = normalize_grouped_query(query)
    if len(normalized_query.group_keys) != 1:
        raise ValueError("experimental partner-resident grouped_sum_count supports exactly one group key")
    if not normalized_query.value_field:
        raise ValueError("experimental partner-resident grouped_sum_count requires a value_field")
    group_key = normalized_query.group_keys[0]
    resolved_group_capacity = _resolve_partner_resident_group_capacity(query, group_capacity)
    if resolved_group_capacity is None:
        raise ValueError("experimental partner-resident grouped_sum_count requires explicit group_capacity")
    fields_array, keepalive = _encode_partner_resident_device_payload_fields(prepared_descriptor)
    clauses_array = _encode_db_clauses(normalized_query.predicates)
    group_key_field = group_key.encode("utf-8")
    value_field = normalized_query.value_field.encode("utf-8")
    keepalive = (keepalive, clauses_array, group_key_field, value_field)
    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(
        lib,
        OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL,
    )
    if symbol is None:
        raise RuntimeError(
            "loaded OptiX backend library does not export "
            f"{OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL}; "
            "rebuild the OptiX backend from current main"
        )
    rows_ptr = ctypes.POINTER(_RtdlGroupedSumCountRow)()
    row_count_out = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        ctypes.c_size_t(prepared_descriptor.row_count),
        clauses_array,
        ctypes.c_size_t(len(clauses_array)),
        group_key_field,
        value_field,
        ctypes.c_size_t(resolved_group_capacity),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        ctypes.byref(overflowed),
        error,
        len(error),
    )
    _check_status(status, error)
    _raise_on_partner_resident_grouped_capacity_overflow(
        overflowed,
        operation="sum_count",
        group_capacity=resolved_group_capacity,
    )
    rows = OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count_out.value,
        row_type=_RtdlGroupedSumCountRow,
        field_names=("group_key", "sum", "count"),
    )
    try:
        return tuple(
            {
                group_key: int(rows.rows_ptr[index].group_key),
                "sum": int(rows.rows_ptr[index].sum),
                "count": int(rows.rows_ptr[index].count),
            }
            for index in range(rows.row_count)
        )
    finally:
        rows.close()


def run_optix_partner_resident_columnar_grouped_stats_i64(
    descriptor,
    query,
    *,
    allow_experimental_native: bool = False,
    group_capacity: int | None = None,
) -> tuple[dict[str, object], ...]:
    if not allow_experimental_native:
        raise RuntimeError(
            f"{OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_STATS_I64_WITH_CAPACITY_SYMBOL} is experimental; "
            "pass allow_experimental_native=True only for controlled partner-resident CUDA validation"
        )
    prepared_descriptor = (
        descriptor
        if isinstance(descriptor, PartnerResidentColumnarRecordSet)
        else prepare_partner_resident_columnar_record_set(descriptor, backend="optix")
    )
    normalized_query = normalize_grouped_query(query)
    if len(normalized_query.group_keys) != 1:
        raise ValueError("experimental partner-resident grouped_stats supports exactly one group key")
    if not normalized_query.value_field:
        raise ValueError("experimental partner-resident grouped_stats requires a value_field")
    group_key = normalized_query.group_keys[0]
    resolved_group_capacity = _resolve_partner_resident_group_capacity(query, group_capacity)
    if resolved_group_capacity is None:
        raise ValueError("experimental partner-resident grouped_stats requires explicit group_capacity")
    fields_array, keepalive = _encode_partner_resident_device_payload_fields(prepared_descriptor)
    clauses_array = _encode_db_clauses(normalized_query.predicates)
    group_key_field = group_key.encode("utf-8")
    value_field = normalized_query.value_field.encode("utf-8")
    keepalive = (keepalive, clauses_array, group_key_field, value_field)
    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(
        lib,
        OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_STATS_I64_WITH_CAPACITY_SYMBOL,
    )
    if symbol is None:
        raise RuntimeError(
            "loaded OptiX backend library does not export "
            f"{OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_STATS_I64_WITH_CAPACITY_SYMBOL}; "
            "rebuild the OptiX backend from current main"
        )
    rows_ptr = ctypes.POINTER(_RtdlGroupedStatsRow)()
    row_count_out = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        ctypes.c_size_t(prepared_descriptor.row_count),
        clauses_array,
        ctypes.c_size_t(len(clauses_array)),
        group_key_field,
        value_field,
        ctypes.c_size_t(resolved_group_capacity),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        ctypes.byref(overflowed),
        error,
        len(error),
    )
    _check_status(status, error)
    _raise_on_partner_resident_grouped_capacity_overflow(
        overflowed,
        operation="stats",
        group_capacity=resolved_group_capacity,
    )
    rows = OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count_out.value,
        row_type=_RtdlGroupedStatsRow,
        field_names=("group_key", "count", "sum", "min", "max"),
    )
    try:
        return tuple(
            {
                group_key: int(rows.rows_ptr[index].group_key),
                "count": int(rows.rows_ptr[index].count),
                "sum": int(rows.rows_ptr[index].sum),
                "min": int(rows.rows_ptr[index].min),
                "max": int(rows.rows_ptr[index].max),
            }
            for index in range(rows.row_count)
        )
    finally:
        rows.close()


def run_optix_partner_resident_columnar_grouped_i64_reduction(
    descriptor,
    query,
    *,
    reduction: str,
    allow_experimental_native: bool = False,
    group_capacity: int | None = None,
    semantic_aggregate: str | None = None,
) -> dict[str, object]:
    """Dispatch one supported partner-resident grouped i64 reduction.

    This is the app-facing Python boundary. It keeps native symbol selection in
    the runtime layer and requires explicit dense group capacity for every mode.
    """
    if not allow_experimental_native:
        raise RuntimeError(
            "partner-resident grouped i64 reductions are experimental; pass "
            "allow_experimental_native=True only for controlled CUDA validation"
        )
    reduction_name = str(reduction)
    if reduction_name not in OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTIONS:
        supported = ", ".join(OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTIONS)
        raise ValueError(f"unsupported partner-resident grouped i64 reduction `{reduction_name}`; supported: {supported}")
    normalized_query = normalize_grouped_query(query)
    if len(normalized_query.group_keys) != 1:
        raise ValueError("partner-resident grouped i64 dispatcher supports exactly one group key")
    if reduction_name != "count" and not normalized_query.value_field:
        raise ValueError(f"partner-resident grouped i64 reduction `{reduction_name}` requires a value_field")
    resolved_group_capacity = _resolve_partner_resident_group_capacity(query, group_capacity)
    if resolved_group_capacity is None:
        raise ValueError("partner-resident grouped i64 dispatcher requires explicit group_capacity")

    if reduction_name == "count":
        rows = run_optix_partner_resident_columnar_grouped_count_i64(
            descriptor,
            query,
            allow_experimental_native=True,
            group_capacity=resolved_group_capacity,
        )
    elif reduction_name == "sum":
        rows = run_optix_partner_resident_columnar_grouped_sum_i64(
            descriptor,
            query,
            allow_experimental_native=True,
            group_capacity=resolved_group_capacity,
        )
    elif reduction_name == "min":
        rows = run_optix_partner_resident_columnar_grouped_min_i64(
            descriptor,
            query,
            allow_experimental_native=True,
            group_capacity=resolved_group_capacity,
        )
    elif reduction_name == "max":
        rows = run_optix_partner_resident_columnar_grouped_max_i64(
            descriptor,
            query,
            allow_experimental_native=True,
            group_capacity=resolved_group_capacity,
        )
    elif reduction_name == "sum_count":
        rows = run_optix_partner_resident_columnar_grouped_sum_count_i64(
            descriptor,
            query,
            allow_experimental_native=True,
            group_capacity=resolved_group_capacity,
        )
    else:
        rows = run_optix_partner_resident_columnar_grouped_stats_i64(
            descriptor,
            query,
            allow_experimental_native=True,
            group_capacity=resolved_group_capacity,
        )

    return {
        "rows": rows,
        "metadata": _partner_resident_grouped_i64_reduction_metadata(
            normalized_query,
            reduction_name=reduction_name,
            semantic_aggregate=semantic_aggregate,
            group_capacity=resolved_group_capacity,
            row_count=len(rows),
        ),
    }


def _partner_resident_grouped_i64_reduction_metadata(
    normalized_query,
    *,
    reduction_name: str,
    semantic_aggregate: str | None,
    group_capacity: int,
    row_count: int,
) -> dict[str, object]:
    symbol_name = _OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTION_SYMBOLS[reduction_name]
    grouped_reduction_spec = GroupedReductionSpec(
        operation=_OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTION_OPERATIONS[reduction_name],
        group_keys=tuple(normalized_query.group_keys),
        value_field=None if reduction_name == "count" else normalized_query.value_field,
        group_capacity=group_capacity,
    )
    capacity_status = GroupedReductionCapacityStatus(
        group_capacity=group_capacity,
        row_count=row_count,
        required_capacity=row_count,
        overflowed=False,
    )
    result_fields = [normalized_query.group_keys[0]]
    if reduction_name == "stats":
        result_fields.extend(("count", "sum", "min", "max"))
    elif reduction_name == "sum_count":
        result_fields.extend(("sum", "count"))
    elif reduction_name == "count":
        result_fields.append("count")
    else:
        result_fields.append(reduction_name)
    return {
        "partner_resident_grouped_i64_dispatcher": True,
        "partner_resident_grouped_i64_dispatcher_version": "goal2519",
        "operation": reduction_name,
        "reduction": reduction_name,
        "grouped_reduction_contract": grouped_reduction_spec.to_metadata(),
        "grouped_reduction_capacity_status": capacity_status.to_metadata(),
        "semantic_aggregate": str(semantic_aggregate) if semantic_aggregate is not None else reduction_name,
        "group_keys": list(normalized_query.group_keys),
        "group_key_field": normalized_query.group_keys[0],
        "value_field": normalized_query.value_field,
        "predicate_count": len(normalized_query.predicates),
        "group_capacity": group_capacity,
        "group_capacity_explicit": True,
        "native_reduction_symbol": symbol_name,
        "native_grouped_reduction_symbol": symbol_name,
        "result_fields": result_fields,
        "native_launch_count": 1,
        "fused_native_reduction": reduction_name in {"sum_count", "stats"},
        "fused_native_reduction_symbol": symbol_name if reduction_name in {"sum_count", "stats"} else None,
        "generic_sum_count_abi_used": reduction_name == "sum_count",
        "generic_stats_abi_used": reduction_name == "stats",
        "native_avg_abi_added": False,
        "native_abi_added": False,
        "experimental_native_execution": True,
        "allow_experimental_native_required": True,
        "compact_grouped_output_materialized": True,
        "input_table_copied_back_to_python_rows": False,
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "Experimental OptiX partner-resident grouped i64 reduction dispatch. "
            "The runtime selects generic grouped native reductions from app-neutral "
            "operation names; this does not authorize SQL, DBMS, true zero-copy, "
            "whole-app, or public performance wording."
        ),
    }



def _run_optix_partner_resident_columnar_grouped_value_i64(
    descriptor,
    query,
    *,
    operation: str,
    symbol_name: str,
    allow_experimental_native: bool,
    group_capacity: int | None,
) -> tuple[dict[str, object], ...]:
    if not allow_experimental_native:
        raise RuntimeError(
            f"{symbol_name} is experimental; pass allow_experimental_native=True only for controlled "
            "partner-resident CUDA validation"
        )
    prepared_descriptor = (
        descriptor
        if isinstance(descriptor, PartnerResidentColumnarRecordSet)
        else prepare_partner_resident_columnar_record_set(descriptor, backend="optix")
    )
    normalized_query = normalize_grouped_query(query)
    if len(normalized_query.group_keys) != 1:
        raise ValueError(f"experimental partner-resident grouped_{operation} supports exactly one group key")
    if not normalized_query.value_field:
        raise ValueError(f"experimental partner-resident grouped_{operation} requires a value_field")
    group_key = normalized_query.group_keys[0]
    resolved_group_capacity = _resolve_partner_resident_group_capacity(query, group_capacity)
    if resolved_group_capacity is None:
        raise ValueError(
            f"experimental partner-resident grouped_{operation} requires explicit group_capacity"
        )
    fields_array, keepalive = _encode_partner_resident_device_payload_fields(prepared_descriptor)
    clauses_array = _encode_db_clauses(normalized_query.predicates)
    group_key_field = group_key.encode("utf-8")
    value_field = normalized_query.value_field.encode("utf-8")
    keepalive = (keepalive, clauses_array, group_key_field, value_field)
    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(lib, symbol_name)
    if symbol is None:
        raise RuntimeError(
            "loaded OptiX backend library does not export "
            f"{symbol_name}; rebuild the OptiX backend from current main"
        )
    rows_ptr = ctypes.POINTER(_RtdlGroupedSumRow)()
    row_count_out = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        ctypes.c_size_t(prepared_descriptor.row_count),
        clauses_array,
        ctypes.c_size_t(len(clauses_array)),
        group_key_field,
        value_field,
        ctypes.c_size_t(resolved_group_capacity),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        ctypes.byref(overflowed),
        error,
        len(error),
    )
    _check_status(status, error)
    _raise_on_partner_resident_grouped_capacity_overflow(
        overflowed,
        operation=operation,
        group_capacity=resolved_group_capacity,
    )
    rows = OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count_out.value,
        row_type=_RtdlGroupedSumRow,
        field_names=("group_key", operation),
    )
    try:
        return tuple(
            {group_key: int(rows.rows_ptr[index].group_key), operation: int(rows.rows_ptr[index].sum)}
            for index in range(rows.row_count)
        )
    finally:
        rows.close()


def _resolve_partner_resident_group_capacity(query, group_capacity: int | None) -> int | None:
    raw_capacity = group_capacity
    if raw_capacity is None and isinstance(query, Mapping):
        raw_capacity = query.get("group_capacity")
    if raw_capacity is None:
        return None
    if isinstance(raw_capacity, bool) or not isinstance(raw_capacity, int):
        raise ValueError("experimental partner-resident group_capacity must be a positive integer")
    if raw_capacity <= 0 or raw_capacity > _DB_MAX_ROWS_PER_JOB:
        raise ValueError("experimental partner-resident group_capacity must be in 1..1000000")
    return int(raw_capacity)


def _encode_partner_resident_device_payload_fields(
    descriptor: PartnerResidentColumnarRecordSet,
) -> tuple[object, tuple[object, ...]]:
    encoded_fields = []
    keepalive: list[object] = []
    for field in descriptor.fields:
        if not isinstance(field, DeviceColumnDescriptor):
            raise ValueError("partner-resident fields must be DeviceColumnDescriptor instances")
        name_bytes = field.name.encode("utf-8")
        keepalive.append(name_bytes)
        encoded_fields.append(
            _RtdlDevicePayloadField(
                name_bytes,
                _partner_resident_device_payload_kind(field.logical_kind),
                _partner_resident_device_payload_dtype(field.dtype_token),
                _DEVICE_PAYLOAD_DEVICE_CUDA,
                int(field.device_id),
                int(field.element_count),
                int(field.stride_bytes),
                int(field.device_ptr),
            )
        )
    return (_RtdlDevicePayloadField * len(encoded_fields))(*encoded_fields), tuple(keepalive)


def _partner_resident_device_payload_kind(logical_kind: str) -> int:
    if logical_kind in {"row_id", "int64"}:
        return _DB_KIND_INT64
    if logical_kind == "float64":
        return _DB_KIND_FLOAT64
    raise ValueError(f"unsupported partner-resident logical kind: {logical_kind}")


def _partner_resident_device_payload_dtype(dtype: str) -> int:
    normalized = _partner_resident_dtype_token(dtype)
    if normalized == "int64":
        return _DEVICE_PAYLOAD_DTYPE_INT64
    if normalized == "uint32":
        return _DEVICE_PAYLOAD_DTYPE_UINT32
    if normalized in {"float64", "double"}:
        return _DEVICE_PAYLOAD_DTYPE_FLOAT64
    raise ValueError(f"unsupported partner-resident dtype: {dtype}")


def _partner_resident_device_payload_itemsize(dtype: str) -> int:
    normalized = _partner_resident_dtype_token(dtype)
    if normalized in {"int64", "float64", "double"}:
        return 8
    if normalized == "uint32":
        return 4
    raise ValueError(f"unsupported partner-resident dtype: {dtype}")


def _partner_resident_device_payload_stride_bytes(
    strides: tuple[int, ...] | None,
    *,
    itemsize: int,
) -> int:
    if strides in (None, (1,), (itemsize,)):
        return itemsize
    raise ValueError("partner-resident device payload fields must be contiguous")


def _partner_resident_dtype_token(dtype: str) -> str:
    normalized = str(dtype).strip().lower()
    if normalized.startswith("torch."):
        normalized = normalized.removeprefix("torch.")
    if normalized.startswith("numpy."):
        normalized = normalized.removeprefix("numpy.")
    aliases = {
        "int64_t": "int64",
        "longlong": "int64",
        "long long": "int64",
        "uint32_t": "uint32",
        "unsigned int": "uint32",
        "float64": "float64",
        "double": "double",
    }
    return aliases.get(normalized, normalized)


def _db_primary_fields_from_clauses(clauses) -> tuple[str, ...]:
    fields = []
    for clause in clauses:
        name = str(clause.field)
        if name not in fields:
            fields.append(name)
        if len(fields) == 3:
            break
    return tuple(fields)


OptixPreparedDbDataset = OptixPreparedColumnarPayload


def _prepare_columnar_optix_execution(compiled: CompiledKernel, normalized_inputs, lib) -> PreparedOptixColumnarExecution:
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
        dataset = OptixPreparedColumnarPayload(
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
        return PreparedOptixColumnarExecution(
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
    dataset = OptixPreparedColumnarPayload(
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
    return PreparedOptixColumnarExecution(
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
    if dimension not in {None, 2, 3}:
        raise ValueError("points dimension must be one of: 2, 3")
    vectorized = _pack_points_columns_numpy(ids, x, y, z, dimension=dimension)
    if vectorized is not None:
        return vectorized
    ids_l = _coerce_list("ids", ids)
    x_l = _coerce_list("x", x)
    y_l = _coerce_list("y", y)
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

    arr = (_RtdlRay3D * n).from_buffer(buf)
    return PackedRays(records=arr, count=n, dimension=3, owner=buf)


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

    arr = (_RtdlRay2D * n).from_buffer(buf)
    return PackedRays(records=arr, count=n, dimension=2, owner=buf)


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

    arr = (_RtdlTriangle * n).from_buffer(buf)
    return PackedTriangles(records=arr, count=n, dimension=2, owner=buf)


def pack_triangles_3d_from_arrays(
    ids,
    x0,
    y0,
    z0,
    x1,
    y1,
    z1,
    x2,
    y2,
    z2,
) -> PackedTriangles:
    """Fast bulk packing of 3-D triangles from array-like inputs."""
    try:
        import numpy as _np
    except ImportError:  # pragma: no cover
        raise RuntimeError("pack_triangles_3d_from_arrays requires numpy")

    ids_a = _np.asarray(ids, dtype=_np.uint32)
    x0_a = _np.asarray(x0, dtype=_np.float64)
    y0_a = _np.asarray(y0, dtype=_np.float64)
    z0_a = _np.asarray(z0, dtype=_np.float64)
    x1_a = _np.asarray(x1, dtype=_np.float64)
    y1_a = _np.asarray(y1, dtype=_np.float64)
    z1_a = _np.asarray(z1, dtype=_np.float64)
    x2_a = _np.asarray(x2, dtype=_np.float64)
    y2_a = _np.asarray(y2, dtype=_np.float64)
    z2_a = _np.asarray(z2, dtype=_np.float64)

    n = len(ids_a)
    if any(len(field) != n for field in (x0_a, y0_a, z0_a, x1_a, y1_a, z1_a, x2_a, y2_a, z2_a)):
        raise ValueError("triangle arrays must have equal lengths")

    _dtype = _np.dtype({
        "names": ["id", "x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2", "z2"],
        "formats": [
            _np.uint32,
            _np.float64,
            _np.float64,
            _np.float64,
            _np.float64,
            _np.float64,
            _np.float64,
            _np.float64,
            _np.float64,
            _np.float64,
        ],
        "offsets": [
            _RtdlTriangle3D.id.offset,
            _RtdlTriangle3D.x0.offset,
            _RtdlTriangle3D.y0.offset,
            _RtdlTriangle3D.z0.offset,
            _RtdlTriangle3D.x1.offset,
            _RtdlTriangle3D.y1.offset,
            _RtdlTriangle3D.z1.offset,
            _RtdlTriangle3D.x2.offset,
            _RtdlTriangle3D.y2.offset,
            _RtdlTriangle3D.z2.offset,
        ],
        "itemsize": ctypes.sizeof(_RtdlTriangle3D),
    })
    buf = _np.empty(n, dtype=_dtype)
    buf["id"] = ids_a
    buf["x0"] = x0_a
    buf["y0"] = y0_a
    buf["z0"] = z0_a
    buf["x1"] = x1_a
    buf["y1"] = y1_a
    buf["z1"] = z1_a
    buf["x2"] = x2_a
    buf["y2"] = y2_a
    buf["z2"] = z2_a

    arr = (_RtdlTriangle3D * n).from_buffer(buf)
    return PackedTriangles(records=arr, count=n, dimension=3, owner=buf)


_PARTNER_RAY_2D_COLUMNS = ("ids", "ox", "oy", "dx", "dy", "tmax")
_PARTNER_TRIANGLE_2D_COLUMNS = ("ids", "x0", "y0", "x1", "y1", "x2", "y2")
_PARTNER_RAY_3D_COLUMNS = ("ids", "ox", "oy", "oz", "dx", "dy", "dz", "tmax")
_PARTNER_TRIANGLE_3D_COLUMNS = ("ids", "x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2", "z2")
_PARTNER_POINT_2D_COLUMNS = ("ids", "x", "y")
_OPTIX_PARTNER_DEVICE_ANYHIT_SYMBOL = "rtdl_optix_count_ray_primitive_anyhit_2d_device_columns"
_OPTIX_PARTNER_PREPARED_DEVICE_RAYS_SYMBOL = "rtdl_optix_count_prepared_ray_anyhit_2d_device_rays"
_OPTIX_PARTNER_PREPARED_DEVICE_OUTPUT_FLAGS_SYMBOL = "rtdl_optix_write_prepared_ray_anyhit_2d_device_flags"
_OPTIX_PARTNER_PREPARED_DEVICE_WITNESSES_SYMBOL = "rtdl_optix_write_prepared_ray_anyhit_2d_device_witnesses"
_OPTIX_PARTNER_PREPARED_DEVICE_ALL_WITNESSES_SYMBOL = (
    "rtdl_optix_write_prepared_ray_anyhit_2d_device_all_witnesses"
)
_OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_TRIANGLES_SYMBOL = (
    "rtdl_optix_static_triangle_scene_3d_create_device_triangles"
)
_OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_WEIGHTED_SUM_SYMBOL = (
    "rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum_device_rays"
)
_OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_HIT_COUNT_SUM_SYMBOL = (
    "rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum_device_rays"
)
_OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLES_SYMBOL = "rtdl_optix_prepare_ray_anyhit_2d_device_triangles"
_OPTIX_PARTNER_PREPARED_DEVICE_TRIANGLE_COLUMNS_AABBS_SYMBOL = (
    "rtdl_optix_prepare_ray_anyhit_2d_device_triangle_columns_aabbs"
)
_OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_SEARCH_SYMBOL = (
    "rtdl_optix_prepare_fixed_radius_count_threshold_2d_device_search_columns"
)
_OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_QUERY_OUTPUT_SYMBOL = (
    "rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns"
)
_OPTIX_PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_3D_DEVICE_OUTPUT_SYMBOL = (
    "rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs"
)
_OPTIX_PREPARED_FIXED_RADIUS_ADJACENCY_3D_DEVICE_OUTPUT_SYMBOL = (
    "rtdl_optix_write_prepared_fixed_radius_adjacency_3d_device_outputs"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_OPTIONS_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs_with_options"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs_with_execution_options"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_OPTIONS_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_options"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_execution_options"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_OPTIONS_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_options"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_EXECUTION_OPTIONS_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_execution_options"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_OPTIONS_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_with_options"
)
_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL = (
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_with_execution_options"
)


def _grouped_union_direct_side_effect_policy(enabled: bool) -> str:
    return (
        "intersection_program_side_effect_no_anyhit_report"
        if enabled
        else "disabled_by_default_anyhit_side_effect"
    )


def _require_bool(value: bool, *, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a bool")
    return value


def _partner_dtype_token(dtype) -> str:
    token = str(dtype).lower()
    if "." in token:
        token = token.rsplit(".", 1)[-1]
    return token


def _partner_dtype_itemsize(dtype_token: str) -> int:
    if dtype_token in {"uint32", "int32", "float32", "float"}:
        return 4
    if dtype_token in {"int64", "uint64", "float64", "double"}:
        return 8
    raise ValueError(f"unsupported partner dtype for stride validation: {dtype_token!r}")


def _partner_contiguous_column_strides(strides, *, itemsize: int) -> bool:
    return strides in (None, (1,), (itemsize,))


def _partner_contiguous_aabb_strides(strides) -> bool:
    return strides in (None, (6, 1), (24, 4))


def _require_partner_device_ray_column_layout(handoffs: dict) -> None:
    expected_dtypes = {
        "ids": {"uint32"},
        "ox": {"float32", "float64", "double"},
        "oy": {"float32", "float64", "double"},
        "dx": {"float32", "float64", "double"},
        "dy": {"float32", "float64", "double"},
        "tmax": {"float32", "float64", "double"},
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


def _require_partner_device_ray3d_column_layout(handoffs: dict) -> None:
    expected_dtypes = {
        "ids": {"uint32"},
        "ox": {"float64", "double"},
        "oy": {"float64", "double"},
        "oz": {"float64", "double"},
        "dx": {"float64", "double"},
        "dy": {"float64", "double"},
        "dz": {"float64", "double"},
        "tmax": {"float64", "double"},
    }
    expected_count = None
    expected_device = None
    for name in _PARTNER_RAY_3D_COLUMNS:
        handoff = handoffs[name]
        dtype = _partner_dtype_token(handoff.dtype)
        if dtype not in expected_dtypes[name]:
            allowed = ", ".join(sorted(expected_dtypes[name]))
            raise ValueError(f"partner device 3-D ray column {name!r} must use dtype {allowed}")
        if not _partner_contiguous_column_strides(
            handoff.strides,
            itemsize=_partner_dtype_itemsize(dtype),
        ):
            raise ValueError(f"partner device 3-D ray column {name!r} must be contiguous")
        count = int(handoff.shape[0])
        if expected_count is None:
            expected_count = count
        elif count != expected_count:
            raise ValueError("partner device 3-D ray columns must have matching lengths")
        device = (handoff.device_type, handoff.device_id)
        if expected_device is None:
            expected_device = device
        elif device != expected_device:
            raise ValueError("partner device 3-D ray columns must live on the same CUDA device")


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


def _require_partner_device_triangle3d_column_layout(handoffs: dict) -> None:
    expected_dtypes = {
        "ids": {"uint32"},
        "x0": {"float64", "double"},
        "y0": {"float64", "double"},
        "z0": {"float64", "double"},
        "x1": {"float64", "double"},
        "y1": {"float64", "double"},
        "z1": {"float64", "double"},
        "x2": {"float64", "double"},
        "y2": {"float64", "double"},
        "z2": {"float64", "double"},
    }
    expected_count = None
    expected_device = None
    for name in _PARTNER_TRIANGLE_3D_COLUMNS:
        handoff = handoffs[name]
        dtype = _partner_dtype_token(handoff.dtype)
        if dtype not in expected_dtypes[name]:
            allowed = ", ".join(sorted(expected_dtypes[name]))
            raise ValueError(f"partner device 3-D triangle column {name!r} must use dtype {allowed}")
        if not _partner_contiguous_column_strides(
            handoff.strides,
            itemsize=_partner_dtype_itemsize(dtype),
        ):
            raise ValueError(f"partner device 3-D triangle column {name!r} must be contiguous")
        count = int(handoff.shape[0])
        if expected_count is None:
            expected_count = count
        elif count != expected_count:
            raise ValueError("partner device 3-D triangle columns must have matching lengths")
        device = (handoff.device_type, handoff.device_id)
        if expected_device is None:
            expected_device = device
        elif device != expected_device:
            raise ValueError("partner device 3-D triangle columns must live on the same CUDA device")


def _require_partner_device_uint64_weight_layout(
    handoff,
    *,
    ray_count: int,
    expected_device: tuple[str, int],
) -> None:
    dtype = _partner_dtype_token(handoff.dtype)
    if dtype != "uint64":
        raise ValueError("partner device ray weight column must use dtype uint64")
    if tuple(handoff.shape) != (ray_count,):
        raise ValueError("partner device ray weight column must have shape (ray_count,)")
    if not _partner_contiguous_column_strides(
        handoff.strides,
        itemsize=_partner_dtype_itemsize(dtype),
    ):
        raise ValueError("partner device ray weight column must be contiguous")
    if (handoff.device_type, handoff.device_id) != expected_device:
        raise ValueError("partner device ray weight column must live on the same CUDA device as ray columns")


def _require_partner_device_point_column_layout(handoffs: dict, *, label: str) -> None:
    expected_dtypes = {
        "ids": {"uint32"},
        "x": {"float64", "double"},
        "y": {"float64", "double"},
    }
    expected_count = None
    expected_device = None
    for name in _PARTNER_POINT_2D_COLUMNS:
        handoff = handoffs[name]
        dtype = _partner_dtype_token(handoff.dtype)
        if dtype not in expected_dtypes[name]:
            allowed = ", ".join(sorted(expected_dtypes[name]))
            raise ValueError(f"partner device {label} point column {name!r} must use dtype {allowed}")
        if not _partner_contiguous_column_strides(
            handoff.strides,
            itemsize=_partner_dtype_itemsize(dtype),
        ):
            raise ValueError(f"partner device {label} point column {name!r} must be contiguous")
        count = int(handoff.shape[0])
        if expected_count is None:
            expected_count = count
        elif count != expected_count:
            raise ValueError(f"partner device {label} point columns must have matching lengths")
        device = (handoff.device_type, handoff.device_id)
        if expected_device is None:
            expected_device = device
        elif device != expected_device:
            raise ValueError(f"partner device {label} point columns must live on the same CUDA device")


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


def _require_partner_device_bounded_witness_output_layout(
    handoff,
    *,
    witness_capacity: int,
    expected_device: tuple[str, int],
) -> None:
    dtype = _partner_dtype_token(handoff.dtype)
    if dtype != "uint32":
        raise ValueError("partner device bounded-witness output buffer must use dtype uint32")
    if tuple(handoff.shape) != (witness_capacity,):
        raise ValueError("partner device bounded-witness output buffer must have shape (witness_capacity,)")
    if not _partner_contiguous_column_strides(
        handoff.strides,
        itemsize=_partner_dtype_itemsize(dtype),
    ):
        raise ValueError("partner device bounded-witness output buffer must be contiguous")
    if (handoff.device_type, handoff.device_id) != expected_device:
        raise ValueError("partner device bounded-witness output buffer must live on the same CUDA device as ray columns")


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


def pack_optix_fixed_radius_count_threshold_2d_device_point_inputs(
    point_columns: dict,
    *,
    label: str,
    native_symbol: str,
) -> dict[str, object]:
    """Validate caller-owned CUDA point columns for fixed-radius OptiX handoff."""
    point_handoffs, timings = _partner_device_descriptor_columns(
        point_columns,
        _PARTNER_POINT_2D_COLUMNS,
        label=label,
    )
    _require_partner_device_point_column_layout(point_handoffs, label=label)
    descriptors = tuple(point_handoffs[name] for name in _PARTNER_POINT_2D_COLUMNS)
    return {
        "points": point_handoffs,
        "metadata": {
            "backend": "optix",
            "transfer_mode": f"device_{label}_point_columns_zero_copy",
            "native_symbol": native_symbol,
            "source_protocols": tuple(sorted({handoff.source_protocol for handoff in descriptors})),
            "source_devices": tuple(sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in descriptors})),
            "point_count": int(point_handoffs["ids"].shape[0]),
            "direct_device_pointer_observed": True,
            "direct_device_handoff_authorized": True,
            f"{label}_point_columns_true_zero_copy_authorized": True,
            "partner_tensor_handoff_authorized": True,
            "rt_core_speedup_claim_authorized": False,
            "partner_phase_timings_s": timings,
        },
    }


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


def pack_optix_static_triangle_scene_3d_device_triangle_inputs(triangle_columns: dict) -> dict[str, object]:
    """Validate partner-owned CUDA 3-D triangle columns for generic OptiX summaries.

    The native engine packs these generic columns on GPU into RTDL's internal
    triangle/AABB layout before building the OptiX GAS. No graph or app
    semantics are part of this ABI.
    """
    triangle_handoffs, timings = _partner_device_descriptor_columns(
        triangle_columns,
        _PARTNER_TRIANGLE_3D_COLUMNS,
        label="triangle3d",
    )
    _require_partner_device_triangle3d_column_layout(triangle_handoffs)
    descriptors = tuple(triangle_handoffs[name] for name in _PARTNER_TRIANGLE_3D_COLUMNS)
    return {
        "triangles": triangle_handoffs,
        "metadata": {
            "backend": "optix",
            "transfer_mode": "device_triangle3d_columns_gpu_pack_gas_build",
            "native_symbol": _OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_TRIANGLES_SYMBOL,
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


def pack_optix_static_triangle_scene_3d_device_ray_inputs(ray_columns: dict) -> dict[str, object]:
    """Validate partner-owned CUDA 3-D ray columns for generic OptiX summaries."""
    ray_handoffs, timings = _partner_device_descriptor_columns(
        ray_columns,
        _PARTNER_RAY_3D_COLUMNS,
        label="ray3d",
    )
    _require_partner_device_ray3d_column_layout(ray_handoffs)
    descriptors = tuple(ray_handoffs[name] for name in _PARTNER_RAY_3D_COLUMNS)
    return {
        "rays": ray_handoffs,
        "metadata": {
            "backend": "optix",
            "transfer_mode": "device_ray3d_columns_gpu_pack",
            "source_protocols": tuple(sorted({handoff.source_protocol for handoff in descriptors})),
            "source_devices": tuple(sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in descriptors})),
            "ray_count": int(ray_handoffs["ids"].shape[0]),
            "direct_device_pointer_observed": True,
            "direct_device_handoff_authorized": True,
            "ray_columns_true_zero_copy_authorized": False,
            "partner_tensor_handoff_authorized": True,
            "rt_core_speedup_claim_authorized": False,
            "partner_phase_timings_s": timings,
        },
    }


def pack_optix_static_triangle_scene_3d_device_weighted_ray_inputs(
    ray_columns: dict,
    ray_weights,
) -> dict[str, object]:
    packet = pack_optix_static_triangle_scene_3d_device_ray_inputs(ray_columns)
    ray_count = int(packet["metadata"]["ray_count"])
    rays = packet["rays"]
    expected_device = (rays["ids"].device_type, rays["ids"].device_id)
    validation_start = time.perf_counter()
    weights_handoff = _partner.prepare_direct_device_pointer_handoff(ray_weights, access="read")
    if len(weights_handoff.shape) != 1:
        raise ValueError("partner device ray weight column must be one-dimensional")
    _require_partner_device_uint64_weight_layout(
        weights_handoff,
        ray_count=ray_count,
        expected_device=expected_device,
    )
    weight_validation_s = time.perf_counter() - validation_start
    metadata = dict(packet["metadata"])
    metadata["native_symbol"] = _OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_WEIGHTED_SUM_SYMBOL
    metadata["ray_weights_device_resident"] = True
    metadata["partner_phase_timings_s"] = {
        **metadata["partner_phase_timings_s"],
        "weight_descriptor_validation_s": weight_validation_s,
    }
    metadata["source_protocols"] = tuple(
        sorted(set(metadata["source_protocols"]) | {weights_handoff.source_protocol})
    )
    metadata["source_devices"] = tuple(
        sorted(set(metadata["source_devices"]) | {f"{weights_handoff.device_type}:{weights_handoff.device_id}"})
    )
    return {
        "rays": rays,
        "ray_weights": weights_handoff,
        "metadata": metadata,
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


def pack_optix_ray_any_hit_2d_device_all_witness_outputs(
    ray_columns: dict,
    witness_ray_ids,
    witness_primitive_ids,
) -> dict[str, object]:
    """Validate partner-owned CUDA output columns for bounded all-hit witnesses."""
    ray_packet = pack_optix_ray_any_hit_2d_device_ray_inputs(ray_columns)
    ray_handoffs = ray_packet["rays"]
    for name in ("ox", "oy", "dx", "dy", "tmax"):
        dtype = _partner_dtype_token(ray_handoffs[name].dtype)
        if dtype not in {"float32", "float"}:
            raise ValueError(
                "partner device bounded all-witness ray column "
                f"{name!r} must use dtype float32"
            )
    ray_count = int(ray_packet["metadata"]["ray_count"])
    expected_device = (ray_handoffs["ids"].device_type, ray_handoffs["ids"].device_id)
    witness_ray_handoff = _partner.prepare_direct_device_pointer_handoff(witness_ray_ids, access="write")
    witness_primitive_handoff = _partner.prepare_direct_device_pointer_handoff(witness_primitive_ids, access="write")
    if tuple(witness_ray_handoff.shape) != tuple(witness_primitive_handoff.shape):
        raise ValueError("partner device bounded-witness output buffers must have matching shapes")
    if len(witness_ray_handoff.shape) != 1:
        raise ValueError("partner device bounded-witness output buffers must be one-dimensional")
    witness_capacity = int(witness_ray_handoff.shape[0])
    _require_partner_device_bounded_witness_output_layout(
        witness_ray_handoff,
        witness_capacity=witness_capacity,
        expected_device=expected_device,
    )
    _require_partner_device_bounded_witness_output_layout(
        witness_primitive_handoff,
        witness_capacity=witness_capacity,
        expected_device=expected_device,
    )
    descriptors = (*ray_handoffs.values(), witness_ray_handoff, witness_primitive_handoff)
    return {
        "rays": ray_handoffs,
        "witness_ray_ids": witness_ray_handoff,
        "witness_primitive_ids": witness_primitive_handoff,
        "metadata": {
            "backend": "optix",
            "transfer_mode": "device_ray_triangle_columns_bounded_all_witness_rows_zero_copy",
            "native_symbol": _OPTIX_PARTNER_PREPARED_DEVICE_ALL_WITNESSES_SYMBOL,
            "source_protocols": tuple(sorted({handoff.source_protocol for handoff in descriptors})),
            "source_devices": tuple(
                sorted({f"{handoff.device_type}:{handoff.device_id}" for handoff in descriptors})
            ),
            "ray_count": ray_count,
            "witness_row_capacity": witness_capacity,
            "witness_contract": "bounded all-hit witness rows; overflow must be false for exact row semantics",
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


def closed_shape_membership_2d_optix(points, shapes, *, result_mode: str = "positive_hits") -> tuple[dict[str, int], ...]:
    """Evaluate generic 2-D point/closed-shape membership on OptiX.

    This public helper intentionally uses shape/membership vocabulary. Higher
    layers may interpret the shape ids as regions, cells, app groups, or
    anything else; the engine surface does not encode that meaning.
    """

    if result_mode not in {"positive_hits", "full_matrix"}:
        raise ValueError("result_mode must be 'positive_hits' or 'full_matrix'")
    packed_points = points if isinstance(points, PackedPoints) else pack_points(records=points, dimension=2)
    packed_shapes = shapes if isinstance(shapes, PackedPolygons) else pack_polygons(records=shapes)
    if packed_points.dimension != 2:
        raise ValueError("closed_shape_membership_2d_optix requires 2-D points")

    shape_refs = ctypes.cast(packed_shapes.refs, ctypes.POINTER(_RtdlClosedShapeRef))

    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_point_closed_shape_membership_2d")
    if symbol is None:
        raise RuntimeError(
            "loaded OptiX backend library does not export "
            "rtdl_optix_run_point_closed_shape_membership_2d; rebuild the OptiX backend from current main"
        )
    rows_ptr = ctypes.POINTER(_RtdlPointClosedShapeMembershipRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        packed_points.records,
        packed_points.count,
        shape_refs,
        packed_shapes.polygon_count,
        packed_shapes.vertices_xy,
        packed_shapes.vertex_xy_count,
        1 if result_mode == "positive_hits" else 0,
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
        row_type=_RtdlPointClosedShapeMembershipRow,
        field_names=("point_id", "shape_id", "membership"),
    )
    try:
        return tuple(
            {
                "point_id": int(row["point_id"]),
                "shape_id": int(row["shape_id"]),
                "membership": int(row["membership"]),
            }
            for row in view.to_dict_rows()
        )
    finally:
        view.close()


class PreparedOptixPointClosedShapeMembership2D:
    """Prepared generic 2-D point/closed-shape membership scene."""

    def __init__(self, shapes):
        packed_shapes = shapes if isinstance(shapes, PackedPolygons) else pack_polygons(records=shapes)
        self._packed_shapes = packed_shapes
        self._handle = ctypes.c_void_p()
        self._closed = False
        self._lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_prepare_point_closed_shape_membership_2d",
        )
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_point_closed_shape_membership_2d; rebuild the OptiX backend from current main"
            )
        shape_refs = ctypes.cast(packed_shapes.refs, ctypes.POINTER(_RtdlClosedShapeRef))
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(
            shape_refs,
            packed_shapes.polygon_count,
            packed_shapes.vertices_xy,
            packed_shapes.vertex_xy_count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)

    @property
    def closed(self) -> bool:
        return self._closed

    def run_raw(self, points, *, result_mode: str = "positive_hits") -> OptixRowView:
        if self._closed:
            raise RuntimeError("prepared OptiX closed-shape membership handle is closed")
        if result_mode != "positive_hits":
            raise ValueError("prepared closed-shape membership currently supports result_mode='positive_hits'")
        packed_points = points if isinstance(points, PackedPoints) else pack_points(records=points, dimension=2)
        if packed_points.dimension != 2:
            raise ValueError("PreparedOptixPointClosedShapeMembership2D.run_raw requires 2-D points")
        if packed_points.count == 0 or self._packed_shapes.polygon_count == 0:
            empty = (_RtdlPointClosedShapeMembershipRow * 0)()
            return OptixRowView(
                library=self._lib,
                rows_ptr=ctypes.cast(empty, ctypes.POINTER(_RtdlPointClosedShapeMembershipRow)),
                row_count=0,
                row_type=_RtdlPointClosedShapeMembershipRow,
                field_names=("point_id", "shape_id", "membership"),
                _free_on_close=False,
                _owner=empty,
            )
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_run_prepared_point_closed_shape_membership_2d",
        )
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_run_prepared_point_closed_shape_membership_2d; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlPointClosedShapeMembershipRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_points.records,
            packed_points.count,
            1,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=self._lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlPointClosedShapeMembershipRow,
            field_names=("point_id", "shape_id", "membership"),
        )

    def run(self, points, *, result_mode: str = "positive_hits") -> tuple[dict[str, int], ...]:
        view = self.run_raw(points, result_mode=result_mode)
        try:
            return tuple(
                {
                    "point_id": int(row["point_id"]),
                    "shape_id": int(row["shape_id"]),
                    "membership": int(row["membership"]),
                }
                for row in view.to_dict_rows()
            )
        finally:
            view.close()

    def count(self, points) -> int:
        """Return the count of positive membership rows without Python row materialization."""
        if self._closed:
            raise RuntimeError("prepared OptiX closed-shape membership handle is closed")
        packed_points = points if isinstance(points, PackedPoints) else pack_points(records=points, dimension=2)
        if packed_points.dimension != 2:
            raise ValueError("PreparedOptixPointClosedShapeMembership2D.count requires 2-D points")
        if packed_points.count == 0 or self._packed_shapes.polygon_count == 0:
            return 0
        count_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_count_prepared_point_closed_shape_membership_2d",
        )
        if count_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_count_prepared_point_closed_shape_membership_2d; rebuild the OptiX backend from current main"
            )
        count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self._handle,
            packed_points.records,
            packed_points.count,
            ctypes.byref(count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(count.value)

    def last_phase_timings(self) -> dict[str, float | int | str] | None:
        return _get_last_closed_shape_membership_phase_timings_from_library(self._lib)

    def close(self) -> None:
        if not self._closed:
            destroy_symbol = _find_optional_backend_symbol(
                self._lib,
                "rtdl_optix_destroy_prepared_point_closed_shape_membership_2d",
            )
            if destroy_symbol is not None and self._handle:
                destroy_symbol(self._handle)
            self._closed = True

    def __enter__(self) -> "PreparedOptixPointClosedShapeMembership2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def prepare_point_closed_shape_membership_2d_optix(shapes) -> PreparedOptixPointClosedShapeMembership2D:
    return PreparedOptixPointClosedShapeMembership2D(shapes)


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


def _call_ray_closest_hit_optix_packed(compiled: CompiledKernel, packed, lib) -> OptixRowView:
    rays = packed[compiled.candidates.left.name]
    triangles = packed[compiled.candidates.right.name]
    rows_ptr = ctypes.POINTER(_RtdlRayClosestHitRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    if rays.dimension != 3 or triangles.dimension != 3:
        raise ValueError("OptiX ray_triangle_closest_hit currently requires 3-D rays and triangles")
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_ray_closest_hit_3d")
    if symbol is None:
        raise RuntimeError(
            "Loaded OptiX backend library does not export rtdl_optix_run_ray_closest_hit_3d. "
            "Rebuild it with 'make build-optix' from current main."
        )
    status = symbol(
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
    return OptixRowView(
        library=lib,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlRayClosestHitRow,
        field_names=("ray_id", "triangle_id", "t"),
    )


def ray_segment_group_count_2d_optix(rays, segments, segment_group_ids) -> tuple[dict[str, int], ...]:
    """Count finite 2-D ray/segment intersections grouped by caller-owned ids.

    This is a generic primitive: the backend sees rays, segments, and integer
    group labels only. Higher-level parity policies for point-in-shape or join
    predicates remain in Python/partner code.
    """
    packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(records=rays, dimension=2)
    packed_segments = segments if isinstance(segments, PackedSegments) else pack_segments(records=segments)
    if packed_rays.dimension != 2:
        raise ValueError("ray_segment_group_count_2d_optix requires 2-D rays")
    group_ids = list(segment_group_ids)
    if len(group_ids) != packed_segments.count:
        raise ValueError("segment_group_ids length must match segment count")
    for group_id in group_ids:
        if int(group_id) < 0 or int(group_id) > 0xFFFFFFFF:
            raise ValueError("segment_group_ids must fit uint32")
    group_array = (ctypes.c_uint32 * len(group_ids))(*[int(value) for value in group_ids])

    lib = _load_optix_library()
    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_ray_segment_group_count_2d")
    if symbol is None:
        raise RuntimeError(
            "loaded OptiX backend library does not export "
            "rtdl_optix_run_ray_segment_group_count_2d; rebuild the OptiX backend from current main"
        )
    rows_ptr = ctypes.POINTER(_RtdlRaySegmentGroupCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        packed_rays.records,
        packed_rays.count,
        packed_segments.records,
        packed_segments.count,
        group_array,
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
        row_type=_RtdlRaySegmentGroupCountRow,
        field_names=("ray_id", "group_id", "hit_count", "parity"),
    )
    try:
        return tuple(
            {
                "ray_id": int(row["ray_id"]),
                "group_id": int(row["group_id"]),
                "hit_count": int(row["hit_count"]),
                "parity": int(row["parity"]),
            }
            for row in view.to_dict_rows()
        )
    finally:
        view.close()


class PreparedOptixRaySegmentGroupCount2D:
    """Prepared generic 2-D ray/segment group-count scene.

    The segment set and its caller-supplied group ids are prepared once. Each
    ``run`` call uploads only rays and returns count/parity rows.
    """

    def __init__(self, segments, segment_group_ids):
        packed_segments = segments if isinstance(segments, PackedSegments) else pack_segments(records=segments)
        group_ids = list(segment_group_ids)
        if len(group_ids) != packed_segments.count:
            raise ValueError("segment_group_ids length must match segment count")
        for group_id in group_ids:
            if int(group_id) < 0 or int(group_id) > 0xFFFFFFFF:
                raise ValueError("segment_group_ids must fit uint32")
        self._packed_segments = packed_segments
        self._group_ids = (ctypes.c_uint32 * len(group_ids))(*[int(value) for value in group_ids])
        self._handle = ctypes.c_void_p()
        self._closed = False

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_ray_segment_group_count_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                "rtdl_optix_prepare_ray_segment_group_count_2d; rebuild the OptiX backend from current main"
            )
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(
            packed_segments.records,
            packed_segments.count,
            self._group_ids,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)

    @property
    def closed(self) -> bool:
        return self._closed

    def run(self, rays) -> tuple[dict[str, int], ...]:
        if self._closed:
            raise RuntimeError("prepared OptiX ray/segment group-count handle is closed")
        return self._run_with_symbol(rays, "rtdl_optix_run_prepared_ray_segment_group_count_2d")

    def run_odd_parity(self, rays) -> tuple[dict[str, int], ...]:
        """Return only rows whose grouped hit-count parity is odd."""

        if self._closed:
            raise RuntimeError("prepared OptiX ray/segment group-count handle is closed")
        return self._run_with_symbol(rays, "rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d")

    def _run_with_symbol(self, rays, symbol_name: str) -> tuple[dict[str, int], ...]:
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(records=rays, dimension=2)
        if packed_rays.dimension != 2:
            raise ValueError("PreparedOptixRaySegmentGroupCount2D requires 2-D rays")
        lib = _load_optix_library()
        run_symbol = _find_optional_backend_symbol(lib, symbol_name)
        if run_symbol is None:
            raise RuntimeError(
                "loaded OptiX backend library does not export "
                f"{symbol_name}; rebuild the OptiX backend from current main"
            )
        rows_ptr = ctypes.POINTER(_RtdlRaySegmentGroupCountRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_rays.records,
            packed_rays.count,
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
            row_type=_RtdlRaySegmentGroupCountRow,
            field_names=("ray_id", "group_id", "hit_count", "parity"),
        )
        try:
            return tuple(
                {
                    "ray_id": int(row["ray_id"]),
                    "group_id": int(row["group_id"]),
                    "hit_count": int(row["hit_count"]),
                    "parity": int(row["parity"]),
                }
                for row in view.to_dict_rows()
            )
        finally:
            view.close()

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_ray_segment_group_count_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixRaySegmentGroupCount2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_ray_segment_group_count_2d_optix(segments, segment_group_ids) -> PreparedOptixRaySegmentGroupCount2D:
    return PreparedOptixRaySegmentGroupCount2D(segments, segment_group_ids)


def _normalize_aabb2d_record(box, fallback_id: int) -> tuple[int, float, float, float, float]:
    try:
        box_id = int(getattr(box, "id", fallback_id))
        min_x = float(box.min_x)
        min_y = float(box.min_y)
        max_x = float(box.max_x)
        max_y = float(box.max_y)
    except AttributeError:
        try:
            if len(box) >= 4:
                box_id = int(getattr(box, "id", fallback_id))
                min_x = float(box[0])
                min_y = float(box[1])
                max_x = float(box[2])
                max_y = float(box[3])
            else:
                raise TypeError
        except TypeError as exc:
            raise TypeError(
                "AABB_INDEX_QUERY_2D requires boxes with min_x/min_y/max_x/max_y or 4-tuples"
            ) from exc
    if max_x < min_x or max_y < min_y:
        raise ValueError("AABB max bounds must be greater than or equal to min bounds")
    return box_id, min_x, min_y, max_x, max_y


def pack_aabbs_2d(boxes) -> PackedAabbs2D:
    if isinstance(boxes, PackedAabbs2D):
        return boxes
    normalized = tuple(_normalize_aabb2d_record(box, index) for index, box in enumerate(boxes))
    arr = (_RtdlAabb2D * len(normalized))(
        *[
            _RtdlAabb2D(box_id, min_x, min_y, max_x, max_y)
            for box_id, min_x, min_y, max_x, max_y in normalized
        ]
    )
    return PackedAabbs2D(records=arr, count=len(normalized))


def _normalize_point2d_xy(point) -> tuple[float, float]:
    try:
        return float(point.x), float(point.y)
    except AttributeError:
        try:
            if len(point) >= 2:
                return float(point[0]), float(point[1])
        except TypeError:
            pass
    raise TypeError("AABB_INDEX_QUERY_2D requires point-like inputs with x/y attributes or 2-tuples")


class PreparedOptixAabbQueries2D:
    """Prepared OptiX device query buffer for generic AABB index count queries."""

    def __init__(self, *, point_queries=None, box_queries=None):
        if (point_queries is None) == (box_queries is None):
            raise ValueError("prepare exactly one of point_queries or box_queries")
        self._handle = ctypes.c_void_p()
        self._closed = False
        if point_queries is not None:
            point_tuple = tuple(point_queries)
            point_xy = tuple(_normalize_point2d_xy(point) for point in point_tuple)
            packed = pack_points(
                ids=range(len(point_xy)),
                x=[xy[0] for xy in point_xy],
                y=[xy[1] for xy in point_xy],
                dimension=2,
            )
            self.operation = "point_contains"
            self.count = packed.count
            symbol_name = "rtdl_optix_prepare_aabb_point_queries_2d"
            args = (packed.records, packed.count)
        else:
            packed = pack_aabbs_2d(box_queries)
            self.operation = "range_contains"
            self.count = packed.count
            symbol_name = "rtdl_optix_prepare_aabb_box_queries_2d"
            args = (packed.records, packed.count)

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, symbol_name)
        if prepare_symbol is None:
            raise RuntimeError(
                f"Loaded OptiX backend library does not export {symbol_name}. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        status = prepare_symbol(*args, ctypes.byref(self._handle), error, len(error))
        _check_status(status, error)

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_aabb_queries_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixAabbQueries2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_aabb_point_queries_2d(point_queries) -> PreparedOptixAabbQueries2D:
    return PreparedOptixAabbQueries2D(point_queries=point_queries)


def prepare_optix_aabb_box_queries_2d(box_queries) -> PreparedOptixAabbQueries2D:
    return PreparedOptixAabbQueries2D(box_queries=box_queries)


class PreparedOptixAabbIndex2D:
    """Prepared generic 2-D AABB index using OptiX RT traversal."""

    supported_operations = OPTIX_AABB_INDEX_SUPPORTED_OPERATIONS

    def __init__(self, boxes):
        packed = pack_aabbs_2d(boxes)
        if packed.count == 0:
            raise ValueError("prepare_optix_aabb_index_2d requires at least one indexed box")
        self._packed_boxes = packed
        self._handle = ctypes.c_void_p()
        self._closed = False

        lib = _load_optix_library()
        prepare_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_aabb_index_2d")
        if prepare_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_prepare_aabb_index_2d. "
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

    def count(
        self,
        *,
        point_queries=(),
        box_queries=(),
        operation: str,
    ) -> int:
        if self._closed:
            raise RuntimeError("prepared OptiX AABB index handle is closed")
        normalized = operation.lower().replace("-", "_")
        if normalized not in _OPTIX_AABB_INDEX_OPERATION_CODES:
            raise ValueError(
                "unsupported OptiX AABB_INDEX_QUERY_2D operation: "
                f"{operation}"
            )

        point_count = 0
        box_count = 0
        point_ptr = None
        box_ptr = None
        if normalized == "point_contains":
            point_tuple = tuple(point_queries)
            point_xy = tuple(_normalize_point2d_xy(point) for point in point_tuple)
            packed_points = pack_points(
                ids=range(len(point_xy)),
                x=[xy[0] for xy in point_xy],
                y=[xy[1] for xy in point_xy],
                dimension=2,
            )
            point_count = packed_points.count
            point_ptr = packed_points.records
            if point_count == 0:
                return 0
        elif normalized in {"range_contains", "range_intersects"}:
            packed_boxes = pack_aabbs_2d(box_queries)
            box_count = packed_boxes.count
            box_ptr = packed_boxes.records
            if box_count == 0:
                return 0

        lib = _load_optix_library()
        count_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_aabb_index_2d")
        if count_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_count_prepared_aabb_index_2d. "
                "Rebuild it with 'make build-optix' from current main."
            )
        hit_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self._handle,
            point_ptr,
            point_count,
            box_ptr,
            box_count,
            _OPTIX_AABB_INDEX_OPERATION_CODES[normalized],
            ctypes.byref(hit_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(hit_count.value)

    def count_prepared_queries(self, queries: PreparedOptixAabbQueries2D, *, operation: str | None = None) -> int:
        if self._closed:
            raise RuntimeError("prepared OptiX AABB index handle is closed")
        if not isinstance(queries, PreparedOptixAabbQueries2D):
            raise ValueError("count_prepared_queries requires a PreparedOptixAabbQueries2D")
        if queries._closed:
            raise RuntimeError("prepared OptiX AABB query handle is closed")
        if queries.count == 0:
            return 0
        normalized = (operation if operation is not None else queries.operation).lower().replace("-", "_")
        if normalized not in _OPTIX_AABB_INDEX_OPERATION_CODES:
            raise ValueError(
                "unsupported OptiX AABB_INDEX_QUERY_2D operation: "
                f"{operation}"
            )
        lib = _load_optix_library()
        count_symbol = _find_optional_backend_symbol(
            lib,
            "rtdl_optix_count_prepared_aabb_index_2d_packed_queries",
        )
        if count_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_count_prepared_aabb_index_2d_packed_queries. "
                "Rebuild it with 'make build-optix' from current main."
            )
        hit_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = count_symbol(
            self._handle,
            queries._handle,
            _OPTIX_AABB_INDEX_OPERATION_CODES[normalized],
            ctypes.byref(hit_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return int(hit_count.value)

    def collect_range_intersection_rows(self, box_queries, *, row_capacity: int) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX AABB index handle is closed")
        if row_capacity < 0:
            raise ValueError("row_capacity must be non-negative")
        packed_boxes = pack_aabbs_2d(box_queries)
        row_array = (
            (_RtdlAabbPairRow * int(row_capacity))()
            if int(row_capacity) != 0
            else None
        )
        emitted_count = ctypes.c_size_t()
        overflowed = ctypes.c_uint32()
        lib = _load_optix_library()
        collect_symbol = _find_optional_backend_symbol(
            lib,
            "rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows",
        )
        if collect_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        status = collect_symbol(
            self._handle,
            packed_boxes.records,
            packed_boxes.count,
            row_array,
            int(row_capacity),
            ctypes.byref(emitted_count),
            ctypes.byref(overflowed),
            error,
            len(error),
        )
        _check_status(status, error)
        emitted = int(emitted_count.value)
        if int(overflowed.value) != 0:
            raise RuntimeError(
                "OptiX AABB_INDEX_QUERY_2D range_intersection_rows overflowed "
                f"capacity {int(row_capacity)}; emitted at least {emitted}; "
                "failure_mode=fail_closed_overflow"
            )
        if emitted > int(row_capacity):
            raise RuntimeError(
                "OptiX AABB_INDEX_QUERY_2D range_intersection_rows reported "
                f"emitted_count {emitted} beyond capacity {int(row_capacity)}; "
                "failure_mode=fail_closed_overflow"
            )
        rows = tuple(
            (int(row_array[index].query_id), int(row_array[index].indexed_id))
            for index in range(emitted)
        )
        return {
            "primitive": "AABB_INDEX_QUERY_2D",
            "contract": "generic_aabb_intersection_pair_rows_2d",
            "backend": "optix",
            "operation": "range_intersection_rows",
            "row_schema": ("query_id", "indexed_id"),
            "candidate_id_rows": rows,
            "valid_count": len(rows),
            "row_capacity": int(row_capacity),
            "overflowed": False,
            "complete_candidate_coverage": True,
            "rt_core_accelerated": True,
            "native_engine_customization": False,
            "native_generic_symbol": (
                "rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows"
            ),
            "claim_boundary": (
                "Generic OptiX AABB_INDEX_QUERY_2D range_intersection_rows output; "
                "returns app-name-free query/indexed id pairs only. Exact app "
                "semantics remain outside the engine."
            ),
        }

    def collect_point_contains_rows(self, point_queries, *, row_capacity: int) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX AABB index handle is closed")
        if row_capacity < 0:
            raise ValueError("row_capacity must be non-negative")
        packed_points = point_queries if isinstance(point_queries, PackedPoints) else pack_points(records=point_queries, dimension=2)
        if packed_points.dimension != 2:
            raise ValueError("OptiX AABB_INDEX_QUERY_2D point row output requires 2-D point queries")
        row_array = (
            (_RtdlAabbPairRow * int(row_capacity))()
            if int(row_capacity) != 0
            else None
        )
        emitted_count = ctypes.c_size_t()
        overflowed = ctypes.c_uint32()
        lib = _load_optix_library()
        collect_symbol = _find_optional_backend_symbol(
            lib,
            "rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows",
        )
        if collect_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        status = collect_symbol(
            self._handle,
            packed_points.records,
            packed_points.count,
            row_array,
            int(row_capacity),
            ctypes.byref(emitted_count),
            ctypes.byref(overflowed),
            error,
            len(error),
        )
        _check_status(status, error)
        emitted = int(emitted_count.value)
        if int(overflowed.value) != 0:
            raise RuntimeError(
                "OptiX AABB_INDEX_QUERY_2D point_contains_rows overflowed "
                f"capacity {int(row_capacity)}; emitted at least {emitted}; "
                "failure_mode=fail_closed_overflow"
            )
        if emitted > int(row_capacity):
            raise RuntimeError(
                "OptiX AABB_INDEX_QUERY_2D point_contains_rows reported "
                f"emitted_count {emitted} beyond capacity {int(row_capacity)}; "
                "failure_mode=fail_closed_overflow"
            )
        rows = tuple(
            (int(row_array[index].query_id), int(row_array[index].indexed_id))
            for index in range(emitted)
        )
        return {
            "primitive": "AABB_INDEX_QUERY_2D",
            "contract": "generic_aabb_point_membership_pair_rows_2d",
            "backend": "optix",
            "operation": "point_contains_rows",
            "row_schema": ("query_id", "indexed_id"),
            "candidate_id_rows": rows,
            "valid_count": len(rows),
            "row_capacity": int(row_capacity),
            "overflowed": False,
            "complete_candidate_coverage": True,
            "rt_core_accelerated": True,
            "native_engine_customization": False,
            "native_generic_symbol": (
                "rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows"
            ),
            "claim_boundary": (
                "Generic OptiX AABB_INDEX_QUERY_2D point_contains_rows output; "
                "returns app-name-free point/indexed-box id pairs only. Exact app "
                "semantics remain outside the engine."
            ),
        }

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            lib = _load_optix_library()
            destroy_symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_aabb_index_2d")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixAabbIndex2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_aabb_index_2d(boxes) -> PreparedOptixAabbIndex2D:
    return PreparedOptixAabbIndex2D(boxes)


def collect_aabb_intersection_pair_rows_2d_optix(
    indexed_boxes,
    query_boxes,
    *,
    row_capacity: int,
) -> dict[str, object]:
    with PreparedOptixAabbIndex2D(indexed_boxes) as prepared:
        return prepared.collect_range_intersection_rows(
            query_boxes,
            row_capacity=row_capacity,
        )


def collect_aabb_point_membership_pair_rows_2d_optix(
    indexed_boxes,
    point_queries,
    *,
    row_capacity: int,
) -> dict[str, object]:
    with PreparedOptixAabbIndex2D(indexed_boxes) as prepared:
        return prepared.collect_point_contains_rows(
            point_queries,
            row_capacity=row_capacity,
        )


@dataclass(frozen=True)
class _DeviceTriangleScene2D:
    count: int
    dimension: int = 2


@dataclass(frozen=True)
class _DevicePointScene2D:
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

    def write_device_any_hit_all_witnesses(
        self,
        ray_columns: dict,
        witness_ray_ids,
        witness_primitive_ids,
    ) -> dict[str, object]:
        """Write bounded all-hit witness rows into partner-owned CUDA buffers."""
        if self._closed:
            raise RuntimeError("prepared OptiX any-hit handle is closed")
        if not getattr(self, "_triangle_scene_true_zero_copy", False):
            raise RuntimeError(
                "write_device_any_hit_all_witnesses requires a triangle-column zero-copy prepared scene"
            )
        packet = pack_optix_ray_any_hit_2d_device_all_witness_outputs(
            ray_columns,
            witness_ray_ids,
            witness_primitive_ids,
        )

        lib = _load_optix_library()
        write_symbol = _find_optional_backend_symbol(lib, _OPTIX_PARTNER_PREPARED_DEVICE_ALL_WITNESSES_SYMBOL)
        if write_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{_OPTIX_PARTNER_PREPARED_DEVICE_ALL_WITNESSES_SYMBOL}. "
                "Partner-owned bounded all-witness output remains blocked; rebuild the "
                "OptiX backend after the native all-witness ABI lands."
            )
        rays = packet["rays"]
        emitted_count = ctypes.c_size_t()
        overflowed = ctypes.c_uint32()
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
            packet["metadata"]["witness_row_capacity"],
            ctypes.byref(emitted_count),
            ctypes.byref(overflowed),
            error,
            len(error),
        )
        _check_status(status, error)
        metadata = dict(packet["metadata"])
        metadata["emitted_count"] = int(emitted_count.value)
        metadata["overflowed"] = bool(overflowed.value)
        metadata["triangle_scene_true_zero_copy_authorized"] = bool(
            getattr(self, "_triangle_scene_true_zero_copy", False)
        )
        metadata["true_zero_copy_authorized"] = bool(
            metadata["ray_columns_true_zero_copy_authorized"]
            and metadata["witness_outputs_true_zero_copy_authorized"]
            and metadata["triangle_scene_true_zero_copy_authorized"]
        )
        metadata["exact_row_semantics_authorized"] = not metadata["overflowed"]
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


class PreparedOptixGroupedSegmentQuery3D:
    """Reusable OptiX device buffers for grouped finite 3D segment queries."""

    contract = "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1"

    def __init__(self, segment_start_xyz, segment_end_xyz, segment_group_offsets) -> None:
        self._lib = _load_optix_library()
        self._handle = ctypes.c_void_p()
        self._closed = False
        self._reuse_count = 0
        prepare_start = time.perf_counter()
        self._host_query = PreparedGroupedSegmentQuery3D(
            segment_start_xyz,
            segment_end_xyz,
            segment_group_offsets,
        )
        self.segment_count = int(self._host_query.segment_count)
        self.group_count = int(self._host_query.group_count)
        self.flags = (ctypes.c_uint8 * self.group_count)()
        create_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_create",
        )
        if create_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_create. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        status = create_symbol(
            self._host_query.segments,
            self._host_query.segment_count,
            self._host_query.group_offsets,
            self._host_query.group_count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)
        self.prepare_seconds = time.perf_counter() - prepare_start

    @property
    def reuse_count(self) -> int:
        return self._reuse_count

    def _mark_reused(self) -> int:
        self._reuse_count += 1
        return self._reuse_count

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            destroy_symbol = _find_optional_backend_symbol(
                self._lib,
                "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_destroy",
            )
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixGroupedSegmentQuery3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def descriptor(self) -> dict[str, object]:
        return {
            "contract": self.contract,
            "segment_count": int(self.segment_count),
            "group_count": int(self.group_count),
            "query_buffer_kind": "native_optix_device_rtdl_segment3d_as_ray_array",
            "group_offsets_buffer_kind": "native_optix_device_uint32_offsets",
            "group_indices_buffer_kind": "native_optix_device_uint32_group_indices",
            "segment_output_buffer_kind": "not_materialized",
            "output_buffer_kind": "native_optix_device_uint32_group_flags",
            "host_output_buffer_kind": "ctypes_host_uint8_group_flags",
            "copy_boundary": "compact_group_flags_device_to_host",
            "device": "cuda_device",
            "owner": "optix_native_runtime",
            "host_query_buffers_reused": True,
            "host_output_buffer_reused": True,
            "native_device_query_buffers_reused": True,
            "native_device_output_buffer_reused": True,
            "query_segments_uploaded_each_run": False,
            "per_segment_records_materialized": False,
            "per_segment_records_downloaded_to_host": False,
            "group_flags_downloaded_to_host": True,
            "true_zero_copy_authorized": False,
            "public_speedup_claim_authorized": False,
        }


def _pack_uint64_weights(weights, expected_count: int):
    try:
        import numpy as _np
    except ImportError:  # pragma: no cover
        _np = None

    if _np is not None:
        raw = _np.asarray(weights)
        if raw.ndim != 1:
            raise ValueError("ray_weights must be one-dimensional")
        if len(raw) != expected_count:
            raise ValueError("ray_weights length must match ray count")
        if raw.dtype.kind == "i" and raw.size and bool((raw < 0).any()):
            raise ValueError("ray_weights entries must fit uint64")
        if raw.dtype.kind in {"b", "i", "u"}:
            try:
                array = _np.ascontiguousarray(raw, dtype=_np.uint64)
            except OverflowError as exc:
                raise ValueError("ray_weights entries must fit uint64") from exc
            return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)), array

    normalized = tuple(int(weight) for weight in weights)
    if len(normalized) != expected_count:
        raise ValueError("ray_weights length must match ray count")
    if any(weight < 0 or weight > 0xFFFFFFFFFFFFFFFF for weight in normalized):
        raise ValueError("ray_weights entries must fit uint64")
    WeightArray = ctypes.c_uint64 * len(normalized)
    array = WeightArray(*normalized)
    return array, array


def _pack_uint32_values(values, expected_count: int, *, label: str):
    try:
        import numpy as _np
    except ImportError:  # pragma: no cover
        _np = None

    if _np is not None:
        raw = _np.asarray(values)
        if raw.ndim != 1:
            raise ValueError(f"{label} must be one-dimensional")
        if len(raw) != expected_count:
            raise ValueError(f"{label} length must match expected count")
        if raw.dtype.kind == "i" and raw.size and bool((raw < 0).any()):
            raise ValueError(f"{label} entries must fit uint32")
        if raw.dtype.kind in {"b", "i", "u"}:
            try:
                array = _np.ascontiguousarray(raw, dtype=_np.uint32)
            except OverflowError as exc:
                raise ValueError(f"{label} entries must fit uint32") from exc
            return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)), array

    normalized = tuple(int(value) for value in values)
    if len(normalized) != expected_count:
        raise ValueError(f"{label} length must match expected count")
    if any(value < 0 or value > 0xFFFFFFFF for value in normalized):
        raise ValueError(f"{label} entries must fit uint32")
    ValueArray = ctypes.c_uint32 * len(normalized)
    array = ValueArray(*normalized)
    return array, array


class PreparedOptixRayBatch3D:
    """Reusable device-resident 3-D ray batch for prepared OptiX scenes."""

    def __init__(self, lib, rays) -> None:
        self._lib = lib
        self._handle = ctypes.c_void_p()
        self._closed = False
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=3)
        if packed_rays.dimension != 3:
            raise ValueError("PreparedOptixRayBatch3D requires 3-D rays")
        self.ray_count = int(packed_rays.count)
        self._packed_rays_owner = packed_rays
        create_symbol = _find_optional_backend_symbol(self._lib, "rtdl_optix_ray_batch_3d_create")
        if create_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export rtdl_optix_ray_batch_3d_create. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        prepare_start = time.perf_counter()
        status = create_symbol(
            packed_rays.records,
            packed_rays.count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        self.prepare_seconds = time.perf_counter() - prepare_start
        _check_status(status, error)
        self.transfer_metadata = {
            "query_rays_uploaded_each_run": False,
            "prepared_rays_resident_on_device": True,
            "ray_batch_created_from": "host_packed_rays",
            "ray_columns_partner_owned": False,
        }

    @classmethod
    def from_device_ray_columns(cls, lib, ray_columns: dict) -> "PreparedOptixRayBatch3D":
        self = cls.__new__(cls)
        self._lib = lib
        self._handle = ctypes.c_void_p()
        self._closed = False
        packet = pack_optix_static_triangle_scene_3d_device_ray_inputs(ray_columns)
        rays = packet["rays"]
        self.ray_count = int(packet["metadata"]["ray_count"])
        self._packed_rays_owner = packet
        create_symbol = _find_optional_backend_symbol(self._lib, OPTIX_RAY_BATCH_3D_CREATE_DEVICE_RAYS_SYMBOL)
        if create_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{OPTIX_RAY_BATCH_3D_CREATE_DEVICE_RAYS_SYMBOL}. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        prepare_start = time.perf_counter()
        status = create_symbol(
            ctypes.c_void_p(rays["ids"].data_ptr),
            ctypes.c_void_p(rays["ox"].data_ptr),
            ctypes.c_void_p(rays["oy"].data_ptr),
            ctypes.c_void_p(rays["oz"].data_ptr),
            ctypes.c_void_p(rays["dx"].data_ptr),
            ctypes.c_void_p(rays["dy"].data_ptr),
            ctypes.c_void_p(rays["dz"].data_ptr),
            ctypes.c_void_p(rays["tmax"].data_ptr),
            self.ray_count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        self.prepare_seconds = time.perf_counter() - prepare_start
        _check_status(status, error)
        self.transfer_metadata = {
            **packet["metadata"],
            "query_rays_uploaded_each_run": False,
            "query_rays_packed_on_device_once": True,
            "prepared_rays_resident_on_device": True,
            "ray_batch_created_from": "partner_device_columns",
            "ray_columns_partner_owned": True,
            "true_zero_copy_authorized": False,
        }
        return self

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            destroy_symbol = _find_optional_backend_symbol(self._lib, "rtdl_optix_ray_batch_3d_destroy")
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixRayBatch3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


class PreparedOptixClosestHitGroupedArgmin3D:
    """Reusable device-resident grouped-argmin maps for closest-hit reductions."""

    def __init__(self, lib, ray_group_ids, candidate_values, candidate_indices, *, group_count=None) -> None:
        self._lib = lib
        self._handle = ctypes.c_void_p()
        self._closed = False
        try:
            import numpy as _np
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("PreparedOptixClosestHitGroupedArgmin3D requires numpy") from exc

        raw_group_ids = _np.asarray(ray_group_ids)
        if raw_group_ids.ndim != 1:
            raise ValueError("ray_group_ids must be a one-dimensional ray-id-to-group map")
        if raw_group_ids.size:
            if bool((raw_group_ids < 0).any()):
                raise ValueError("ray_group_ids must be nonnegative")
            max_group_id = int(raw_group_ids.max())
        else:
            max_group_id = -1
        if group_count is None:
            group_count = max_group_id + 1 if max_group_id >= 0 else 0
        self.group_count = int(group_count)
        if self.group_count < 0:
            raise ValueError("group_count must be nonnegative")
        if max_group_id >= self.group_count:
            raise ValueError("ray_group_ids contains a group outside group_count")

        raw_candidate_indices = _np.asarray(candidate_indices)
        if raw_candidate_indices.ndim != 1:
            raise ValueError("candidate_indices must be one-dimensional")
        if raw_candidate_indices.size and bool((raw_candidate_indices < 0).any()):
            raise ValueError("candidate_indices must be nonnegative")
        candidate_values_np = _np.ascontiguousarray(candidate_values, dtype=_np.float64)
        candidate_indices_np = _np.ascontiguousarray(raw_candidate_indices, dtype=_np.uint32)
        if candidate_values_np.ndim != 1:
            raise ValueError("candidate_values must be one-dimensional")
        if candidate_values_np.shape[0] != candidate_indices_np.shape[0]:
            raise ValueError("candidate_values and candidate_indices must have the same length")
        group_ids_np = _np.ascontiguousarray(raw_group_ids, dtype=_np.uint32)

        self.ray_group_id_count = int(group_ids_np.shape[0])
        self.candidate_count = int(candidate_values_np.shape[0])
        self._group_ids_owner = group_ids_np
        self._candidate_values_owner = candidate_values_np
        self._candidate_indices_owner = candidate_indices_np
        create_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create",
        )
        if create_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        prepare_start = time.perf_counter()
        status = create_symbol(
            group_ids_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
            ctypes.c_size_t(group_ids_np.shape[0]),
            candidate_values_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            candidate_indices_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
            ctypes.c_size_t(candidate_values_np.shape[0]),
            ctypes.c_size_t(self.group_count),
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        self.prepare_seconds = time.perf_counter() - prepare_start
        _check_status(status, error)

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            destroy_symbol = _find_optional_backend_symbol(
                self._lib,
                "rtdl_optix_closest_hit_grouped_argmin_inputs_3d_destroy",
            )
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixClosestHitGroupedArgmin3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def _normalize_grouped_candidate_argmin_inputs(
    candidate_group_ids,
    candidate_values,
    candidate_indices,
    *,
    group_count: int | None = None,
):
    try:
        import numpy as _np
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("grouped candidate argmin requires numpy") from exc

    raw_group_ids = _np.asarray(candidate_group_ids)
    if raw_group_ids.ndim != 1:
        raise ValueError("candidate_group_ids must be one-dimensional")
    if raw_group_ids.size:
        if bool((raw_group_ids < 0).any()):
            raise ValueError("candidate_group_ids must be nonnegative")
        max_group_id = int(raw_group_ids.max())
    else:
        max_group_id = -1
    if max_group_id > int(_np.iinfo(_np.uint32).max):
        raise ValueError("candidate_group_ids entries must fit uint32")
    if group_count is None:
        group_count = max_group_id + 1 if max_group_id >= 0 else 0
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be nonnegative")
    if group_count > int(_np.iinfo(_np.uint32).max):
        raise ValueError("group_count must fit uint32")
    if max_group_id >= group_count:
        raise ValueError("candidate_group_ids contains a group outside group_count")

    values_np = _np.ascontiguousarray(candidate_values, dtype=_np.float64)
    raw_indices = _np.asarray(candidate_indices)
    if values_np.ndim != 1:
        raise ValueError("candidate_values must be one-dimensional")
    if raw_indices.ndim != 1:
        raise ValueError("candidate_indices must be one-dimensional")
    if values_np.shape[0] != raw_group_ids.shape[0] or values_np.shape[0] != raw_indices.shape[0]:
        raise ValueError("candidate_group_ids, candidate_values, and candidate_indices must have the same length")
    if raw_indices.size:
        if bool((raw_indices < 0).any()):
            raise ValueError("candidate_indices must be nonnegative")
        if int(raw_indices.max()) > int(_np.iinfo(_np.uint32).max):
            raise ValueError("candidate_indices entries must fit uint32")

    return (
        _np,
        _np.ascontiguousarray(raw_group_ids, dtype=_np.uint32),
        values_np,
        _np.ascontiguousarray(raw_indices, dtype=_np.uint32),
        group_count,
    )


def grouped_candidate_argmin_host_reference(
    candidate_group_ids,
    candidate_values,
    candidate_indices,
    *,
    group_count: int | None = None,
) -> dict[str, object]:
    """Reference grouped argmin over generic ``(group_id, value, tie_index)`` candidates."""
    _np, group_ids_np, values_np, indices_np, group_count = _normalize_grouped_candidate_argmin_inputs(
        candidate_group_ids,
        candidate_values,
        candidate_indices,
        group_count=group_count,
    )
    has_value = _np.zeros(group_count, dtype=_np.uint8)
    group_index = _np.full(group_count, _np.iinfo(_np.uint32).max, dtype=_np.uint32)
    group_value = _np.zeros(group_count, dtype=_np.float64)
    if group_ids_np.size:
        valid = ~_np.isnan(values_np)
        if bool(valid.any()):
            valid_group_ids = group_ids_np[valid]
            valid_values = values_np[valid]
            valid_indices = indices_np[valid]
            order = _np.lexsort((valid_indices, valid_values, valid_group_ids))
            sorted_group_ids = valid_group_ids[order]
            sorted_values = valid_values[order]
            sorted_indices = valid_indices[order]
            first = _np.empty(sorted_group_ids.size, dtype=bool)
            first[0] = True
            first[1:] = sorted_group_ids[1:] != sorted_group_ids[:-1]
            winners = sorted_group_ids[first]
            has_value[winners] = 1
            group_index[winners] = sorted_indices[first]
            group_value[winners] = sorted_values[first]
    return {
        "has_value": has_value,
        "index": group_index,
        "value": group_value,
        "metadata": {
            "backend": "host_reference",
            "contract": "GROUPED_CANDIDATE_ARGMIN_V1",
            "result_kind": "grouped_argmin_from_candidate_arrays",
            "candidate_count": int(group_ids_np.shape[0]),
            "group_count": int(group_count),
            "native_device_grouped_candidate_argmin": False,
            "native_engine_customization": False,
        },
    }


class PreparedOptixGroupedCandidateArgmin:
    """Reusable generic device-resident grouped argmin over candidate arrays."""

    contract = "OPTIX_GROUPED_CANDIDATE_ARGMIN_V1"

    def __init__(
        self,
        candidate_group_ids,
        candidate_values,
        candidate_indices,
        *,
        group_count: int | None = None,
        lib=None,
        allow_numpy_fallback: bool = False,
    ) -> None:
        (
            self._np,
            self._candidate_group_ids_owner,
            self._candidate_values_owner,
            self._candidate_indices_owner,
            self.group_count,
        ) = _normalize_grouped_candidate_argmin_inputs(
            candidate_group_ids,
            candidate_values,
            candidate_indices,
            group_count=group_count,
        )
        self.candidate_count = int(self._candidate_group_ids_owner.shape[0])
        self._lib = lib
        self._handle = ctypes.c_void_p()
        self._closed = False
        self._fallback_reason: str | None = None
        self._native = False

        prepare_start = time.perf_counter()
        try:
            if self._lib is None:
                self._lib = _load_optix_library()
            create_symbol = _find_optional_backend_symbol(
                self._lib,
                "rtdl_optix_grouped_candidate_argmin_inputs_create",
            )
            if create_symbol is None:
                raise RuntimeError(
                    "Loaded OptiX backend library does not export "
                    "rtdl_optix_grouped_candidate_argmin_inputs_create. "
                    "Rebuild it with 'make build-optix' from current main."
                )
            error = ctypes.create_string_buffer(4096)
            status = create_symbol(
                self._candidate_group_ids_owner.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                self._candidate_values_owner.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                self._candidate_indices_owner.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                ctypes.c_size_t(self.candidate_count),
                ctypes.c_size_t(self.group_count),
                ctypes.byref(self._handle),
                error,
                len(error),
            )
            _check_status(status, error)
            self._native = True
        except (OSError, RuntimeError) as exc:
            if not allow_numpy_fallback:
                raise
            self._fallback_reason = str(exc)
        self.prepare_seconds = time.perf_counter() - prepare_start

    def finalize(self) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared grouped candidate argmin handle is closed")
        if not self._native:
            result = grouped_candidate_argmin_host_reference(
                self._candidate_group_ids_owner,
                self._candidate_values_owner,
                self._candidate_indices_owner,
                group_count=self.group_count,
            )
            metadata = dict(result["metadata"])
            metadata.update(
                {
                    "backend": "numpy_fallback",
                    "prepared_reused": True,
                    "prepare_seconds": float(self.prepare_seconds),
                    "fallback_reason": self._fallback_reason,
                }
            )
            result["metadata"] = metadata
            return result

        finalize_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_grouped_candidate_argmin_finalize",
        )
        if finalize_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_grouped_candidate_argmin_finalize. "
                "Rebuild it with 'make build-optix' from current main."
            )

        group_has_value = self._np.zeros(self.group_count, dtype=self._np.uint8)
        group_index = self._np.full(self.group_count, self._np.iinfo(self._np.uint32).max, dtype=self._np.uint32)
        group_value = self._np.zeros(self.group_count, dtype=self._np.float64)
        finalize_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        query_start = time.perf_counter()
        status = finalize_symbol(
            self._handle,
            group_has_value.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            group_index.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
            group_value.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            ctypes.byref(finalize_seconds),
            error,
            len(error),
        )
        query_total_seconds = time.perf_counter() - query_start
        _check_status(status, error)
        return {
            "has_value": group_has_value,
            "index": group_index,
            "value": group_value,
            "metadata": {
                "backend": "optix",
                "contract": self.contract,
                "result_kind": "grouped_argmin_from_candidate_arrays",
                "candidate_count": int(self.candidate_count),
                "group_count": int(self.group_count),
                "prepared_reused": True,
                "prepare_seconds": float(self.prepare_seconds),
                "phase_timing_seconds": {
                    "finalize": float(finalize_seconds.value),
                    "query_total": float(query_total_seconds),
                },
                "transfer_metadata": {
                    "candidate_group_ids_uploaded_each_run": False,
                    "candidate_values_uploaded_each_run": False,
                    "candidate_indices_uploaded_each_run": False,
                    "per_group_results_downloaded_to_host": True,
                    "native_device_grouped_candidate_argmin": True,
                    "true_zero_copy_authorized": False,
                },
                "native_engine_customization": False,
                "claim_boundary": {
                    "native_app_api": False,
                    "public_speedup_claim": False,
                    "true_zero_copy": False,
                },
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if self._native and handle.value:
            destroy_symbol = _find_optional_backend_symbol(
                self._lib,
                "rtdl_optix_grouped_candidate_argmin_inputs_destroy",
            )
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixGroupedCandidateArgmin":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_grouped_candidate_argmin(
    candidate_group_ids,
    candidate_values,
    candidate_indices,
    *,
    group_count: int | None = None,
    allow_numpy_fallback: bool = False,
) -> PreparedOptixGroupedCandidateArgmin:
    return PreparedOptixGroupedCandidateArgmin(
        candidate_group_ids,
        candidate_values,
        candidate_indices,
        group_count=group_count,
        allow_numpy_fallback=allow_numpy_fallback,
    )


class PreparedOptixPrimitiveGroupedI64Payload3D:
    """Reusable device-resident primitive group/value payload for generic 3-D reductions."""

    contract = "PREPARED_PRIMITIVE_GROUPED_I64_PAYLOAD_3D_V1"

    def __init__(
        self,
        primitive_group_ids,
        primitive_values,
        *,
        primitive_count: int,
        group_count: int,
    ) -> None:
        self._lib = _load_optix_library()
        self._handle = ctypes.c_void_p()
        self._closed = False
        self.primitive_count = int(primitive_count)
        self.group_count = int(group_count)
        group_array, self._group_owner = _pack_uint32_values(
            primitive_group_ids,
            self.primitive_count,
            label="primitive_group_ids",
        )
        value_array, self._value_owner = _pack_uint64_weights(
            primitive_values,
            self.primitive_count,
        )
        create_symbol = _find_optional_backend_symbol(
            self._lib,
            OPTIX_PRIMITIVE_GROUPED_I64_PAYLOAD_3D_CREATE_SYMBOL,
        )
        if create_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{OPTIX_PRIMITIVE_GROUPED_I64_PAYLOAD_3D_CREATE_SYMBOL}. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        prepare_start = time.perf_counter()
        status = create_symbol(
            group_array,
            self.primitive_count,
            value_array,
            self.primitive_count,
            self.group_count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        _check_status(status, error)
        self.prepare_seconds = time.perf_counter() - prepare_start

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            destroy_symbol = _find_optional_backend_symbol(
                self._lib,
                "rtdl_optix_primitive_grouped_i64_payload_3d_destroy",
            )
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixPrimitiveGroupedI64Payload3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_optix_primitive_grouped_i64_payload_3d(
    primitive_group_ids,
    primitive_values,
    *,
    primitive_count: int,
    group_count: int,
) -> PreparedOptixPrimitiveGroupedI64Payload3D:
    return PreparedOptixPrimitiveGroupedI64Payload3D(
        primitive_group_ids,
        primitive_values,
        primitive_count=primitive_count,
        group_count=group_count,
    )


class PreparedOptixStaticTriangleScene3D:
    """Reusable OptiX handle for grouped finite 3D segment any-hit flags."""

    contract = "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1"

    def __init__(self, triangles) -> None:
        self._lib = _load_optix_library()
        self._handle = ctypes.c_void_p()
        self._closed = False
        self._run_count = 0
        self._packed_triangles = _pack_static_triangles_3d(triangles)
        self.triangle_count = int(self._packed_triangles.count)
        create_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_create",
        )
        if create_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_create. "
                "Rebuild it with 'make build-optix' from current main."
            )
        error = ctypes.create_string_buffer(4096)
        prepare_start = time.perf_counter()
        status = create_symbol(
            self._packed_triangles.records,
            self._packed_triangles.count,
            ctypes.byref(self._handle),
            error,
            len(error),
        )
        self.prepare_seconds = time.perf_counter() - prepare_start
        _check_status(status, error)

    def close(self) -> None:
        if self._closed:
            return
        handle = self._handle
        self._handle = ctypes.c_void_p()
        self._closed = True
        if handle.value:
            destroy_symbol = _find_optional_backend_symbol(
                self._lib,
                "rtdl_optix_static_triangle_scene_3d_destroy",
            )
            if destroy_symbol is not None:
                destroy_symbol(handle)

    def __enter__(self) -> "PreparedOptixStaticTriangleScene3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def prepare_ray_batch(self, rays) -> PreparedOptixRayBatch3D:
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        return PreparedOptixRayBatch3D(self._lib, rays)

    def prepare_ray_batch_device_columns(self, ray_columns: dict) -> PreparedOptixRayBatch3D:
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        return PreparedOptixRayBatch3D.from_device_ray_columns(self._lib, ray_columns)

    def prepare_closest_hit_grouped_argmin_inputs(
        self,
        ray_group_ids,
        candidate_values,
        candidate_indices,
        *,
        group_count: int | None = None,
    ) -> PreparedOptixClosestHitGroupedArgmin3D:
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        return PreparedOptixClosestHitGroupedArgmin3D(
            self._lib,
            ray_group_ids,
            candidate_values,
            candidate_indices,
            group_count=group_count,
        )

    def ray_closest_hit_prepared_grouped_argmin(
        self,
        rays: PreparedOptixRayBatch3D,
        grouped_inputs: PreparedOptixClosestHitGroupedArgmin3D,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        if not isinstance(rays, PreparedOptixRayBatch3D):
            raise TypeError("ray_closest_hit_prepared_grouped_argmin requires PreparedOptixRayBatch3D")
        if not isinstance(grouped_inputs, PreparedOptixClosestHitGroupedArgmin3D):
            raise TypeError(
                "ray_closest_hit_prepared_grouped_argmin requires "
                "PreparedOptixClosestHitGroupedArgmin3D"
            )
        if rays._closed:
            raise RuntimeError("prepared OptiX ray batch handle is closed")
        if grouped_inputs._closed:
            raise RuntimeError("prepared grouped argmin inputs handle is closed")
        try:
            import numpy as _np
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("ray_closest_hit_prepared_grouped_argmin requires numpy") from exc

        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin. "
                "Rebuild it with 'make build-optix' from current main."
            )

        group_count = int(grouped_inputs.group_count)
        group_has_value = _np.zeros(group_count, dtype=_np.uint8)
        group_index = _np.full(group_count, _np.iinfo(_np.uint32).max, dtype=_np.uint32)
        group_value = _np.zeros(group_count, dtype=_np.float64)
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        query_start = time.perf_counter()
        status = run_symbol(
            self._handle,
            rays._handle,
            grouped_inputs._handle,
            group_has_value.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            group_index.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
            group_value.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        query_total_seconds = time.perf_counter() - query_start
        _check_status(status, error)

        self._run_count += 1
        self.last_closest_hit_metadata = {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_PREPARED_GROUPED_ARGMIN_V1",
            "result_kind": "grouped_argmin_from_ray_triangle_closest_hit",
            "ray_count": int(rays.ray_count),
            "triangle_count": self.triangle_count,
            "group_count": group_count,
            "candidate_count": int(grouped_inputs.candidate_count),
            "ray_group_id_count": int(grouped_inputs.ray_group_id_count),
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_ray_batch_used": True,
            "prepared_grouped_argmin_inputs_used": True,
            "prepared_ray_batch_seconds": float(rays.prepare_seconds),
            "prepared_grouped_argmin_inputs_seconds": float(grouped_inputs.prepare_seconds),
            "prepared_run_index": self._run_count,
            "rows_materialized": False,
            "row_arrays_materialized": False,
            "native_grouped_argmin": True,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": 0.0,
                "traversal": float(traversal_seconds.value),
                "query_total": float(query_total_seconds),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": False,
                "prepared_rays_resident_on_device": True,
                "group_ids_uploaded_each_run": False,
                "candidate_values_uploaded_each_run": False,
                "candidate_indices_uploaded_each_run": False,
                "closest_hit_rows_downloaded_to_host": False,
                "per_group_results_downloaded_to_host": True,
                "python_dict_rows_materialized": False,
                "native_host_grouped_argmin": False,
                "native_device_grouped_argmin": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }
        return {
            "has_value": group_has_value,
            "index": group_index,
            "value": group_value,
            "metadata": dict(self.last_closest_hit_metadata),
        }

    def two_scene_ray_closest_hit_prepared_grouped_argmin(
        self,
        rays_a: PreparedOptixRayBatch3D,
        grouped_inputs_a: PreparedOptixClosestHitGroupedArgmin3D,
        scene_b: "PreparedOptixStaticTriangleScene3D",
        rays_b: PreparedOptixRayBatch3D,
        grouped_inputs_b: PreparedOptixClosestHitGroupedArgmin3D,
    ) -> dict[str, object]:
        if self._closed or scene_b._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        for rays in (rays_a, rays_b):
            if not isinstance(rays, PreparedOptixRayBatch3D):
                raise TypeError("two_scene_ray_closest_hit_prepared_grouped_argmin requires prepared ray batches")
            if rays._closed:
                raise RuntimeError("prepared OptiX ray batch handle is closed")
        for grouped_inputs in (grouped_inputs_a, grouped_inputs_b):
            if not isinstance(grouped_inputs, PreparedOptixClosestHitGroupedArgmin3D):
                raise TypeError(
                    "two_scene_ray_closest_hit_prepared_grouped_argmin requires "
                    "prepared grouped argmin inputs"
                )
            if grouped_inputs._closed:
                raise RuntimeError("prepared grouped argmin inputs handle is closed")
        if grouped_inputs_a.group_count != grouped_inputs_b.group_count:
            raise ValueError("two-scene grouped argmin inputs must have the same group_count")
        try:
            import numpy as _np
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("two_scene_ray_closest_hit_prepared_grouped_argmin requires numpy") from exc

        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin. "
                "Rebuild it with 'make build-optix' from current main."
            )

        group_count = int(grouped_inputs_a.group_count)
        group_has_value = _np.zeros(group_count, dtype=_np.uint8)
        group_index = _np.full(group_count, _np.iinfo(_np.uint32).max, dtype=_np.uint32)
        group_value = _np.zeros(group_count, dtype=_np.float64)
        traversal_a_seconds = ctypes.c_double()
        traversal_b_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        query_start = time.perf_counter()
        status = run_symbol(
            self._handle,
            rays_a._handle,
            grouped_inputs_a._handle,
            scene_b._handle,
            rays_b._handle,
            grouped_inputs_b._handle,
            group_has_value.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            group_index.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
            group_value.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            ctypes.byref(traversal_a_seconds),
            ctypes.byref(traversal_b_seconds),
            error,
            len(error),
        )
        query_total_seconds = time.perf_counter() - query_start
        _check_status(status, error)

        self._run_count += 1
        metadata = {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_TWO_PREPARED_RAY_BATCHES_PREPARED_GROUPED_ARGMIN_V1",
            "result_kind": "two_source_grouped_argmin_from_ray_triangle_closest_hit",
            "ray_count_a": int(rays_a.ray_count),
            "ray_count_b": int(rays_b.ray_count),
            "triangle_count_a": self.triangle_count,
            "triangle_count_b": scene_b.triangle_count,
            "group_count": group_count,
            "candidate_count_a": int(grouped_inputs_a.candidate_count),
            "candidate_count_b": int(grouped_inputs_b.candidate_count),
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_ray_batch_used": True,
            "prepared_grouped_argmin_inputs_used": True,
            "native_two_source_grouped_merge": True,
            "prepared_run_index": self._run_count,
            "rows_materialized": False,
            "row_arrays_materialized": False,
            "native_grouped_argmin": True,
            "phase_timing_seconds": {
                "prepare_build_a": float(self.prepare_seconds),
                "prepare_build_b": float(scene_b.prepare_seconds),
                "query_pack": 0.0,
                "traversal_a": float(traversal_a_seconds.value),
                "traversal_b": float(traversal_b_seconds.value),
                "query_total": float(query_total_seconds),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": False,
                "prepared_rays_resident_on_device": True,
                "group_ids_uploaded_each_run": False,
                "candidate_values_uploaded_each_run": False,
                "candidate_indices_uploaded_each_run": False,
                "closest_hit_rows_downloaded_to_host": False,
                "per_group_results_downloaded_to_host": True,
                "python_cross_source_merge": False,
                "native_device_two_source_merge": True,
                "python_dict_rows_materialized": False,
                "native_host_grouped_argmin": False,
                "native_device_grouped_argmin": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }
        self.last_closest_hit_metadata = dict(metadata)
        scene_b.last_closest_hit_metadata = dict(metadata)
        return {
            "has_value": group_has_value,
            "index": group_index,
            "value": group_value,
            "metadata": metadata,
        }

    def run_grouped_segment_any_hit_flags(
        self,
        segment_start_xyz,
        segment_end_xyz,
        segment_group_offsets,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags. "
                "Rebuild it with 'make build-optix' from current main."
            )

        pack_start = time.perf_counter()
        segments, segment_count = _pack_segments_3d_from_endpoints(segment_start_xyz, segment_end_xyz)
        group_offsets, group_count = _pack_group_offsets_u32(segment_group_offsets, segment_count)
        query_pack_seconds = time.perf_counter() - pack_start

        flags = (ctypes.c_uint8 * group_count)()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            segments,
            segment_count,
            group_offsets,
            group_count,
            flags,
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        post_start = time.perf_counter()
        flags_list = [int(flags[index]) for index in range(group_count)]
        output_postprocess_seconds = time.perf_counter() - post_start
        self._run_count += 1
        return {
            "backend": "optix",
            "contract": self.contract,
            "flags": flags_list,
            "flag_format": "uint8_byte_per_query_group",
            "segment_count": int(segment_count),
            "group_count": int(group_count),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
                "output_postprocess": float(output_postprocess_seconds),
            },
            "precision_metadata": {
                "host_input": "float64",
                "optix_bvh_bounds": "float32",
                "device_traversal_input": "float32",
                "device_intersection_kernel": "float32",
                "coordinate_narrowing_recorded": True,
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_segments_uploaded_each_run": True,
                "group_flags_downloaded_to_host": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "paper_reproduction": False,
                "authors_code_comparison": False,
                "public_speedup_claim": False,
                "native_app_api": False,
                "exact_solid_contact": False,
                "continuous_swept_support": False,
                "row_witnesses": False,
                "release_action": False,
            },
        }

    def run_prepared_grouped_segment_any_hit_flags(
        self,
        prepared_query: PreparedGroupedSegmentQuery3D,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        if not isinstance(prepared_query, PreparedGroupedSegmentQuery3D):
            raise TypeError("prepared_query must be PreparedGroupedSegmentQuery3D")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags. "
                "Rebuild it with 'make build-optix' from current main."
            )

        clear_start = time.perf_counter()
        prepared_query.reset_flags()
        output_clear_seconds = time.perf_counter() - clear_start

        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            prepared_query.segments,
            prepared_query.segment_count,
            prepared_query.group_offsets,
            prepared_query.group_count,
            prepared_query.flags,
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        post_start = time.perf_counter()
        flags_list = [int(prepared_query.flags[index]) for index in range(int(prepared_query.group_count))]
        output_postprocess_seconds = time.perf_counter() - post_start
        self._run_count += 1
        prepared_query_run_index = prepared_query._mark_reused()
        descriptor = prepared_query.descriptor()
        return {
            "backend": "optix",
            "contract": self.contract,
            "flags": flags_list,
            "flag_format": "uint8_byte_per_query_group",
            "segment_count": int(prepared_query.segment_count),
            "group_count": int(prepared_query.group_count),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "prepared_query_used": True,
            "prepared_query_run_index": prepared_query_run_index,
            "host_query_output_buffers_reused": True,
            "native_query_output_buffers_reused": False,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": 0.0,
                "prepared_query_build": float(prepared_query.prepare_seconds),
                "output_clear": float(output_clear_seconds),
                "traversal": float(traversal_seconds.value),
                "output_postprocess": float(output_postprocess_seconds),
            },
            "buffer_reuse_metadata": descriptor,
            "precision_metadata": {
                "host_input": "float64",
                "optix_bvh_bounds": "float32",
                "device_traversal_input": "float32",
                "device_intersection_kernel": "float32",
                "coordinate_narrowing_recorded": True,
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_segments_uploaded_each_run": True,
                "group_flags_downloaded_to_host": True,
                "host_query_output_buffers_reused": True,
                "native_device_query_buffers_reused": False,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "paper_reproduction": False,
                "authors_code_comparison": False,
                "public_speedup_claim": False,
                "native_app_api": False,
                "exact_solid_contact": False,
                "continuous_swept_support": False,
                "row_witnesses": False,
                "release_action": False,
                "true_zero_copy": False,
            },
        }

    def run_native_prepared_grouped_segment_any_hit_flags(
        self,
        prepared_query: PreparedOptixGroupedSegmentQuery3D,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        if not isinstance(prepared_query, PreparedOptixGroupedSegmentQuery3D):
            raise TypeError("prepared_query must be PreparedOptixGroupedSegmentQuery3D")
        if prepared_query._closed:
            raise RuntimeError("prepared OptiX grouped segment query handle is closed")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_flags",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_flags. "
                "Rebuild it with 'make build-optix' from current main."
            )

        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            prepared_query._handle,
            prepared_query.flags,
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        post_start = time.perf_counter()
        flags_list = [int(prepared_query.flags[index]) for index in range(int(prepared_query.group_count))]
        output_postprocess_seconds = time.perf_counter() - post_start
        self._run_count += 1
        prepared_query_run_index = prepared_query._mark_reused()
        descriptor = prepared_query.descriptor()
        return {
            "backend": "optix",
            "contract": self.contract,
            "flags": flags_list,
            "flag_format": "uint8_byte_per_query_group",
            "segment_count": int(prepared_query.segment_count),
            "group_count": int(prepared_query.group_count),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "prepared_query_used": True,
            "prepared_query_run_index": prepared_query_run_index,
            "host_query_output_buffers_reused": True,
            "native_query_output_buffers_reused": True,
            "native_device_query_buffers_reused": True,
            "native_device_output_buffer_reused": True,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": 0.0,
                "prepared_query_build": float(prepared_query.prepare_seconds),
                "traversal": float(traversal_seconds.value),
                "output_postprocess": float(output_postprocess_seconds),
            },
            "buffer_reuse_metadata": descriptor,
            "precision_metadata": {
                "host_input": "float64",
                "optix_bvh_bounds": "float32",
                "device_traversal_input": "float32",
                "device_intersection_kernel": "float32",
                "coordinate_narrowing_recorded": True,
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_segments_uploaded_each_run": False,
                "group_flags_downloaded_to_host": True,
                "per_segment_records_downloaded_to_host": False,
                "host_query_output_buffers_reused": True,
                "native_device_query_buffers_reused": True,
                "native_device_output_buffer_reused": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "paper_reproduction": False,
                "authors_code_comparison": False,
                "public_speedup_claim": False,
                "native_app_api": False,
                "exact_solid_contact": False,
                "continuous_swept_support": False,
                "row_witnesses": False,
                "release_action": False,
                "true_zero_copy": False,
            },
        }

    def run_native_prepared_grouped_segment_any_hit_count(
        self,
        prepared_query: PreparedOptixGroupedSegmentQuery3D,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        if not isinstance(prepared_query, PreparedOptixGroupedSegmentQuery3D):
            raise TypeError("prepared_query must be PreparedOptixGroupedSegmentQuery3D")
        if prepared_query._closed:
            raise RuntimeError("prepared OptiX grouped segment query handle is closed")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_count",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_count. "
                "Rebuild it with 'make build-optix' from current main."
            )

        flagged_group_count = ctypes.c_uint32()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            prepared_query._handle,
            ctypes.byref(flagged_group_count),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        post_start = time.perf_counter()
        count_value = int(flagged_group_count.value)
        output_postprocess_seconds = time.perf_counter() - post_start
        self._run_count += 1
        prepared_query_run_index = prepared_query._mark_reused()
        descriptor = prepared_query.descriptor()
        descriptor.update(
            {
                "result_kind": "uint32_flagged_group_count",
                "copy_boundary": "group_flags_device_to_native_host_then_scalar_to_python",
                "group_flags_downloaded_to_python": False,
                "python_group_flags_materialized": False,
                "flagged_group_count_returned_to_python": True,
            }
        )
        return {
            "backend": "optix",
            "contract": self.contract,
            "result_kind": "uint32_flagged_group_count",
            "flagged_group_count": count_value,
            "flag_format": "count_only_no_group_flags",
            "segment_count": int(prepared_query.segment_count),
            "group_count": int(prepared_query.group_count),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "prepared_query_used": True,
            "prepared_query_run_index": prepared_query_run_index,
            "host_query_output_buffers_reused": True,
            "native_query_output_buffers_reused": True,
            "native_device_query_buffers_reused": True,
            "native_device_output_buffer_reused": True,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": 0.0,
                "prepared_query_build": float(prepared_query.prepare_seconds),
                "traversal": float(traversal_seconds.value),
                "output_postprocess": float(output_postprocess_seconds),
            },
            "buffer_reuse_metadata": descriptor,
            "precision_metadata": {
                "host_input": "float64",
                "optix_bvh_bounds": "float32",
                "device_traversal_input": "float32",
                "device_intersection_kernel": "float32",
                "coordinate_narrowing_recorded": True,
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_segments_uploaded_each_run": False,
                "group_flags_downloaded_to_host": True,
                "group_flags_downloaded_to_python": False,
                "per_segment_records_downloaded_to_host": False,
                "python_group_flags_materialized": False,
                "host_query_output_buffers_reused": True,
                "native_device_query_buffers_reused": True,
                "native_device_output_buffer_reused": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "paper_reproduction": False,
                "authors_code_comparison": False,
                "public_speedup_claim": False,
                "native_app_api": False,
                "exact_solid_contact": False,
                "continuous_swept_support": False,
                "row_witnesses": False,
                "release_action": False,
                "true_zero_copy": False,
            },
        }

    def ray_any_hit_weighted_sum(self, rays, ray_weights) -> dict[str, object]:
        """Return sum(weights[i]) for 3-D rays that hit a prepared triangle scene.

        This is a generic summary primitive: the native engine sees only rays,
        triangles, and caller-supplied integer weights. Domain interpretation of
        those weights remains in Python/app code.
        """
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum. "
                "Rebuild it with 'make build-optix' from current main."
            )

        pack_start = time.perf_counter()
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=3)
        if packed_rays.dimension != 3:
            raise ValueError("ray_any_hit_weighted_sum requires 3-D rays")
        weight_array, _weight_owner = _pack_uint64_weights(ray_weights, packed_rays.count)
        query_pack_seconds = time.perf_counter() - pack_start

        weighted_sum = ctypes.c_uint64()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_rays.records,
            packed_rays.count,
            weight_array,
            ctypes.byref(weighted_sum),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        self._run_count += 1
        return {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_RAY_ANY_HIT_WEIGHTED_SUM_V1",
            "result_kind": "uint64_weighted_any_hit_sum",
            "weighted_hit_sum": int(weighted_sum.value),
            "ray_count": int(packed_rays.count),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "rows_materialized": False,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": True,
                "ray_weights_uploaded_each_run": True,
                "per_ray_records_downloaded_to_host": False,
                "scalar_sum_returned_to_python": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "row_witnesses": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }

    def ray_triangle_primitive_grouped_i64_reduction(
        self,
        rays,
        *,
        primitive_group_ids,
        primitive_values,
        group_count: int,
        reduction: str,
    ) -> dict[str, object]:
        """Run generic all-hit primitive-id dedup plus grouped i64 reduction."""
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        if reduction not in {"count", "sum", "min", "max", "sum_count"}:
            raise ValueError("reduction must be one of: count, sum, min, max, sum_count")
        if group_count < 0:
            raise ValueError("group_count must be non-negative")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            OPTIX_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{OPTIX_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL}. "
                "Rebuild it with 'make build-optix' from current main."
            )

        pack_start = time.perf_counter()
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=3)
        if packed_rays.dimension != 3:
            raise ValueError("ray_triangle_primitive_grouped_i64_reduction requires 3-D rays")
        group_array, _group_owner = _pack_uint32_values(
            primitive_group_ids,
            self.triangle_count,
            label="primitive_group_ids",
        )
        value_array, _value_owner = _pack_uint64_weights(primitive_values, self.triangle_count)
        output_count = int(group_count)
        CountsArray = ctypes.c_uint64 * output_count
        counts = CountsArray()
        sums = CountsArray()
        mins = CountsArray()
        maxs = CountsArray()
        query_pack_seconds = time.perf_counter() - pack_start

        hit_event_count = ctypes.c_uint64()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        operation = {
            "count": 1,
            "sum": 2,
            "min": 3,
            "max": 4,
            "sum_count": 5,
        }[reduction]
        status = run_symbol(
            self._handle,
            packed_rays.records,
            packed_rays.count,
            group_array,
            self.triangle_count,
            value_array,
            self.triangle_count,
            output_count,
            ctypes.c_uint32(operation),
            counts,
            sums,
            mins,
            maxs,
            ctypes.byref(hit_event_count),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        rows: list[dict[str, int]] = []
        for group_id in range(output_count):
            if reduction == "count":
                value = int(counts[group_id])
                if value == 0:
                    continue
                rows.append({"group_id": group_id, "count": value})
            elif reduction == "sum":
                value = int(sums[group_id])
                if value == 0:
                    continue
                rows.append({"group_id": group_id, "sum": value})
            elif reduction == "min":
                value = int(mins[group_id])
                if value == 0xFFFFFFFFFFFFFFFF:
                    continue
                rows.append({"group_id": group_id, "min": value})
            elif reduction == "max":
                value = int(maxs[group_id])
                if value == 0:
                    continue
                rows.append({"group_id": group_id, "max": value})
            else:
                count_value = int(counts[group_id])
                if count_value == 0:
                    continue
                rows.append({"group_id": group_id, "sum": int(sums[group_id]), "count": count_value})

        self._run_count += 1
        return {
            "backend": "optix",
            "primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
            "native_symbol": OPTIX_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
            "reduction": reduction,
            "rows": tuple(rows),
            "ray_count": int(packed_rays.count),
            "triangle_count": self.triangle_count,
            "group_count": output_count,
            "hit_event_count_before_dedup": int(hit_event_count.value),
            "rt_core_accelerated": True,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": True,
                "primitive_group_ids_uploaded_each_run": True,
                "primitive_values_uploaded_each_run": True,
                "per_ray_records_downloaded_to_host": False,
                "group_rows_downloaded_to_host": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "row_witnesses": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }

    def ray_triangle_hit_stream(
        self,
        rays,
        *,
        max_rows: int | None = None,
        deduplicate_primitives: bool = True,
    ) -> dict[str, object]:
        """Emit generic bounded 3-D ray/triangle hit rows from OptiX."""
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        run_symbol = _find_optional_backend_symbol(self._lib, OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_SYMBOL)
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_SYMBOL}. "
                "Rebuild it with 'make build-optix' from current main."
            )

        pack_start = time.perf_counter()
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=3)
        if packed_rays.dimension != 3:
            raise ValueError("ray_triangle_hit_stream requires 3-D rays")
        capacity = self.triangle_count if max_rows is None and deduplicate_primitives else int(max_rows if max_rows is not None else max(1, packed_rays.count * self.triangle_count))
        if capacity < 0:
            raise ValueError("max_rows must be non-negative")
        RowArray = _RtdlRayTriangleHitStreamRow * capacity
        rows_array = RowArray()
        query_pack_seconds = time.perf_counter() - pack_start

        row_count = ctypes.c_size_t()
        hit_event_count = ctypes.c_uint64()
        overflow = ctypes.c_uint32()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        native_start = time.perf_counter()
        status = run_symbol(
            self._handle,
            packed_rays.records,
            packed_rays.count,
            ctypes.c_uint32(1 if deduplicate_primitives else 0),
            rows_array,
            capacity,
            ctypes.byref(row_count),
            ctypes.byref(hit_event_count),
            ctypes.byref(overflow),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        native_call_seconds = time.perf_counter() - native_start
        _check_status(status, error)

        if overflow.value:
            rows: tuple[dict[str, int], ...] = ()
        else:
            rows = tuple(
                {
                    "ray_id": int(rows_array[index].ray_id),
                    "primitive_id": int(rows_array[index].primitive_id),
                }
                for index in range(int(row_count.value))
            )

        self._run_count += 1
        return {
            "backend": "optix",
            "primitive": "RAY_TRIANGLE_HIT_STREAM_3D",
            "row_schema": ("ray_id", "primitive_id"),
            "native_symbol": OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_SYMBOL,
            "rows": rows,
            "ray_count": int(packed_rays.count),
            "triangle_count": self.triangle_count,
            "max_rows": int(capacity),
            "row_count": int(row_count.value),
            "overflow": bool(overflow.value),
            "deduplicate_primitives": bool(deduplicate_primitives),
            "hit_event_count_before_dedup": int(hit_event_count.value),
            "rt_core_accelerated": True,
            "native_lowering_ready": True,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
                "hit_stream_materialization": max(0.0, float(native_call_seconds) - float(traversal_seconds.value)),
                "native_call": float(native_call_seconds),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": True,
                "hit_stream_rows_downloaded_to_host": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "raydb_semantics_embedded": False,
                "row_schema": ("ray_id", "primitive_id"),
                "fail_closed_overflow": True,
                "public_speedup_claim": False,
            },
        }

    def ray_triangle_prepared_primitive_grouped_i64_reduction(
        self,
        rays,
        payload: PreparedOptixPrimitiveGroupedI64Payload3D,
        *,
        reduction: str,
    ) -> dict[str, object]:
        """Run grouped i64 reduction with device-resident primitive group/value payload."""
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        if payload._closed:
            raise RuntimeError("prepared OptiX primitive grouped payload handle is closed")
        if payload.primitive_count != self.triangle_count:
            raise ValueError("prepared primitive payload count must match prepared triangle count")
        if reduction not in {"count", "sum", "min", "max", "sum_count"}:
            raise ValueError("reduction must be one of: count, sum, min, max, sum_count")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            OPTIX_PREPARED_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{OPTIX_PREPARED_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL}. "
                "Rebuild it with 'make build-optix' from current main."
            )

        pack_start = time.perf_counter()
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=3)
        if packed_rays.dimension != 3:
            raise ValueError("ray_triangle_prepared_primitive_grouped_i64_reduction requires 3-D rays")
        output_count = int(payload.group_count)
        CountsArray = ctypes.c_uint64 * output_count
        counts = CountsArray()
        sums = CountsArray()
        mins = CountsArray()
        maxs = CountsArray()
        query_pack_seconds = time.perf_counter() - pack_start

        hit_event_count = ctypes.c_uint64()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        operation = {
            "count": 1,
            "sum": 2,
            "min": 3,
            "max": 4,
            "sum_count": 5,
        }[reduction]
        status = run_symbol(
            self._handle,
            payload._handle,
            packed_rays.records,
            packed_rays.count,
            ctypes.c_uint32(operation),
            counts,
            sums,
            mins,
            maxs,
            ctypes.byref(hit_event_count),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        rows: list[dict[str, int]] = []
        for group_id in range(output_count):
            if reduction == "count":
                value = int(counts[group_id])
                if value == 0:
                    continue
                rows.append({"group_id": group_id, "count": value})
            elif reduction == "sum":
                value = int(sums[group_id])
                if value == 0:
                    continue
                rows.append({"group_id": group_id, "sum": value})
            elif reduction == "min":
                value = int(mins[group_id])
                if value == 0xFFFFFFFFFFFFFFFF:
                    continue
                rows.append({"group_id": group_id, "min": value})
            elif reduction == "max":
                value = int(maxs[group_id])
                if value == 0:
                    continue
                rows.append({"group_id": group_id, "max": value})
            else:
                count_value = int(counts[group_id])
                if count_value == 0:
                    continue
                rows.append({"group_id": group_id, "sum": int(sums[group_id]), "count": count_value})

        self._run_count += 1
        return {
            "backend": "optix",
            "primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
            "native_symbol": OPTIX_PREPARED_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
            "reduction": reduction,
            "rows": tuple(rows),
            "ray_count": int(packed_rays.count),
            "triangle_count": self.triangle_count,
            "group_count": output_count,
            "hit_event_count_before_dedup": int(hit_event_count.value),
            "rt_core_accelerated": True,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_primitive_payload_used": True,
            "prepared_run_index": self._run_count,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "primitive_payload_prepare": float(payload.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": True,
                "primitive_group_ids_uploaded_each_run": False,
                "primitive_values_uploaded_each_run": False,
                "prepared_primitive_payload_on_device": True,
                "per_ray_records_downloaded_to_host": False,
                "group_rows_downloaded_to_host": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "row_witnesses": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }

    def ray_batch_prepared_primitive_grouped_i64_reduction(
        self,
        rays: PreparedOptixRayBatch3D,
        payload: PreparedOptixPrimitiveGroupedI64Payload3D,
        *,
        reduction: str,
    ) -> dict[str, object]:
        """Run grouped i64 reduction with prepared rays and prepared primitive payload."""
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        if not isinstance(rays, PreparedOptixRayBatch3D):
            raise TypeError("ray_batch_prepared_primitive_grouped_i64_reduction requires PreparedOptixRayBatch3D")
        if rays._closed:
            raise RuntimeError("prepared OptiX ray batch handle is closed")
        if payload._closed:
            raise RuntimeError("prepared OptiX primitive grouped payload handle is closed")
        if payload.primitive_count != self.triangle_count:
            raise ValueError("prepared primitive payload count must match prepared triangle count")
        if reduction not in {"count", "sum", "min", "max", "sum_count"}:
            raise ValueError("reduction must be one of: count, sum, min, max, sum_count")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            OPTIX_RAY_BATCH_PREPARED_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{OPTIX_RAY_BATCH_PREPARED_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL}. "
                "Rebuild it with 'make build-optix' from current main."
            )

        output_count = int(payload.group_count)
        CountsArray = ctypes.c_uint64 * output_count
        counts = CountsArray()
        sums = CountsArray()
        mins = CountsArray()
        maxs = CountsArray()

        hit_event_count = ctypes.c_uint64()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        operation = {
            "count": 1,
            "sum": 2,
            "min": 3,
            "max": 4,
            "sum_count": 5,
        }[reduction]
        status = run_symbol(
            self._handle,
            payload._handle,
            rays._handle,
            ctypes.c_uint32(operation),
            counts,
            sums,
            mins,
            maxs,
            ctypes.byref(hit_event_count),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        rows: list[dict[str, int]] = []
        for group_id in range(output_count):
            if reduction == "count":
                value = int(counts[group_id])
                if value == 0:
                    continue
                rows.append({"group_id": group_id, "count": value})
            elif reduction == "sum":
                value = int(sums[group_id])
                if value == 0:
                    continue
                rows.append({"group_id": group_id, "sum": value})
            elif reduction == "min":
                value = int(mins[group_id])
                if value == 0xFFFFFFFFFFFFFFFF:
                    continue
                rows.append({"group_id": group_id, "min": value})
            elif reduction == "max":
                value = int(maxs[group_id])
                if value == 0:
                    continue
                rows.append({"group_id": group_id, "max": value})
            else:
                count_value = int(counts[group_id])
                if count_value == 0:
                    continue
                rows.append({"group_id": group_id, "sum": int(sums[group_id]), "count": count_value})

        self._run_count += 1
        return {
            "backend": "optix",
            "primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
            "native_symbol": OPTIX_RAY_BATCH_PREPARED_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
            "reduction": reduction,
            "rows": tuple(rows),
            "ray_count": int(rays.ray_count),
            "triangle_count": self.triangle_count,
            "group_count": output_count,
            "hit_event_count_before_dedup": int(hit_event_count.value),
            "rt_core_accelerated": True,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_ray_batch_used": True,
            "prepared_primitive_payload_used": True,
            "prepared_run_index": self._run_count,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "prepared_ray_batch_prepare": float(rays.prepare_seconds),
                "primitive_payload_prepare": float(payload.prepare_seconds),
                "query_pack": 0.0,
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                **getattr(rays, "transfer_metadata", {}),
                "primitive_group_ids_uploaded_each_run": False,
                "primitive_values_uploaded_each_run": False,
                "prepared_primitive_payload_on_device": True,
                "per_ray_records_downloaded_to_host": False,
                "group_rows_downloaded_to_host": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "row_witnesses": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }

    def ray_hit_count_sum(self, rays) -> dict[str, object]:
        """Return the scalar sum of per-ray 3-D triangle hit counts."""
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum. "
                "Rebuild it with 'make build-optix' from current main."
            )

        pack_start = time.perf_counter()
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=3)
        if packed_rays.dimension != 3:
            raise ValueError("ray_hit_count_sum requires 3-D rays")
        query_pack_seconds = time.perf_counter() - pack_start

        hit_count_sum = ctypes.c_uint64()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_rays.records,
            packed_rays.count,
            ctypes.byref(hit_count_sum),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        self._run_count += 1
        return {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_RAY_HIT_COUNT_SUM_V1",
            "result_kind": "uint64_ray_hit_count_sum",
            "hit_count_sum": int(hit_count_sum.value),
            "ray_count": int(packed_rays.count),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "rows_materialized": False,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": True,
                "per_ray_records_downloaded_to_host": False,
                "scalar_sum_returned_to_python": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "row_witnesses": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }

    def ray_closest_hit_rows(self, rays) -> tuple[dict[str, float | int], ...]:
        """Return generic closest-hit rows against this prepared 3-D scene."""
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_ray_closest_hit_rows",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_ray_closest_hit_rows. "
                "Rebuild it with 'make build-optix' from current main."
            )

        pack_start = time.perf_counter()
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=3)
        if packed_rays.dimension != 3:
            raise ValueError("ray_closest_hit_rows requires 3-D rays")
        query_pack_seconds = time.perf_counter() - pack_start

        rows_ptr = ctypes.POINTER(_RtdlRayClosestHitRow)()
        row_count = ctypes.c_size_t()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_rays.records,
            packed_rays.count,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)
        view = OptixRowView(
            library=self._lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlRayClosestHitRow,
            field_names=("ray_id", "triangle_id", "t"),
        )
        try:
            rows = tuple(
                {
                    "ray_id": int(row["ray_id"]),
                    "triangle_id": int(row["triangle_id"]),
                    "t": float(row["t"]),
                }
                for row in view.to_dict_rows()
            )
        finally:
            view.close()

        self._run_count += 1
        self.last_closest_hit_metadata = {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_RAY_CLOSEST_HIT_ROWS_V1",
            "result_kind": "ray_triangle_closest_hit_rows",
            "ray_count": int(packed_rays.count),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "rows_materialized": True,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": True,
                "closest_hit_rows_downloaded_to_host": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }
        return rows

    def ray_closest_hit_row_arrays(self, rays) -> dict[str, object]:
        """Return generic closest-hit rows as NumPy arrays.

        This keeps the primitive app-agnostic while avoiding per-row Python dict
        materialization for benchmark paths that naturally consume columns.
        """
        if isinstance(rays, PreparedOptixRayBatch3D):
            return self.ray_closest_hit_row_arrays_prepared_rays(rays)
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        try:
            import numpy as _np
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("ray_closest_hit_row_arrays requires numpy") from exc
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_ray_closest_hit_rows",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_ray_closest_hit_rows. "
                "Rebuild it with 'make build-optix' from current main."
            )

        pack_start = time.perf_counter()
        packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=3)
        if packed_rays.dimension != 3:
            raise ValueError("ray_closest_hit_row_arrays requires 3-D rays")
        query_pack_seconds = time.perf_counter() - pack_start

        rows_ptr = ctypes.POINTER(_RtdlRayClosestHitRow)()
        row_count = ctypes.c_size_t()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            packed_rays.records,
            packed_rays.count,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)
        view = OptixRowView(
            library=self._lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlRayClosestHitRow,
            field_names=("ray_id", "triangle_id", "t"),
        )
        try:
            row_array = _np.ctypeslib.as_array(rows_ptr, shape=(row_count.value,))
            arrays = {
                "ray_id": _np.array(row_array["ray_id"], dtype=_np.uint32, copy=True),
                "triangle_id": _np.array(row_array["triangle_id"], dtype=_np.uint32, copy=True),
                "t": _np.array(row_array["t"], dtype=_np.float64, copy=True),
            }
        finally:
            view.close()

        self._run_count += 1
        self.last_closest_hit_metadata = {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_RAY_CLOSEST_HIT_ROW_ARRAYS_V1",
            "result_kind": "ray_triangle_closest_hit_row_arrays",
            "ray_count": int(packed_rays.count),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "rows_materialized": False,
            "row_arrays_materialized": True,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": True,
                "closest_hit_rows_downloaded_to_host": True,
                "python_dict_rows_materialized": False,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }
        return arrays

    def ray_closest_hit_row_arrays_prepared_rays(self, ray_batch: PreparedOptixRayBatch3D) -> dict[str, object]:
        """Return closest-hit row arrays using a reusable device-resident ray batch."""
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        if ray_batch._closed:
            raise RuntimeError("prepared OptiX ray batch handle is closed")
        try:
            import numpy as _np
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("ray_closest_hit_row_arrays_prepared_rays requires numpy") from exc
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            "rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_rows",
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                "rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_rows. "
                "Rebuild it with 'make build-optix' from current main."
            )

        rows_ptr = ctypes.POINTER(_RtdlRayClosestHitRow)()
        row_count = ctypes.c_size_t()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            ray_batch._handle,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)
        view = OptixRowView(
            library=self._lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlRayClosestHitRow,
            field_names=("ray_id", "triangle_id", "t"),
        )
        try:
            row_array = _np.ctypeslib.as_array(rows_ptr, shape=(row_count.value,))
            arrays = {
                "ray_id": _np.array(row_array["ray_id"], dtype=_np.uint32, copy=True),
                "triangle_id": _np.array(row_array["triangle_id"], dtype=_np.uint32, copy=True),
                "t": _np.array(row_array["t"], dtype=_np.float64, copy=True),
            }
        finally:
            view.close()

        self._run_count += 1
        self.last_closest_hit_metadata = {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_CLOSEST_HIT_ROW_ARRAYS_V1",
            "result_kind": "ray_triangle_closest_hit_row_arrays",
            "ray_count": int(ray_batch.ray_count),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_ray_batch_used": True,
            "prepared_ray_batch_seconds": float(ray_batch.prepare_seconds),
            "prepared_run_index": self._run_count,
            "rows_materialized": False,
            "row_arrays_materialized": True,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": 0.0,
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": False,
                "prepared_rays_resident_on_device": True,
                "closest_hit_rows_downloaded_to_host": True,
                "python_dict_rows_materialized": False,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }
        return arrays

    def ray_closest_hit_grouped_argmin(
        self,
        rays,
        ray_group_ids,
        candidate_values,
        candidate_indices,
        *,
        group_count: int | None = None,
    ) -> dict[str, object]:
        """Return grouped argmin over closest-hit triangle ids.

        ``ray_group_ids`` maps RTDL ray ids to output groups. ``candidate_values``
        and ``candidate_indices`` map closest-hit triangle ids to caller-owned
        values and tie-break indices. The primitive stays app-agnostic: the
        runtime only sees ray ids, triangle ids, groups, values, and argmin.
        """
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        try:
            import numpy as _np
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("ray_closest_hit_grouped_argmin requires numpy") from exc

        pack_start = time.perf_counter()
        prepared_ray_batch = isinstance(rays, PreparedOptixRayBatch3D)
        if prepared_ray_batch:
            if rays._closed:
                raise RuntimeError("prepared OptiX ray batch handle is closed")
            packed_rays = None
            ray_count = int(rays.ray_count)
        else:
            packed_rays = rays if isinstance(rays, PackedRays) else pack_rays(rays, dimension=3)
            if packed_rays.dimension != 3:
                raise ValueError("ray_closest_hit_grouped_argmin requires 3-D rays")
            ray_count = int(packed_rays.count)

        raw_group_ids = _np.asarray(ray_group_ids)
        if raw_group_ids.ndim != 1:
            raise ValueError("ray_group_ids must be a one-dimensional ray-id-to-group map")
        if raw_group_ids.size:
            if bool((raw_group_ids < 0).any()):
                raise ValueError("ray_group_ids must be nonnegative")
            max_group_id = int(raw_group_ids.max())
        else:
            max_group_id = -1
        if group_count is None:
            group_count = max_group_id + 1 if max_group_id >= 0 else 0
        group_count = int(group_count)
        if group_count < 0:
            raise ValueError("group_count must be nonnegative")
        if max_group_id >= group_count:
            raise ValueError("ray_group_ids contains a group outside group_count")
        group_ids_np = _np.ascontiguousarray(raw_group_ids, dtype=_np.uint32)

        candidate_values_np = _np.ascontiguousarray(candidate_values, dtype=_np.float64)
        raw_candidate_indices = _np.asarray(candidate_indices)
        if raw_candidate_indices.ndim != 1:
            raise ValueError("candidate_indices must be one-dimensional")
        if raw_candidate_indices.size:
            if bool((raw_candidate_indices < 0).any()):
                raise ValueError("candidate_indices must be nonnegative")
        candidate_indices_np = _np.ascontiguousarray(raw_candidate_indices, dtype=_np.uint32)
        if candidate_values_np.ndim != 1:
            raise ValueError("candidate_values must be one-dimensional")
        if candidate_values_np.shape[0] != candidate_indices_np.shape[0]:
            raise ValueError("candidate_values and candidate_indices must have the same length")

        group_has_value = _np.zeros(group_count, dtype=_np.uint8)
        group_index = _np.full(group_count, _np.iinfo(_np.uint32).max, dtype=_np.uint32)
        group_value = _np.zeros(group_count, dtype=_np.float64)
        query_pack_seconds = time.perf_counter() - pack_start

        run_symbol_name = (
            "rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_grouped_argmin"
            if prepared_ray_batch
            else "rtdl_optix_static_triangle_scene_3d_ray_closest_hit_grouped_argmin"
        )
        run_symbol = _find_optional_backend_symbol(self._lib, run_symbol_name)
        if run_symbol is None:
            fallback_arrays = self.ray_closest_hit_row_arrays(rays if prepared_ray_batch else packed_rays)
            ray_ids = _np.asarray(fallback_arrays["ray_id"], dtype=_np.int64)
            triangle_ids = _np.asarray(fallback_arrays["triangle_id"], dtype=_np.int64)
            fallback_metadata = dict(getattr(self, "last_closest_hit_metadata", {}))
            for ray_id, triangle_id in zip(ray_ids, triangle_ids):
                if ray_id < 0 or ray_id >= group_ids_np.shape[0]:
                    raise RuntimeError("hit ray_id is outside the ray group-id map")
                if triangle_id < 0 or triangle_id >= candidate_values_np.shape[0]:
                    continue
                group_id = int(group_ids_np[ray_id])
                candidate_value = float(candidate_values_np[triangle_id])
                candidate_index = int(candidate_indices_np[triangle_id])
                take = (
                    group_has_value[group_id] == 0
                    or candidate_value < float(group_value[group_id])
                    or (
                        candidate_value == float(group_value[group_id])
                        and candidate_index < int(group_index[group_id])
                    )
                )
                if take:
                    group_has_value[group_id] = 1
                    group_index[group_id] = candidate_index
                    group_value[group_id] = candidate_value

            self.last_closest_hit_metadata = {
                "backend": "optix",
                "contract": "PREPARED_TRIANGLE_SCENE_3D_RAY_CLOSEST_HIT_GROUPED_ARGMIN_V1",
                "result_kind": "grouped_argmin_from_ray_triangle_closest_hit",
                "ray_count": int(ray_count),
                "triangle_count": self.triangle_count,
                "group_count": int(group_count),
                "prepared_reused": True,
                "prepared_scene_used": True,
                "prepared_run_index": int(self._run_count),
                "native_grouped_argmin": False,
                "fallback_row_arrays_metadata": fallback_metadata,
                "phase_timing_seconds": {
                    "prepare_build": float(self.prepare_seconds),
                    "query_pack": float(query_pack_seconds),
                    "traversal": fallback_metadata.get("phase_timing_seconds", {}).get("traversal", 0.0),
                },
                "transfer_metadata": {
                    "static_scene_prepared_on_device": True,
                    "query_rays_uploaded_each_run": not prepared_ray_batch,
                    "prepared_rays_resident_on_device": bool(prepared_ray_batch),
                    "closest_hit_rows_downloaded_to_host": True,
                    "python_dict_rows_materialized": False,
                    "native_host_grouped_argmin": False,
                    "native_device_grouped_argmin": False,
                    "true_zero_copy_authorized": False,
                },
                "claim_boundary": {
                    "native_app_api": False,
                    "public_speedup_claim": False,
                    "true_zero_copy": False,
                },
            }
            return {
                "has_value": group_has_value,
                "index": group_index,
                "value": group_value,
                "metadata": dict(self.last_closest_hit_metadata),
            }

        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        if prepared_ray_batch:
            status = run_symbol(
                self._handle,
                rays._handle,
                group_ids_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                ctypes.c_size_t(group_ids_np.shape[0]),
                candidate_values_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                candidate_indices_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                ctypes.c_size_t(candidate_values_np.shape[0]),
                ctypes.c_size_t(group_count),
                group_has_value.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
                group_index.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                group_value.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                ctypes.byref(traversal_seconds),
                error,
                len(error),
            )
        else:
            status = run_symbol(
                self._handle,
                packed_rays.records,
                packed_rays.count,
                group_ids_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                ctypes.c_size_t(group_ids_np.shape[0]),
                candidate_values_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                candidate_indices_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                ctypes.c_size_t(candidate_values_np.shape[0]),
                ctypes.c_size_t(group_count),
                group_has_value.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
                group_index.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                group_value.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                ctypes.byref(traversal_seconds),
                error,
                len(error),
            )
        _check_status(status, error)

        self._run_count += 1
        self.last_closest_hit_metadata = {
            "backend": "optix",
            "contract": (
                "PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_CLOSEST_HIT_GROUPED_ARGMIN_V1"
                if prepared_ray_batch
                else "PREPARED_TRIANGLE_SCENE_3D_RAY_CLOSEST_HIT_GROUPED_ARGMIN_V1"
            ),
            "result_kind": "grouped_argmin_from_ray_triangle_closest_hit",
            "ray_count": int(ray_count),
            "triangle_count": self.triangle_count,
            "group_count": int(group_count),
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_ray_batch_used": bool(prepared_ray_batch),
            "prepared_ray_batch_seconds": (
                float(rays.prepare_seconds)
                if prepared_ray_batch
                else 0.0
            ),
            "prepared_run_index": self._run_count,
            "rows_materialized": False,
            "row_arrays_materialized": False,
            "native_grouped_argmin": True,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": not prepared_ray_batch,
                "prepared_rays_resident_on_device": bool(prepared_ray_batch),
                "closest_hit_rows_downloaded_to_host": False,
                "per_group_results_downloaded_to_host": True,
                "python_dict_rows_materialized": False,
                "native_host_grouped_argmin": False,
                "native_device_grouped_argmin": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }
        return {
            "has_value": group_has_value,
            "index": group_index,
            "value": group_value,
            "metadata": dict(self.last_closest_hit_metadata),
        }

    def ray_any_hit_weighted_sum_device_columns(self, ray_columns: dict, ray_weights) -> dict[str, object]:
        """Return weighted any-hit sum from partner-owned 3-D ray columns."""
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            _OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_WEIGHTED_SUM_SYMBOL,
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{_OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_WEIGHTED_SUM_SYMBOL}. "
                "Rebuild it with 'make build-optix' from current main."
            )
        pack_start = time.perf_counter()
        packet = pack_optix_static_triangle_scene_3d_device_weighted_ray_inputs(ray_columns, ray_weights)
        query_pack_seconds = time.perf_counter() - pack_start
        rays = packet["rays"]

        weighted_sum = ctypes.c_uint64()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            ctypes.c_void_p(rays["ids"].data_ptr),
            ctypes.c_void_p(rays["ox"].data_ptr),
            ctypes.c_void_p(rays["oy"].data_ptr),
            ctypes.c_void_p(rays["oz"].data_ptr),
            ctypes.c_void_p(rays["dx"].data_ptr),
            ctypes.c_void_p(rays["dy"].data_ptr),
            ctypes.c_void_p(rays["dz"].data_ptr),
            ctypes.c_void_p(rays["tmax"].data_ptr),
            packet["metadata"]["ray_count"],
            ctypes.c_void_p(packet["ray_weights"].data_ptr),
            ctypes.byref(weighted_sum),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        self._run_count += 1
        return {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_RAY_ANY_HIT_WEIGHTED_SUM_DEVICE_COLUMNS_V1",
            "result_kind": "uint64_weighted_any_hit_sum",
            "weighted_hit_sum": int(weighted_sum.value),
            "ray_count": int(packet["metadata"]["ray_count"]),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "rows_materialized": False,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                **packet["metadata"],
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": False,
                "ray_weights_uploaded_each_run": False,
                "query_rays_packed_on_device_each_run": True,
                "per_ray_records_downloaded_to_host": False,
                "scalar_sum_returned_to_python": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "row_witnesses": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }

    def ray_hit_count_sum_device_columns(self, ray_columns: dict) -> dict[str, object]:
        """Return hit-count sum from partner-owned 3-D ray columns."""
        if self._closed:
            raise RuntimeError("prepared OptiX static triangle scene handle is closed")
        run_symbol = _find_optional_backend_symbol(
            self._lib,
            _OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_HIT_COUNT_SUM_SYMBOL,
        )
        if run_symbol is None:
            raise RuntimeError(
                "Loaded OptiX backend library does not export "
                f"{_OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_HIT_COUNT_SUM_SYMBOL}. "
                "Rebuild it with 'make build-optix' from current main."
            )
        pack_start = time.perf_counter()
        packet = pack_optix_static_triangle_scene_3d_device_ray_inputs(ray_columns)
        query_pack_seconds = time.perf_counter() - pack_start
        rays = packet["rays"]

        hit_count_sum = ctypes.c_uint64()
        traversal_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        status = run_symbol(
            self._handle,
            ctypes.c_void_p(rays["ids"].data_ptr),
            ctypes.c_void_p(rays["ox"].data_ptr),
            ctypes.c_void_p(rays["oy"].data_ptr),
            ctypes.c_void_p(rays["oz"].data_ptr),
            ctypes.c_void_p(rays["dx"].data_ptr),
            ctypes.c_void_p(rays["dy"].data_ptr),
            ctypes.c_void_p(rays["dz"].data_ptr),
            ctypes.c_void_p(rays["tmax"].data_ptr),
            packet["metadata"]["ray_count"],
            ctypes.byref(hit_count_sum),
            ctypes.byref(traversal_seconds),
            error,
            len(error),
        )
        _check_status(status, error)

        self._run_count += 1
        return {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_RAY_HIT_COUNT_SUM_DEVICE_COLUMNS_V1",
            "result_kind": "uint64_ray_hit_count_sum",
            "hit_count_sum": int(hit_count_sum.value),
            "ray_count": int(packet["metadata"]["ray_count"]),
            "triangle_count": self.triangle_count,
            "prepared_reused": True,
            "prepared_scene_used": True,
            "prepared_run_index": self._run_count,
            "rows_materialized": False,
            "phase_timing_seconds": {
                "prepare_build": float(self.prepare_seconds),
                "query_pack": float(query_pack_seconds),
                "traversal": float(traversal_seconds.value),
            },
            "transfer_metadata": {
                **packet["metadata"],
                "static_scene_prepared_on_device": True,
                "query_rays_uploaded_each_run": False,
                "query_rays_packed_on_device_each_run": True,
                "per_ray_records_downloaded_to_host": False,
                "scalar_sum_returned_to_python": True,
                "true_zero_copy_authorized": False,
            },
            "claim_boundary": {
                "native_app_api": False,
                "row_witnesses": False,
                "public_speedup_claim": False,
                "true_zero_copy": False,
            },
        }


def prepare_optix_static_triangle_scene_3d(triangles) -> PreparedOptixStaticTriangleScene3D:
    return PreparedOptixStaticTriangleScene3D(triangles)


def ray_triangle_hit_stream_3d_optix(
    rays,
    triangles,
    *,
    max_rows: int | None = None,
    deduplicate_primitives: bool = True,
) -> dict[str, object]:
    """Emit generic 3-D ray/triangle hit rows on OptiX."""
    with prepare_optix_static_triangle_scene_3d(triangles) as prepared:
        return prepared.ray_triangle_hit_stream(
            rays,
            max_rows=max_rows,
            deduplicate_primitives=deduplicate_primitives,
        )


def prepare_optix_static_triangle_scene_3d_device_triangles(
    triangle_columns: dict,
) -> PreparedOptixStaticTriangleScene3D:
    packet = pack_optix_static_triangle_scene_3d_device_triangle_inputs(triangle_columns)
    prepared = PreparedOptixStaticTriangleScene3D.__new__(PreparedOptixStaticTriangleScene3D)
    prepared._lib = _load_optix_library()
    prepared._handle = ctypes.c_void_p()
    prepared._closed = False
    prepared._run_count = 0
    prepared._packed_triangles = PackedTriangles(
        records=None,
        count=int(packet["metadata"]["triangle_count"]),
        dimension=3,
        owner=packet,
    )
    prepared.triangle_count = int(packet["metadata"]["triangle_count"])
    prepared._device_triangle_packet = packet
    create_symbol = _find_optional_backend_symbol(
        prepared._lib,
        _OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_TRIANGLES_SYMBOL,
    )
    if create_symbol is None:
        raise RuntimeError(
            "Loaded OptiX backend library does not export "
            f"{_OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_TRIANGLES_SYMBOL}. "
            "Rebuild it with 'make build-optix' from current main."
        )
    if prepared.triangle_count == 0:
        prepared.prepare_seconds = 0.0
        return prepared

    triangles = packet["triangles"]
    error = ctypes.create_string_buffer(4096)
    prepare_start = time.perf_counter()
    status = create_symbol(
        ctypes.c_void_p(triangles["ids"].data_ptr),
        ctypes.c_void_p(triangles["x0"].data_ptr),
        ctypes.c_void_p(triangles["y0"].data_ptr),
        ctypes.c_void_p(triangles["z0"].data_ptr),
        ctypes.c_void_p(triangles["x1"].data_ptr),
        ctypes.c_void_p(triangles["y1"].data_ptr),
        ctypes.c_void_p(triangles["z1"].data_ptr),
        ctypes.c_void_p(triangles["x2"].data_ptr),
        ctypes.c_void_p(triangles["y2"].data_ptr),
        ctypes.c_void_p(triangles["z2"].data_ptr),
        prepared.triangle_count,
        ctypes.byref(prepared._handle),
        error,
        len(error),
    )
    prepared.prepare_seconds = time.perf_counter() - prepare_start
    _check_status(status, error)
    return prepared


def prepare_optix_grouped_segment_query_3d(
    segment_start_xyz,
    segment_end_xyz,
    segment_group_offsets,
) -> PreparedOptixGroupedSegmentQuery3D:
    """Prepare reusable native OptiX device buffers for a grouped finite 3D segment query."""
    return PreparedOptixGroupedSegmentQuery3D(
        segment_start_xyz,
        segment_end_xyz,
        segment_group_offsets,
    )


def run_optix_grouped_segment_any_hit_flags_3d(
    triangles,
    segment_start_xyz,
    segment_end_xyz,
    segment_group_offsets,
) -> dict[str, object]:
    with prepare_optix_static_triangle_scene_3d(triangles) as prepared:
        return prepared.run_grouped_segment_any_hit_flags(
            segment_start_xyz,
            segment_end_xyz,
            segment_group_offsets,
        )


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
    _ensure_cuda_driver_initialized()
    lib_path = _find_optix_library()
    lib = ctypes.CDLL(str(lib_path))
    lib._rtdl_library_path = str(lib_path)
    _register_argtypes(lib)
    return lib


@functools.lru_cache(maxsize=1)
def _ensure_cuda_driver_initialized() -> None:
    """Initialize CUDA before the first OptiX native call.

    CuPy/PyTorch users often initialize the CUDA driver before reaching RTDL.
    Host-staged NumPy inputs do not, so RTDL must not accidentally depend on a
    partner framework side effect.
    """
    name = ctypes.util.find_library("cuda") or "libcuda.so.1"
    try:
        cuda = ctypes.CDLL(name)
    except OSError as exc:
        raise RuntimeError(
            "CUDA driver library is required for the OptiX backend; "
            "could not load libcuda.so.1"
        ) from exc
    cuda.cuInit.argtypes = [ctypes.c_uint]
    cuda.cuInit.restype = ctypes.c_int
    status = int(cuda.cuInit(0))
    if status != 0:
        raise RuntimeError(f"CUDA driver initialization failed with cuInit status {status}")
    device = ctypes.c_int()
    cuda.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cuda.cuDeviceGet.restype = ctypes.c_int
    status = int(cuda.cuDeviceGet(ctypes.byref(device), 0))
    if status != 0:
        raise RuntimeError(f"CUDA device 0 lookup failed with cuDeviceGet status {status}")
    context = ctypes.c_void_p()
    cuda.cuDevicePrimaryCtxRetain.argtypes = [
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_int,
    ]
    cuda.cuDevicePrimaryCtxRetain.restype = ctypes.c_int
    status = int(cuda.cuDevicePrimaryCtxRetain(ctypes.byref(context), device.value))
    if status != 0:
        raise RuntimeError(
            f"CUDA primary context retain failed with cuDevicePrimaryCtxRetain status {status}"
        )
    cuda.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
    cuda.cuCtxSetCurrent.restype = ctypes.c_int
    status = int(cuda.cuCtxSetCurrent(context))
    if status != 0:
        raise RuntimeError(f"CUDA current context setup failed with cuCtxSetCurrent status {status}")


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
    optional_prepare_segment_pair = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_segment_pair_intersection",
    )
    if optional_prepare_segment_pair is not None:
        optional_prepare_segment_pair.argtypes = [
            ctypes.POINTER(_RtdlSegment),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_segment_pair.restype = ctypes.c_int
    optional_run_prepared_segment_pair = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_prepared_segment_pair_intersection",
    )
    if optional_run_prepared_segment_pair is not None:
        optional_run_prepared_segment_pair.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlSegment),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_run_prepared_segment_pair.restype = ctypes.c_int
    optional_count_prepared_segment_pair = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_count_prepared_segment_pair_intersection",
    )
    if optional_count_prepared_segment_pair is not None:
        optional_count_prepared_segment_pair.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlSegment),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_count_prepared_segment_pair.restype = ctypes.c_int
    optional_run_prepared_segment_first_hit = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_prepared_segment_first_hit",
    )
    if optional_run_prepared_segment_first_hit is not None:
        optional_run_prepared_segment_first_hit.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlSegment),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlSegmentFirstHitRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_run_prepared_segment_first_hit.restype = ctypes.c_int
    optional_count_prepared_segment_first_hit = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_count_prepared_segment_first_hit",
    )
    if optional_count_prepared_segment_first_hit is not None:
        optional_count_prepared_segment_first_hit.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlSegment),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_count_prepared_segment_first_hit.restype = ctypes.c_int
    optional_destroy_prepared_segment_pair = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_destroy_prepared_segment_pair_intersection",
    )
    if optional_destroy_prepared_segment_pair is not None:
        optional_destroy_prepared_segment_pair.argtypes = [ctypes.c_void_p]
        optional_destroy_prepared_segment_pair.restype = None

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

    optional_closed_shape_membership = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_point_closed_shape_membership_2d",
    )
    if optional_closed_shape_membership is not None:
        optional_closed_shape_membership.argtypes = [
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.POINTER(_RtdlClosedShapeRef), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.POINTER(_RtdlPointClosedShapeMembershipRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_closed_shape_membership.restype = ctypes.c_int

    optional_prepare_closed_shape_membership = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_point_closed_shape_membership_2d",
    )
    if optional_prepare_closed_shape_membership is not None:
        optional_prepare_closed_shape_membership.argtypes = [
            ctypes.POINTER(_RtdlClosedShapeRef), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_prepare_closed_shape_membership.restype = ctypes.c_int

    optional_run_prepared_closed_shape_membership = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_prepared_point_closed_shape_membership_2d",
    )
    if optional_run_prepared_closed_shape_membership is not None:
        optional_run_prepared_closed_shape_membership.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.POINTER(_RtdlPointClosedShapeMembershipRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_run_prepared_closed_shape_membership.restype = ctypes.c_int

    optional_count_prepared_closed_shape_membership = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_count_prepared_point_closed_shape_membership_2d",
    )
    if optional_count_prepared_closed_shape_membership is not None:
        optional_count_prepared_closed_shape_membership.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_count_prepared_closed_shape_membership.restype = ctypes.c_int

    optional_destroy_prepared_closed_shape_membership = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_destroy_prepared_point_closed_shape_membership_2d",
    )
    if optional_destroy_prepared_closed_shape_membership is not None:
        optional_destroy_prepared_closed_shape_membership.argtypes = [ctypes.c_void_p]
        optional_destroy_prepared_closed_shape_membership.restype = None

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
    optional_prepare_shape_pair_relation = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_shape_pair_relation_flags",
    )
    if optional_prepare_shape_pair_relation is not None:
        optional_prepare_shape_pair_relation.argtypes = [
            ctypes.POINTER(_RtdlPolygonRef),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_shape_pair_relation.restype = ctypes.c_int
    optional_run_prepared_shape_pair_relation = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_prepared_shape_pair_relation_flags",
    )
    if optional_run_prepared_shape_pair_relation is not None:
        optional_run_prepared_shape_pair_relation.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPolygonRef),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlOverlayRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_run_prepared_shape_pair_relation.restype = ctypes.c_int
    optional_destroy_prepared_shape_pair_relation = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_destroy_prepared_shape_pair_relation_flags",
    )
    if optional_destroy_prepared_shape_pair_relation is not None:
        optional_destroy_prepared_shape_pair_relation.argtypes = [ctypes.c_void_p]
        optional_destroy_prepared_shape_pair_relation.restype = None

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
    optional_closest_hit3d = _find_optional_backend_symbol(lib, "rtdl_optix_run_ray_closest_hit_3d")
    if optional_closest_hit3d is not None:
        optional_closest_hit3d.argtypes = [
            ctypes.POINTER(_RtdlRay3D), ctypes.c_size_t,
            ctypes.POINTER(_RtdlTriangle3D), ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayClosestHitRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_closest_hit3d.restype = ctypes.c_int
    optional_static_scene_3d_create = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_create",
    )
    if optional_static_scene_3d_create is not None:
        optional_static_scene_3d_create.argtypes = [
            ctypes.POINTER(_RtdlTriangle3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_create.restype = ctypes.c_int
    optional_static_scene_3d_device_create = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_TRIANGLES_SYMBOL,
    )
    if optional_static_scene_3d_device_create is not None:
        optional_static_scene_3d_device_create.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
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
        optional_static_scene_3d_device_create.restype = ctypes.c_int
    optional_static_scene_3d_run = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags",
    )
    if optional_static_scene_3d_run is not None:
        optional_static_scene_3d_run.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlSegment3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_run.restype = ctypes.c_int
    optional_static_scene_3d_query_create = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_create",
    )
    if optional_static_scene_3d_query_create is not None:
        optional_static_scene_3d_query_create.argtypes = [
            ctypes.POINTER(_RtdlSegment3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_query_create.restype = ctypes.c_int
    optional_static_scene_3d_query_run = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_flags",
    )
    if optional_static_scene_3d_query_run is not None:
        optional_static_scene_3d_query_run.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_query_run.restype = ctypes.c_int
    optional_static_scene_3d_query_count = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_count",
    )
    if optional_static_scene_3d_query_count is not None:
        optional_static_scene_3d_query_count.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_query_count.restype = ctypes.c_int
    optional_static_scene_3d_weighted_sum = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum",
    )
    if optional_static_scene_3d_weighted_sum is not None:
        optional_static_scene_3d_weighted_sum.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_weighted_sum.restype = ctypes.c_int
    optional_static_scene_3d_device_weighted_sum = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_WEIGHTED_SUM_SYMBOL,
    )
    if optional_static_scene_3d_device_weighted_sum is not None:
        optional_static_scene_3d_device_weighted_sum.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_device_weighted_sum.restype = ctypes.c_int
    optional_static_scene_3d_primitive_grouped = _find_optional_backend_symbol(
        lib,
        OPTIX_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
    )
    if optional_static_scene_3d_primitive_grouped is not None:
        optional_static_scene_3d_primitive_grouped.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_primitive_grouped.restype = ctypes.c_int
    optional_primitive_grouped_payload_3d_create = _find_optional_backend_symbol(
        lib,
        OPTIX_PRIMITIVE_GROUPED_I64_PAYLOAD_3D_CREATE_SYMBOL,
    )
    if optional_primitive_grouped_payload_3d_create is not None:
        optional_primitive_grouped_payload_3d_create.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_primitive_grouped_payload_3d_create.restype = ctypes.c_int
    optional_prepared_static_scene_3d_primitive_grouped = _find_optional_backend_symbol(
        lib,
        OPTIX_PREPARED_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
    )
    if optional_prepared_static_scene_3d_primitive_grouped is not None:
        optional_prepared_static_scene_3d_primitive_grouped.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepared_static_scene_3d_primitive_grouped.restype = ctypes.c_int
    optional_ray_batch_prepared_primitive_grouped = _find_optional_backend_symbol(
        lib,
        OPTIX_RAY_BATCH_PREPARED_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
    )
    if optional_ray_batch_prepared_primitive_grouped is not None:
        optional_ray_batch_prepared_primitive_grouped.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_ray_batch_prepared_primitive_grouped.restype = ctypes.c_int
    optional_primitive_grouped_payload_3d_destroy = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_primitive_grouped_i64_payload_3d_destroy",
    )
    if optional_primitive_grouped_payload_3d_destroy is not None:
        optional_primitive_grouped_payload_3d_destroy.argtypes = [ctypes.c_void_p]
        optional_primitive_grouped_payload_3d_destroy.restype = None
    optional_static_scene_3d_hit_count_sum = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum",
    )
    if optional_static_scene_3d_hit_count_sum is not None:
        optional_static_scene_3d_hit_count_sum.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_hit_count_sum.restype = ctypes.c_int
    optional_static_scene_3d_hit_stream = _find_optional_backend_symbol(
        lib,
        OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_SYMBOL,
    )
    if optional_static_scene_3d_hit_stream is not None:
        optional_static_scene_3d_hit_stream.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(_RtdlRayTriangleHitStreamRow),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_hit_stream.restype = ctypes.c_int
    optional_static_scene_3d_closest_hit_rows = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_ray_closest_hit_rows",
    )
    if optional_static_scene_3d_closest_hit_rows is not None:
        optional_static_scene_3d_closest_hit_rows.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayClosestHitRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_closest_hit_rows.restype = ctypes.c_int
    optional_ray_batch_3d_create = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_ray_batch_3d_create",
    )
    if optional_ray_batch_3d_create is not None:
        optional_ray_batch_3d_create.argtypes = [
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_ray_batch_3d_create.restype = ctypes.c_int
    optional_ray_batch_3d_create_device = _find_optional_backend_symbol(
        lib,
        OPTIX_RAY_BATCH_3D_CREATE_DEVICE_RAYS_SYMBOL,
    )
    if optional_ray_batch_3d_create_device is not None:
        optional_ray_batch_3d_create_device.argtypes = [
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
        optional_ray_batch_3d_create_device.restype = ctypes.c_int
    optional_grouped_argmin_inputs_3d_create = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create",
    )
    if optional_grouped_argmin_inputs_3d_create is not None:
        optional_grouped_argmin_inputs_3d_create.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_grouped_argmin_inputs_3d_create.restype = ctypes.c_int
    optional_grouped_candidate_argmin_inputs_create = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_grouped_candidate_argmin_inputs_create",
    )
    if optional_grouped_candidate_argmin_inputs_create is not None:
        optional_grouped_candidate_argmin_inputs_create.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_grouped_candidate_argmin_inputs_create.restype = ctypes.c_int
    optional_grouped_candidate_argmin_finalize = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_grouped_candidate_argmin_finalize",
    )
    if optional_grouped_candidate_argmin_finalize is not None:
        optional_grouped_candidate_argmin_finalize.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_grouped_candidate_argmin_finalize.restype = ctypes.c_int
    optional_static_scene_3d_ray_batch_closest_hit_rows = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_rows",
    )
    if optional_static_scene_3d_ray_batch_closest_hit_rows is not None:
        optional_static_scene_3d_ray_batch_closest_hit_rows.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlRayClosestHitRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_ray_batch_closest_hit_rows.restype = ctypes.c_int
    optional_static_scene_3d_closest_hit_grouped_argmin = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_ray_closest_hit_grouped_argmin",
    )
    if optional_static_scene_3d_closest_hit_grouped_argmin is not None:
        optional_static_scene_3d_closest_hit_grouped_argmin.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay3D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_closest_hit_grouped_argmin.restype = ctypes.c_int
    optional_static_scene_3d_ray_batch_closest_hit_grouped_argmin = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_grouped_argmin",
    )
    if optional_static_scene_3d_ray_batch_closest_hit_grouped_argmin is not None:
        optional_static_scene_3d_ray_batch_closest_hit_grouped_argmin.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_ray_batch_closest_hit_grouped_argmin.restype = ctypes.c_int
    optional_static_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin",
    )
    if optional_static_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin is not None:
        optional_static_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin.restype = ctypes.c_int
    optional_static_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin",
    )
    if optional_static_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin is not None:
        optional_static_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin.restype = ctypes.c_int
    optional_static_scene_3d_device_hit_count_sum = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_STATIC_TRIANGLE_SCENE_3D_DEVICE_HIT_COUNT_SUM_SYMBOL,
    )
    if optional_static_scene_3d_device_hit_count_sum is not None:
        optional_static_scene_3d_device_hit_count_sum.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_static_scene_3d_device_hit_count_sum.restype = ctypes.c_int
    optional_static_scene_3d_query_destroy = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_destroy",
    )
    if optional_static_scene_3d_query_destroy is not None:
        optional_static_scene_3d_query_destroy.argtypes = [ctypes.c_void_p]
        optional_static_scene_3d_query_destroy.restype = None
    optional_ray_batch_3d_destroy = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_ray_batch_3d_destroy",
    )
    if optional_ray_batch_3d_destroy is not None:
        optional_ray_batch_3d_destroy.argtypes = [ctypes.c_void_p]
        optional_ray_batch_3d_destroy.restype = None
    optional_grouped_argmin_inputs_3d_destroy = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_closest_hit_grouped_argmin_inputs_3d_destroy",
    )
    if optional_grouped_argmin_inputs_3d_destroy is not None:
        optional_grouped_argmin_inputs_3d_destroy.argtypes = [ctypes.c_void_p]
        optional_grouped_argmin_inputs_3d_destroy.restype = None
    optional_grouped_candidate_argmin_inputs_destroy = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_grouped_candidate_argmin_inputs_destroy",
    )
    if optional_grouped_candidate_argmin_inputs_destroy is not None:
        optional_grouped_candidate_argmin_inputs_destroy.argtypes = [ctypes.c_void_p]
        optional_grouped_candidate_argmin_inputs_destroy.restype = None
    optional_static_scene_3d_destroy = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_static_triangle_scene_3d_destroy",
    )
    if optional_static_scene_3d_destroy is not None:
        optional_static_scene_3d_destroy.argtypes = [ctypes.c_void_p]
        optional_static_scene_3d_destroy.restype = None
    optional_ray_segment_group_count = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_ray_segment_group_count_2d",
    )
    if optional_ray_segment_group_count is not None:
        optional_ray_segment_group_count.argtypes = [
            ctypes.POINTER(_RtdlRay2D), ctypes.c_size_t,
            ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.POINTER(_RtdlRaySegmentGroupCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_ray_segment_group_count.restype = ctypes.c_int
    optional_prepare_ray_segment_group_count = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_ray_segment_group_count_2d",
    )
    if optional_prepare_ray_segment_group_count is not None:
        optional_prepare_ray_segment_group_count.argtypes = [
            ctypes.POINTER(_RtdlSegment), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_prepare_ray_segment_group_count.restype = ctypes.c_int
    optional_run_prepared_ray_segment_group_count = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_prepared_ray_segment_group_count_2d",
    )
    if optional_run_prepared_ray_segment_group_count is not None:
        optional_run_prepared_ray_segment_group_count.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay2D), ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRaySegmentGroupCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_run_prepared_ray_segment_group_count.restype = ctypes.c_int
    optional_run_prepared_ray_segment_group_odd_parity = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d",
    )
    if optional_run_prepared_ray_segment_group_odd_parity is not None:
        optional_run_prepared_ray_segment_group_odd_parity.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlRay2D), ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlRaySegmentGroupCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_run_prepared_ray_segment_group_odd_parity.restype = ctypes.c_int
    optional_destroy_prepared_ray_segment_group_count = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_destroy_prepared_ray_segment_group_count_2d",
    )
    if optional_destroy_prepared_ray_segment_group_count is not None:
        optional_destroy_prepared_ray_segment_group_count.argtypes = [ctypes.c_void_p]
        optional_destroy_prepared_ray_segment_group_count.restype = None
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
    optional_write_anyhit2d_device_all_witnesses = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_DEVICE_ALL_WITNESSES_SYMBOL,
    )
    if optional_write_anyhit2d_device_all_witnesses is not None:
        optional_write_anyhit2d_device_all_witnesses.argtypes = [
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
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_write_anyhit2d_device_all_witnesses.restype = ctypes.c_int
    optional_destroy_anyhit2d = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_ray_anyhit_2d")
    if optional_destroy_anyhit2d is not None:
        optional_destroy_anyhit2d.argtypes = [ctypes.c_void_p]
        optional_destroy_anyhit2d.restype = None
    optional_prepare_aabb_index2d = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_aabb_index_2d")
    if optional_prepare_aabb_index2d is not None:
        optional_prepare_aabb_index2d.argtypes = [
            ctypes.POINTER(_RtdlAabb2D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_aabb_index2d.restype = ctypes.c_int
    optional_count_aabb_index2d = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_aabb_index_2d")
    if optional_count_aabb_index2d is not None:
        optional_count_aabb_index2d.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlAabb2D),
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_count_aabb_index2d.restype = ctypes.c_int
    optional_prepare_aabb_point_queries2d = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_aabb_point_queries_2d",
    )
    if optional_prepare_aabb_point_queries2d is not None:
        optional_prepare_aabb_point_queries2d.argtypes = [
            ctypes.POINTER(_RtdlPoint),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_aabb_point_queries2d.restype = ctypes.c_int
    optional_prepare_aabb_box_queries2d = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_prepare_aabb_box_queries_2d",
    )
    if optional_prepare_aabb_box_queries2d is not None:
        optional_prepare_aabb_box_queries2d.argtypes = [
            ctypes.POINTER(_RtdlAabb2D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_aabb_box_queries2d.restype = ctypes.c_int
    optional_count_aabb_index2d_packed_queries = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_count_prepared_aabb_index_2d_packed_queries",
    )
    if optional_count_aabb_index2d_packed_queries is not None:
        optional_count_aabb_index2d_packed_queries.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_count_aabb_index2d_packed_queries.restype = ctypes.c_int
    optional_collect_aabb_index2d_rows = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows",
    )
    if optional_collect_aabb_index2d_rows is not None:
        optional_collect_aabb_index2d_rows.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlAabb2D),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlAabbPairRow),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_collect_aabb_index2d_rows.restype = ctypes.c_int
    optional_collect_aabb_index2d_point_rows = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows",
    )
    if optional_collect_aabb_index2d_point_rows is not None:
        optional_collect_aabb_index2d_point_rows.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlAabbPairRow),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_collect_aabb_index2d_point_rows.restype = ctypes.c_int
    optional_destroy_aabb_queries2d = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_destroy_prepared_aabb_queries_2d",
    )
    if optional_destroy_aabb_queries2d is not None:
        optional_destroy_aabb_queries2d.argtypes = [ctypes.c_void_p]
        optional_destroy_aabb_queries2d.restype = None
    optional_destroy_aabb_index2d = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_aabb_index_2d")
    if optional_destroy_aabb_index2d is not None:
        optional_destroy_aabb_index2d.argtypes = [ctypes.c_void_p]
        optional_destroy_aabb_index2d.restype = None
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

    optional_aggregate_frontier_collect = _find_optional_backend_symbol(
        lib,
        "rtdl_optix_collect_aggregate_frontier_2d",
    )
    if optional_aggregate_frontier_collect is not None:
        optional_aggregate_frontier_collect.argtypes = [
            ctypes.POINTER(_RtdlAggregateFrontierSource2D),
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlAggregateFrontierNode2D),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_int64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_int64),
            ctypes.c_double,
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_int64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_aggregate_frontier_collect.restype = ctypes.c_int

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

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_fixed_radius_neighbors_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_fixed_radius_neighbors_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_count_prepared_fixed_radius_neighbors_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_exact_fixed_radius_neighbors_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusRankedNeighborSummary)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_summarize_prepared_fixed_radius_neighbors_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(_RtdlFixedRadiusNeighborSummary),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d")
    if symbol is not None:
        symbol.argtypes = [ctypes.c_void_p]
        symbol.restype = None

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_fixed_radius_count_threshold_3d")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(
        lib,
        _OPTIX_PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_3D_DEVICE_OUTPUT_SYMBOL,
    )
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(
        lib,
        _OPTIX_PREPARED_FIXED_RADIUS_ADJACENCY_3D_DEVICE_OUTPUT_SYMBOL,
    )
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(
        lib,
        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_SYMBOL,
    )
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    for symbol_name, option_count in (
        (_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_OPTIONS_SYMBOL, 1),
        (_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL, 2),
    ):
        symbol = _find_optional_backend_symbol(lib, symbol_name)
        if symbol is not None:
            symbol.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(_RtdlPoint3D), ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_double,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                *([ctypes.c_uint32] * option_count),
                ctypes.c_size_t,
                ctypes.c_char_p, ctypes.c_size_t,
            ]
            symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(
        lib,
        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_SYMBOL,
    )
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.c_double,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    for symbol_name, option_count in (
        (_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_OPTIONS_SYMBOL, 1),
        (_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL, 2),
    ):
        symbol = _find_optional_backend_symbol(lib, symbol_name)
        if symbol is not None:
            symbol.argtypes = [
                ctypes.c_void_p,
                ctypes.c_double,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                *([ctypes.c_uint32] * option_count),
                ctypes.c_size_t,
                ctypes.c_char_p, ctypes.c_size_t,
            ]
            symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(
        lib,
        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_SYMBOL,
    )
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.c_double,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    for symbol_name, option_count in (
        (_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_OPTIONS_SYMBOL, 1),
        (_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_EXECUTION_OPTIONS_SYMBOL, 2),
    ):
        symbol = _find_optional_backend_symbol(lib, symbol_name)
        if symbol is not None:
            symbol.argtypes = [
                ctypes.c_void_p,
                ctypes.c_double,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                *([ctypes.c_uint32] * option_count),
                ctypes.c_size_t,
                ctypes.c_char_p, ctypes.c_size_t,
            ]
            symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(
        lib,
        _OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_SYMBOL,
    )
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    for symbol_name, option_count in (
        (_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_OPTIONS_SYMBOL, 1),
        (_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_EXECUTION_OPTIONS_SYMBOL, 2),
    ):
        symbol = _find_optional_backend_symbol(lib, symbol_name)
        if symbol is not None:
            symbol.argtypes = [
                ctypes.c_void_p,
                ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_double,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                *([ctypes.c_uint32] * option_count),
                ctypes.c_size_t,
                ctypes.c_char_p, ctypes.c_size_t,
            ]
            symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_3d")
    if symbol is not None:
        symbol.argtypes = [ctypes.c_void_p]
        symbol.restype = None

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

    optional_prepare_frn_count_device_search = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_SEARCH_SYMBOL,
    )
    if optional_prepare_frn_count_device_search is not None:
        optional_prepare_frn_count_device_search.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_prepare_frn_count_device_search.restype = ctypes.c_int

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

    optional_write_prepared_frn_count_device_query = _find_optional_backend_symbol(
        lib,
        _OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_QUERY_OUTPUT_SYMBOL,
    )
    if optional_write_prepared_frn_count_device_query is not None:
        optional_write_prepared_frn_count_device_query.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        optional_write_prepared_frn_count_device_query.restype = ctypes.c_int

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

    optional_prepared_frn_nearest = _find_optional_backend_symbol(
        lib, "rtdl_optix_run_prepared_fixed_radius_nearest_witness_2d"
    )
    if optional_prepared_frn_nearest is not None:
        optional_prepared_frn_nearest.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_prepared_frn_nearest.restype = ctypes.c_int

    optional_destroy_prepared_frn_count = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d")
    if optional_destroy_prepared_frn_count is not None:
        optional_destroy_prepared_frn_count.argtypes = [ctypes.c_void_p]
        optional_destroy_prepared_frn_count.restype = None

    optional_prepare_point_group = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_point_group_nearest_witness_2d")
    if optional_prepare_point_group is not None:
        optional_prepare_point_group.argtypes = [
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.POINTER(_RtdlPointGroupBounds2D), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_prepare_point_group.restype = ctypes.c_int

    optional_count_point_group_threshold = _find_optional_backend_symbol(
        lib, "rtdl_optix_count_prepared_point_group_threshold_reached_2d"
    )
    if optional_count_point_group_threshold is not None:
        optional_count_point_group_threshold.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_count_point_group_threshold.restype = ctypes.c_int

    optional_write_point_group_threshold_flags = _find_optional_backend_symbol(
        lib, "rtdl_optix_write_prepared_point_group_threshold_flags_2d"
    )
    if optional_write_point_group_threshold_flags is not None:
        optional_write_point_group_threshold_flags.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_write_point_group_threshold_flags.restype = ctypes.c_int

    optional_run_point_group_nearest = _find_optional_backend_symbol(
        lib, "rtdl_optix_run_prepared_point_group_nearest_witness_2d"
    )
    if optional_run_point_group_nearest is not None:
        optional_run_point_group_nearest.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_run_point_group_nearest.restype = ctypes.c_int

    optional_reduce_point_group_nearest = _find_optional_backend_symbol(
        lib, "rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d"
    )
    if optional_reduce_point_group_nearest is not None:
        optional_reduce_point_group_nearest.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlPoint), ctypes.c_size_t,
            ctypes.c_double,
            ctypes.POINTER(_RtdlFixedRadiusNeighborRow),
            ctypes.c_char_p, ctypes.c_size_t,
        ]
        optional_reduce_point_group_nearest.restype = ctypes.c_int

    optional_destroy_point_group = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_point_group_nearest_witness_2d")
    if optional_destroy_point_group is not None:
        optional_destroy_point_group.argtypes = [ctypes.c_void_p]
        optional_destroy_point_group.restype = None

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
            ctypes.POINTER(_RtdlColumnField),
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlColumnRowIdRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_grouped_count")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlColumnField),
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_grouped_sum")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlColumnField),
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedSumRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_create")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlColumnField),
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

    symbol = _find_optional_backend_symbol(lib, OPTIX_PARTNER_RESIDENT_COLUMNAR_DEVICE_SYMBOL)
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDevicePayloadField),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_SYMBOL)
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDevicePayloadField),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_WITH_CAPACITY_SYMBOL)
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDevicePayloadField),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_SYMBOL)
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDevicePayloadField),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedSumRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_WITH_CAPACITY_SYMBOL)
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDevicePayloadField),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedSumRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    for symbol_name in (
        OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MIN_I64_WITH_CAPACITY_SYMBOL,
        OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MAX_I64_WITH_CAPACITY_SYMBOL,
    ):
        symbol = _find_optional_backend_symbol(lib, symbol_name)
        if symbol is not None:
            symbol.argtypes = [
                ctypes.POINTER(_RtdlDevicePayloadField),
                ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_void_p,
                ctypes.c_size_t,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.POINTER(_RtdlGroupedSumRow)),
                ctypes.POINTER(ctypes.c_size_t),
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.c_char_p,
                ctypes.c_size_t,
            ]
            symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(
        lib,
        OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL,
    )
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDevicePayloadField),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedSumCountRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(
        lib,
        OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_STATS_I64_WITH_CAPACITY_SYMBOL,
    )
    if symbol is not None:
        symbol.argtypes = [
            ctypes.POINTER(_RtdlDevicePayloadField),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedStatsRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint32),
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
            ctypes.POINTER(ctypes.POINTER(_RtdlColumnRowIdRow)),
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
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedCountRow)),
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
            ctypes.POINTER(ctypes.POINTER(_RtdlGroupedSumRow)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_compact_summary_batch")
    if symbol is not None:
        symbol.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_RtdlColumnCompactSummaryRequest),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(_RtdlColumnCompactSummaryResult)),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        symbol.restype = ctypes.c_int

    symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_compact_summary_results_destroy")
    if symbol is not None:
        symbol.argtypes = [ctypes.POINTER(_RtdlColumnCompactSummaryResult), ctypes.c_size_t]
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
