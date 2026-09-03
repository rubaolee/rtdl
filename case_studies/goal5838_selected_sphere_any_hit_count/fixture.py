"""Deterministic post-selection fixture for the Goal5838 GPU exam."""

from __future__ import annotations


def selected_exam_fixture() -> dict[str, tuple]:
    return {
        "centers": (
            (3.0, 0.0, 0.0),
            (3.0, 0.0, 0.0),
            (5.0, 0.0, 0.0),
            (5.0, 2.0, 0.0),
            (7.0, -2.0, 0.0),
            (9.0, 0.0, 0.0),
        ),
        "radii": (1.0, 0.5, 1.25, 0.75, 0.5, 1.0),
        "queries": (
            ((0.0, 0.0, 0.0), (12.0, 0.0, 0.0)),
            ((0.0, 2.0, 0.0), (12.0, 2.0, 0.0)),
            ((0.0, -2.0, 0.0), (12.0, -2.0, 0.0)),
            ((0.0, 4.0, 0.0), (12.0, 4.0, 0.0)),
            ((12.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
            ((0.0, 0.0, 3.0), (12.0, 0.0, 3.0)),
        ),
        "case_names": (
            "four_hits_with_overlapping_centers",
            "one_offset_hit",
            "one_negative_offset_hit",
            "all_miss",
            "reverse_direction_four_hits",
            "parallel_plane_miss",
        ),
    }


__all__ = ["selected_exam_fixture"]
