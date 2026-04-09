from __future__ import annotations

"""Release-facing reference kernels and fixture builders."""

from examples.reference.rtdl_workload_reference import WORKLOAD_REFERENCE_KERNELS
from examples.reference.rtdl_workload_reference import make_fixture_point_nearest_segment_case
from examples.reference.rtdl_workload_reference import make_fixture_segment_polygon_case
from examples.reference.rtdl_workload_reference import make_point_nearest_segment_authored_case
from examples.reference.rtdl_workload_reference import make_segment_polygon_authored_case
from examples.reference.rtdl_workload_reference import point_nearest_segment_reference
from examples.reference.rtdl_workload_reference import segment_polygon_anyhit_rows_reference
from examples.reference.rtdl_workload_reference import segment_polygon_hitcount_reference

__all__ = [
    "WORKLOAD_REFERENCE_KERNELS",
    "make_fixture_point_nearest_segment_case",
    "make_fixture_segment_polygon_case",
    "make_point_nearest_segment_authored_case",
    "make_segment_polygon_authored_case",
    "point_nearest_segment_reference",
    "segment_polygon_anyhit_rows_reference",
    "segment_polygon_hitcount_reference",
]
