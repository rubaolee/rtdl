import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_dbscan_clustering_app
from examples import rtdl_hausdorff_distance_app
from examples import rtdl_outlier_detection_app
from scripts import goal714_embree_app_thread_perf


class Goal741EmbreeCompactAppPerfHarnessTest(unittest.TestCase):
    def test_dbscan_core_flags_avoid_full_cluster_oracle(self) -> None:
        payload = rtdl_dbscan_clustering_app.run_app(
            "cpu_python_reference",
            copies=3,
            output_mode="core_flags",
        )
        self.assertEqual(payload["neighbor_row_count"], 0)
        self.assertEqual(payload["cluster_rows"], ())
        self.assertEqual(payload["oracle_cluster_rows"], ())
        self.assertEqual(len(payload["core_flag_rows"]), 24)
        self.assertTrue(payload["matches_oracle"])

    def test_outlier_density_summary_avoids_neighbor_rows(self) -> None:
        payload = rtdl_outlier_detection_app.run_app(
            "cpu_python_reference",
            copies=3,
            output_mode="density_summary",
        )
        self.assertEqual(payload["neighbor_row_count"], 0)
        self.assertEqual(len(payload["density_rows"]), 24)
        self.assertEqual(payload["outlier_point_ids"], [7, 8, 107, 108, 207, 208])
        self.assertTrue(payload["matches_oracle"])

    def test_hausdorff_directed_summary_uses_tiled_oracle(self) -> None:
        payload = rtdl_hausdorff_distance_app.run_app(
            "cpu_python_reference",
            copies=5,
            embree_result_mode="directed_summary",
        )
        self.assertEqual(payload["directed_a_to_b"]["row_count"], 20)
        self.assertEqual(payload["directed_b_to_a"]["row_count"], 20)
        self.assertTrue(payload["matches_oracle"])

    def test_harness_uses_compact_modes_for_scaled_apps(self) -> None:
        args_by_app = {
            case.app: case.args
            for case in goal714_embree_app_thread_perf.APP_CASES
        }
        self.assertIn("--output-mode", args_by_app["dbscan_clustering"])
        self.assertIn("core_flags", args_by_app["dbscan_clustering"])
        self.assertIn("--output-mode", args_by_app["outlier_detection"])
        self.assertIn("density_summary", args_by_app["outlier_detection"])
        self.assertIn("--embree-result-mode", args_by_app["hausdorff_distance"])
        self.assertIn("directed_summary", args_by_app["hausdorff_distance"])
        self.assertIn("--output-mode", args_by_app["ann_candidate_search"])
        self.assertIn("rerank_summary", args_by_app["ann_candidate_search"])


if __name__ == "__main__":
    unittest.main()
