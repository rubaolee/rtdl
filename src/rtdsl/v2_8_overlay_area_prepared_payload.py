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
    errors: list[str] = []
    if left.component_count != 1 or right.component_count != 1:
        errors.append("fixture payloads must each contain one component")
    if left.triangle_count != 4:
        errors.append(f"concave fixture must triangulate into 4 triangles, saw {left.triangle_count}")
    if rows[0].triangle_pair_count != 8:
        errors.append(f"fixture must produce 8 triangle pairs, saw {rows[0].triangle_pair_count}")
    if abs(result.total_area - 1.75) > 1.0e-10:
        errors.append(f"fixture prepared total area mismatch: {result.total_area}")
    for metadata in (left.to_metadata(), result.to_metadata()):
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
        "fixture_total_area": result.total_area,
        "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
    }


__all__ = [
    "PreparedOverlayAreaEvaluationResult",
    "PreparedOverlayAreaPairRow",
    "PreparedSimplePolygonComponentPayload",
    "PreparedSimplePolygonComponentRecord",
    "V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_STATUS",
    "V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_VERSION",
    "evaluate_prepared_overlay_area_scalar",
    "prepare_overlay_area_pair_rows",
    "prepare_simple_polygon_component_payload",
    "validate_v2_8_overlay_area_prepared_payload_contract",
]
