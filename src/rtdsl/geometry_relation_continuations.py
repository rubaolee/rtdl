from __future__ import annotations

from dataclasses import dataclass
from typing import Any


GEOMETRY_RELATION_BOUNDS_OVERLAP_AREA_CUPY_VERSION = (
    "rtdl.v2_8.geometry_relation.bounds_overlap_area_cupy.v1"
)
GEOMETRY_RELATION_WITNESS_CUPY_VERSION = "rtdl.v2_8.geometry_relation.witness_cupy.v1"
GEOMETRY_RELATION_COMPLEXITY_CUPY_VERSION = "rtdl.v2_8.geometry_relation.complexity_cupy.v1"


_SHAPE_PAIR_CONVEXITY_KERNEL = r"""
static __device__ float rtdl_relation_complexity_absf(float value)
{
    return value < 0.0f ? -value : value;
}

extern "C" __global__ void shape_pair_relation_convexity_kernel(
        const unsigned int* polygon_refs,
        const float* vertices_x,
        const float* vertices_y,
        unsigned int shape_count,
        unsigned int* convex_flags)
{
    const unsigned int shape = blockIdx.x * blockDim.x + threadIdx.x;
    if (shape >= shape_count) return;

    const unsigned int offset = polygon_refs[shape * 3u + 1u];
    const unsigned int count = polygon_refs[shape * 3u + 2u];
    if (count < 3u) {
        convex_flags[shape] = 0u;
        return;
    }

    int sign = 0;
    for (unsigned int i = 0u; i < count; ++i) {
        const unsigned int ia = offset + i;
        const unsigned int ib = offset + ((i + 1u) % count);
        const unsigned int ic = offset + ((i + 2u) % count);
        const float ax = vertices_x[ia];
        const float ay = vertices_y[ia];
        const float bx = vertices_x[ib];
        const float by = vertices_y[ib];
        const float cx = vertices_x[ic];
        const float cy = vertices_y[ic];
        const float cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx);
        if (rtdl_relation_complexity_absf(cross) <= 1.0e-7f) {
            continue;
        }
        const int this_sign = cross > 0.0f ? 1 : -1;
        if (sign == 0) {
            sign = this_sign;
        } else if (sign != this_sign) {
            convex_flags[shape] = 0u;
            return;
        }
    }
    convex_flags[shape] = 1u;
}
"""


