from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELTA = ROOT / "future" / "v4" / "evidence" / "v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.md"
REVIEW_DEBT = ROOT / "future" / "v4" / "reviews" / "v4_goal4770_rt_barneshut_release_packet_delta_review_debt_2026-06-26.md"


class V4Goal4770RtBarnesHutReleasePacketDeltaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.delta = json.loads(DELTA.read_text(encoding="utf-8"))

    def test_goal4770_delta_preserves_history_and_claim_boundaries(self) -> None:
        self.assertEqual("Goal4770", self.delta["goal"])
        self.assertEqual("barnes_hut", self.delta["app"])
        self.assertTrue(self.delta["current_matrix_policy"]["goal4756_matrix_is_historical"])
        self.assertTrue(self.delta["current_matrix_policy"]["do_not_rewrite_goal4756_rows"])
        self.assertFalse(self.delta["claim_boundary"]["release_authorized"])
        self.assertFalse(self.delta["claim_boundary"]["paper_reproduction_claim_authorized"])
        self.assertFalse(self.delta["claim_boundary"]["no_copy_tree_build_claim_authorized"])

    def test_native_author_route_is_checksum_valid_but_bounded(self) -> None:
        route = self.delta["native_author_route_10m"]
        self.assertTrue(route["checksum_valid"])
        self.assertTrue(route["rt_core_execution"])
        self.assertFalse(route["host_fallback_used"])
        self.assertTrue(route["input_columns_downloaded_for_tree_build"])
        self.assertTrue(route["custom_primitive_control_geometry"])
        self.assertFalse(route["literal_author_triangle_geometry"])
        self.assertLess(route["checksum_relative_error"], 1e-5)

    def test_author_phase_comparison_supports_corrected_reading(self) -> None:
        ratios = self.delta["ratios"]
        self.assertGreater(ratios["author_sort_over_rtdl_sort"], 1.10)
        self.assertGreater(ratios["author_sort_tree_over_rtdl_preprocessing"], 1.20)
        self.assertGreater(ratios["author_total_program_over_rtdl_execution_plus_input_download"], 1.30)
        self.assertGreater(ratios["author_rt_force_over_rtdl_rt_force"], 1.20)

    def test_report_and_review_debt_carry_goal_delta(self) -> None:
        for path in (REPORT, REVIEW_DEBT):
            text = path.read_text(encoding="utf-8")
            self.assertIn("Goal4770", text)
            self.assertIn("RT-BarnesHut", text)
            self.assertIn("paper", text.lower())

    def test_public_docs_carry_clean_barnes_hut_boundary(self) -> None:
        for path in (
            ROOT / "docs" / "app_level_benchmark_summary.md",
            ROOT / "docs" / "current_v4_status.md",
            ROOT / "README.md",
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIn("RT-BarnesHut", text)
            self.assertIn("paper", text.lower())
            self.assertNotIn("full workflow author loss", text)


if __name__ == "__main__":
    unittest.main()
