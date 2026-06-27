import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_language_reference import county_soil_overlay_reference
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from examples.rtdl_goal10_reference import point_nearest_segment_reference
from examples.rtdl_goal10_reference import segment_polygon_hitcount_reference
from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference


class EmbreeBaselineContractsTest(unittest.TestCase):
    def test_workload_order_is_frozen(self) -> None:
        self.assertEqual(
            rt.BASELINE_WORKLOAD_ORDER,
            ("lsi", "pip", "overlay", "ray_tri_hitcount", "segment_polygon_hitcount", "point_nearest_segment"),
        )

    def test_reference_kernels_match_frozen_contracts(self) -> None:
        rt.validate_compiled_kernel_against_baseline(
            rt.compile_kernel(county_zip_join_reference),
            "lsi",
        )
        rt.validate_compiled_kernel_against_baseline(
            rt.compile_kernel(point_in_counties_reference),
            "pip",
        )
        rt.validate_compiled_kernel_against_baseline(
            rt.compile_kernel(county_soil_overlay_reference),
            "overlay",
        )
        rt.validate_compiled_kernel_against_baseline(
            rt.compile_kernel(ray_triangle_hitcount_reference),
            "ray_tri_hitcount",
        )
        rt.validate_compiled_kernel_against_baseline(
            rt.compile_kernel(segment_polygon_hitcount_reference),
            "segment_polygon_hitcount",
        )
        rt.validate_compiled_kernel_against_baseline(
            rt.compile_kernel(point_nearest_segment_reference),
            "point_nearest_segment",
        )

    def test_lsi_comparison_policy_uses_float_tolerance(self) -> None:
        self.assertTrue(
            rt.compare_baseline_rows(
                "lsi",
                (
                    {
                        "left_id": 1,
                        "right_id": 2,
                        "intersection_point_x": 1.0,
                        "intersection_point_y": 1.0,
                    },
                ),
                (
                    {
                        "left_id": 1,
                        "right_id": 2,
                        "intersection_point_x": 1.0 + 1e-7,
                        "intersection_point_y": 1.0 - 1e-7,
                    },
                ),
            )
        )

    def test_exact_mode_workloads_reject_changed_integer_results(self) -> None:
        self.assertFalse(
            rt.compare_baseline_rows(
                "ray_tri_hitcount",
                ({"ray_id": 1, "hit_count": 2},),
                ({"ray_id": 1, "hit_count": 3},),
            )
        )

    def test_nearest_segment_uses_float_tolerance_for_distance(self) -> None:
        self.assertTrue(
            rt.compare_baseline_rows(
                "point_nearest_segment",
                ({"point_id": 1, "segment_id": 2, "distance": 0.5},),
                ({"point_id": 1, "segment_id": 2, "distance": 0.5000001},),
            )
        )
