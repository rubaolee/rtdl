"""Paper-derived linear RT-CCD subset over a generic RTDL primitive.

The application owns all collision vocabulary and all semantic mappings.  The
RTDL engine sees only round-linear curve primitives, owner IDs, finite segment
queries, and an owner-sized Boolean output.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import struct

from rtdsl.v4_curve_owner_grouped_any_hit_public import (
    OwnerGroupedCurveQueryBatch,
    OwnerGroupedCurveStaticInput,
)


def _f32(value: object, *, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) \
            or not math.isfinite(float(value)):
        raise ValueError(f"{field} must be finite numeric")
    try:
        result = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    except OverflowError as exc:
        raise ValueError(f"{field} must fit binary32") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field} must fit binary32")
    return result


def _vec3(value: object, *, field: str) -> tuple[float, float, float]:
    try:
        row = tuple(value)
    except TypeError as exc:
        raise ValueError(f"{field} must be vec3") from exc
    if len(row) != 3:
        raise ValueError(f"{field} must be vec3")
    return tuple(_f32(item, field=f"{field}[{index}]")
                 for index, item in enumerate(row))


def _identity(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a nonempty string")
    return value


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _length_bound(first, second, *, upper: bool) -> float:
    squared = math.fsum(
        (left - right) * (left - right)
        for left, right in zip(first, second))
    direction = math.inf if upper else -math.inf
    return math.nextafter(math.sqrt(squared), direction)


def _capsule_diameter_upper_bound(segment) -> float:
    axis_upper = _length_bound(segment.start, segment.end, upper=True)
    return math.nextafter(axis_upper + 2.0 * segment.radius, math.inf)


@dataclass(frozen=True)
class SweptSphereSegment:
    segment_id: str
    sphere_id: str
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    radius: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "segment_id", _identity(self.segment_id, field="segment_id"))
        object.__setattr__(
            self, "sphere_id", _identity(self.sphere_id, field="sphere_id"))
        start = _vec3(self.start, field="segment.start")
        end = _vec3(self.end, field="segment.end")
        radius = _f32(self.radius, field="segment.radius")
        if start == end:
            raise ValueError("swept sphere segment must be nonzero")
        if radius <= 0.0:
            raise ValueError("swept sphere radius must be positive")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "radius", radius)


@dataclass(frozen=True)
class LinearTrajectoryCandidate:
    trajectory_id: str
    swept_segments: tuple[SweptSphereSegment, ...]

    def __post_init__(self) -> None:
        trajectory_id = _identity(self.trajectory_id, field="trajectory_id")
        segments = tuple(self.swept_segments)
        if not segments or any(not isinstance(row, SweptSphereSegment)
                               for row in segments):
            raise ValueError("trajectory requires swept sphere segments")
        if len({row.segment_id for row in segments}) != len(segments):
            raise ValueError("segment IDs must be unique within a trajectory")
        object.__setattr__(self, "trajectory_id", trajectory_id)
        object.__setattr__(
            self, "swept_segments",
            tuple(sorted(segments, key=lambda row: row.segment_id)),
        )


@dataclass(frozen=True)
class DirectedObstacleEdge:
    edge_id: str
    start: tuple[float, float, float]
    end: tuple[float, float, float]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "edge_id", _identity(self.edge_id, field="edge_id"))
        start = _vec3(self.start, field="edge.start")
        end = _vec3(self.end, field="edge.end")
        if start == end:
            raise ValueError("directed obstacle edge must be nonzero")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)


@dataclass(frozen=True)
class UndirectedObstacleEdge:
    edge_id: str
    first: tuple[float, float, float]
    second: tuple[float, float, float]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "edge_id", _identity(self.edge_id, field="edge_id"))
        first = _vec3(self.first, field="edge.first")
        second = _vec3(self.second, field="edge.second")
        if first == second:
            raise ValueError("undirected obstacle edge must be nonzero")
        object.__setattr__(self, "first", first)
        object.__setattr__(self, "second", second)


def bidirect_obstacle_edges(edges) -> tuple[DirectedObstacleEdge, ...]:
    """Expand each app-owned undirected edge into both query directions.

    This deliberately conservative app policy is stronger than selecting an
    arbitrary direction.  It is not represented as engine or primitive logic.
    """

    rows = tuple(edges)
    if any(not isinstance(row, UndirectedObstacleEdge) for row in rows):
        raise TypeError("UndirectedObstacleEdge values required")
    if len({row.edge_id for row in rows}) != len(rows):
        raise ValueError("undirected edge IDs must be unique")
    directed = []
    for row in sorted(rows, key=lambda item: item.edge_id):
        directed.extend((
            DirectedObstacleEdge(f"{row.edge_id}:forward", row.first, row.second),
            DirectedObstacleEdge(f"{row.edge_id}:reverse", row.second, row.first),
        ))
    return tuple(directed)


@dataclass(frozen=True)
class LinearRTCCDOwnerGroupedProblem:
    problem_id: str
    trajectories: tuple[LinearTrajectoryCandidate, ...]
    directed_obstacle_edges: tuple[DirectedObstacleEdge, ...]

    def __post_init__(self) -> None:
        problem_id = _identity(self.problem_id, field="problem_id")
        trajectories = tuple(self.trajectories)
        edges = tuple(self.directed_obstacle_edges)
        if not trajectories or any(not isinstance(row, LinearTrajectoryCandidate)
                                   for row in trajectories):
            raise ValueError("problem requires trajectory candidates")
        if not edges or any(not isinstance(row, DirectedObstacleEdge)
                            for row in edges):
            raise ValueError("problem requires directed obstacle edges")
        if len({row.trajectory_id for row in trajectories}) != len(trajectories):
            raise ValueError("trajectory IDs must be unique")
        if len({row.edge_id for row in edges}) != len(edges):
            raise ValueError("directed edge IDs must be unique")
        object.__setattr__(self, "problem_id", problem_id)
        object.__setattr__(
            self, "trajectories",
            tuple(sorted(trajectories, key=lambda row: row.trajectory_id)),
        )
        object.__setattr__(
            self, "directed_obstacle_edges",
            tuple(sorted(edges, key=lambda row: row.edge_id)),
        )

    @property
    def trajectory_ids(self) -> tuple[str, ...]:
        return tuple(row.trajectory_id for row in self.trajectories)

    def public_inputs(
        self,
    ) -> tuple[OwnerGroupedCurveStaticInput, OwnerGroupedCurveQueryBatch]:
        points = []
        widths = []
        segment_indices = []
        owner_ids = []
        for owner_id, trajectory in enumerate(self.trajectories):
            for segment in trajectory.swept_segments:
                segment_indices.append(len(points))
                points.extend((segment.start, segment.end))
                widths.extend((segment.radius, segment.radius))
                owner_ids.append(owner_id)
        static = OwnerGroupedCurveStaticInput(
            points, widths, segment_indices, owner_ids, len(self.trajectories))
        batch = OwnerGroupedCurveQueryBatch(tuple(
            (row.start, row.end) for row in self.directed_obstacle_edges))
        return static, batch

    def identity_projection(self) -> dict[str, object]:
        primitive_rows = []
        primitive_id = 0
        for owner_id, trajectory in enumerate(self.trajectories):
            for segment in trajectory.swept_segments:
                primitive_rows.append({
                    "primitive_id": primitive_id,
                    "owner_id": owner_id,
                    "trajectory_id": trajectory.trajectory_id,
                    "sphere_id": segment.sphere_id,
                    "segment_id": segment.segment_id,
                })
                primitive_id += 1
        value = {
            "schema": "rtdl.case_study.linear_rtccd_owner_projection.v1",
            "problem_id": self.problem_id,
            "owner_to_trajectory": [
                {"owner_id": index, "trajectory_id": trajectory_id}
                for index, trajectory_id in enumerate(self.trajectory_ids)
            ],
            "primitive_to_owner": primitive_rows,
            "query_to_directed_edge": [
                {"query_id": index, "edge_id": row.edge_id}
                for index, row in enumerate(self.directed_obstacle_edges)
            ],
        }
        return {**value, "projection_sha256": _digest(value)}

    def surface_crossing_domain_admission(self) -> dict[str, object]:
        """Certify that no finite query can be wholly inside one capsule.

        This O(P+Q) sufficient condition deliberately avoids performing the
        O(P*Q) collision discovery that the RT path exists to accelerate.
        """

        maximum_capsule_diameter_upper_bound = max(
            _capsule_diameter_upper_bound(segment)
            for trajectory in self.trajectories
            for segment in trajectory.swept_segments
        )
        minimum_query_length_lower_bound = min(
            _length_bound(edge.start, edge.end, upper=False)
            for edge in self.directed_obstacle_edges
        )
        if minimum_query_length_lower_bound <= \
                maximum_capsule_diameter_upper_bound:
            raise ValueError(
                "bounded surface-crossing domain requires every query edge "
                "to be longer than every capsule diameter"
            )
        value = {
            "schema": "rtdl.case_study.linear_rtccd_surface_crossing_domain.v2",
            "proof": (
                "minimum_query_length_lower_bound_gt_"
                "maximum_capsule_diameter_upper_bound"
            ),
            "minimum_query_length_lower_bound":
                minimum_query_length_lower_bound,
            "maximum_capsule_diameter_upper_bound":
                maximum_capsule_diameter_upper_bound,
            "certified_length_margin": (
                minimum_query_length_lower_bound
                - maximum_capsule_diameter_upper_bound
            ),
            "rounding_policy": (
                "canonical_f32_inputs__binary64_fsum_sqrt__"
                "nextafter_outward_bounds"
            ),
            "fully_contained_query_excluded": True,
            "pairwise_collision_discovery_performed": False,
        }
        return {**value, "admission_sha256": _digest(value)}


@dataclass(frozen=True)
class LinearRTCCDOwnerGroupedResult:
    problem_id: str
    trajectory_ids: tuple[str, ...]
    per_trajectory_collision: tuple[int, ...]
    collided_trajectory_ids: tuple[str, ...]
    any_collision: int
    output_sha256: str
    identity_projection: dict[str, object]
    application_admission: dict[str, object]
    physical_receipt: dict[str, object]
    traversal_receipt: dict[str, object]


def _project_generic_result(
    problem: LinearRTCCDOwnerGroupedProblem,
    generic,
    admission,
) -> LinearRTCCDOwnerGroupedResult:
    bits = tuple(generic.owner_hit_bits)
    if len(bits) != len(problem.trajectories) \
            or any(value not in (0, 1) for value in bits):
        raise RuntimeError("RTDL owner output violates application contract")
    any_collision = int(any(bits))
    if generic.any_hit != any_collision \
            or generic.hit_owner_count != sum(bits) \
            or len(generic.query_completion_tokens) != len(
                problem.directed_obstacle_edges) \
            or any(generic.query_completion_tokens):
        raise RuntimeError("RTDL grouped result metadata violates application contract")
    trajectory_ids = problem.trajectory_ids
    return LinearRTCCDOwnerGroupedResult(
        problem.problem_id,
        trajectory_ids,
        bits,
        tuple(trajectory_id for trajectory_id, bit
              in zip(trajectory_ids, bits) if bit),
        any_collision,
        generic.output_sha256,
        problem.identity_projection(),
        admission,
        generic.physical_receipt,
        generic.traversal_receipt,
    )


class PreparedLinearRTCCDOwnerGroupedProblem:
    """App-owned prepared wrapper over the generic RTDL lifecycle."""

    def __init__(self, materialized_program, problem) -> None:
        if not isinstance(problem, LinearRTCCDOwnerGroupedProblem):
            raise TypeError("LinearRTCCDOwnerGroupedProblem required")
        static, batch = problem.public_inputs()
        self._problem = problem
        self._batch = batch
        self._admission = problem.surface_crossing_domain_admission()
        self._generic = materialized_program.prepare(static)
        self._closed = False

    @property
    def lifecycle_receipt(self):
        if self._closed:
            raise RuntimeError("prepared linear RT-CCD problem is closed")
        return self._generic.lifecycle_receipt

    def execute(self) -> LinearRTCCDOwnerGroupedResult:
        if self._closed:
            raise RuntimeError("prepared linear RT-CCD problem is closed")
        return _project_generic_result(
            self._problem, self._generic.execute(self._batch), self._admission)

    def close(self) -> None:
        if self._closed:
            return
        self._generic.close()
        self._closed = True

    def __enter__(self):
        if self._closed:
            raise RuntimeError("prepared linear RT-CCD problem is closed")
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            self.close()
        except Exception as cleanup:
            if exc is None:
                raise
            raise RuntimeError(
                "linear RT-CCD context body and cleanup both failed; "
                f"primary={type(exc).__name__}: {exc}; "
                f"cleanup={type(cleanup).__name__}: {cleanup}"
            ) from exc
        return False


def prepare_problem(
    materialized_program,
    problem,
) -> PreparedLinearRTCCDOwnerGroupedProblem:
    return PreparedLinearRTCCDOwnerGroupedProblem(materialized_program, problem)


def execute_problem(materialized_program, problem) -> LinearRTCCDOwnerGroupedResult:
    """Run one problem through the app-owned public prepared lifecycle."""

    with prepare_problem(materialized_program, problem) as prepared:
        return prepared.execute()


__all__ = [
    "DirectedObstacleEdge", "LinearRTCCDOwnerGroupedProblem",
    "LinearRTCCDOwnerGroupedResult", "LinearTrajectoryCandidate",
    "PreparedLinearRTCCDOwnerGroupedProblem",
    "SweptSphereSegment", "UndirectedObstacleEdge",
    "bidirect_obstacle_edges", "execute_problem", "prepare_problem",
]
