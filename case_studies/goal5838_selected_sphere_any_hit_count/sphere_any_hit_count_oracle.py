"""Independent stdlib-only oracle for Goal5838 sphere intersection counts."""

from __future__ import annotations

import math
import struct
from collections.abc import Sequence
from fractions import Fraction


def f32(value: object) -> float:
    try:
        projected = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    except (OverflowError, TypeError, ValueError, struct.error) as exc:
        raise ValueError("finite binary32 value required") from exc
    if not math.isfinite(projected):
        raise ValueError("finite binary32 value required")
    return projected


def _compare_to_entry(
    value: Fraction,
    *,
    a: Fraction,
    half_b: Fraction,
    discriminant: Fraction,
) -> int:
    """Return sign(value - front-entry-root) without evaluating a sqrt."""

    y = a * value + half_b
    if y >= 0:
        return 1
    residual = discriminant - y * y
    return 1 if residual > 0 else (-1 if residual < 0 else 0)


def _intersects_conditioned_segment(
    start: tuple[float, float, float],
    direction: tuple[float, float, float],
    center: Sequence[float],
    radius: object,
) -> bool:
    if len(center) != 3:
        raise ValueError("sphere center must be vec3")
    projected_center = tuple(f32(item) for item in center)
    projected_radius = f32(radius)
    if projected_radius <= 0.0:
        raise ValueError("sphere radius must be positive")
    exact_start = tuple(Fraction.from_float(item) for item in start)
    exact_direction = tuple(Fraction.from_float(item) for item in direction)
    exact_center = tuple(Fraction.from_float(item) for item in projected_center)
    exact_radius = Fraction.from_float(projected_radius)
    offset = tuple(
        exact_start[axis] - exact_center[axis] for axis in range(3)
    )
    a = sum((item * item for item in exact_direction), Fraction(0))
    c = sum((item * item for item in offset), Fraction(0)) - (
        exact_radius * exact_radius
    )
    if c <= 0:
        raise ValueError("segment start must be strictly outside every sphere")
    half_b = sum(
        (offset[axis] * exact_direction[axis] for axis in range(3)),
        Fraction(0),
    )
    discriminant = half_b * half_b - a * c
    if discriminant == 0:
        raise ValueError("exact tangent is outside the conditioned domain")
    if discriminant < 0:
        return False
    return (
        _compare_to_entry(
            Fraction(0),
            a=a,
            half_b=half_b,
            discriminant=discriminant,
        )
        <= 0
        and _compare_to_entry(
            Fraction(1),
            a=a,
            half_b=half_b,
            discriminant=discriminant,
        )
        >= 0
    )


def count_intersections(
    start: Sequence[float],
    end: Sequence[float],
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
) -> int:
    if len(start) != 3 or len(end) != 3:
        raise ValueError("query must contain two vec3 endpoints")
    if not centers or len(centers) != len(radii):
        raise ValueError("equal nonempty center/radius columns required")
    projected_start = tuple(f32(item) for item in start)
    projected_end = tuple(f32(item) for item in end)
    direction = tuple(
        f32(projected_end[axis] - projected_start[axis]) for axis in range(3)
    )
    if direction == (0.0, 0.0, 0.0):
        raise ValueError("nonzero binary32 segment required")
    return sum(
        _intersects_conditioned_segment(
            projected_start, direction, center, radius
        )
        for center, radius in zip(centers, radii)
    )


def count_batch(
    queries: Sequence[Sequence[Sequence[float]]],
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
) -> tuple[int, ...]:
    return tuple(
        count_intersections(query[0], query[1], centers, radii)
        for query in queries
    )


__all__ = ["count_batch", "count_intersections", "f32"]
