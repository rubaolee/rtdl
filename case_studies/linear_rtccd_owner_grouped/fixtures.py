"""Deterministic local fixtures for the bounded owner-grouped RT-CCD app."""

from __future__ import annotations

from dataclasses import dataclass

from .linear_rtccd_owner_grouped import (
    DirectedObstacleEdge,
    LinearRTCCDOwnerGroupedProblem,
    LinearTrajectoryCandidate,
    SweptSphereSegment,
    UndirectedObstacleEdge,
    bidirect_obstacle_edges,
)


REGISTERED_SURFACE_GAP_FLOOR_EXPONENT2 = -10
REGISTERED_SURFACE_GAP_FLOOR = 2.0 ** REGISTERED_SURFACE_GAP_FLOOR_EXPONENT2


def _segment(name, sphere, start, end, radius=0.25):
    return SweptSphereSegment(name, sphere, start, end, radius)


def _trajectory(name, *segments):
    return LinearTrajectoryCandidate(name, segments)


def _bidirect(name, first, second):
    return bidirect_obstacle_edges((
        UndirectedObstacleEdge(name, first, second),
    ))


@dataclass(frozen=True)
class RegisteredLocalCase:
    case_id: str
    problem: LinearRTCCDOwnerGroupedProblem
    expected_bits: tuple[int, ...]
    purpose: str


def registered_local_cases() -> tuple[RegisteredLocalCase, ...]:
    clear = LinearRTCCDOwnerGroupedProblem(
        "clear_two_owners",
        (
            _trajectory("alpha", _segment(
                "a0", "sphere-a", (0, 0, 0), (2, 0, 0))),
            _trajectory("beta", _segment(
                "b0", "sphere-b", (0, 3, 0), (2, 3, 0))),
        ),
        _bidirect("clear", (1, 1.5, -2), (1, 1.5, 2)),
    )
    one_owner = LinearRTCCDOwnerGroupedProblem(
        "one_owner_hit",
        clear.trajectories,
        _bidirect("cross-alpha", (1, -2, 0), (1, 2, 0)),
    )
    multi_segment = LinearRTCCDOwnerGroupedProblem(
        "many_primitives_one_owner",
        (
            _trajectory(
                "alpha",
                _segment("a0", "sphere-a", (0, 0, 0), (1, 0, 0)),
                _segment("a1", "sphere-a", (1, 0, 0), (2, 0, 0)),
            ),
            clear.trajectories[1],
        ),
        _bidirect("cross-second", (1.75, -2, 0), (1.75, 2, 0)),
    )
    both = LinearRTCCDOwnerGroupedProblem(
        "two_owners_hit",
        clear.trajectories,
        _bidirect("cross-alpha", (1, -2, 0), (1, 2, 0))
        + _bidirect("cross-beta", (1, 1, 0), (1, 5, 0)),
    )
    start_inside = LinearRTCCDOwnerGroupedProblem(
        "start_inside_bidirectional",
        clear.trajectories,
        _bidirect("inside-alpha", (1, 0, 0), (1, 0, 3)),
    )
    duplicate_events = LinearRTCCDOwnerGroupedProblem(
        "duplicate_geometric_queries",
        clear.trajectories,
        (
            DirectedObstacleEdge("duplicate-a", (1, -2, 0), (1, 2, 0)),
            DirectedObstacleEdge("duplicate-b", (1, -2, 0), (1, 2, 0)),
            DirectedObstacleEdge("duplicate-c", (1, 2, 0), (1, -2, 0)),
        ),
    )
    return (
        RegisteredLocalCase(
            clear.problem_id, clear, (0, 0), "all-owner miss"),
        RegisteredLocalCase(
            one_owner.problem_id, one_owner, (1, 0), "single owner hit"),
        RegisteredLocalCase(
            multi_segment.problem_id, multi_segment, (1, 0),
            "many primitives reduce into one owner"),
        RegisteredLocalCase(
            both.problem_id, both, (1, 1), "multiple owners hit"),
        RegisteredLocalCase(
            start_inside.problem_id, start_inside, (1, 0),
            "start-inside query with conservative reverse direction"),
        RegisteredLocalCase(
            duplicate_events.problem_id, duplicate_events, (1, 0),
            "duplicate accepted events remain Boolean-idempotent"),
    )


def deterministic_scale_case(
    owner_count: int,
    segments_per_owner: int,
    *,
    hit_stride: int = 2,
    duplicate_query_factor: int = 1,
) -> RegisteredLocalCase:
    """Create a separated deterministic correctness and reuse workload."""

    values = {
        "owner_count": owner_count,
        "segments_per_owner": segments_per_owner,
        "hit_stride": hit_stride,
        "duplicate_query_factor": duplicate_query_factor,
    }
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0
           for value in values.values()):
        raise ValueError("scale-case dimensions must be positive integers")
    primitive_count = owner_count * segments_per_owner
    if owner_count > 4096 or segments_per_owner > 4096 \
            or primitive_count > 1 << 20:
        raise ValueError("scale-case primitive cardinality is excessive")
    hit_owner_count = (owner_count + hit_stride - 1) // hit_stride
    directed_query_count = (
        2 * hit_owner_count * segments_per_owner * duplicate_query_factor)
    if directed_query_count > 1 << 20:
        raise ValueError("scale-case query cardinality is excessive")
    if primitive_count * directed_query_count > 1 << 22:
        raise ValueError("scale-case oracle pair cardinality is excessive")
    trajectories = []
    undirected_edges = []
    for owner in range(owner_count):
        y = float(owner * 4)
        segments = []
        for segment in range(segments_per_owner):
            x = float(segment * 3)
            segments.append(_segment(
                f"segment-{segment:06d}",
                f"sphere-{owner:06d}",
                (x, y, 0.0),
                (x + 1.0, y, 0.0),
                radius=0.125,
            ))
            if owner % hit_stride == 0:
                for duplicate in range(duplicate_query_factor):
                    undirected_edges.append(UndirectedObstacleEdge(
                        f"owner-{owner:06d}-segment-{segment:06d}-"
                        f"duplicate-{duplicate:06d}",
                        (x + 0.5, y - 1.0, 0.0),
                        (x + 0.5, y + 1.0, 0.0),
                    ))
        trajectories.append(_trajectory(f"owner-{owner:06d}", *segments))
    problem = LinearRTCCDOwnerGroupedProblem(
        f"scale-o{owner_count}-s{segments_per_owner}-h{hit_stride}-"
        f"d{duplicate_query_factor}",
        tuple(trajectories),
        bidirect_obstacle_edges(tuple(undirected_edges)),
    )
    return RegisteredLocalCase(
        problem.problem_id,
        problem,
        tuple(int(owner % hit_stride == 0) for owner in range(owner_count)),
        "separated scale ladder with owner reduction and duplicate delivery",
    )


__all__ = [
    "REGISTERED_SURFACE_GAP_FLOOR", "REGISTERED_SURFACE_GAP_FLOOR_EXPONENT2",
    "RegisteredLocalCase",
    "deterministic_scale_case", "registered_local_cases",
]
