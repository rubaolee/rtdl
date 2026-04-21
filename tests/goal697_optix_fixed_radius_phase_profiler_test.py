import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal697_optix_fixed_radius_phase_profiler.py"
REPORT = ROOT / "docs" / "reports" / "goal697_optix_fixed_radius_phase_profiler_2026-04-21.md"


class Goal697OptixFixedRadiusPhaseProfilerTest(unittest.TestCase):
    def test_dry_run_profile_has_all_fixed_radius_cases(self):
        payload = json.loads(
            subprocess.check_output(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "dry-run",
                    "--copies",
                    "1",
                    "--iterations",
                    "1",
                ],
                cwd=ROOT,
                text=True,
            )
        )
        self.assertEqual(payload["goal"], "Goal697 OptiX fixed-radius app-level phase profiler")
        self.assertEqual(payload["backend"], "cpu_python_reference_dry_run")
        self.assertFalse(payload["classification_change"])
        self.assertFalse(payload["rtx_speedup_claim"])
        observed = {(case["app"], case["path"]) for case in payload["cases"]}
        self.assertEqual(
            observed,
            {
                ("outlier_detection", "rows"),
                ("outlier_detection", "rt_count_threshold"),
                ("dbscan_clustering", "rows"),
                ("dbscan_clustering", "rt_core_flags"),
            },
        )
        for case in payload["cases"]:
            with self.subTest(case=(case["app"], case["path"])):
                self.assertTrue(case["last_output"]["matches_oracle"])
                self.assertIn("total", case["phase_stats"])
                self.assertGreaterEqual(case["phase_stats"]["total"]["median_sec"], 0.0)

    def test_summary_paths_avoid_neighbor_row_materialization_in_dry_run(self):
        payload = json.loads(
            subprocess.check_output(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "dry-run",
                    "--copies",
                    "2",
                    "--iterations",
                    "1",
                ],
                cwd=ROOT,
                text=True,
            )
        )
        cases = {(case["app"], case["path"]): case for case in payload["cases"]}
        outlier_summary = cases[("outlier_detection", "rt_count_threshold")]["last_output"]
        dbscan_summary = cases[("dbscan_clustering", "rt_core_flags")]["last_output"]
        self.assertEqual(outlier_summary["neighbor_row_count"], 0)
        self.assertEqual(dbscan_summary["neighbor_row_count"], 0)
        self.assertEqual(outlier_summary["native_summary_row_count"], outlier_summary["point_count"])
        self.assertEqual(dbscan_summary["native_summary_row_count"], dbscan_summary["point_count"])

    def test_report_records_rtx_ready_boundary_not_speedup_claim(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "RTX-ready phase profiler",
            "No RTX speedup claim",
            "GTX 1070 timing is not RT-core timing",
            "whole-call results only",
            "classification_change: false",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
