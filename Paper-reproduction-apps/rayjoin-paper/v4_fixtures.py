"""Application-owned exact fixtures for the three scoped RayJoin lanes."""

from __future__ import annotations

from rtdsl.v4_exact_predicate_witness import ExactPoint2D, ExactSegment2D


def point_location_fixture():
    segments = (
        ExactSegment2D(100, 0, 10, 10, 10, left_face_id=9,
                       right_face_id=10, group_id=1),
        ExactSegment2D(101, 0, 20, 10, 20, left_face_id=19,
                       right_face_id=20, group_id=2),
        ExactSegment2D(102, 12, 5, 20, 13, left_face_id=29,
                       right_face_id=30, group_id=3),
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


__all__ = ["point_location_fixture", "segment_pair_fixture"]
