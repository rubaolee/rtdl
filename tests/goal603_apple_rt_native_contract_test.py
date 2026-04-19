from __future__ import annotations

import unittest

import rtdsl as rt
from tests.goal582_apple_rt_full_surface_dispatch_test import ray_hitcount_kernel


class Goal603AppleRtNativeContractTest(unittest.TestCase):
    def test_support_matrix_exposes_native_coverage_contract_fields(self) -> None:
        rows = rt.apple_rt_support_matrix()
        self.assertEqual(len(rows), 18)
        required = {
            "predicate",
            "mode",
            "native_candidate_discovery",
            "cpu_refinement",
            "native_only",
            "native_shapes",
            "notes",
        }
        for row in rows:
            with self.subTest(predicate=row["predicate"]):
                self.assertTrue(required.issubset(row), row)

    def test_current_native_rows_are_explicit(self) -> None:
        by_predicate = {row["predicate"]: row for row in rt.apple_rt_support_matrix()}

        self.assertEqual(by_predicate["ray_triangle_closest_hit"]["native_candidate_discovery"], "yes")
        self.assertEqual(by_predicate["ray_triangle_closest_hit"]["native_shapes"], ("Ray3D/Triangle3D",))
        self.assertEqual(by_predicate["ray_triangle_hit_count"]["native_candidate_discovery"], "shape_dependent")
        self.assertEqual(by_predicate["ray_triangle_hit_count"]["native_only"], "supported_for_2d_and_3d")
        self.assertEqual(by_predicate["ray_triangle_hit_count"]["native_shapes"], ("Ray2D/Triangle2D", "Ray3D/Triangle3D"))
        self.assertEqual(by_predicate["segment_intersection"]["native_candidate_discovery"], "yes")
        self.assertEqual(by_predicate["segment_intersection"]["cpu_refinement"], "exact_intersection_point")

    def test_compatibility_rows_are_not_marked_hardware_backed(self) -> None:
        native_candidates = {
            row["predicate"]
            for row in rt.apple_rt_support_matrix()
            if row["native_candidate_discovery"] in {"yes", "shape_dependent"}
        }
        self.assertEqual(
            native_candidates,
            {"ray_triangle_closest_hit", "ray_triangle_hit_count", "segment_intersection"},
        )
        for row in rt.apple_rt_support_matrix():
            if row["predicate"] in native_candidates:
                continue
            with self.subTest(predicate=row["predicate"]):
                self.assertEqual(row["native_candidate_discovery"], "no")
                self.assertEqual(row["cpu_refinement"], "full_cpu_reference_compat")
                self.assertEqual(row["native_shapes"], ())

    def test_native_only_still_rejects_unsupported_compatibility_predicate(self) -> None:
        with self.assertRaises(NotImplementedError):
            rt.run_apple_rt(
                ray_hitcount_kernel,
                native_only=True,
                rays=(rt.Ray2D(1, -1.0, 0.5, 1.0, 0.0, 3.0),),
                triangles=(rt.Triangle3D(2, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0),),
            )


if __name__ == "__main__":
    unittest.main()
