from __future__ import annotations

"""Release-facing reference kernels and fixture builders."""

from examples.reference.rtdl_workload_reference import WORKLOAD_REFERENCE_KERNELS
from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixed_radius_neighbors_authored_case
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixture_fixed_radius_neighbors_case
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_natural_earth_fixed_radius_neighbors_case
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from examples.reference.rtdl_knn_rows_reference import make_fixture_knn_rows_case
from examples.reference.rtdl_knn_rows_reference import make_knn_rows_authored_case
from examples.reference.rtdl_knn_rows_reference import make_natural_earth_knn_rows_case
from examples.reference.rtdl_workload_reference import make_fixture_point_nearest_segment_case
from examples.reference.rtdl_workload_reference import make_fixture_segment_polygon_case
from examples.reference.rtdl_workload_reference import make_point_nearest_segment_authored_case
from examples.reference.rtdl_workload_reference import make_segment_polygon_authored_case
from examples.reference.rtdl_workload_reference import point_nearest_segment_reference
from examples.reference.rtdl_workload_reference import segment_polygon_anyhit_rows_reference
from examples.reference.rtdl_workload_reference import segment_polygon_hitcount_reference

__all__ = [
    "WORKLOAD_REFERENCE_KERNELS",
    "fixed_radius_neighbors_reference",
    "knn_rows_reference",
    "make_fixed_radius_neighbors_authored_case",
    "make_fixture_fixed_radius_neighbors_case",
    "make_natural_earth_fixed_radius_neighbors_case",
    "make_knn_rows_authored_case",
    "make_fixture_knn_rows_case",
    "make_natural_earth_knn_rows_case",
    "make_fixture_point_nearest_segment_case",
    "make_fixture_segment_polygon_case",
    "make_point_nearest_segment_authored_case",
    "make_segment_polygon_authored_case",
    "point_nearest_segment_reference",
    "segment_polygon_anyhit_rows_reference",
    "segment_polygon_hitcount_reference",
]