_SHAPE_PAIR_RELATION_WITNESS_KERNEL = r"""
static __device__ float rtdl_relation_absf(float value)
{
    return value < 0.0f ? -value : value;
}

extern "C" __global__ void shape_pair_relation_witness_kernel(
        const unsigned int* left_ordinals,
        const unsigned int* right_ordinals,
        const unsigned int* requires_segment_intersection,
        const unsigned int* requires_point_containment,
        const unsigned int* left_polygon_refs,
        const unsigned int* right_polygon_refs,
        const float* left_vx,
        const float* left_vy,
        const float* right_vx,
        const float* right_vy,
        unsigned int row_count,
        unsigned int* witness_kind,
        int* left_boundary_ordinal,
        int* right_boundary_ordinal,
        float* segment_t,
        float* segment_u)
{
    const unsigned int row = blockIdx.x * blockDim.x + threadIdx.x;
    if (row >= row_count) return;

    witness_kind[row] = 0u;
    left_boundary_ordinal[row] = -1;
    right_boundary_ordinal[row] = -1;
    segment_t[row] = -1.0f;
    segment_u[row] = -1.0f;

    const unsigned int li = left_ordinals[row];
    const unsigned int ri = right_ordinals[row];
    const unsigned int left_offset = left_polygon_refs[li * 3u + 1u];
    const unsigned int left_count = left_polygon_refs[li * 3u + 2u];
    const unsigned int right_offset = right_polygon_refs[ri * 3u + 1u];
    const unsigned int right_count = right_polygon_refs[ri * 3u + 2u];

    if (requires_segment_intersection[row] != 0u) {
        for (unsigned int i = 0u; i < left_count; ++i) {
            const unsigned int i0 = left_offset + i;
            const unsigned int i1 = left_offset + ((i + 1u) % left_count);
            const float ax0 = left_vx[i0];
            const float ay0 = left_vy[i0];
            const float ax1 = left_vx[i1];
            const float ay1 = left_vy[i1];
            const float rx = ax1 - ax0;
            const float ry = ay1 - ay0;
            for (unsigned int j = 0u; j < right_count; ++j) {
                const unsigned int j0 = right_offset + j;
                const unsigned int j1 = right_offset + ((j + 1u) % right_count);
                const float bx0 = right_vx[j0];
                const float by0 = right_vy[j0];
                const float bx1 = right_vx[j1];
                const float by1 = right_vy[j1];
                const float sx = bx1 - bx0;
                const float sy = by1 - by0;
                const float denom = rx * sy - ry * sx;
                if (rtdl_relation_absf(denom) < 1.0e-8f) continue;
                const float qpx = bx0 - ax0;
                const float qpy = by0 - ay0;
                const float t = (qpx * sy - qpy * sx) / denom;
                const float u = (qpx * ry - qpy * rx) / denom;
                if (t >= -1.0e-5f && t <= 1.00001f && u >= -1.0e-5f && u <= 1.00001f) {
                    witness_kind[row] = 1u;
                    left_boundary_ordinal[row] = static_cast<int>(i);
                    right_boundary_ordinal[row] = static_cast<int>(j);
                    segment_t[row] = t;
                    segment_u[row] = u;
                    return;
                }
            }
        }
        witness_kind[row] = 4u;
        return;
    }

    if (requires_point_containment[row] == 0u || left_count == 0u || right_count == 0u) {
        witness_kind[row] = 5u;
        return;
    }

    const float left_px = left_vx[left_offset];
    const float left_py = left_vy[left_offset];
    bool left_inside_right = false;
    for (unsigned int i = 0u, j = right_count - 1u; i < right_count; j = i++) {
        const float xi = right_vx[right_offset + i];
        const float yi = right_vy[right_offset + i];
        const float xj = right_vx[right_offset + j];
        const float yj = right_vy[right_offset + j];
        const float cross = (left_px - xi) * (yj - yi) - (left_py - yi) * (xj - xi);
        const float min_x = xi < xj ? xi : xj;
        const float max_x = xi > xj ? xi : xj;
        const float min_y = yi < yj ? yi : yj;
        const float max_y = yi > yj ? yi : yj;
        if (rtdl_relation_absf(cross) <= 1.0e-5f &&
            left_px >= min_x - 1.0e-5f && left_px <= max_x + 1.0e-5f &&
            left_py >= min_y - 1.0e-5f && left_py <= max_y + 1.0e-5f) {
            left_inside_right = true;
            break;
        }
    }
    if (!left_inside_right) {
        for (unsigned int i = 0u, j = right_count - 1u; i < right_count; j = i++) {
            const float xi = right_vx[right_offset + i];
            const float yi = right_vy[right_offset + i];
            const float xj = right_vx[right_offset + j];
            const float yj = right_vy[right_offset + j];
            if (((yi > left_py) != (yj > left_py)) &&
                (left_px <= (xj - xi) * (left_py - yi) / ((yj - yi) != 0.0f ? (yj - yi) : 1.0e-20f) + xi)) {
                left_inside_right = !left_inside_right;
            }
        }
    }
    if (left_inside_right) {
        witness_kind[row] = 2u;
        left_boundary_ordinal[row] = 0;
        return;
    }

    const float right_px = right_vx[right_offset];
    const float right_py = right_vy[right_offset];
    bool right_inside_left = false;
    for (unsigned int i = 0u, j = left_count - 1u; i < left_count; j = i++) {
        const float xi = left_vx[left_offset + i];
        const float yi = left_vy[left_offset + i];
        const float xj = left_vx[left_offset + j];
        const float yj = left_vy[left_offset + j];
        const float cross = (right_px - xi) * (yj - yi) - (right_py - yi) * (xj - xi);
        const float min_x = xi < xj ? xi : xj;
        const float max_x = xi > xj ? xi : xj;
        const float min_y = yi < yj ? yi : yj;
        const float max_y = yi > yj ? yi : yj;
        if (rtdl_relation_absf(cross) <= 1.0e-5f &&
            right_px >= min_x - 1.0e-5f && right_px <= max_x + 1.0e-5f &&
            right_py >= min_y - 1.0e-5f && right_py <= max_y + 1.0e-5f) {
            right_inside_left = true;
            break;
        }
    }
    if (!right_inside_left) {
        for (unsigned int i = 0u, j = left_count - 1u; i < left_count; j = i++) {
            const float xi = left_vx[left_offset + i];
            const float yi = left_vy[left_offset + i];
            const float xj = left_vx[left_offset + j];
            const float yj = left_vy[left_offset + j];
            if (((yi > right_py) != (yj > right_py)) &&
                (right_px <= (xj - xi) * (right_py - yi) / ((yj - yi) != 0.0f ? (yj - yi) : 1.0e-20f) + xi)) {
                right_inside_left = !right_inside_left;
            }
        }
    }
    if (right_inside_left) {
        witness_kind[row] = 3u;
        right_boundary_ordinal[row] = 0;
        return;
    }

    witness_kind[row] = 5u;
}
"""


