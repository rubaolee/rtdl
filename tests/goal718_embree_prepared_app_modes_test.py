from __future__ import annotations

import subprocess
import unittest

from examples import rtdl_dbscan_clustering_app
from examples import rtdl_outlier_detection_app


class Goal718EmbreePreparedAppModesTest(unittest.TestCase):
    def test_outlier_app_exposes_prepared_embree_summary_mode(self):
        try:
            result = rtdl_outlier_detection_app.run_app(
                "embree",
                embree_summary_mode="rt_count_threshold_prepared",
            )
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")
        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["neighbor_row_count"], 0)
        self.assertEqual(result["native_summary_row_count"], result["point_count"])
        self.assertEqual(result["outlier_point_ids"], [7, 8])
        self.assertEqual(result["embree_summary_mode"], "rt_count_threshold_prepared")
        self.assertIn("reusable Embree BVH handle", result["rtdl_role"])

    def test_dbscan_app_exposes_prepared_embree_core_flag_mode(self):
        try:
            result = rtdl_dbscan_clustering_app.run_app(
                "embree",
                embree_summary_mode="rt_core_flags_prepared",
            )
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")
        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["neighbor_row_count"], 0)
        self.assertEqual(result["cluster_rows"], ())
        self.assertEqual(len(result["core_flag_rows"]), result["point_count"])
        self.assertEqual(result["embree_summary_mode"], "rt_core_flags_prepared")
        self.assertIn("reusable Embree BVH handle", result["rtdl_role"])


if __name__ == "__main__":
    unittest.main()
