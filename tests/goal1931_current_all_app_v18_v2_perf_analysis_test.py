from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1931_current_all_app_v18_v2_perf_analysis.py"
REPORT = ROOT / "docs" / "reports" / "goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json"


class Goal1931CurrentAllAppPerfAnalysisTest(unittest.TestCase):
    def test_script_builds_current_all_app_analysis(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--output-json",
                "scratch/goal1931_current_all_app_perf_test.json",
                "--output-md",
                "scratch/goal1931_current_all_app_perf_test.md",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout[-2000:])
        payload = json.loads((ROOT / "scratch/goal1931_current_all_app_perf_test.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["row_count"], 16)
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["all_apps_have_final_pod_timing"])
        self.assertTrue(payload["claim_boundary"]["implemented_v2_rows_have_pod_timing"])

    def test_analysis_keeps_measured_pending_and_control_rows_distinct(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        classes = {row["app"]: row["classification"] for row in payload["rows"]}

        self.assertEqual(classes["service_coverage_gaps"], "positive")
        self.assertEqual(classes["event_hotspot_screening"], "positive")
        self.assertEqual(classes["segment_polygon_hitcount"], "positive")
        self.assertEqual(classes["road_hazard_screening"], "positive")
        self.assertEqual(classes["robot_collision_screening"], "positive-subsecond")
        self.assertEqual(classes["facility_knn_assignment"], "positive-bounded-exact")
        self.assertEqual(classes["segment_polygon_anyhit_rows"], "positive")
        self.assertEqual(classes["hausdorff_distance"], "positive-bounded-exact")
        self.assertEqual(classes["ann_candidate_search"], "positive-bounded-exact")
        self.assertEqual(classes["outlier_detection"], "positive")
        self.assertEqual(classes["dbscan_clustering"], "positive-bounded-exact")
        self.assertEqual(classes["barnes_hut_force_app"], "positive-bounded-exact")
        self.assertEqual(classes["database_analytics"], "positive")
        self.assertEqual(classes["graph_analytics"], "positive-bounded")
        self.assertEqual(classes["polygon_pair_overlap_area_rows"], "positive-bounded")
        self.assertEqual(classes["polygon_set_jaccard"], "positive-bounded")

    def test_report_contains_insight_not_only_ratios(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Current All-App v1.8 vs v2.0 Performance Analysis", text)
        self.assertIn("What The Table Says", text)
        self.assertIn("Prepared fixed-radius", text)
        self.assertIn("Segment any-hit now has a seconds-scale", text)
        self.assertIn("positive-subsecond", text)
        self.assertIn("positive bounded v2 evidence", text)
        self.assertIn("compact CuPy extent candidate table", text)
        self.assertIn("upgrades Hausdorff", text)
        self.assertIn("upgrades facility KNN", text)
        self.assertIn("upgrades Barnes-Hut", text)
        self.assertIn("upgrades DBSCAN", text)
        self.assertIn("upgrades ANN candidate search", text)


if __name__ == "__main__":
    unittest.main()