@dataclass(frozen=True)
class ShapePairBoundsOverlapAreaCupyResult:
    row_areas: object
    group_keys: object | None
    group_area_sums: object | None
    metadata: dict[str, Any]

    def to_metadata(self) -> dict[str, Any]:
        return dict(self.metadata)


@dataclass(frozen=True)
class ShapePairRelationWitnessCupyResult:
    witness_kind: object
    left_boundary_ordinal: object
    right_boundary_ordinal: object
    segment_t: object
    segment_u: object
    metadata: dict[str, Any]

    def to_metadata(self) -> dict[str, Any]:
        return dict(self.metadata)


@dataclass(frozen=True)
class ShapePairRelationComplexityCupyResult:
    left_vertex_count: object
    right_vertex_count: object
    left_convex: object
    right_convex: object
    general_overlay_required: object
    metadata: dict[str, Any]

    def to_metadata(self) -> dict[str, Any]:
        return dict(self.metadata)


def shape_pair_relation_bounds_overlap_area_cupy(
    relation_columns,
    *,
    group_by: str | None = "left",
) -> ShapePairBoundsOverlapAreaCupyResult:
    """Compute bounds-overlap areas for active shape-pair relation rows.

    This consumes generic relation id/ordinal columns plus generic shape-pair
    geometry payload columns. It intentionally computes axis-aligned bounds
    overlap area, not exact polygon overlay area.
    """
    if group_by not in (None, "left", "right"):
        raise ValueError("group_by must be None, 'left', or 'right'")
    if getattr(relation_columns, "overflow", False):
        raise RuntimeError("cannot consume an overflowed shape-pair relation stream")

    import cupy as cp  # type: ignore

    ids = relation_columns.as_cupy_columns()
    ordinals = relation_columns.as_cupy_ordinal_columns()
    geometry = relation_columns.as_cupy_geometry_payload_columns()

    left_ordinal = ordinals["left_ordinal"].astype(cp.int64, copy=False)
    right_ordinal = ordinals["right_ordinal"].astype(cp.int64, copy=False)
    left_bounds = geometry["left_bounds"][left_ordinal]
    right_bounds = geometry["right_bounds"][right_ordinal]

    overlap_min_x = cp.maximum(left_bounds[:, 0], right_bounds[:, 0])
    overlap_min_y = cp.maximum(left_bounds[:, 1], right_bounds[:, 1])
    overlap_max_x = cp.minimum(left_bounds[:, 2], right_bounds[:, 2])
    overlap_max_y = cp.minimum(left_bounds[:, 3], right_bounds[:, 3])
    widths = cp.maximum(cp.asarray(0.0, dtype=cp.float32), overlap_max_x - overlap_min_x)
    heights = cp.maximum(cp.asarray(0.0, dtype=cp.float32), overlap_max_y - overlap_min_y)
    row_areas = (widths * heights).astype(cp.float64)

    group_keys = None
    group_area_sums = None
    if group_by is not None:
        source_keys = ids["left_id"] if group_by == "left" else ids["right_id"]
        group_keys = cp.unique(source_keys)
        inverse = cp.searchsorted(group_keys, source_keys)
        group_area_sums = cp.zeros((int(group_keys.size),), dtype=cp.float64)
        cp.add.at(group_area_sums, inverse, row_areas)

    metadata = {
        "schema": GEOMETRY_RELATION_BOUNDS_OVERLAP_AREA_CUPY_VERSION,
        "operation": "shape_pair_bounds_overlap_area",
        "partner": "cupy",
        "input_contract": "shape_pair_relation_flags_with_ordinals_and_geometry_payload",
        "row_count": int(getattr(relation_columns, "row_count")),
        "group_by": group_by,
        "area_semantics": "axis_aligned_bounds_overlap_area_upper_bound",
        "exact_polygon_overlay_area": False,
        "requires_relation_ordinals": True,
        "requires_geometry_payload_columns": True,
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }
    return ShapePairBoundsOverlapAreaCupyResult(
        row_areas=row_areas,
        group_keys=group_keys,
        group_area_sums=group_area_sums,
        metadata=metadata,
    )


