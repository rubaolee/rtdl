from __future__ import annotations

import unittest

import rtdsl as rt
from tests.goal582_apple_rt_full_surface_dispatch_test import ray_hitcount_kernel


class Goal603AppleRtNativeContractTest(unittest.TestCase):
    def test_support_matrix_exposes_native_coverage_contract_fields(self) -> None:
        rows = rt.apple_rt_support_matrix()
        self.assertEqual(len(rows), 19)
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
        self.assertEqual(by_predicate["ray_triangle_any_hit"]["native_candidate_discovery"], "shape_dependent")
        self.assertEqual(
            by_predicate["ray_triangle_any_hit"]["cpu_refinement"],
            "2d_exact_acceptance_or_3d_row_materialization",
        )
        self.assertIn("nearest-intersection any-hit for 3D", by_predicate["ray_triangle_any_hit"]["notes"])
        self.assertIn("per-ray mask early-exit plus exact 2D acceptance", by_predicate["ray_triangle_any_hit"]["notes"])
        self.assertEqual(by_predicate["segment_intersection"]["native_candidate_discovery"], "yes")
        self.assertEqual(by_predicate["segment_intersection"]["cpu_refinement"], "exact_intersection_point")
        self.assertEqual(by_predicate["point_nearest_segment"]["native_candidate_discovery"], "yes")
        self.assertEqual(by_predicate["point_nearest_segment"]["cpu_refinement"], "exact_distance_ranking")
        self.assertEqual(by_predicate["overlay_compose"]["native_candidate_discovery"], "yes")
        self.assertEqual(by_predicate["overlay_compose"]["cpu_refinement"], "full_pair_row_materialization")
        self.assertEqual(by_predicate["polygon_pair_overlap_area_rows"]["native_candidate_discovery"], "yes")
        self.assertEqual(by_predicate["polygon_pair_overlap_area_rows"]["cpu_refinement"], "exact_unit_cell_area")
        self.assertEqual(by_predicate["polygon_set_jaccard"]["native_candidate_discovery"], "yes")
        self.assertEqual(by_predicate["polygon_set_jaccard"]["cpu_refinement"], "exact_unit_cell_set_jaccard")
        self.assertEqual(by_predicate["segment_polygon_anyhit_rows"]["native_candidate_discovery"], "yes")
        self.assertEqual(by_predicate["segment_polygon_anyhit_rows"]["cpu_refinement"], "exact_segment_polygon")
        self.assertEqual(by_predicate["segment_polygon_hitcount"]["native_candidate_discovery"], "yes")
        self.assertEqual(by_predicate["segment_polygon_hitcount"]["cpu_refinement"], "exact_segment_polygon")
        self.assertEqual(by_predicate["conjunctive_scan"]["mode"], "native_metal_compute")
        self.assertEqual(by_predicate["conjunctive_scan"]["cpu_refinement"], "row_id_materialization_only")
        self.assertEqual(by_predicate["conjunctive_scan"]["native_only"], "supported_for_numeric_predicates")
        self.assertEqual(by_predicate["grouped_count"]["mode"], "native_metal_filter_cpu_aggregate")
        self.assertEqual(by_predicate["grouped_count"]["cpu_refinement"], "cpu_group_aggregation_after_metal_filter")
        self.assertEqual(by_predicate["grouped_sum"]["mode"], "native_metal_filter_cpu_aggregate")
        self.assertEqual(by_predicate["grouped_sum"]["cpu_refinement"], "cpu_group_aggregation_after_metal_filter")
        self.assertEqual(by_predicate["bfs_discover"]["mode"], "native_metal_compute")
        self.assertEqual(by_predicate["bfs_discover"]["cpu_refinement"], "dedupe_and_sorted_row_materialization")
        self.assertEqual(by_predicate["bfs_discover"]["native_only"], "supported_for_csr_frontier_vertex_set")
        self.assertEqual(by_predicate["triangle_match"]["mode"], "native_metal_compute")
        self.assertEqual(by_predicate["triangle_match"]["cpu_refinement"], "unique_and_sorted_row_materialization")
        self.assertEqual(by_predicate["triangle_match"]["native_only"], "supported_for_csr_edge_seeds")
        self.assertEqual(by_predicate["triangle_match"]["native_shapes"], ("EdgeSet/CSRGraph",))

    def test_compatibility_rows_are_not_marked_hardware_backed(self) -> None:
        native_candidates = {
            row["predicate"]
            for row in rt.apple_rt_support_matrix()
            if row["native_candidate_discovery"] in {"yes", "shape_dependent"}
        }
        self.assertEqual(
            native_candidates,
            {
                "bounded_knn_rows",
                "fixed_radius_neighbors",
                "knn_rows",
                "point_in_polygon",
                "point_nearest_segment",
                "overlay_compose",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
                "ray_triangle_any_hit",
                "ray_triangle_closest_hit",
                "ray_triangle_hit_count",
                "segment_intersection",
                "segment_polygon_anyhit_rows",
                "segment_polygon_hitcount",
            },
        )
        for row in rt.apple_rt_support_matrix():
            if row["predicate"] in native_candidates or row["mode"] in {
                "native_metal_compute",
                "native_metal_filter_cpu_aggregate",
            }:
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
