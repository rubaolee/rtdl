from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .simple_polygon_overlay_area_reference import Point2
from .simple_polygon_overlay_area_reference import Triangle2
from .simple_polygon_overlay_area_reference import convex_polygon_overlap_area
from .simple_polygon_overlay_area_reference import triangulate_simple_polygon_ear_clip
from .v2_8_overlay_area_continuation_contract import V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY
from .v2_8_overlay_area_continuation_contract import V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE
from .v2_8_overlay_area_continuation_contract import V2_8_OVERLAY_AREA_SCALAR_TARGET
from .v2_8_overlay_area_continuation_contract import V2_8_OVERLAY_AREA_TOPOLOGY_INPUT_STATUS
from .v2_8_overlay_area_continuation_contract import V2_8_OVERLAY_AREA_UNSUPPORTED_TOPOLOGY_STATUS


V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION = (
    "rtdl.v2_8.simple_polygon_overlay_area_prepared_payload.v1"
)
V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_STATUS = "cpu_prepared_payload_prototype_no_runtime_kernel_yet"
V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_CUPY_VERSION = (
    "rtdl.v2_8.simple_polygon_overlay_area_prepared_payload_cupy_tiled.v1"
)
V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_SERIALIZATION_VERSION = (
    "rtdl.v2_8.simple_polygon_overlay_area_prepared_payload_serialized.v1"
)


_PREPARED_OVERLAY_AREA_TILED_CUPY_KERNEL = r"""
static __device__ double rtdl_overlay_absd(double value)
{
    return value < 0.0 ? -value : value;
}

static __device__ double rtdl_overlay_cross(
        double ax, double ay,
        double bx, double by,
        double cx, double cy)
{
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
}

static __device__ double rtdl_overlay_signed_area(const double* vx, const double* vy, unsigned int count)
{
    double area2 = 0.0;
    for (unsigned int i = 0u; i < count; ++i) {
        const unsigned int j = (i + 1u) % count;
        area2 += vx[i] * vy[j] - vx[j] * vy[i];
    }
    return 0.5 * area2;
}

static __device__ bool rtdl_overlay_inside(
        double px, double py,
        double ax, double ay,
        double bx, double by,
        double orientation)
{
    const double cross = (bx - ax) * (py - ay) - (by - ay) * (px - ax);
    return orientation * cross >= -1.0e-12;
}

static __device__ void rtdl_overlay_line_intersection(
        double sx, double sy,
        double ex, double ey,
        double ax, double ay,
        double bx, double by,
        double* out_x,
        double* out_y)
{
    const double dx = ex - sx;
    const double dy = ey - sy;
    const double cx = bx - ax;
    const double cy = by - ay;
    const double denom = dx * cy - dy * cx;
    if (rtdl_overlay_absd(denom) <= 1.0e-20) {
        *out_x = ex;
        *out_y = ey;
        return;
    }
    const double qx = ax - sx;
    const double qy = ay - sy;
    const double t = (qx * cy - qy * cx) / denom;
    *out_x = sx + t * dx;
    *out_y = sy + t * dy;
}

static __device__ double rtdl_triangle_overlap_area(
        const double* left_x0,
        const double* left_y0,
        const double* left_x1,
        const double* left_y1,
        const double* left_x2,
        const double* left_y2,
        const double* right_x0,
        const double* right_y0,
        const double* right_x1,
        const double* right_y1,
        const double* right_x2,
        const double* right_y2,
        unsigned int left_index,
        unsigned int right_index)
{
    double clip_x[8];
    double clip_y[8];
    double temp_x[8];
    double temp_y[8];
    clip_x[0] = left_x0[left_index];
    clip_y[0] = left_y0[left_index];
    clip_x[1] = left_x1[left_index];
    clip_y[1] = left_y1[left_index];
    clip_x[2] = left_x2[left_index];
    clip_y[2] = left_y2[left_index];
    unsigned int clip_count = 3u;

    double rx[3];
    double ry[3];
    rx[0] = right_x0[right_index];
    ry[0] = right_y0[right_index];
    rx[1] = right_x1[right_index];
    ry[1] = right_y1[right_index];
    rx[2] = right_x2[right_index];
    ry[2] = right_y2[right_index];
    const double right_orientation = rtdl_overlay_signed_area(rx, ry, 3u) >= 0.0 ? 1.0 : -1.0;

    for (unsigned int edge = 0u; edge < 3u; ++edge) {
        const unsigned int next_edge = (edge + 1u) % 3u;
        const double ax = rx[edge];
        const double ay = ry[edge];
        const double bx = rx[next_edge];
        const double by = ry[next_edge];
        const unsigned int input_count = clip_count;
        if (input_count == 0u) return 0.0;
        for (unsigned int i = 0u; i < input_count; ++i) {
            temp_x[i] = clip_x[i];
            temp_y[i] = clip_y[i];
        }
        clip_count = 0u;
        double sx = temp_x[input_count - 1u];
        double sy = temp_y[input_count - 1u];
        bool s_inside = rtdl_overlay_inside(sx, sy, ax, ay, bx, by, right_orientation);
        for (unsigned int i = 0u; i < input_count; ++i) {
            const double ex = temp_x[i];
            const double ey = temp_y[i];
            const bool e_inside = rtdl_overlay_inside(ex, ey, ax, ay, bx, by, right_orientation);
            if (e_inside != s_inside) {
                double ix = 0.0;
                double iy = 0.0;
                rtdl_overlay_line_intersection(sx, sy, ex, ey, ax, ay, bx, by, &ix, &iy);
                if (clip_count < 8u) {
                    clip_x[clip_count] = ix;
                    clip_y[clip_count] = iy;
                    ++clip_count;
                }
            }
            if (e_inside && clip_count < 8u) {
                clip_x[clip_count] = ex;
                clip_y[clip_count] = ey;
                ++clip_count;
            }
            sx = ex;
            sy = ey;
            s_inside = e_inside;
        }
    }
    if (clip_count < 3u) return 0.0;
    const double area = rtdl_overlay_signed_area(clip_x, clip_y, clip_count);
    return area < 0.0 ? -area : area;
}

extern "C" __global__ void prepared_overlay_area_tiled_kernel(
        const double* left_x0,
        const double* left_y0,
        const double* left_x1,
        const double* left_y1,
        const double* left_x2,
        const double* left_y2,
        unsigned int left_triangle_total,
        const double* right_x0,
        const double* right_y0,
        const double* right_x1,
        const double* right_y1,
        const double* right_x2,
        const double* right_y2,
        unsigned int right_triangle_total,
        const unsigned int* left_start,
        const unsigned int* left_count,
        const unsigned int* right_start,
        const unsigned int* right_count,
        unsigned int row_count,
        unsigned int max_pairs_per_tile,
        double* row_area,
        unsigned int* row_status,
        unsigned int* processed_pairs,
        unsigned int* tile_counts)
{
    const unsigned int row = blockIdx.x * blockDim.x + threadIdx.x;
    if (row >= row_count) return;

    row_area[row] = 0.0;
    row_status[row] = 0u;
    processed_pairs[row] = 0u;
    tile_counts[row] = 0u;

    if (max_pairs_per_tile == 0u) {
        row_status[row] = 2u;
        return;
    }

    const unsigned int ls = left_start[row];
    const unsigned int lc = left_count[row];
    const unsigned int rs = right_start[row];
    const unsigned int rc = right_count[row];
    if (ls + lc > left_triangle_total || rs + rc > right_triangle_total) {
        row_status[row] = 1u;
        return;
    }

    double area = 0.0;
    unsigned int tile_pairs = 0u;
    for (unsigned int li = 0u; li < lc; ++li) {
        for (unsigned int ri = 0u; ri < rc; ++ri) {
            area += rtdl_triangle_overlap_area(
                left_x0, left_y0, left_x1, left_y1, left_x2, left_y2,
                right_x0, right_y0, right_x1, right_y1, right_x2, right_y2,
                ls + li,
                rs + ri);
            ++processed_pairs[row];
            ++tile_pairs;
            if (tile_pairs == max_pairs_per_tile) {
                ++tile_counts[row];
                tile_pairs = 0u;
            }
        }
    }
    if (tile_pairs != 0u) {
        ++tile_counts[row];
    }
    row_area[row] = area;
}
"""


