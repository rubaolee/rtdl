from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts import goal2637_build_perf_diff_table as builder


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "docs" / "reports" / "goal2637_all_benchmark_perf_diffs_2026-05-27.json"
REPORT_PATH = ROOT / "docs" / "reports" / "goal2637_all_benchmark_perf_diffs_2026-05-27.md"


class Goal2637AllBenchmarkPerfDiffsTest(unittest.TestCase):
    def test_machine_readable_table_matches_measured_artifacts(self) -> None:
        generated = builder.build_payload()
        recorded = json.loads(JSON_PATH.read_text(encoding="utf-8"))

        self.assertEqual(recorded, generated)

    def test_standard_and_strengthened_rows_are_complete_and_positive(self) -> None:
        payload = builder.build_payload()

        self.assertEqual(payload["benchmark_app_count"], 10)
        self.assertEqual(payload["standard_summary"]["row_count"], 11)
        self.assertEqual(payload["standard_summary"]["optix_win_count"], 11)
        self.assertEqual(payload["strengthened_summary"]["row_count"], 13)
        self.assertEqual(payload["strengthened_summary"]["optix_win_count"], 13)
        self.assertEqual(payload["strengthened_stress_summary"]["row_count"], 16)
        self.assertEqual(payload["strengthened_stress_summary"]["optix_win_count"], 16)
        self.assertGreater(payload["standard_summary"]["geomean_speedup"], 32.0)
        self.assertGreater(payload["strengthened_summary"]["geomean_speedup"], 16.0)
        self.assertGreater(payload["strengthened_stress_summary"]["geomean_speedup"], 21.0)

    def test_strengthened_rows_cover_the_former_weak_apps(self) -> None:
        payload = builder.build_payload()
        strengthened_apps = {row["app_id"] for row in payload["strengthened_rows"]}
        stress_apps = {row["app_id"] for row in payload["strengthened_stress_rows"]}

        self.assertEqual(
            strengthened_apps,
            {"hausdorff_xhd", "spatial_rayjoin", "rtnn", "barnes_hut", "triangle_counting"},
        )
        self.assertEqual(stress_apps, strengthened_apps)

    def test_report_points_to_machine_readable_artifact_and_boundary(self) -> None:
        text = REPORT_PATH.read_text(encoding="utf-8")

        self.assertIn("goal2637_all_benchmark_perf_diffs_2026-05-27.json", text)
        self.assertIn("not public speedup", text)
        self.assertIn("13 additional strengthened rows", text)
        self.assertIn("16 stress rows", text)


if __name__ == "__main__":
    unittest.main()
