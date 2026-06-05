from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .simple_polygon_overlay_area_reference import Point2
from .simple_polygon_overlay_area_reference import Triangle2
from .simple_polygon_overlay_area_reference import convex_polygon_overlap_area
from .simple_polygon_overlay_area_reference import triangulate_simple_polygon_ear_clip
from .v2_8_overlay_area_continuation_contract import V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY
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


@dataclass(frozen=True)
class PreparedSimplePolygonComponentRecord:
    component_ordinal: int
    source_shape_id: int
    triangle_start: int
    triangle_count: int
    input_vertex_count: int
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
        records.append(
            PreparedSimplePolygonComponentRecord(
                component_ordinal=component_ordinal,
                source_shape_id=source_shape_id,
                triangle_start=start,
                triangle_count=len(component_triangles),
                input_vertex_count=len(vertices),
            )
        )
    return PreparedSimplePolygonComponentPayload(triangles=tuple(triangles), components=tuple(records))


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


def evaluate_prepared_overlay_area_scalar(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    pair_rows: Sequence[PreparedOverlayAreaPairRow],
    *,
    eps: float = 1.0e-12,
) -> PreparedOverlayAreaEvaluationResult:
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
        positive_row_count=sum(1 for area in row_areas if area > eps),
        triangle_pair_count=total_triangle_pairs,
    )


def evaluate_prepared_overlay_area_scalar_tiled(
    left_payload: PreparedSimplePolygonComponentPayload,
    right_payload: PreparedSimplePolygonComponentPayload,
    pair_rows: Sequence[PreparedOverlayAreaPairRow],
    *,
    max_triangle_pairs_per_tile: int,
    eps: float = 1.0e-12,
) -> PreparedOverlayAreaTiledEvaluationResult:
    if max_triangle_pairs_per_tile <= 0:
        raise ValueError("max_triangle_pairs_per_tile must be positive; scratch capacity must fail closed")

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
        positive_row_count=sum(1 for area in row_areas if area > eps),
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
    "PreparedOverlayAreaTiledEvaluationResult",
    "PreparedSimplePolygonComponentPayload",
    "PreparedSimplePolygonComponentRecord",
    "V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_STATUS",
    "V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_CUPY_VERSION",
    "V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION",
    "evaluate_prepared_overlay_area_scalar",
    "evaluate_prepared_overlay_area_scalar_tiled",
    "evaluate_prepared_overlay_area_scalar_tiled_cupy",
    "prepare_overlay_area_pair_rows",
    "prepare_simple_polygon_component_payload",
    "validate_v2_8_overlay_area_prepared_payload_contract",
]
