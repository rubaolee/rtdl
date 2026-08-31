"""Independent closed-capsule Boolean oracle for Goal5834-B1.

This module is deliberately standard-library only and imports no RTDL code.
The normative path evaluates canonical IEEE-754 binary32 input values in
Python binary64.  It is an evaluation oracle for frozen fixtures, not a
provider implementation and not a universal theorem about OptiX curves.
"""

from __future__ import annotations

import math
import struct


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def f32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", f32(value)))[0]


def f64_bits(value: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", float(value)))[0]


def _dot(a, b) -> float:
    return sum(x * y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _add_scaled(a, b, scale: float):
    return tuple(x + scale * y for x, y in zip(a, b))


def point_segment_distance2(point, start, end) -> float:
    axis = _sub(end, start)
    axis2 = _dot(axis, axis)
    if axis2 <= 0.0:
        return _dot(_sub(point, start), _sub(point, start))
    parameter = max(0.0, min(1.0, _dot(_sub(point, start), axis) / axis2))
    nearest = _add_scaled(start, axis, parameter)
    delta = _sub(point, nearest)
    return _dot(delta, delta)


def segment_segment_distance2(first_start, first_end, second_start, second_end):
    """Return squared distance and the two clamped segment parameters.

    This is the standard closest-points calculation for two finite segments.
    Degenerate segments are supported here so the independent evaluator can
    classify malformed/boundary inputs; the public B1 worker rejects them.
    """

    epsilon = 2.0 ** -52
    u = _sub(first_end, first_start)
    v = _sub(second_end, second_start)
    w = _sub(first_start, second_start)
    a = _dot(u, u)
    b = _dot(u, v)
    c = _dot(v, v)
    d = _dot(u, w)
    e = _dot(v, w)
    denominator = a * c - b * b
    s_numerator = denominator
    s_denominator = denominator
    t_numerator = denominator
    t_denominator = denominator

    if a <= epsilon and c <= epsilon:
        delta = _sub(first_start, second_start)
        return _dot(delta, delta), 0.0, 0.0
    if a <= epsilon:
        s_numerator = 0.0
        s_denominator = 1.0
        t_numerator = e
        t_denominator = c
    else:
        if c <= epsilon:
            t_numerator = 0.0
            t_denominator = 1.0
            s_numerator = -d
            s_denominator = a
        else:
            if denominator <= epsilon * max(1.0, a * c):
                s_numerator = 0.0
                s_denominator = 1.0
                t_numerator = e
                t_denominator = c
            else:
                s_numerator = b * e - c * d
                t_numerator = a * e - b * d
                if s_numerator < 0.0:
                    s_numerator = 0.0
                    t_numerator = e
                    t_denominator = c
                elif s_numerator > s_denominator:
                    s_numerator = s_denominator
                    t_numerator = e + b
                    t_denominator = c

            if t_numerator < 0.0:
                t_numerator = 0.0
                if -d < 0.0:
                    s_numerator = 0.0
                elif -d > a:
                    s_numerator = s_denominator
                else:
                    s_numerator = -d
                    s_denominator = a
            elif t_numerator > t_denominator:
                t_numerator = t_denominator
                if -d + b < 0.0:
                    s_numerator = 0.0
                elif -d + b > a:
                    s_numerator = s_denominator
                else:
                    s_numerator = -d + b
                    s_denominator = a

    s = 0.0 if abs(s_numerator) <= epsilon else s_numerator / s_denominator
    t = 0.0 if abs(t_numerator) <= epsilon else t_numerator / t_denominator
    first_point = _add_scaled(first_start, u, s)
    second_point = _add_scaled(second_start, v, t)
    delta = _sub(first_point, second_point)
    return _dot(delta, delta), s, t


def _sphere_roots(origin, direction, center, radius: float):
    offset = _sub(origin, center)
    a = _dot(direction, direction)
    half_b = _dot(offset, direction)
    c = _dot(offset, offset) - radius * radius
    discriminant = half_b * half_b - a * c
    if a <= 0.0 or discriminant < 0.0:
        return ()
    root = math.sqrt(max(0.0, discriminant))
    return ((-half_b - root) / a, (-half_b + root) / a)


def capsule_entry(origin, end, point_a, point_b, radius: float) -> float | None:
    """Return the first closed-capsule boundary entry on a finite query."""

    direction = _sub(end, origin)
    axis = _sub(point_b, point_a)
    origin_a = _sub(origin, point_a)
    axis2 = _dot(axis, axis)
    axis_direction = _dot(axis, direction)
    axis_origin = _dot(axis, origin_a)
    direction_origin = _dot(direction, origin_a)
    origin2 = _dot(origin_a, origin_a)
    direction2 = _dot(direction, direction)
    side_a = axis2 * direction2 - axis_direction * axis_direction
    side_b = axis2 * direction_origin - axis_origin * axis_direction
    side_c = axis2 * origin2 - axis_origin * axis_origin - radius * radius * axis2
    candidates: list[float] = []
    side_discriminant = side_b * side_b - side_a * side_c
    if side_a > 0.0 and side_discriminant >= 0.0:
        root = math.sqrt(max(0.0, side_discriminant))
        for value in ((-side_b - root) / side_a,
                      (-side_b + root) / side_a):
            axial = axis_origin + value * axis_direction
            if 0.0 < axial < axis2:
                candidates.append(value)
    for center, first_cap in ((point_a, True), (point_b, False)):
        for value in _sphere_roots(origin, direction, center, radius):
            point = _add_scaled(origin, direction, value)
            projection = _dot(_sub(point, center), axis)
            if (first_cap and projection <= 0.0) \
                    or (not first_cap and projection >= 0.0):
                candidates.append(value)
    legal = [value for value in candidates if 0.0 <= value <= 1.0]
    return min(legal) if legal else None


def cross_ratio(first_start, first_end, second_start, second_end) -> float:
    u = _sub(first_end, first_start)
    v = _sub(second_end, second_start)
    u2 = _dot(u, u)
    v2 = _dot(v, v)
    if u2 <= 0.0 or v2 <= 0.0:
        return 0.0
    cross = (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )
    return _dot(cross, cross) / (u2 * v2)


def evaluate_pair(query_start, query_end, capsule_start, capsule_end, radius):
    distance2, query_parameter, capsule_parameter = segment_segment_distance2(
        query_start, query_end, capsule_start, capsule_end)
    radius2 = radius * radius
    denominator = max(distance2 + radius2, 2.0 ** -126)
    separation = abs(distance2 - radius2) / denominator
    start_outside = point_segment_distance2(
        query_start, capsule_start, capsule_end) > radius2
    end_outside = point_segment_distance2(
        query_end, capsule_start, capsule_end) > radius2
    hit = distance2 <= radius2
    entry = capsule_entry(
        query_start, query_end, capsule_start, capsule_end, radius) if hit else None
    return {
        "hit": bool(hit),
        "distance_squared": distance2,
        "radius_squared": radius2,
        "decision_separation": separation,
        "both_query_endpoints_outside": bool(start_outside and end_outside),
        "direction_cross_ratio": cross_ratio(
            query_start, query_end, capsule_start, capsule_end),
        "entry_parameter": entry,
        "closest_query_parameter": query_parameter,
        "closest_capsule_parameter": capsule_parameter,
    }


def evaluate_scene(capsules, queries):
    """Evaluate per-query hit bits and retain every pair qualification row."""

    pair_rows = []
    per_query_hit = []
    for query_index, (query_start, query_end) in enumerate(queries):
        hit = False
        for capsule_index, (start, end, radius, _identity) in enumerate(capsules):
            row = evaluate_pair(
                query_start, query_end, start, end, radius)
            row.update({"query_index": query_index, "capsule_index": capsule_index})
            pair_rows.append(row)
            hit = hit or row["hit"]
        per_query_hit.append(int(hit))
    return {
        "per_query_hit": tuple(per_query_hit),
        "collision": int(any(per_query_hit)),
        "pair_rows": tuple(pair_rows),
    }


__all__ = [
    "capsule_entry", "cross_ratio", "evaluate_pair", "evaluate_scene", "f32",
    "f32_bits", "f64_bits", "point_segment_distance2",
    "segment_segment_distance2",
]