def _shape_convexity_flags_cupy(cp, polygon_refs, vertices_x, vertices_y):
    shape_count = int(polygon_refs.shape[0])
    flags = cp.zeros((shape_count,), dtype=cp.uint32)
    if shape_count > 0:
        kernel = cp.RawKernel(_SHAPE_PAIR_CONVEXITY_KERNEL, "shape_pair_relation_convexity_kernel")
        block_size = 128
        grid_size = (shape_count + block_size - 1) // block_size
        kernel(
            (grid_size,),
            (block_size,),
            (
                polygon_refs.reshape(-1),
                vertices_x,
                vertices_y,
                cp.uint32(shape_count),
                flags,
            ),
        )
    return flags


def shape_pair_relation_complexity_cupy(
    relation_columns,
    *,
    simple_vertex_threshold: int = 64,
) -> ShapePairRelationComplexityCupyResult:
    """Classify active shape-pair relation rows before exact overlay routing."""
    if getattr(relation_columns, "overflow", False):
        raise RuntimeError("cannot consume an overflowed shape-pair relation stream")
    threshold = int(simple_vertex_threshold)
    if threshold < 3:
        raise ValueError("simple_vertex_threshold must be at least 3")

    import cupy as cp  # type: ignore

    ordinals = relation_columns.as_cupy_ordinal_columns()
    geometry = relation_columns.as_cupy_geometry_payload_columns()
    row_count = int(getattr(relation_columns, "row_count"))
    left_ordinal = ordinals["left_ordinal"].astype(cp.int64, copy=False)
    right_ordinal = ordinals["right_ordinal"].astype(cp.int64, copy=False)

    left_counts_all = geometry["left_polygon_refs"][:, 2].astype(cp.uint32, copy=False)
    right_counts_all = geometry["right_polygon_refs"][:, 2].astype(cp.uint32, copy=False)
    left_vertex_count = left_counts_all[left_ordinal]
    right_vertex_count = right_counts_all[right_ordinal]
    left_convex_all = _shape_convexity_flags_cupy(
        cp,
        geometry["left_polygon_refs"],
        geometry["left_vertices_x"],
        geometry["left_vertices_y"],
    )
    right_convex_all = _shape_convexity_flags_cupy(
        cp,
        geometry["right_polygon_refs"],
        geometry["right_vertices_x"],
        geometry["right_vertices_y"],
    )
    cp.cuda.Stream.null.synchronize()
    left_convex = left_convex_all[left_ordinal]
    right_convex = right_convex_all[right_ordinal]
    threshold_value = cp.asarray(threshold, dtype=cp.uint32)
    high_vertex = (left_vertex_count > threshold_value) | (right_vertex_count > threshold_value)
    nonconvex = (left_convex == 0) | (right_convex == 0)
    general_overlay_required = (high_vertex | nonconvex).astype(cp.uint32)

    if row_count > 0:
        both_convex_row_count = int(cp.sum((left_convex != 0) & (right_convex != 0)).get())
        nonconvex_row_count = int(cp.sum(nonconvex).get())
        rows_above_threshold = int(cp.sum(high_vertex).get())
        general_overlay_required_row_count = int(cp.sum(general_overlay_required).get())
        max_left_vertex_count = int(cp.max(left_vertex_count).get())
        max_right_vertex_count = int(cp.max(right_vertex_count).get())
        max_pair_vertex_count = int(cp.max(left_vertex_count + right_vertex_count).get())
    else:
        both_convex_row_count = 0
        nonconvex_row_count = 0
        rows_above_threshold = 0
        general_overlay_required_row_count = 0
        max_left_vertex_count = 0
        max_right_vertex_count = 0
        max_pair_vertex_count = 0

    metadata = {
        "schema": GEOMETRY_RELATION_COMPLEXITY_CUPY_VERSION,
        "operation": "shape_pair_relation_complexity_columns",
        "partner": "cupy",
        "input_contract": "shape_pair_relation_flags_with_ordinals_and_geometry_payload",
        "row_count": row_count,
        "simple_vertex_threshold": threshold,
        "both_convex_row_count": both_convex_row_count,
        "nonconvex_row_count": nonconvex_row_count,
        "rows_above_simple_vertex_threshold": rows_above_threshold,
        "general_overlay_required_row_count": general_overlay_required_row_count,
        "max_left_vertex_count": max_left_vertex_count,
        "max_right_vertex_count": max_right_vertex_count,
        "max_pair_vertex_count": max_pair_vertex_count,
        "classification_semantics": (
            "device-resident row-complexity classifier for routing exact overlay continuation; "
            "not an exact overlay-area computation"
        ),
        "exact_polygon_overlay_area": False,
        "requires_relation_ordinals": True,
        "requires_geometry_payload_columns": True,
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }
    return ShapePairRelationComplexityCupyResult(
        left_vertex_count=left_vertex_count,
        right_vertex_count=right_vertex_count,
        left_convex=left_convex,
        right_convex=right_convex,
        general_overlay_required=general_overlay_required,
        metadata=metadata,
    )


