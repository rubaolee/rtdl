from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3578_raydb_grouped_i64_mode_reprobe_2026-06-06.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3578_raydb_grouped_i64_mode_reprobe_current_a5000"
MODES = ("count", "sum", "min", "max", "stats", "avg_as_sum_count")


class Goal3578RaydbGroupedI64ModeReprobeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifacts = {
            mode: json.loads((ARTIFACT_DIR / f"{mode}.json").read_text(encoding="utf-8"))
            for mode in MODES
        }

    def test_report_states_diagnostic_scope_and_boundary(self) -> None:
        self.assertIn("diagnostic follow-up to Goal3575", self.report)
        self.assertIn("not a new speedup claim", self.report)
        self.assertIn("classified as integration", self.report)
        self.assertIn("coverage only", self.report)
        for boundary in (
            "public speedup claims",
            "whole-app acceleration claims",
            "broad RT-core speedup claims",
            "true zero-copy claims",
            "paper reproduction claims",
            "package-install claims",
        ):
            self.assertIn(boundary, self.report)

    def test_all_modes_match_cpu_reference_with_one_launch(self) -> None:
        for mode, payload in self.artifacts.items():
            with self.subTest(mode=mode):
                self.assertEqual(payload["backend"], "optix_partner_resident_experimental")
                self.assertEqual(payload["mode"], mode)
                self.assertEqual(payload["row_count"], 960000)
                self.assertIs(payload["matches_cpu_reference"], True)
                self.assertEqual(payload["metadata"]["native_launch_count"], 1)
                self.assertEqual(payload["metadata"]["timings"]["query_repeat"], 5000)
                self.assertEqual(payload["metadata"]["timings"]["query_warmup"], 3)

    def test_count_sum_and_stats_are_in_long_run_steady_state_band(self) -> None:
        for mode in MODES:
            with self.subTest(mode=mode):
                median = self.artifacts[mode]["metadata"]["timings"]["query_median_sec"]
                self.assertLess(median, 0.001)
        self.assertLess(
            self.artifacts["count"]["metadata"]["timings"]["query_median_sec"],
            self.artifacts["stats"]["metadata"]["timings"]["query_median_sec"],
        )
        self.assertLess(
            self.artifacts["sum"]["metadata"]["timings"]["query_median_sec"],
            0.0006,
        )


if __name__ == "__main__":
    unittest.main()