_PREPARED_OVERLAY_AREA_TILE_TASK_CUPY_KERNEL = _PREPARED_OVERLAY_AREA_TILED_CUPY_KERNEL + r"""
extern "C" __global__ void prepared_overlay_area_tile_task_kernel(
        const double* left_x0,
        const double* left_y0,
        const double* left_x1,
        const double* left_y1,
        const double* left_x2,
        const double* left_y2,
        unsigned int left_triangle_total,
        const double* right_x0,
        const double* right_y0,
        const double* right_x1,
        const double* right_y1,
        const double* right_x2,
        const double* right_y2,
        unsigned int right_triangle_total,
        const unsigned int* relation_row_ordinal,
        const unsigned int* pair_offset,
        const unsigned int* pair_count,
        const unsigned int* left_start,
        const unsigned int* left_count,
        const unsigned int* right_start,
        const unsigned int* right_count,
        unsigned int task_count,
        double* task_area,
        unsigned int* task_status,
        unsigned int* processed_pairs)
{
    const unsigned int task = blockIdx.x * blockDim.x + threadIdx.x;
    if (task >= task_count) return;

    task_area[task] = 0.0;
    task_status[task] = 0u;
    processed_pairs[task] = 0u;

    const unsigned int ls = left_start[task];
    const unsigned int lc = left_count[task];
    const unsigned int rs = right_start[task];
    const unsigned int rc = right_count[task];
    if (rc == 0u || ls + lc > left_triangle_total || rs + rc > right_triangle_total) {
        task_status[task] = 1u;
        return;
    }

    double area = 0.0;
    const unsigned int begin = pair_offset[task];
    const unsigned int stop = begin + pair_count[task];
    if (stop > lc * rc) {
        task_status[task] = 2u;
        return;
    }
    for (unsigned int flat = begin; flat < stop; ++flat) {
        const unsigned int li = flat / rc;
        const unsigned int ri = flat - li * rc;
        area += rtdl_triangle_overlap_area(
            left_x0, left_y0, left_x1, left_y1, left_x2, left_y2,
            right_x0, right_y0, right_x1, right_y1, right_x2, right_y2,
            ls + li,
            rs + ri);
        ++processed_pairs[task];
    }
    task_area[task] = area;
}
"""


_PREPARED_OVERLAY_AREA_TILE_TASK_PLANNER_CUPY_KERNEL = r"""
extern "C" __global__ void prepared_overlay_area_tile_task_count_kernel(
        const unsigned int* relation_row_ordinals,
        const unsigned int* left_relation_ordinals,
        const unsigned int* right_relation_ordinals,
        const unsigned int* left_shape_component_start,
        const unsigned int* left_shape_component_count,
        const unsigned int* right_shape_component_start,
        const unsigned int* right_shape_component_count,
        const unsigned int* left_component_triangle_start,
        const unsigned int* left_component_triangle_count,
        const unsigned int* right_component_triangle_start,
        const unsigned int* right_component_triangle_count,
        const double* left_component_bounds,
        const double* right_component_bounds,
        unsigned int candidate_count,
        unsigned int relation_row_count,
        unsigned int left_shape_count,
        unsigned int right_shape_count,
        unsigned int max_triangle_pairs_per_task,
        unsigned int component_bounds_positive_filter,
        unsigned int* task_counts,
        unsigned int* component_pair_counts,
        unsigned long long* triangle_pair_counts)
{
    const unsigned int candidate = blockIdx.x * blockDim.x + threadIdx.x;
    if (candidate >= candidate_count) return;

    task_counts[candidate] = 0u;
    component_pair_counts[candidate] = 0u;
    triangle_pair_counts[candidate] = 0ull;
    if (max_triangle_pairs_per_task == 0u) return;

    const unsigned int relation_row = relation_row_ordinals[candidate];
    if (relation_row >= relation_row_count) return;
    const unsigned int left_shape = left_relation_ordinals[relation_row];
    const unsigned int right_shape = right_relation_ordinals[relation_row];
    if (left_shape >= left_shape_count || right_shape >= right_shape_count) return;

    const unsigned int left_start = left_shape_component_start[left_shape];
    const unsigned int left_count = left_shape_component_count[left_shape];
    const unsigned int right_start = right_shape_component_start[right_shape];
    const unsigned int right_count = right_shape_component_count[right_shape];
    unsigned int task_total = 0u;
    unsigned int component_pair_total = 0u;
    unsigned long long triangle_pair_total = 0ull;

    for (unsigned int li = 0u; li < left_count; ++li) {
        const unsigned int left_component = left_start + li;
        const unsigned int left_tri_count = left_component_triangle_count[left_component];
        for (unsigned int ri = 0u; ri < right_count; ++ri) {
            const unsigned int right_component = right_start + ri;
            const unsigned int right_tri_count = right_component_triangle_count[right_component];
            if (component_bounds_positive_filter != 0u) {
                const double min_x = left_component_bounds[left_component * 4u + 0u] > right_component_bounds[right_component * 4u + 0u]
                    ? left_component_bounds[left_component * 4u + 0u]
                    : right_component_bounds[right_component * 4u + 0u];
                const double min_y = left_component_bounds[left_component * 4u + 1u] > right_component_bounds[right_component * 4u + 1u]
                    ? left_component_bounds[left_component * 4u + 1u]
                    : right_component_bounds[right_component * 4u + 1u];
                const double max_x = left_component_bounds[left_component * 4u + 2u] < right_component_bounds[right_component * 4u + 2u]
                    ? left_component_bounds[left_component * 4u + 2u]
                    : right_component_bounds[right_component * 4u + 2u];
                const double max_y = left_component_bounds[left_component * 4u + 3u] < right_component_bounds[right_component * 4u + 3u]
                    ? left_component_bounds[left_component * 4u + 3u]
                    : right_component_bounds[right_component * 4u + 3u];
                if (!(max_x > min_x && max_y > min_y)) continue;
            }
            const unsigned int pair_count = left_tri_count * right_tri_count;
            if (pair_count == 0u) continue;
            ++component_pair_total;
            triangle_pair_total += static_cast<unsigned long long>(pair_count);
            task_total += (pair_count + max_triangle_pairs_per_task - 1u) / max_triangle_pairs_per_task;
        }
    }
    task_counts[candidate] = task_total;
    component_pair_counts[candidate] = component_pair_total;
    triangle_pair_counts[candidate] = triangle_pair_total;
}

extern "C" __global__ void prepared_overlay_area_tile_task_fill_kernel(
        const unsigned int* relation_row_ordinals,
        const unsigned int* left_relation_ordinals,
        const unsigned int* right_relation_ordinals,
        const unsigned int* left_shape_component_start,
        const unsigned int* left_shape_component_count,
        const unsigned int* right_shape_component_start,
        const unsigned int* right_shape_component_count,
        const unsigned int* left_component_triangle_start,
        const unsigned int* left_component_triangle_count,
        const unsigned int* right_component_triangle_start,
        const unsigned int* right_component_triangle_count,
        const double* left_component_bounds,
        const double* right_component_bounds,
        const unsigned int* task_offsets,
        unsigned int candidate_count,
        unsigned int relation_row_count,
        unsigned int left_shape_count,
        unsigned int right_shape_count,
        unsigned int max_triangle_pairs_per_task,
        unsigned int component_bounds_positive_filter,
        unsigned int* out_relation_row_ordinal,
        unsigned int* out_pair_offset,
        unsigned int* out_pair_count,
        unsigned int* out_left_start,
        unsigned int* out_left_count,
        unsigned int* out_right_start,
        unsigned int* out_right_count)
{
    const unsigned int candidate = blockIdx.x * blockDim.x + threadIdx.x;
    if (candidate >= candidate_count || max_triangle_pairs_per_task == 0u) return;

    const unsigned int relation_row = relation_row_ordinals[candidate];
    if (relation_row >= relation_row_count) return;
    const unsigned int left_shape = left_relation_ordinals[relation_row];
    const unsigned int right_shape = right_relation_ordinals[relation_row];
    if (left_shape >= left_shape_count || right_shape >= right_shape_count) return;

    const unsigned int left_start = left_shape_component_start[left_shape];
    const unsigned int left_count = left_shape_component_count[left_shape];
    const unsigned int right_start = right_shape_component_start[right_shape];
    const unsigned int right_count = right_shape_component_count[right_shape];
    unsigned int out = task_offsets[candidate];

    for (unsigned int li = 0u; li < left_count; ++li) {
        const unsigned int left_component = left_start + li;
        const unsigned int left_tri_start = left_component_triangle_start[left_component];
        const unsigned int left_tri_count = left_component_triangle_count[left_component];
        for (unsigned int ri = 0u; ri < right_count; ++ri) {
            const unsigned int right_component = right_start + ri;
            const unsigned int right_tri_start = right_component_triangle_start[right_component];
            const unsigned int right_tri_count = right_component_triangle_count[right_component];
            if (component_bounds_positive_filter != 0u) {
                const double min_x = left_component_bounds[left_component * 4u + 0u] > right_component_bounds[right_component * 4u + 0u]
                    ? left_component_bounds[left_component * 4u + 0u]
                    : right_component_bounds[right_component * 4u + 0u];
                const double min_y = left_component_bounds[left_component * 4u + 1u] > right_component_bounds[right_component * 4u + 1u]
                    ? left_component_bounds[left_component * 4u + 1u]
                    : right_component_bounds[right_component * 4u + 1u];
                const double max_x = left_component_bounds[left_component * 4u + 2u] < right_component_bounds[right_component * 4u + 2u]
                    ? left_component_bounds[left_component * 4u + 2u]
                    : right_component_bounds[right_component * 4u + 2u];
                const double max_y = left_component_bounds[left_component * 4u + 3u] < right_component_bounds[right_component * 4u + 3u]
                    ? left_component_bounds[left_component * 4u + 3u]
                    : right_component_bounds[right_component * 4u + 3u];
                if (!(max_x > min_x && max_y > min_y)) continue;
            }
            const unsigned int pair_total = left_tri_count * right_tri_count;
            for (unsigned int pair_offset = 0u; pair_offset < pair_total; pair_offset += max_triangle_pairs_per_task) {
                const unsigned int remaining = pair_total - pair_offset;
                out_relation_row_ordinal[out] = relation_row;
                out_pair_offset[out] = pair_offset;
                out_pair_count[out] = remaining < max_triangle_pairs_per_task ? remaining : max_triangle_pairs_per_task;
                out_left_start[out] = left_tri_start;
                out_left_count[out] = left_tri_count;
                out_right_start[out] = right_tri_start;
                out_right_count[out] = right_tri_count;
                ++out;
            }
        }
    }
}
"""