def shape_pair_relation_witness_cupy(relation_columns) -> ShapePairRelationWitnessCupyResult:
    """Emit generic boundary/containment witness columns for active relation rows."""
    if getattr(relation_columns, "overflow", False):
        raise RuntimeError("cannot consume an overflowed shape-pair relation stream")

    import cupy as cp  # type: ignore

    ids = relation_columns.as_cupy_columns()
    ordinals = relation_columns.as_cupy_ordinal_columns()
    geometry = relation_columns.as_cupy_geometry_payload_columns()
    row_count = int(getattr(relation_columns, "row_count"))
    witness_kind = cp.zeros((row_count,), dtype=cp.uint32)
    left_boundary_ordinal = cp.full((row_count,), -1, dtype=cp.int32)
    right_boundary_ordinal = cp.full((row_count,), -1, dtype=cp.int32)
    segment_t = cp.full((row_count,), -1.0, dtype=cp.float32)
    segment_u = cp.full((row_count,), -1.0, dtype=cp.float32)

    if row_count > 0:
        kernel = cp.RawKernel(_SHAPE_PAIR_RELATION_WITNESS_KERNEL, "shape_pair_relation_witness_kernel")
        block_size = 128
        grid_size = (row_count + block_size - 1) // block_size
        kernel(
            (grid_size,),
            (block_size,),
            (
                ordinals["left_ordinal"],
                ordinals["right_ordinal"],
                ids["requires_segment_intersection"],
                ids["requires_point_containment"],
                geometry["left_polygon_refs"].reshape(-1),
                geometry["right_polygon_refs"].reshape(-1),
                geometry["left_vertices_x"],
                geometry["left_vertices_y"],
                geometry["right_vertices_x"],
                geometry["right_vertices_y"],
                cp.uint32(row_count),
                witness_kind,
                left_boundary_ordinal,
                right_boundary_ordinal,
                segment_t,
                segment_u,
            ),
        )
        cp.cuda.Stream.null.synchronize()

    unique_kinds, unique_counts = cp.unique(witness_kind, return_counts=True)
    kind_counts = {
        str(int(kind)): int(count)
        for kind, count in zip(cp.asnumpy(unique_kinds).tolist(), cp.asnumpy(unique_counts).tolist())
    }
    metadata = {
        "schema": GEOMETRY_RELATION_WITNESS_CUPY_VERSION,
        "operation": "shape_pair_relation_witness_columns",
        "partner": "cupy",
        "input_contract": "shape_pair_relation_flags_with_ordinals_and_geometry_payload",
        "row_count": row_count,
        "witness_kind_semantics": {
            "0": "unset",
            "1": "segment_edge_intersection",
            "2": "left_first_vertex_inside_right",
            "3": "right_first_vertex_inside_left",
            "4": "segment_flag_without_found_edge_witness",
            "5": "containment_flag_without_found_vertex_witness",
        },
        "witness_kind_counts": kind_counts,
        "all_rows_have_witness": not any(kind in kind_counts for kind in ("0", "4", "5")),
        "segment_witness_endpoint_tolerance": "denom_abs_at_least_1e-8_t_u_within_1e-5_for_native_segment_flag_rows",
        "exact_polygon_overlay_area": False,
        "requires_relation_ordinals": True,
        "requires_geometry_payload_columns": True,
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }
    return ShapePairRelationWitnessCupyResult(
        witness_kind=witness_kind,
        left_boundary_ordinal=left_boundary_ordinal,
        right_boundary_ordinal=right_boundary_ordinal,
        segment_t=segment_t,
        segment_u=segment_u,
        metadata=metadata,
    )
