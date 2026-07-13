from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5314_water_bg_corrected_comparison_summary.json"
)


class Goal5314XhdWaterBgCorrectedComparisonSummaryTest(unittest.TestCase):
    def test_paper_config_author_denominator_supersedes_default_for_paper_log(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5314.water_bg_corrected_comparison_summary.v1",
        )
        decision = payload["denominator_decision"]
        self.assertEqual(
            decision["paper_config_author_denominator"],
            "author_hd_exec_full_public_wkt_n_points_cell_8",
        )
        self.assertTrue(decision["supersedes_default_author_denominator_for_paper_log_comparison"])
        self.assertTrue(decision["default_author_rerun_retained_as_config_sensitivity_evidence"])

        author = payload["author"]
        self.assertEqual(author["paper_log"]["num_points_per_cell"], 8)
        self.assertEqual(author["default_rerun_n_points_cell_15"]["num_points_per_cell"], 15)
        self.assertEqual(author["paper_config_rerun_n_points_cell_8"]["num_points_per_cell"], 8)
        self.assertFalse(author["default_rerun_n_points_cell_15"]["matches_paper_log"])
        self.assertTrue(author["paper_config_rerun_n_points_cell_8"]["matches_paper_log"])

    def test_rtdl_exact_witness_uses_declared_float_boundary(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

        exact = payload["rtdl"]["exact_witness"]
        self.assertTrue(exact["correctness_gate"])
        self.assertTrue(exact["per_source_witness_exact"])
        self.assertAlmostEqual(exact["hd_result_float64"], 0.8964380566690101)
        self.assertAlmostEqual(exact["abs_diff_vs_author_paper_config"], 1.305780185645311e-06)

        tolerance = payload["tolerance_boundary"]
        self.assertEqual(tolerance["author_numeric_type"], "float32")
        self.assertEqual(tolerance["rtdl_reported_distance_type"], "float64")
        self.assertFalse(tolerance["matches_at_1e_6"])
        self.assertTrue(tolerance["matches_at_2e_6"])
        self.assertTrue(tolerance["exact_float32_match"])

        decision = payload["decision"]
        self.assertTrue(decision["water_bg_full_public_author_paper_config_value_reproduced"])
        self.assertTrue(decision["water_bg_full_public_rtdl_exact_witness_matches_author_float32_with_declared_tolerance"])
        self.assertFalse(decision["water_bg_full_public_rtdl_exact_witness_exact_float64_equals_author_float32"])

    def test_claim_boundary_remains_limited(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertFalse(payload["decision"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(payload["decision"]["figure5_reproduction_claimed"])
        self.assertFalse(payload["decision"]["performance_ratio_claimed"])

        forbidden = "\n".join(payload["claim_boundary"]["forbidden"])
        self.assertIn("Exact paper WKT files", forbidden)
        self.assertIn("Figure 5", forbidden)
        self.assertIn("Performance parity", forbidden)
        self.assertIn("identical numeric precision", forbidden)
        self.assertIn("n_points_cell=15", forbidden)


if __name__ == "__main__":
    unittest.main()