@dataclass(frozen=True)
class PreparedSimplePolygonComponentRecord:
    component_ordinal: int
    source_shape_id: int
    triangle_start: int
    triangle_count: int
    input_vertex_count: int
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    status: str = "prepared_simple_polygon_component"

    @property
    def triangle_stop(self) -> int:
        return self.triangle_start + self.triangle_count

    def to_metadata(self) -> dict[str, Any]:
        return {
            "component_ordinal": self.component_ordinal,
            "source_shape_id": self.source_shape_id,
            "triangle_start": self.triangle_start,
            "triangle_count": self.triangle_count,
            "triangle_stop": self.triangle_stop,
            "input_vertex_count": self.input_vertex_count,
            "bounds": (self.min_x, self.min_y, self.max_x, self.max_y),
            "status": self.status,
        }


@dataclass(frozen=True)
class PreparedSimplePolygonComponentPayload:
    triangles: tuple[Triangle2, ...]
    components: tuple[PreparedSimplePolygonComponentRecord, ...]
    status: str = V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_STATUS

    @property
    def component_count(self) -> int:
        return len(self.components)

    @property
    def triangle_count(self) -> int:
        return len(self.triangles)

    def component(self, component_ordinal: int) -> PreparedSimplePolygonComponentRecord:
        if component_ordinal < 0 or component_ordinal >= len(self.components):
            raise IndexError(f"component ordinal out of range: {component_ordinal}")
        return self.components[component_ordinal]

    def triangles_for_component(self, component_ordinal: int) -> tuple[Triangle2, ...]:
        record = self.component(component_ordinal)
        return self.triangles[record.triangle_start : record.triangle_stop]

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION,
            "status": self.status,
            "component_count": self.component_count,
            "triangle_count": self.triangle_count,
            "topology_input_status": V2_8_OVERLAY_AREA_TOPOLOGY_INPUT_STATUS,
            "unsupported_topology_status": V2_8_OVERLAY_AREA_UNSUPPORTED_TOPOLOGY_STATUS,
            "component_records": tuple(record.to_metadata() for record in self.components),
            "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "runtime_kernel_authorized": False,
        }


@dataclass(frozen=True)
class PreparedOverlayAreaPairRow:
    row_ordinal: int
    left_component_ordinal: int
    right_component_ordinal: int
    left_triangle_start: int
    left_triangle_count: int
    right_triangle_start: int
    right_triangle_count: int

    @property
    def left_triangle_stop(self) -> int:
        return self.left_triangle_start + self.left_triangle_count

    @property
    def right_triangle_stop(self) -> int:
        return self.right_triangle_start + self.right_triangle_count

    @property
    def triangle_pair_count(self) -> int:
        return self.left_triangle_count * self.right_triangle_count

    def to_metadata(self) -> dict[str, Any]:
        return {
            "row_ordinal": self.row_ordinal,
            "left_component_ordinal": self.left_component_ordinal,
            "right_component_ordinal": self.right_component_ordinal,
            "left_triangle_start": self.left_triangle_start,
            "left_triangle_count": self.left_triangle_count,
            "left_triangle_stop": self.left_triangle_stop,
            "right_triangle_start": self.right_triangle_start,
            "right_triangle_count": self.right_triangle_count,
            "right_triangle_stop": self.right_triangle_stop,
            "triangle_pair_count": self.triangle_pair_count,
        }


@dataclass(frozen=True)
class PreparedOverlayAreaTileTask:
    task_ordinal: int
    relation_row_ordinal: int
    pair_row_ordinal: int
    pair_offset: int
    pair_count: int
    left_triangle_start: int
    left_triangle_count: int
    right_triangle_start: int
    right_triangle_count: int

    @property
    def pair_stop(self) -> int:
        return self.pair_offset + self.pair_count

    @property
    def left_triangle_stop(self) -> int:
        return self.left_triangle_start + self.left_triangle_count

    @property
    def right_triangle_stop(self) -> int:
        return self.right_triangle_start + self.right_triangle_count

    def to_metadata(self) -> dict[str, int]:
        return {
            "task_ordinal": self.task_ordinal,
            "relation_row_ordinal": self.relation_row_ordinal,
            "pair_row_ordinal": self.pair_row_ordinal,
            "pair_offset": self.pair_offset,
            "pair_count": self.pair_count,
            "pair_stop": self.pair_stop,
            "left_triangle_start": self.left_triangle_start,
            "left_triangle_count": self.left_triangle_count,
            "left_triangle_stop": self.left_triangle_stop,
            "right_triangle_start": self.right_triangle_start,
            "right_triangle_count": self.right_triangle_count,
            "right_triangle_stop": self.right_triangle_stop,
        }


@dataclass(frozen=True)
class PreparedOverlayAreaEvaluationResult:
    row_areas: tuple[float, ...]
    total_area: float
    positive_row_count: int
    triangle_pair_count: int
    target: str = V2_8_OVERLAY_AREA_SCALAR_TARGET
    algorithm: str = "prepared_component_triangle_pair_convex_clip"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION,
            "target": self.target,
            "algorithm": self.algorithm,
            "row_count": len(self.row_areas),
            "total_area": self.total_area,
            "positive_row_count": self.positive_row_count,
            "triangle_pair_count": self.triangle_pair_count,
            "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "runtime_kernel_authorized": False,
        }


@dataclass(frozen=True)
class PreparedOverlayAreaTiledEvaluationResult:
    row_areas: tuple[float, ...]
    total_area: float
    positive_row_count: int
    triangle_pair_count: int
    tile_count: int
    max_triangle_pairs_per_tile: int
    max_observed_tile_pairs: int
    completed_without_truncation: bool
    target: str = V2_8_OVERLAY_AREA_SCALAR_TARGET
    algorithm: str = "prepared_component_triangle_pair_tiled_convex_clip"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION,
            "target": self.target,
            "algorithm": self.algorithm,
            "row_count": len(self.row_areas),
            "total_area": self.total_area,
            "positive_row_count": self.positive_row_count,
            "triangle_pair_count": self.triangle_pair_count,
            "tile_count": self.tile_count,
            "max_triangle_pairs_per_tile": self.max_triangle_pairs_per_tile,
            "max_observed_tile_pairs": self.max_observed_tile_pairs,
            "completed_without_truncation": self.completed_without_truncation,
            "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "runtime_kernel_authorized": False,
        }


