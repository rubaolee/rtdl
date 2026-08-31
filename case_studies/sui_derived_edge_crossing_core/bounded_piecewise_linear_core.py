"""Bounded piecewise-linear sphere/edge collision mapping for Goal5835.

This is the small research core selected from the Sui et al. RT-CCD idea:
sphere motion segments become round-linear curve capsules, obstacle edges
become finite ray queries, and the application consumes only a collision bit.
It is not a complete collision detector and contains no CPU geometry oracle.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import struct

from rtdsl.v4_curve import BuiltinCurveStaticInput, CurveBooleanSegmentBatch


def _f32(value: float) -> float:
    projected = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    if not math.isfinite(projected):
        raise ValueError("finite binary32 value required")
    return projected


def _vec3(value, *, field: str):
    row = tuple(value)
    if len(row) != 3:
        raise ValueError(f"{field} must be vec3")
    return tuple(_f32(item) for item in row)


@dataclass(frozen=True)
class SweptSphereSegment:
    sphere_id: int
    path_segment_id: int
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    radius: float

    def __post_init__(self):
        if isinstance(self.sphere_id, bool) or not 0 <= self.sphere_id <= 0xFFFFFFFF:
            raise ValueError("sphere_id must be u32")
        if isinstance(self.path_segment_id, bool) \
                or not 0 <= self.path_segment_id <= 0xFFFFFFFF:
            raise ValueError("path_segment_id must be u32")
        start = _vec3(self.start, field="start")
        end = _vec3(self.end, field="end")
        radius = _f32(self.radius)
        if start == end or radius <= 0.0:
            raise ValueError("nonzero path segment and positive radius required")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "radius", radius)

    @property
    def application_id(self) -> int:
        # The current native curve provider carries one u32 identity. Goal5835
        # freezes path_segment_id as that reconstructable physical identity;
        # sphere_id remains in the application mapping receipt.
        return self.path_segment_id


@dataclass(frozen=True)
class ObstacleEdge:
    edge_id: str
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    source_triangle_ids: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.edge_id, str) or not self.edge_id:
            raise ValueError("nonempty edge_id required")
        start = _vec3(self.start, field="edge.start")
        end = _vec3(self.end, field="edge.end")
        if start == end:
            raise ValueError("obstacle edge must be nonzero")
        triangles = tuple(self.source_triangle_ids)
        if any(not isinstance(item, str) or not item for item in triangles):
            raise ValueError("triangle identities must be nonempty strings")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "source_triangle_ids", triangles)


@dataclass(frozen=True)
class ObstacleTriangle:
    triangle_id: str
    vertex_ids: tuple[str, str, str]
    vertices: tuple[tuple[float, float, float], ...]

    def __post_init__(self):
        if not isinstance(self.triangle_id, str) or not self.triangle_id:
            raise ValueError("nonempty triangle_id required")
        ids = tuple(self.vertex_ids)
        vertices = tuple(_vec3(row, field="triangle.vertex")
                         for row in self.vertices)
        if len(ids) != 3 or len(set(ids)) != 3 or len(vertices) != 3:
            raise ValueError("triangle requires three distinct vertex IDs/positions")
        if any(not isinstance(item, str) or not item for item in ids):
            raise ValueError("vertex identities must be nonempty strings")
        object.__setattr__(self, "vertex_ids", ids)
        object.__setattr__(self, "vertices", vertices)


def trajectory_to_swept_segments(
    sphere_id: int, points, radius: float, *, first_path_segment_id: int = 0,
):
    points = tuple(_vec3(row, field="trajectory.point") for row in points)
    if len(points) < 2:
        raise ValueError("trajectory requires at least two samples")
    return tuple(SweptSphereSegment(
        sphere_id, first_path_segment_id + index,
        points[index], points[index + 1], radius,
    ) for index in range(len(points) - 1))


def deduplicate_triangle_edges(triangles):
    """Deterministically deduplicate shared mesh edges.

    Triangles are ordered by triangle ID. Local directed order is `(0,1)`,
    `(1,2)`, `(2,0)`; the first occurrence fixes query direction. Deduplication
    uses the unordered vertex-ID pair, and inconsistent shared coordinates
    reject instead of silently selecting one.
    """

    rows = {}
    positions = {}
    for triangle in sorted(tuple(triangles), key=lambda item: item.triangle_id):
        if not isinstance(triangle, ObstacleTriangle):
            raise TypeError("ObstacleTriangle values required")
        for vertex_id, position in zip(triangle.vertex_ids, triangle.vertices):
            prior = positions.setdefault(vertex_id, position)
            if prior != position:
                raise ValueError("shared vertex identity has inconsistent position")
        for first, second in ((0, 1), (1, 2), (2, 0)):
            first_id, second_id = (
                triangle.vertex_ids[first], triangle.vertex_ids[second])
            key = tuple(sorted((first_id, second_id)))
            if key not in rows:
                rows[key] = {
                    "start": triangle.vertices[first],
                    "end": triangle.vertices[second],
                    "triangles": [triangle.triangle_id],
                }
            else:
                rows[key]["triangles"].append(triangle.triangle_id)
    return tuple(ObstacleEdge(
        f"{key[0]}--{key[1]}", row["start"], row["end"],
        tuple(sorted(row["triangles"])),
    ) for key, row in sorted(rows.items()))


@dataclass(frozen=True)
class BoundedEdgeCrossingProblem:
    problem_id: str
    swept_segments: tuple[SweptSphereSegment, ...]
    obstacle_edges: tuple[ObstacleEdge, ...]

    def __post_init__(self):
        segments = tuple(self.swept_segments)
        edges = tuple(self.obstacle_edges)
        if not self.problem_id or not segments or not edges:
            raise ValueError("problem ID, swept segments and obstacle edges required")
        if any(not isinstance(row, SweptSphereSegment) for row in segments) \
                or any(not isinstance(row, ObstacleEdge) for row in edges):
            raise TypeError("typed swept segments and obstacle edges required")
        if len({row.path_segment_id for row in segments}) != len(segments):
            raise ValueError("path segment IDs must be unique")
        if len({row.edge_id for row in edges}) != len(edges):
            raise ValueError("edge IDs must be unique")
        object.__setattr__(self, "swept_segments", segments)
        object.__setattr__(self, "obstacle_edges", edges)

    def public_inputs(self):
        points, widths, indices, identities = [], [], [], []
        for segment in self.swept_segments:
            indices.append(len(points))
            points.extend((segment.start, segment.end))
            widths.extend((segment.radius, segment.radius))
            identities.append(segment.application_id)
        static = BuiltinCurveStaticInput(
            points, widths, indices, identities)
        batch = CurveBooleanSegmentBatch(tuple(
            (edge.start, edge.end) for edge in self.obstacle_edges))
        return static, batch

    def identity_projection(self):
        return {
            "problem_id": self.problem_id,
            "curve_to_path": [{
                "primitive_index": index,
                "sphere_id": row.sphere_id,
                "path_segment_id": row.path_segment_id,
                "application_id": row.application_id,
            } for index, row in enumerate(self.swept_segments)],
            "query_to_edge": [{
                "query_index": index,
                "edge_id": row.edge_id,
                "source_triangle_ids": list(row.source_triangle_ids),
            } for index, row in enumerate(self.obstacle_edges)],
        }


@dataclass(frozen=True)
class RTCCDBooleanResult:
    problem_id: str
    edge_ids: tuple[str, ...]
    per_edge_hit: tuple[int, ...]
    collision: int
    raw_gpu_bit_vector_commitment_sha256: str
    physical_receipt: dict[str, object]
    traversal_receipt: dict[str, object]


def execute_registered_problem(materialized_program, problem):
    """Execute one mapped static scene through the public Boolean lifecycle."""

    if not isinstance(problem, BoundedEdgeCrossingProblem):
        raise TypeError("BoundedEdgeCrossingProblem required")
    static, batch = problem.public_inputs()
    prepared = materialized_program.prepare(static)
    with prepared:
        generic = prepared.execute(batch)
    # The generic runtime seals the raw vector before its own host OR. This
    # adapter only renames those already-sealed fields for the case study.
    return RTCCDBooleanResult(
        problem.problem_id,
        tuple(edge.edge_id for edge in problem.obstacle_edges),
        generic.per_query_hit,
        generic.any_hit,
        generic.output_sha256,
        generic.physical_receipt,
        generic.traversal_receipt,
    )


__all__ = [
    "BoundedEdgeCrossingProblem", "ObstacleEdge", "ObstacleTriangle",
    "RTCCDBooleanResult", "SweptSphereSegment",
    "deduplicate_triangle_edges", "execute_registered_problem",
    "trajectory_to_swept_segments",
]
