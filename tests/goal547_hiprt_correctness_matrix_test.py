from __future__ import annotations

import unittest

from scripts.goal547_hiprt_correctness_matrix import run_matrix


class Goal547HiprtCorrectnessMatrixTest(unittest.TestCase):
    def test_matrix_covers_all_v09_target_workloads(self) -> None:
        payload = run_matrix()
        workloads = {entry["workload"] for entry in payload["results"]}
        self.assertEqual(
            workloads,
            {
                "segment_intersection",
                "point_in_polygon",
                "overlay_compose",
                "ray_triangle_hit_count_2d",
                "ray_triangle_hit_count_3d",
                "segment_polygon_hitcount",
                "segment_polygon_anyhit_rows",
                "point_nearest_segment",
                "fixed_radius_neighbors_2d",
                "fixed_radius_neighbors_3d",
                "bounded_knn_rows_3d",
                "knn_rows_2d",
                "knn_rows_3d",
                "bfs_discover",
                "triangle_match",
                "conjunctive_scan",
                "grouped_count",
                "grouped_sum",
            },
        )
        self.assertEqual(payload["summary"]["fail"], 0)

    def test_unimplemented_workloads_are_explicit_not_cpu_fallbacks(self) -> None:
        payload = run_matrix()
        not_implemented = [entry for entry in payload["results"] if entry["status"] == "NOT_IMPLEMENTED"]
        for entry in not_implemented:
            self.assertIn("No CPU fallback is used", entry["message"])


if __name__ == "__main__":
    unittest.main()