@dataclass(frozen=True)
class PreparedOverlayAreaCupyTiledResult:
    row_areas: object
    row_status: object
    processed_pairs: object
    tile_counts: object
    metadata: dict[str, Any]

    def to_metadata(self) -> dict[str, Any]:
        return dict(self.metadata)


@dataclass(frozen=True)
class PreparedOverlayAreaCupyTileTaskResult:
    task_areas: object
    relation_areas: object
    task_status: object
    processed_pairs: object
    relation_row_ordinals: object
    metadata: dict[str, Any]

    def to_metadata(self) -> dict[str, Any]:
        return dict(self.metadata)


@dataclass(frozen=True)
class PreparedOverlayAreaCupyTileTaskInputs:
    left_columns: tuple[object, ...]
    right_columns: tuple[object, ...]
    relation_row_ordinals: object
    pair_offset: object
    pair_count: object
    left_start: object
    left_count: object
    right_start: object
    right_count: object
    task_count: int
    relation_row_count: int
    left_triangle_count: int
    right_triangle_count: int
    metadata: dict[str, Any]

    def to_metadata(self) -> dict[str, Any]:
        return dict(self.metadata)


def prepare_simple_polygon_component_payload(
    components: Sequence[Sequence[Point2]],
    *,
    source_shape_ids: Sequence[int] | None = None,
    eps: float = 1.0e-12,
) -> PreparedSimplePolygonComponentPayload:
    if source_shape_ids is not None and len(source_shape_ids) != len(components):
        raise ValueError("source_shape_ids length must match components length")

    triangles: list[Triangle2] = []
    records: list[PreparedSimplePolygonComponentRecord] = []
    for component_ordinal, vertices in enumerate(components):
        start = len(triangles)
        try:
            component_triangles = triangulate_simple_polygon_ear_clip(vertices, eps=eps)
        except ValueError as exc:
            raise ValueError(
                f"{V2_8_OVERLAY_AREA_UNSUPPORTED_TOPOLOGY_STATUS}: component "
                f"{component_ordinal} is not a prepared simple polygon"
            ) from exc
        triangles.extend(component_triangles)
        source_shape_id = (
            int(source_shape_ids[component_ordinal])
            if source_shape_ids is not None
            else component_ordinal
        )
        xs = [float(point[0]) for point in vertices]
        ys = [float(point[1]) for point in vertices]
        records.append(
            PreparedSimplePolygonComponentRecord(
                component_ordinal=component_ordinal,
                source_shape_id=source_shape_id,
                triangle_start=start,
                triangle_count=len(component_triangles),
                input_vertex_count=len(vertices),
                min_x=min(xs),
                min_y=min(ys),
                max_x=max(xs),
                max_y=max(ys),
            )
        )
    return PreparedSimplePolygonComponentPayload(triangles=tuple(triangles), components=tuple(records))


def prepare_simple_polygon_component_payload_from_triangles(
    component_triangles: Sequence[Sequence[Triangle2]],
    *,
    source_shape_ids: Sequence[int] | None = None,
    component_vertex_counts: Sequence[int] | None = None,
    component_bounds: Sequence[tuple[float, float, float, float]] | None = None,
) -> PreparedSimplePolygonComponentPayload:
    """Build a prepared component payload from caller-validated triangles.

    Callers own topology validation before using this constructor. When the
    original component vertex count or bounds are authoritative, pass
    `component_vertex_counts` and `component_bounds`; otherwise the fallback
    derives them from triangle vertices, which is correct for ear-clipped simple
    polygons without inserted Steiner points.
    """

    if source_shape_ids is not None and len(source_shape_ids) != len(component_triangles):
        raise ValueError("source_shape_ids length must match component_triangles length")
    if component_vertex_counts is not None and len(component_vertex_counts) != len(component_triangles):
        raise ValueError("component_vertex_counts length must match component_triangles length")
    if component_bounds is not None and len(component_bounds) != len(component_triangles):
        raise ValueError("component_bounds length must match component_triangles length")

    triangles: list[Triangle2] = []
    records: list[PreparedSimplePolygonComponentRecord] = []
    for component_ordinal, triangle_sequence in enumerate(component_triangles):
        start = len(triangles)
        normalized_triangles: list[Triangle2] = []
        for triangle in triangle_sequence:
            if len(triangle) != 3:
                raise ValueError("pretriangulated component triangles must have exactly three vertices")
            normalized_triangles.append(
                (
                    (float(triangle[0][0]), float(triangle[0][1])),
                    (float(triangle[1][0]), float(triangle[1][1])),
                    (float(triangle[2][0]), float(triangle[2][1])),
                )
            )
        if not normalized_triangles:
            raise ValueError("pretriangulated component must contain at least one triangle")
        triangles.extend(normalized_triangles)
        source_shape_id = (
            int(source_shape_ids[component_ordinal])
            if source_shape_ids is not None
            else component_ordinal
        )
        if component_bounds is None:
            xs = [point[0] for triangle in normalized_triangles for point in triangle]
            ys = [point[1] for triangle in normalized_triangles for point in triangle]
            min_x, min_y, max_x, max_y = min(xs), min(ys), max(xs), max(ys)
        else:
            min_x, min_y, max_x, max_y = (
                float(component_bounds[component_ordinal][0]),
                float(component_bounds[component_ordinal][1]),
                float(component_bounds[component_ordinal][2]),
                float(component_bounds[component_ordinal][3]),
            )
        vertex_count = (
            int(component_vertex_counts[component_ordinal])
            if component_vertex_counts is not None
            else len({point for triangle in normalized_triangles for point in triangle})
        )
        records.append(
            PreparedSimplePolygonComponentRecord(
                component_ordinal=component_ordinal,
                source_shape_id=source_shape_id,
                triangle_start=start,
                triangle_count=len(normalized_triangles),
                input_vertex_count=vertex_count,
                min_x=min_x,
                min_y=min_y,
                max_x=max_x,
                max_y=max_y,
            )
        )
    return PreparedSimplePolygonComponentPayload(triangles=tuple(triangles), components=tuple(records))


def prepared_simple_polygon_component_payload_to_dict(
    payload: PreparedSimplePolygonComponentPayload,
) -> dict[str, Any]:
    return {
        "schema": V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_SERIALIZATION_VERSION,
        "payload_version": V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION,
        "status": payload.status,
        "triangles": [
            [[float(x), float(y)] for x, y in triangle]
            for triangle in payload.triangles
        ],
        "components": [
            {
                "component_ordinal": int(component.component_ordinal),
                "source_shape_id": int(component.source_shape_id),
                "triangle_start": int(component.triangle_start),
                "triangle_count": int(component.triangle_count),
                "input_vertex_count": int(component.input_vertex_count),
                "min_x": float(component.min_x),
                "min_y": float(component.min_y),
                "max_x": float(component.max_x),
                "max_y": float(component.max_y),
                "status": component.status,
            }
            for component in payload.components
        ],
        "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
    }


def prepared_simple_polygon_component_payload_from_dict(
    data: dict[str, Any],
) -> PreparedSimplePolygonComponentPayload:
    if data.get("schema") != V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_SERIALIZATION_VERSION:
        raise ValueError("unexpected prepared payload serialization schema")
    triangles: list[Triangle2] = []
    for triangle in data.get("triangles", ()):
        if len(triangle) != 3:
            raise ValueError("serialized prepared payload triangles must have exactly three vertices")
        triangles.append(
            (
                (float(triangle[0][0]), float(triangle[0][1])),
                (float(triangle[1][0]), float(triangle[1][1])),
                (float(triangle[2][0]), float(triangle[2][1])),
            )
        )
    components: list[PreparedSimplePolygonComponentRecord] = []
    for component in data.get("components", ()):
        components.append(
            PreparedSimplePolygonComponentRecord(
                component_ordinal=int(component["component_ordinal"]),
                source_shape_id=int(component["source_shape_id"]),
                triangle_start=int(component["triangle_start"]),
                triangle_count=int(component["triangle_count"]),
                input_vertex_count=int(component["input_vertex_count"]),
                min_x=float(component["min_x"]),
                min_y=float(component["min_y"]),
                max_x=float(component["max_x"]),
                max_y=float(component["max_y"]),
                status=str(component.get("status", "prepared_simple_polygon_component")),
            )
        )
    return PreparedSimplePolygonComponentPayload(
        triangles=tuple(triangles),
        components=tuple(components),
        status=str(data.get("status", V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_STATUS)),
    )


