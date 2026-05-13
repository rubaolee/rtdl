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

    def test_analysis_keeps_measured_pending_and_control_rows_distinct(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        classes = {row["app"]: row["classification"] for row in payload["rows"]}

        self.assertEqual(classes["service_coverage_gaps"], "positive")
        self.assertEqual(classes["event_hotspot_screening"], "positive")
        self.assertEqual(classes["segment_polygon_hitcount"], "positive")
        self.assertEqual(classes["road_hazard_screening"], "positive")
        self.assertEqual(classes["robot_collision_screening"], "pending-pod")
        self.assertEqual(classes["facility_knn_assignment"], "pending-pod")
        self.assertEqual(classes["database_analytics"], "control")
        self.assertEqual(classes["graph_analytics"], "control")
        self.assertEqual(classes["polygon_pair_overlap_area_rows"], "control")
        self.assertEqual(classes["polygon_set_jaccard"], "control")

    def test_report_contains_insight_not_only_ratios(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Current All-App v1.8 vs v2.0 Performance Analysis", text)
        self.assertIn("What The Table Says", text)
        self.assertIn("prepared fixed-radius", text)
        self.assertIn("small rows remain setup-bound", text)
        self.assertIn("controls/fallbacks", text)
        self.assertIn("not v2 partner speedup rows", text)


if __name__ == "__main__":
    unittest.main()
