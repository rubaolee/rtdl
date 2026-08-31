"""Independent CPU oracle for Goal5834 constant-radius capsules.

This module imports no RTDL code.  Inputs are projected to IEEE-754 binary32,
then capsule entry times are solved in Python binary64.  A curve primitive is
the round-linear swept volume of a sphere with equal endpoint radii.
"""

from __future__ import annotations

import math
import struct


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def f32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", f32(value)))[0]


def _dot(a, b) -> float:
    return sum(x * y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _add_scaled(a, b, scale: float):
    return tuple(x + scale * y for x, y in zip(a, b))


def _sphere_roots(origin, direction, center, radius: float):
    offset = _sub(origin, center)
    a = _dot(direction, direction)
    half_b = _dot(offset, direction)
    c = _dot(offset, offset) - radius * radius
    discriminant = half_b * half_b - a * c
    if discriminant < 0.0:
        return ()
    root = math.sqrt(max(0.0, discriminant))
    return ((-half_b - root) / a, (-half_b + root) / a)


def capsule_entry(origin, end, point_a, point_b, radius: float) -> float | None:
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


def first_contact(
    control_points,
    widths,
    segment_indices,
    application_ids,
    queries,
):
    points = tuple(tuple(f32(value) for value in point)
                   for point in control_points)
    radii = tuple(f32(value) for value in widths)
    indices = tuple(int(value) for value in segment_indices)
    identities = tuple(int(value) for value in application_ids)
    outputs = []
    for start, end in queries:
        origin = tuple(f32(value) for value in start)
        endpoint = tuple(f32(value) for value in end)
        candidates = []
        for primitive, (segment_start, identity) in enumerate(
                zip(indices, identities)):
            entry = capsule_entry(
                origin, endpoint, points[segment_start],
                points[segment_start + 1], radii[segment_start])
            if entry is not None:
                # The protocol orders the observable binary32 hit time before
                # the application ID.  Project before ordering so an
                # unobservable binary64 difference cannot break an f32 tie.
                candidates.append((f32(entry), identity, primitive))
        if not candidates:
            outputs.append((0, f32_bits(1.0), 0xFFFFFFFF))
            continue
        entry_f32, identity, _primitive = min(candidates)
        outputs.append((1, f32_bits(entry_f32), identity))
    return tuple(outputs)


__all__ = ["capsule_entry", "f32", "f32_bits", "first_contact"]