def prepare_overlay_area_pair_rows(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    component_pairs: Sequence[tuple[int, int]],
) -> tuple[PreparedOverlayAreaPairRow, ...]:
    rows: list[PreparedOverlayAreaPairRow] = []
    for row_ordinal, (left_component_ordinal, right_component_ordinal) in enumerate(component_pairs):
        left = left_payload.component(int(left_component_ordinal))
        right = right_payload.component(int(right_component_ordinal))
        rows.append(
            PreparedOverlayAreaPairRow(
                row_ordinal=row_ordinal,
                left_component_ordinal=left.component_ordinal,
                right_component_ordinal=right.component_ordinal,
                left_triangle_start=left.triangle_start,
                left_triangle_count=left.triangle_count,
                right_triangle_start=right.triangle_start,
                right_triangle_count=right.triangle_count,
            )
        )
    return tuple(rows)


def prepared_overlay_area_component_bounds_overlap_positive(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    left_component_ordinal: int,
    right_component_ordinal: int,
) -> bool:
    left = left_payload.component(int(left_component_ordinal))
    right = right_payload.component(int(right_component_ordinal))
    return (
        min(left.max_x, right.max_x) > max(left.min_x, right.min_x)
        and min(left.max_y, right.max_y) > max(left.min_y, right.min_y)
    )


def plan_prepared_overlay_area_tile_tasks(
    pair_rows: Sequence[PreparedOverlayAreaPairRow],
    *,
    max_triangle_pairs_per_task: int,
    relation_row_ordinals: Sequence[int] | None = None,
) -> tuple[PreparedOverlayAreaTileTask, ...]:
    if max_triangle_pairs_per_task <= 0:
        raise ValueError("max_triangle_pairs_per_task must be positive; tile planning must fail closed")
    if relation_row_ordinals is not None and len(relation_row_ordinals) != len(pair_rows):
        raise ValueError("relation_row_ordinals length must match pair_rows length")

    tasks: list[PreparedOverlayAreaTileTask] = []
    for pair_index, pair_row in enumerate(pair_rows):
        relation_row_ordinal = (
            int(relation_row_ordinals[pair_index])
            if relation_row_ordinals is not None
            else int(pair_row.row_ordinal)
        )
        pair_offset = 0
        while pair_offset < pair_row.triangle_pair_count:
            pair_count = min(max_triangle_pairs_per_task, pair_row.triangle_pair_count - pair_offset)
            tasks.append(
                PreparedOverlayAreaTileTask(
                    task_ordinal=len(tasks),
                    relation_row_ordinal=relation_row_ordinal,
                    pair_row_ordinal=int(pair_row.row_ordinal),
                    pair_offset=pair_offset,
                    pair_count=pair_count,
                    left_triangle_start=pair_row.left_triangle_start,
                    left_triangle_count=pair_row.left_triangle_count,
                    right_triangle_start=pair_row.right_triangle_start,
                    right_triangle_count=pair_row.right_triangle_count,
                )
            )
            pair_offset += pair_count
    return tuple(tasks)


def summarize_prepared_overlay_area_tile_tasks(
    pair_rows: Sequence[PreparedOverlayAreaPairRow],
    tasks: Sequence[PreparedOverlayAreaTileTask],
) -> dict[str, Any]:
    expected_pairs = sum(int(row.triangle_pair_count) for row in pair_rows)
    planned_pairs = sum(int(task.pair_count) for task in tasks)
    relation_rows = {int(task.relation_row_ordinal) for task in tasks}
    errors: list[str] = []
    if expected_pairs != planned_pairs:
        errors.append(f"planned pair count {planned_pairs} does not match expected {expected_pairs}")
    if any(task.pair_count <= 0 for task in tasks):
        errors.append("tile tasks must have positive pair counts")
    return {
        "version": V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "pair_row_count": len(pair_rows),
        "task_count": len(tasks),
        "relation_row_count": len(relation_rows),
        "expected_triangle_pair_count": expected_pairs,
        "planned_triangle_pair_count": planned_pairs,
        "max_task_pair_count": max((int(task.pair_count) for task in tasks), default=0),
        "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "runtime_kernel_authorized": False,
    }


def evaluate_prepared_overlay_area_scalar(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    pair_rows: Sequence[PreparedOverlayAreaPairRow],
    *,
    eps: float = 1.0e-12,
    row_positive_threshold: float | None = None,
) -> PreparedOverlayAreaEvaluationResult:
    positive_threshold = (
        V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE
        if row_positive_threshold is None
        else float(row_positive_threshold)
    )
    row_areas: list[float] = []
    total_triangle_pairs = 0
    for row in pair_rows:
        row_area = 0.0
        total_triangle_pairs += row.triangle_pair_count
        left_triangles = left_payload.triangles[row.left_triangle_start : row.left_triangle_stop]
        right_triangles = right_payload.triangles[row.right_triangle_start : row.right_triangle_stop]
        for left_triangle in left_triangles:
            for right_triangle in right_triangles:
                row_area += convex_polygon_overlap_area(left_triangle, right_triangle, eps=eps)
        row_areas.append(row_area)
    return PreparedOverlayAreaEvaluationResult(
        row_areas=tuple(row_areas),
        total_area=sum(row_areas),
        positive_row_count=sum(1 for area in row_areas if area > positive_threshold),
        triangle_pair_count=total_triangle_pairs,
    )


def evaluate_prepared_overlay_area_scalar_tiled(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    pair_rows: Sequence[PreparedOverlayAreaPairRow],
    *,
    max_triangle_pairs_per_tile: int,
    eps: float = 1.0e-12,
    row_positive_threshold: float | None = None,
) -> PreparedOverlayAreaTiledEvaluationResult:
    if max_triangle_pairs_per_tile <= 0:
        raise ValueError("max_triangle_pairs_per_tile must be positive; scratch capacity must fail closed")
    positive_threshold = (
        V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE
        if row_positive_threshold is None
        else float(row_positive_threshold)
    )

    row_areas: list[float] = []
    total_triangle_pairs = 0
    tile_count = 0
    max_observed_tile_pairs = 0
    for row in pair_rows:
        row_area = 0.0
        tile_area = 0.0
        tile_pairs = 0
        left_triangles = left_payload.triangles[row.left_triangle_start : row.left_triangle_stop]
        right_triangles = right_payload.triangles[row.right_triangle_start : row.right_triangle_stop]
        for left_triangle in left_triangles:
            for right_triangle in right_triangles:
                tile_area += convex_polygon_overlap_area(left_triangle, right_triangle, eps=eps)
                tile_pairs += 1
                total_triangle_pairs += 1
                if tile_pairs == max_triangle_pairs_per_tile:
                    row_area += tile_area
                    tile_count += 1
                    max_observed_tile_pairs = max(max_observed_tile_pairs, tile_pairs)
                    tile_area = 0.0
                    tile_pairs = 0
        if tile_pairs:
            row_area += tile_area
            tile_count += 1
            max_observed_tile_pairs = max(max_observed_tile_pairs, tile_pairs)
        row_areas.append(row_area)
    return PreparedOverlayAreaTiledEvaluationResult(
        row_areas=tuple(row_areas),
        total_area=sum(row_areas),
        positive_row_count=sum(1 for area in row_areas if area > positive_threshold),
        triangle_pair_count=total_triangle_pairs,
        tile_count=tile_count,
        max_triangle_pairs_per_tile=max_triangle_pairs_per_tile,
        max_observed_tile_pairs=max_observed_tile_pairs,
        completed_without_truncation=True,
    )


