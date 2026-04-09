from __future__ import annotations

"""Release-facing reference kernels and fixture builders.

This module gives user-facing examples a stable import path without exposing
internal goal-numbered file names in the public example chain.
"""

from examples.rtdl_goal10_reference import GOAL10_KERNELS
from examples.rtdl_goal10_reference import make_fixture_point_nearest_segment_case
from examples.rtdl_goal10_reference import make_fixture_segment_polygon_case
from examples.rtdl_goal10_reference import make_point_nearest_segment_authored_case
from examples.rtdl_goal10_reference import make_segment_polygon_authored_case
from examples.rtdl_goal10_reference import point_nearest_segment_reference
from examples.rtdl_goal10_reference import segment_polygon_anyhit_rows_reference
from examples.rtdl_goal10_reference import segment_polygon_hitcount_reference

__all__ = [
    "GOAL10_KERNELS",
    "make_fixture_point_nearest_segment_case",
    "make_fixture_segment_polygon_case",
    "make_point_nearest_segment_authored_case",
    "make_segment_polygon_authored_case",
    "point_nearest_segment_reference",
    "segment_polygon_anyhit_rows_reference",
    "segment_polygon_hitcount_reference",
]
