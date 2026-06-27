from __future__ import annotations

import unittest
from pathlib import Path

from scripts.v4_goal4754_analyze_final_rt_core_matrix import analyze


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "future" / "v4" / "evidence" / "v4_goal4756_serious_all30_generated_spatial_2026-06-26"


class V4Goal4754FinalRtCoreMatrixAnalysisTest(unittest.TestCase):
    def test_analysis_has_ten_complete_app_rows(self) -> None:
        payload = analyze(MATRIX)

        self.assertEqual("analysis_complete_not_release_authorization", payload["status"])
        self.assertEqual(10, payload["summary"]["app_count"])
        self.assertTrue(payload["summary"]["all_rows_have_v2_v3_v4"])
        self.assertFalse(payload["summary"]["embree_primary_denominator_used"])

    def test_every_app_row_has_numeric_hot_values_and_classification(self) -> None:
        payload = analyze(MATRIX)
        for row in payload["app_rows"]:
            with self.subTest(app=row["app"]):
                self.assertIsInstance(row["v2_14_hot_sec"], float)
                self.assertIsInstance(row["v3_0_2_hot_sec"], float)
                self.assertIsInstance(row["v4_0_hot_sec"], float)
                self.assertIsInstance(row["v4_over_v2_14_hot_speedup"], float)
                self.assertIn(
                    row["claim_class"],
                    {
                        "material_v4_over_v2_candidate",
                        "parity_or_control",
                        "v4_regression_vs_v2",
                        "v4_regression_vs_v3",
                        "wall_win_hot_replay_regression",
                    },
                )

    def test_claim_boundary_blocks_release(self) -> None:
        payload = analyze(MATRIX)
        boundary = payload["claim_boundary"]

        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speed_claim_authorized"])
        self.assertFalse(boundary["all_benchmark_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