def _triangles_to_cupy_columns(cp, triangles: Sequence[Triangle2]) -> tuple[object, ...]:
    return (
        cp.asarray([triangle[0][0] for triangle in triangles], dtype=cp.float64),
        cp.asarray([triangle[0][1] for triangle in triangles], dtype=cp.float64),
        cp.asarray([triangle[1][0] for triangle in triangles], dtype=cp.float64),
        cp.asarray([triangle[1][1] for triangle in triangles], dtype=cp.float64),
        cp.asarray([triangle[2][0] for triangle in triangles], dtype=cp.float64),
        cp.asarray([triangle[2][1] for triangle in triangles], dtype=cp.float64),
    )


def _validate_prepared_overlay_area_tile_tasks(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    tasks: Sequence[PreparedOverlayAreaTileTask],
    relation_row_count: int | None,
) -> tuple[list[int], int]:
    relation_ids_host = [int(task.relation_row_ordinal) for task in tasks]
    if relation_row_count is None:
        relation_row_count = (max(relation_ids_host) + 1) if relation_ids_host else 0
    if relation_row_count < 0:
        raise ValueError("relation_row_count must be non-negative")
    if any(relation_id < 0 or relation_id >= relation_row_count for relation_id in relation_ids_host):
        raise ValueError("tile task relation_row_ordinal is outside relation_row_count")
    for task in tasks:
        if task.pair_count <= 0:
            raise ValueError("tile task pair_count must be positive")
        if task.pair_offset < 0 or task.pair_offset + task.pair_count > task.left_triangle_count * task.right_triangle_count:
            raise ValueError("tile task pair range is outside component triangle product")
        if task.left_triangle_start < 0 or task.left_triangle_stop > left_payload.triangle_count:
            raise ValueError("tile task left triangle range is outside left payload")
        if task.right_triangle_start < 0 or task.right_triangle_stop > right_payload.triangle_count:
            raise ValueError("tile task right triangle range is outside right payload")
    return relation_ids_host, int(relation_row_count)


def _component_triangle_columns_cupy(cp, payload: PreparedSimplePolygonComponentPayload) -> tuple[object, object]:
    return (
        cp.asarray([component.triangle_start for component in payload.components], dtype=cp.uint32),
        cp.asarray([component.triangle_count for component in payload.components], dtype=cp.uint32),
    )


def _component_bounds_column_cupy(cp, payload: PreparedSimplePolygonComponentPayload):
    return cp.asarray(
        [
            value
            for component in payload.components
            for value in (component.min_x, component.min_y, component.max_x, component.max_y)
        ],
        dtype=cp.float64,
    )


def evaluate_prepared_overlay_area_scalar_tiled_cupy(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    pair_rows: Sequence[PreparedOverlayAreaPairRow],
    *,
    max_triangle_pairs_per_tile: int,
) -> PreparedOverlayAreaCupyTiledResult:
    if max_triangle_pairs_per_tile <= 0:
        raise ValueError("max_triangle_pairs_per_tile must be positive; scratch capacity must fail closed")

    import cupy as cp  # type: ignore

    row_count = len(pair_rows)
    left_columns = _triangles_to_cupy_columns(cp, left_payload.triangles)
    right_columns = _triangles_to_cupy_columns(cp, right_payload.triangles)
    left_start = cp.asarray([row.left_triangle_start for row in pair_rows], dtype=cp.uint32)
    left_count = cp.asarray([row.left_triangle_count for row in pair_rows], dtype=cp.uint32)
    right_start = cp.asarray([row.right_triangle_start for row in pair_rows], dtype=cp.uint32)
    right_count = cp.asarray([row.right_triangle_count for row in pair_rows], dtype=cp.uint32)
    row_areas = cp.zeros((row_count,), dtype=cp.float64)
    row_status = cp.zeros((row_count,), dtype=cp.uint32)
    processed_pairs = cp.zeros((row_count,), dtype=cp.uint32)
    tile_counts = cp.zeros((row_count,), dtype=cp.uint32)

    if row_count:
        kernel = cp.RawKernel(_PREPARED_OVERLAY_AREA_TILED_CUPY_KERNEL, "prepared_overlay_area_tiled_kernel")
        block_size = 128
        grid_size = (row_count + block_size - 1) // block_size
        kernel(
            (grid_size,),
            (block_size,),
            (
                *left_columns,
                cp.uint32(left_payload.triangle_count),
                *right_columns,
                cp.uint32(right_payload.triangle_count),
                left_start,
                left_count,
                right_start,
                right_count,
                cp.uint32(row_count),
                cp.uint32(max_triangle_pairs_per_tile),
                row_areas,
                row_status,
                processed_pairs,
                tile_counts,
            ),
        )
        cp.cuda.Stream.null.synchronize()

    status_values = {}
    if row_count:
        unique_status, unique_counts = cp.unique(row_status, return_counts=True)
        status_values = {
            str(int(status)): int(count)
            for status, count in zip(cp.asnumpy(unique_status).tolist(), cp.asnumpy(unique_counts).tolist())
        }
    metadata = {
        "schema": V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_CUPY_VERSION,
        "operation": "prepared_simple_polygon_overlay_area_tiled",
        "partner": "cupy",
        "row_count": row_count,
        "left_triangle_count": left_payload.triangle_count,
        "right_triangle_count": right_payload.triangle_count,
        "max_triangle_pairs_per_tile": int(max_triangle_pairs_per_tile),
        "processed_triangle_pair_count": int(cp.sum(processed_pairs).get()) if row_count else 0,
        "tile_count": int(cp.sum(tile_counts).get()) if row_count else 0,
        "status_counts": status_values,
        "status_semantics": {
            "0": "computed",
            "1": "invalid_triangle_range",
            "2": "invalid_tile_capacity",
        },
        "total_area": float(cp.sum(row_areas).get()) if row_count else 0.0,
        "completed_without_truncation": (
            bool(cp.all(row_status == 0).get()) if row_count else True
        ),
        "input_contract": "prepared_simple_polygon_component_payload",
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "runtime_kernel_authorized": False,
        "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
    }
    return PreparedOverlayAreaCupyTiledResult(
        row_areas=row_areas,
        row_status=row_status,
        processed_pairs=processed_pairs,
        tile_counts=tile_counts,
        metadata=metadata,
    )


def prepare_overlay_area_tile_task_cupy_inputs(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    tasks: Sequence[PreparedOverlayAreaTileTask],
    *,
    relation_row_count: int | None = None,
) -> PreparedOverlayAreaCupyTileTaskInputs:
    task_count = len(tasks)
    relation_ids_host, relation_row_count = _validate_prepared_overlay_area_tile_tasks(
        left_payload,
        right_payload,
        tasks,
        relation_row_count,
    )

    import cupy as cp  # type: ignore

    left_columns = _triangles_to_cupy_columns(cp, left_payload.triangles)
    right_columns = _triangles_to_cupy_columns(cp, right_payload.triangles)

    relation_ids = cp.asarray(relation_ids_host, dtype=cp.uint32)
    pair_offset = cp.asarray([task.pair_offset for task in tasks], dtype=cp.uint32)
    pair_count = cp.asarray([task.pair_count for task in tasks], dtype=cp.uint32)
    left_start = cp.asarray([task.left_triangle_start for task in tasks], dtype=cp.uint32)
    left_count = cp.asarray([task.left_triangle_count for task in tasks], dtype=cp.uint32)
    right_start = cp.asarray([task.right_triangle_start for task in tasks], dtype=cp.uint32)
    right_count = cp.asarray([task.right_triangle_count for task in tasks], dtype=cp.uint32)
    metadata = {
        "schema": "rtdl.v2_8.simple_polygon_overlay_area_tile_task_cupy_inputs.v1",
        "operation": "prepared_simple_polygon_overlay_area_tile_task_inputs",
        "partner": "cupy",
        "task_count": task_count,
        "relation_row_count": int(relation_row_count),
        "left_triangle_count": left_payload.triangle_count,
        "right_triangle_count": right_payload.triangle_count,
        "input_contract": "prepared_overlay_area_tile_tasks",
        "resident_cupy_columns": True,
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "runtime_kernel_authorized": False,
        "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
    }
    return PreparedOverlayAreaCupyTileTaskInputs(
        left_columns=left_columns,
        right_columns=right_columns,
        relation_row_ordinals=relation_ids,
        pair_offset=pair_offset,
        pair_count=pair_count,
        left_start=left_start,
        left_count=left_count,
        right_start=right_start,
        right_count=right_count,
        task_count=task_count,
        relation_row_count=int(relation_row_count),
        left_triangle_count=left_payload.triangle_count,
        right_triangle_count=right_payload.triangle_count,
        metadata=metadata,
    )


def prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    *,
    relation_row_ordinals,
    left_relation_ordinals,
    right_relation_ordinals,
    left_shape_component_starts: Sequence[int],
    left_shape_component_counts: Sequence[int],
    right_shape_component_starts: Sequence[int],
    right_shape_component_counts: Sequence[int],
    relation_row_count: int,
    max_triangle_pairs_per_task: int,
    component_bounds_positive_filter: bool = False,
) -> PreparedOverlayAreaCupyTileTaskInputs:
    """Plan overlay tile tasks with CuPy from generic relation ordinal columns.

    Prepared payload construction is still CPU-owned. This helper moves the
    component-pair and tile-task expansion step to a generic partner
    continuation once component tables are available.
    """
    if max_triangle_pairs_per_task <= 0:
        raise ValueError("max_triangle_pairs_per_task must be positive")
    if relation_row_count < 0:
        raise ValueError("relation_row_count must be non-negative")

    import cupy as cp  # type: ignore

    relation_rows = cp.asarray(relation_row_ordinals, dtype=cp.uint32)
    left_relation_rows = cp.asarray(left_relation_ordinals, dtype=cp.uint32)
    right_relation_rows = cp.asarray(right_relation_ordinals, dtype=cp.uint32)
    left_shape_start = cp.asarray(left_shape_component_starts, dtype=cp.uint32)
    left_shape_count = cp.asarray(left_shape_component_counts, dtype=cp.uint32)
    right_shape_start = cp.asarray(right_shape_component_starts, dtype=cp.uint32)
    right_shape_count = cp.asarray(right_shape_component_counts, dtype=cp.uint32)
    left_component_start, left_component_count = _component_triangle_columns_cupy(cp, left_payload)
    right_component_start, right_component_count = _component_triangle_columns_cupy(cp, right_payload)
    left_component_bounds = _component_bounds_column_cupy(cp, left_payload)
    right_component_bounds = _component_bounds_column_cupy(cp, right_payload)

    candidate_count = int(relation_rows.size)
    if int(left_relation_rows.size) < int(relation_row_count) or int(right_relation_rows.size) < int(relation_row_count):
        raise ValueError("relation ordinal columns must cover relation_row_count")

    left_columns = _triangles_to_cupy_columns(cp, left_payload.triangles)
    right_columns = _triangles_to_cupy_columns(cp, right_payload.triangles)
    task_counts = cp.zeros((candidate_count,), dtype=cp.uint32)
    component_pair_counts = cp.zeros((candidate_count,), dtype=cp.uint32)
    triangle_pair_counts = cp.zeros((candidate_count,), dtype=cp.uint64)

    if candidate_count:
        block_size = 128
        grid_size = (candidate_count + block_size - 1) // block_size
        count_kernel = cp.RawKernel(
            _PREPARED_OVERLAY_AREA_TILE_TASK_PLANNER_CUPY_KERNEL,
            "prepared_overlay_area_tile_task_count_kernel",
        )
        count_kernel(
            (grid_size,),
            (block_size,),
            (
                relation_rows,
                left_relation_rows,
                right_relation_rows,
                left_shape_start,
                left_shape_count,
                right_shape_start,
                right_shape_count,
                left_component_start,
                left_component_count,
                right_component_start,
                right_component_count,
                left_component_bounds,
                right_component_bounds,
                cp.uint32(candidate_count),
                cp.uint32(relation_row_count),
                cp.uint32(int(left_shape_start.size)),
                cp.uint32(int(right_shape_start.size)),
                cp.uint32(int(max_triangle_pairs_per_task)),
                cp.uint32(1 if component_bounds_positive_filter else 0),
                task_counts,
                component_pair_counts,
                triangle_pair_counts,
            ),
        )
        cp.cuda.Stream.null.synchronize()

    task_count = int(cp.sum(task_counts).get()) if candidate_count else 0
    component_pair_count = int(cp.sum(component_pair_counts).get()) if candidate_count else 0
    planned_triangle_pair_count = int(cp.sum(triangle_pair_counts).get()) if candidate_count else 0
    supported_relation_row_count = int(cp.count_nonzero(component_pair_counts).get()) if candidate_count else 0
    if candidate_count:
        task_offsets = cp.concatenate(
            (
                cp.zeros((1,), dtype=cp.uint32),
                cp.cumsum(task_counts[:-1], dtype=cp.uint32),
            )
        )
    else:
        task_offsets = cp.zeros((0,), dtype=cp.uint32)

    relation_ids = cp.zeros((task_count,), dtype=cp.uint32)
    pair_offset = cp.zeros((task_count,), dtype=cp.uint32)
    pair_count = cp.zeros((task_count,), dtype=cp.uint32)
    left_start = cp.zeros((task_count,), dtype=cp.uint32)
    left_count = cp.zeros((task_count,), dtype=cp.uint32)
    right_start = cp.zeros((task_count,), dtype=cp.uint32)
    right_count = cp.zeros((task_count,), dtype=cp.uint32)

    if candidate_count and task_count:
        block_size = 128
        grid_size = (candidate_count + block_size - 1) // block_size
        fill_kernel = cp.RawKernel(
            _PREPARED_OVERLAY_AREA_TILE_TASK_PLANNER_CUPY_KERNEL,
            "prepared_overlay_area_tile_task_fill_kernel",
        )
        fill_kernel(
            (grid_size,),
            (block_size,),
            (
                relation_rows,
                left_relation_rows,
                right_relation_rows,
                left_shape_start,
                left_shape_count,
                right_shape_start,
                right_shape_count,
                left_component_start,
                left_component_count,
                right_component_start,
                right_component_count,
                left_component_bounds,
                right_component_bounds,
                task_offsets,
                cp.uint32(candidate_count),
                cp.uint32(relation_row_count),
                cp.uint32(int(left_shape_start.size)),
                cp.uint32(int(right_shape_start.size)),
                cp.uint32(int(max_triangle_pairs_per_task)),
                cp.uint32(1 if component_bounds_positive_filter else 0),
                relation_ids,
                pair_offset,
                pair_count,
                left_start,
                left_count,
                right_start,
                right_count,
            ),
        )
        cp.cuda.Stream.null.synchronize()

    metadata = {
        "schema": "rtdl.v2_8.simple_polygon_overlay_area_device_planned_tile_task_cupy_inputs.v1",
        "operation": "prepared_simple_polygon_overlay_area_device_planned_tile_task_inputs",
        "partner": "cupy",
        "candidate_relation_row_count": candidate_count,
        "supported_relation_row_count": supported_relation_row_count,
        "relation_row_count": int(relation_row_count),
        "component_pair_row_count": component_pair_count,
        "task_count": task_count,
        "planned_triangle_pair_count": planned_triangle_pair_count,
        "max_triangle_pairs_per_task": int(max_triangle_pairs_per_task),
        "component_bounds_positive_filter": bool(component_bounds_positive_filter),
        "left_triangle_count": left_payload.triangle_count,
        "right_triangle_count": right_payload.triangle_count,
        "input_contract": "relation_ordinals_plus_prepared_component_tables",
        "resident_cupy_columns": True,
        "planner_summary": {
            "version": V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION,
            "status": "accept",
            "errors": (),
            "pair_row_count": component_pair_count,
            "task_count": task_count,
            "candidate_relation_row_count": candidate_count,
            "relation_row_count": supported_relation_row_count,
            "expected_triangle_pair_count": planned_triangle_pair_count,
            "planned_triangle_pair_count": planned_triangle_pair_count,
            "max_task_pair_count": int(max_triangle_pairs_per_task) if task_count else 0,
            "component_bounds_positive_filter": bool(component_bounds_positive_filter),
            "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "runtime_kernel_authorized": False,
        },
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "runtime_kernel_authorized": False,
        "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
    }
    return PreparedOverlayAreaCupyTileTaskInputs(
        left_columns=left_columns,
        right_columns=right_columns,
        relation_row_ordinals=relation_ids,
        pair_offset=pair_offset,
        pair_count=pair_count,
        left_start=left_start,
        left_count=left_count,
        right_start=right_start,
        right_count=right_count,
        task_count=task_count,
        relation_row_count=int(relation_row_count),
        left_triangle_count=left_payload.triangle_count,
        right_triangle_count=right_payload.triangle_count,
        metadata=metadata,
    )


