from __future__ import annotations

import unittest
import subprocess
from pathlib import Path

from examples import rtdl_dbscan_clustering_app
from examples import rtdl_outlier_detection_app


ROOT = Path(__file__).resolve().parents[1]


class Goal715EmbreeFixedRadiusSummaryTest(unittest.TestCase):
    def test_native_sources_export_embree_count_threshold(self):
        required = {
            "src/native/embree/rtdl_embree_prelude.h": [
                "RtdlFixedRadiusCountRow",
                "rtdl_embree_run_fixed_radius_count_threshold",
            ],
            "src/native/embree/rtdl_embree_scene.cpp": [
                "kFixedRadiusCountThreshold",
                "FixedRadiusCountThresholdQueryState",
            ],
            "src/native/embree/rtdl_embree_api.cpp": [
                "rtdl_embree_run_fixed_radius_count_threshold",
                "run_query_index_ranges(query_values.size()",
            ],
            "src/rtdsl/embree_runtime.py": [
                "fixed_radius_count_threshold_2d_embree",
                "rtdl_embree_run_fixed_radius_count_threshold",
            ],
        }
        for relative_path, needles in required.items():
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, relative_path)

    def test_outlier_embree_summary_matches_oracle_without_neighbor_rows(self):
        try:
            result = rtdl_outlier_detection_app.run_app(
                "embree",
                embree_summary_mode="rt_count_threshold",
            )
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:  # type: ignore[name-defined]
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")
        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["neighbor_row_count"], 0)
        self.assertEqual(result["native_summary_row_count"], result["point_count"])
        self.assertEqual(result["outlier_point_ids"], [7, 8])

    def test_dbscan_embree_summary_matches_core_flags_without_neighbor_rows(self):
        try:
            result = rtdl_dbscan_clustering_app.run_app(
                "embree",
                embree_summary_mode="rt_core_flags",
            )
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:  # type: ignore[name-defined]
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")
        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["neighbor_row_count"], 0)
        self.assertEqual(result["cluster_rows"], ())
        self.assertEqual(len(result["core_flag_rows"]), result["point_count"])


if __name__ == "__main__":
    unittest.main()
