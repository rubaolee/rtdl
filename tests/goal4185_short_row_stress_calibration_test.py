from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4185_short_row_stress_calibration_rtx4000ada"
REPORT = ROOT / "docs" / "reports" / "goal4185_short_row_stress_calibration_rtx4000ada_2026-06-09.md"


def _load(name: str):
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal4185ShortRowStressCalibrationTest(unittest.TestCase):
    def test_stress_artifacts_are_present_and_parseable(self) -> None:
        summary = _load("summary.json")

        self.assertEqual(summary["schema"], "rtdl.goal4185.short_row_stress.v1")
        rows = {row["name"]: row for row in summary["rows"]}
        self.assertEqual(
            set(rows),
            {
                "hausdorff_xhd_stress",
                "contact_manifold_stress",
                "librts_spatial_index_stress",
                "rtnn_stress",
                "triangle_counting_stress",
            },
        )
        for name, row in rows.items():
            self.assertTrue(row["json_parseable"], name)
            self.assertIsNone(row["error"], name)
            self.assertGreater(row["stdout_bytes"], 0, name)
            self.assertEqual(row["stderr_bytes"], 0, name)

    def test_second_level_rows_and_measurement_gaps_are_classified(self) -> None:
        librts = _load("librts_spatial_index_stress.stdout.json")
        triangle = _load("triangle_counting_stress.stdout.json")
        hausdorff = _load("hausdorff_xhd_stress.stdout.json")
        contact = _load("contact_manifold_stress.stdout.json")
        rtnn = _load("rtnn_stress.stdout.json")

        self.assertGreater(librts["run_phases"]["query_total_sec"], 1.0)
        self.assertGreater(triangle["timing_ms"]["run_backend"] / 1000.0, 1.0)

        self.assertGreater(hausdorff["repeat_protocol"]["measured_query_total_sec"], 1.0)
        self.assertLess(contact["native_collect_elapsed_sec"], 0.01)
        self.assertEqual(rtnn["runner_payload"]["repeat"], 5000)
        self.assertGreater(sum(rtnn["runner_payload"]["elapsed_runs_sec"]), 0.8)
        self.assertLess(sum(rtnn["runner_payload"]["elapsed_runs_sec"]), 1.0)
        self.assertLess(rtnn["runner_payload"]["elapsed_median_sec"], 0.001)

    def test_report_does_not_overclaim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("measurement-adequacy evidence", text)
        self.assertIn("not a public speedup report", text)
        self.assertIn("Not claim-grade yet", text)
        self.assertIn("Adequate second-level repeated-query evidence", text)
        self.assertIn("does not authorize public performance claims", text)


if __name__ == "__main__":
    unittest.main()