def evaluate_prepared_overlay_area_tile_task_cupy_inputs(
    inputs: PreparedOverlayAreaCupyTileTaskInputs,
    *,
    input_contract: str = "resident_prepared_overlay_area_tile_task_cupy_inputs",
) -> PreparedOverlayAreaCupyTileTaskResult:
    import cupy as cp  # type: ignore

    task_count = int(inputs.task_count)
    task_areas = cp.zeros((task_count,), dtype=cp.float64)
    task_status = cp.zeros((task_count,), dtype=cp.uint32)
    processed_pairs = cp.zeros((task_count,), dtype=cp.uint32)

    if task_count:
        kernel = cp.RawKernel(_PREPARED_OVERLAY_AREA_TILE_TASK_CUPY_KERNEL, "prepared_overlay_area_tile_task_kernel")
        block_size = 128
        grid_size = (task_count + block_size - 1) // block_size
        kernel(
            (grid_size,),
            (block_size,),
            (
                *inputs.left_columns,
                cp.uint32(inputs.left_triangle_count),
                *inputs.right_columns,
                cp.uint32(inputs.right_triangle_count),
                inputs.relation_row_ordinals,
                inputs.pair_offset,
                inputs.pair_count,
                inputs.left_start,
                inputs.left_count,
                inputs.right_start,
                inputs.right_count,
                cp.uint32(task_count),
                task_areas,
                task_status,
                processed_pairs,
            ),
        )
        cp.cuda.Stream.null.synchronize()

    relation_areas = cp.zeros((int(inputs.relation_row_count),), dtype=cp.float64)
    if task_count:
        cp.add.at(relation_areas, inputs.relation_row_ordinals, task_areas)
        cp.cuda.Stream.null.synchronize()
    status_values = {}
    if task_count:
        unique_status, unique_counts = cp.unique(task_status, return_counts=True)
        status_values = {
            str(int(status)): int(count)
            for status, count in zip(cp.asnumpy(unique_status).tolist(), cp.asnumpy(unique_counts).tolist())
        }
    metadata = {
        "schema": "rtdl.v2_8.simple_polygon_overlay_area_tile_task_cupy.v1",
        "operation": "prepared_simple_polygon_overlay_area_tile_tasks",
        "partner": "cupy",
        "task_count": task_count,
        "relation_row_count": int(inputs.relation_row_count),
        "left_triangle_count": inputs.left_triangle_count,
        "right_triangle_count": inputs.right_triangle_count,
        "processed_triangle_pair_count": int(cp.sum(processed_pairs).get()) if task_count else 0,
        "status_counts": status_values,
        "total_area": float(cp.sum(relation_areas).get()) if inputs.relation_row_count else 0.0,
        "completed_without_truncation": bool(cp.all(task_status == 0).get()) if task_count else True,
        "input_contract": input_contract,
        "reduction": "cupy_add_at_by_relation_row_ordinal",
        "resident_cupy_columns": input_contract in {
            "resident_prepared_overlay_area_tile_task_cupy_inputs",
            "device_planned_prepared_overlay_area_tile_task_cupy_inputs",
        },
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "runtime_kernel_authorized": False,
        "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
    }
    return PreparedOverlayAreaCupyTileTaskResult(
        task_areas=task_areas,
        relation_areas=relation_areas,
        task_status=task_status,
        processed_pairs=processed_pairs,
        relation_row_ordinals=inputs.relation_row_ordinals,
        metadata=metadata,
    )


def evaluate_prepared_overlay_area_tile_tasks_cupy(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    tasks: Sequence[PreparedOverlayAreaTileTask],
    *,
    relation_row_count: int | None = None,
) -> PreparedOverlayAreaCupyTileTaskResult:
    inputs = prepare_overlay_area_tile_task_cupy_inputs(
        left_payload,
        right_payload,
        tasks,
        relation_row_count=relation_row_count,
    )
    return evaluate_prepared_overlay_area_tile_task_cupy_inputs(
        inputs,
        input_contract="prepared_overlay_area_tile_tasks",
    )


def validate_v2_8_overlay_area_prepared_payload_contract() -> dict[str, Any]:
    left = prepare_simple_polygon_component_payload(
        (
            ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0)),
        )
    )
    right = prepare_simple_polygon_component_payload(
        (((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5)),)
    )
    rows = prepare_overlay_area_pair_rows(left, right, ((0, 0),))
    result = evaluate_prepared_overlay_area_scalar(left, right, rows)
    tiled = evaluate_prepared_overlay_area_scalar_tiled(
        left,
        right,
        rows,
        max_triangle_pairs_per_tile=3,
    )
    errors: list[str] = []
    if left.component_count != 1 or right.component_count != 1:
        errors.append("fixture payloads must each contain one component")
    if left.triangle_count != 4:
        errors.append(f"concave fixture must triangulate into 4 triangles, saw {left.triangle_count}")
    if rows[0].triangle_pair_count != 8:
        errors.append(f"fixture must produce 8 triangle pairs, saw {rows[0].triangle_pair_count}")
    if abs(result.total_area - 1.75) > 1.0e-10:
        errors.append(f"fixture prepared total area mismatch: {result.total_area}")
    if abs(tiled.total_area - result.total_area) > 1.0e-10:
        errors.append(f"fixture tiled total area mismatch: {tiled.total_area}")
    if tiled.tile_count != 3:
        errors.append(f"fixture tiled evaluator should use 3 tiles, saw {tiled.tile_count}")
    if tiled.max_observed_tile_pairs > tiled.max_triangle_pairs_per_tile:
        errors.append("fixture tiled evaluator exceeded its max triangle-pair tile capacity")
    if tiled.triangle_pair_count != result.triangle_pair_count:
        errors.append("fixture tiled evaluator did not process all triangle pairs")
    for metadata in (left.to_metadata(), result.to_metadata(), tiled.to_metadata()):
        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "runtime_kernel_authorized",
        ):
            if metadata[field] is not False:
                errors.append(f"prepared payload contract authorizes {field}")
    return {
        "version": V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "left_triangle_count": left.triangle_count,
        "right_triangle_count": right.triangle_count,
        "triangle_pair_count": rows[0].triangle_pair_count,
        "tiled_tile_count": tiled.tile_count,
        "tiled_max_observed_tile_pairs": tiled.max_observed_tile_pairs,
        "fixture_total_area": result.total_area,
        "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
    }


__all__ = [
    "PreparedOverlayAreaEvaluationResult",
    "PreparedOverlayAreaPairRow",
    "PreparedOverlayAreaCupyTiledResult",
    "PreparedOverlayAreaCupyTileTaskInputs",
    "PreparedOverlayAreaCupyTileTaskResult",
    "PreparedOverlayAreaTiledEvaluationResult",
    "PreparedOverlayAreaTileTask",
    "PreparedSimplePolygonComponentPayload",
    "PreparedSimplePolygonComponentRecord",
    "V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_STATUS",
    "V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_CUPY_VERSION",
    "V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_SERIALIZATION_VERSION",
    "V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION",
    "evaluate_prepared_overlay_area_scalar",
    "evaluate_prepared_overlay_area_scalar_tiled",
    "evaluate_prepared_overlay_area_scalar_tiled_cupy",
    "evaluate_prepared_overlay_area_tile_task_cupy_inputs",
    "evaluate_prepared_overlay_area_tile_tasks_cupy",
    "plan_prepared_overlay_area_tile_tasks",
    "prepared_simple_polygon_component_payload_from_dict",
    "prepared_simple_polygon_component_payload_to_dict",
    "prepared_overlay_area_component_bounds_overlap_positive",
    "prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals",
    "prepare_overlay_area_tile_task_cupy_inputs",
    "prepare_overlay_area_pair_rows",
    "prepare_simple_polygon_component_payload",
    "prepare_simple_polygon_component_payload_from_triangles",
    "summarize_prepared_overlay_area_tile_tasks",
    "validate_v2_8_overlay_area_prepared_payload_contract",
]
