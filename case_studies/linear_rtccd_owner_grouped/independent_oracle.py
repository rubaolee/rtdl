"""Independent finite segment/capsule oracle for the successor app."""

from __future__ import annotations

from dataclasses import dataclass
import math


def _dot(first, second):
    return sum(left * right for left, right in zip(first, second))


def _sub(first, second):
    return tuple(left - right for left, right in zip(first, second))


def _distance2_at(first, first_delta, second, second_delta, s, t):
    delta = tuple(
        first[index] + s * first_delta[index]
        - second[index] - t * second_delta[index]
        for index in range(3)
    )
    return _dot(delta, delta)


def segment_segment_distance2(first_start, first_end, second_start, second_end):
    """Minimum squared distance between two closed nonzero 3-D segments."""

    first = tuple(first_start)
    second = tuple(second_start)
    first_delta = _sub(tuple(first_end), first)
    second_delta = _sub(tuple(second_end), second)
    offset = _sub(first, second)
    a = _dot(first_delta, first_delta)
    b = _dot(first_delta, second_delta)
    c = _dot(second_delta, second_delta)
    d = _dot(first_delta, offset)
    e = _dot(second_delta, offset)
    if a <= 0.0 or c <= 0.0:
        raise ValueError("nonzero segments required")

    def clamp(value):
        return max(0.0, min(1.0, value))

    candidates = [
        (0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0),
        (0.0, clamp(e / c)), (1.0, clamp((e + b) / c)),
        (clamp(-d / a), 0.0), (clamp((b - d) / a), 1.0),
    ]
    determinant = a * c - b * b
    if determinant > 0.0:
        s = (b * e - c * d) / determinant
        t = (a * e - b * d) / determinant
        if 0.0 <= s <= 1.0 and 0.0 <= t <= 1.0:
            candidates.append((s, t))
    return min(_distance2_at(
        first, first_delta, second, second_delta, s, t)
        for s, t in candidates)


@dataclass(frozen=True)
class OwnerGroupedCollisionReference:
    trajectory_ids: tuple[str, ...]
    per_trajectory_collision: tuple[int, ...]
    collided_trajectory_ids: tuple[str, ...]
    any_collision: int
    intersecting_pair_count: int
    minimum_surface_gap: float


def evaluate_owner_grouped_collision_reference(problem):
    """Evaluate exact app semantics without importing any RTDL implementation."""

    from .linear_rtccd_owner_grouped import LinearRTCCDOwnerGroupedProblem

    if not isinstance(problem, LinearRTCCDOwnerGroupedProblem):
        raise TypeError("LinearRTCCDOwnerGroupedProblem required")
    bits = []
    pair_count = 0
    minimum_surface_gap = math.inf
    for trajectory in problem.trajectories:
        owner_hit = False
        for edge in problem.directed_obstacle_edges:
            for segment in trajectory.swept_segments:
                distance = math.sqrt(segment_segment_distance2(
                    edge.start, edge.end, segment.start, segment.end,
                ))
                minimum_surface_gap = min(
                    minimum_surface_gap, abs(distance - segment.radius))
                if distance <= segment.radius:
                    owner_hit = True
                    pair_count += 1
        bits.append(int(owner_hit))
    bit_tuple = tuple(bits)
    trajectory_ids = problem.trajectory_ids
    return OwnerGroupedCollisionReference(
        trajectory_ids,
        bit_tuple,
        tuple(trajectory_id for trajectory_id, bit
              in zip(trajectory_ids, bit_tuple) if bit),
        int(any(bit_tuple)),
        pair_count,
        minimum_surface_gap,
    )


__all__ = [
    "OwnerGroupedCollisionReference",
    "evaluate_owner_grouped_collision_reference",
    "segment_segment_distance2",
]
