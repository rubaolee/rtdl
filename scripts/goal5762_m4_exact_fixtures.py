"""Frozen app-facing fixtures for Goal5762/M4.

Only this evidence script names the consuming paper lanes.  Product code sees
typed points, segments, candidate rows, and a closed partner-algebra enum.
"""

from __future__ import annotations

import math

import numpy as np

from rtdsl.v4_exact_predicate_witness import ExactPoint2D, ExactSegment2D


def xhd_fixture():
    sources = np.asarray([
        (0.0, 1.0, 0.0),
        (5.0, 0.0, 0.0),
        (2.0, 8.0, 0.0),
        (4.0, 0.0, 0.0),
    ], dtype=np.float32)
    targets = np.asarray([
        (0.0, 0.0, 0.0),
        (4.0, 0.0, 0.0),
        (2.0, 4.0, 0.0),
        (8.0, 0.0, 0.0),
    ], dtype=np.float32)
    return sources, targets


def point_location_fixture():
    segments = (
        ExactSegment2D(
            100, 0, 10, 10, 10,
            left_face_id=9, right_face_id=10, group_id=1),
        ExactSegment2D(
            101, 0, 20, 10, 20,
            left_face_id=19, right_face_id=20, group_id=2),
        ExactSegment2D(
            102, 12, 5, 20, 13,
            left_face_id=29, right_face_id=30, group_id=3),
    )
    points = (
        ExactPoint2D(200, 5, 5),
        ExactPoint2D(201, 5, 10),
        ExactPoint2D(202, 0, 5),
        ExactPoint2D(203, 10, 5),
        ExactPoint2D(204, 15, 0),
    )
    return points, segments


def segment_pair_fixture():
    left = (
        ExactSegment2D(300, 0, 0, 10, 10, group_id=7),
        ExactSegment2D(301, 0, 30, 10, 30, group_id=7),
        ExactSegment2D(302, 20, 0, 30, 10, group_id=8),
    )
    right = (
        ExactSegment2D(400, 0, 10, 10, 0, group_id=70),
        ExactSegment2D(401, 20, 20, 30, 20, group_id=70),
        ExactSegment2D(402, 10, 10, 20, 0, group_id=71),
        ExactSegment2D(403, 10, 10, 0, 0, group_id=72),
    )
    return left, right


def _outward_f32(value: int, direction: float) -> float:
    rounded = np.float32(value)
    return float(np.nextafter(
        rounded,
        np.float32(-math.inf if direction < 0 else math.inf),
        dtype=np.float32,
    ))


def segment_boxes(segments):
    return tuple(
        (
            _outward_f32(min(row.x0, row.x1), -1.0),
            _outward_f32(min(row.y0, row.y1), -1.0),
            _outward_f32(max(row.x0, row.x1), 1.0),
            _outward_f32(max(row.y0, row.y1), 1.0),
            row.segment_id,
        )
        for row in segments
    )


def vertical_ray_boxes(points, segments):
    maximum_y = max(max(row.y0, row.y1) for row in segments) + 1
    return tuple(
        (
            _outward_f32(row.x, -1.0),
            _outward_f32(row.y, -1.0),
            _outward_f32(row.x, 1.0),
            _outward_f32(maximum_y, 1.0),
            row.point_id,
        )
        for row in points
    )


__all__ = [
    "point_location_fixture", "segment_boxes", "segment_pair_fixture",
    "vertical_ray_boxes", "xhd_fixture",
]
