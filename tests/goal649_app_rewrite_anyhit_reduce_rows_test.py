from __future__ import annotations

import unittest

from examples import rtdl_dbscan_clustering_app as dbscan_app
from examples import rtdl_hausdorff_distance_app as hausdorff_app
from examples import rtdl_outlier_detection_app as outlier_app
from examples import rtdl_robot_collision_screening_app as robot_app


class Goal649AppRewriteAnyhitReduceRowsTest(unittest.TestCase):
    def test_robot_collision_uses_anyhit_and_reduce_rows(self) -> None:
        result = robot_app.run_app("cpu_python_reference")

        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["colliding_pose_ids"], [2, 3])
        self.assertTrue(all("any_hit" in row for row in result["rows"]))
        self.assertTrue(all("hit_count" not in row for row in result["rows"]))
        self.assertEqual(
            result["pose_collision_flags"],
            (
                {"pose_id": 1, "collides": False},
                {"pose_id": 2, "collides": True},
                {"pose_id": 3, "collides": True},
                {"pose_id": 4, "collides": False},
            ),
        )
        self.assertIn("ray/triangle any-hit", result["rtdl_role"])
        self.assertIn("rt.reduce_rows(any)", result["rtdl_role"])

    def test_hausdorff_uses_reduce_rows_max_for_directed_distances(self) -> None:
        result = hausdorff_app.run_app("cpu_python_reference")

        self.assertTrue(result["matches_oracle"])
        self.assertIn("rt.reduce_rows(max)", result["rtdl_role"])
        self.assertEqual(
            result["directed_a_to_b"]["distance"],
            result["directed_a_to_b"]["distance_reduction_rows"][0]["directed_distance"],
        )
        self.assertEqual(
            result["directed_b_to_a"]["distance"],
            result["directed_b_to_a"]["distance_reduction_rows"][0]["directed_distance"],
        )

    def test_outlier_uses_reduce_rows_count_for_density(self) -> None:
        result = outlier_app.run_app("cpu_python_reference")

        self.assertTrue(result["matches_oracle"])
        self.assertIn("rt.reduce_rows(count)", result["rtdl_role"])
        self.assertEqual(result["outlier_point_ids"], [7, 8])
        self.assertEqual(
            {row["point_id"]: row["neighbor_count"] for row in result["density_rows"]},
            {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 1, 8: 1},
        )

    def test_dbscan_uses_reduce_rows_count_for_core_classification(self) -> None:
        result = dbscan_app.run_app("cpu_python_reference")

        self.assertTrue(result["matches_oracle"])
        self.assertIn("rt.reduce_rows(count)", result["rtdl_role"])
        self.assertEqual(result["cluster_sizes"], {1: 4, 2: 3})
        self.assertEqual(result["noise_point_ids"], [8])


if __name__ == "__main__":
    unittest.main()
