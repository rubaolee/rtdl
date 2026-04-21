from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from examples import rtdl_service_coverage_gaps


ROOT = Path(__file__).resolve().parents[1]


class Goal724ServiceCoverageEmbreeSummaryTest(unittest.TestCase):
    def test_service_coverage_app_exposes_embree_gap_summary(self):
        text = (ROOT / "examples/rtdl_service_coverage_gaps.py").read_text(encoding="utf-8")
        self.assertIn("embree_summary_mode", text)
        self.assertIn("gap_summary", text)
        self.assertIn("fixed_radius_count_threshold_2d_embree", text)

    def test_gap_summary_matches_row_mode_for_uncovered_households(self):
        try:
            rows_result = rtdl_service_coverage_gaps.run_case("embree", copies=8)
            summary_result = rtdl_service_coverage_gaps.run_case(
                "embree",
                copies=8,
                embree_summary_mode="gap_summary",
            )
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")

        self.assertEqual(summary_result["uncovered_household_ids"], rows_result["uncovered_household_ids"])
        self.assertEqual(summary_result["covered_household_count"], rows_result["covered_household_count"])
        self.assertEqual(summary_result["rows"], [])
        self.assertEqual(summary_result["nearby_clinics_by_household"], {})
        self.assertEqual(summary_result["clinic_loads"], {})
        self.assertEqual(len(summary_result["coverage_summary_rows"]), summary_result["household_count"])
        self.assertEqual(summary_result["embree_summary_mode"], "gap_summary")
        self.assertIn("covered/uncovered households only", summary_result["summary_boundary"])


if __name__ == "__main__":
    unittest.main()
