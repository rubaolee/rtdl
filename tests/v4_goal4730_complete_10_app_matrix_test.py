from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "future" / "v4" / "evidence" / "v4_goal4730_complete_10_app_matrix_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4730_complete_10_app_matrix_2026-06-26.md"
CALL_FOR_REVIEW = (
    ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_goal4730_complete_10_app_matrix_2026-06-26.md"
)
REVIEW_DEBT = ROOT / "future" / "v4" / "reviews" / "v4_goal4730_complete_10_app_matrix_review_debt_2026-06-26.md"


EXPECTED_APPS = {
    "rt_dbscan",
    "raydb_style",
    "triangle_counting",
    "librts_spatial_index",
    "hausdorff_xhd",
    "rtnn",
    "robot_collision",
    "contact_manifold",
    "spatial_rayjoin",
    "barnes_hut",
}


class V4Goal4730Complete10AppMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.rows = {row["app"]: row for row in self.matrix["rows"]}

    def test_matrix_has_all_10_apps_exactly_once(self) -> None:
        self.assertEqual(EXPECTED_APPS, set(self.rows))
        self.assertEqual(10, self.matrix["summary"]["app_count"])
        self.assertEqual(10, len(self.matrix["rows"]))
        self.assertTrue(self.matrix["summary"]["complete_matrix_assembled"])

    def test_release_gate_blocks_formal_high_performance(self) -> None:
        summary = self.matrix["summary"]
        self.assertFalse(summary["formal_high_performance_v4_supported"])
        self.assertTrue(summary["bounded_operator_v4_only"])
        self.assertFalse(summary["final_tag_authorized"])
        self.assertFalse(summary["public_broad_speedup_claim_authorized"])
        self.assertEqual("fail_formal_high_performance_release", self.matrix["release_gate"]["status"])

    def test_only_one_true_full_app_v4_win_candidate(self) -> None:
        winners = [
            row["app"]
            for row in self.matrix["rows"]
            if row["contributes_to_formal_high_performance_v4"]
        ]
        self.assertEqual(["hausdorff_xhd"], winners)
        self.assertEqual(1, self.matrix["summary"]["true_full_app_v4_candidate_win_count"])

    def test_known_regressions_and_no_wins_are_visible(self) -> None:
        self.assertLess(self.rows["raydb_style"]["v4_vs_v2_14_hot"], 0.98)
        self.assertLess(self.rows["triangle_counting"]["v4_vs_v3_0_2_hot"], 0.98)
        self.assertLess(self.rows["rtnn"]["v4_vs_v2_14_hot_serious_1048576"], 1.0)
        self.assertEqual(
            "closed_partial_operator_no_go_for_current_high_performance_path",
            self.rows["robot_collision"]["row_status"],
        )
        self.assertEqual("closed_no_current_v4_app_route_blocker", self.rows["spatial_rayjoin"]["row_status"])
        self.assertEqual("closed_deferred_subprobe_not_complete_app_route", self.rows["barnes_hut"]["row_status"])

    def test_aggregate_and_hausdorff_outliers_do_not_authorize_geomean_headline(self) -> None:
        self.assertGreater(self.rows["hausdorff_xhd"]["v4_vs_v2_14_hot"], 1000.0)
        self.assertGreater(self.rows["barnes_hut"]["aggregate_frontier_v4_full_hot_over_v2_14"], 100.0)
        boundary = self.matrix["claim_boundary"]
        self.assertFalse(boundary["geomean_headline_authorized"])
        self.assertFalse(boundary["all_benchmark_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_high_performance_claim_authorized"])

    def test_claim_boundary_blocks_release_and_hidden_fallback(self) -> None:
        boundary = self.matrix["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "public_speedup_claim_authorized",
            "whole_app_high_performance_claim_authorized",
            "all_benchmark_speedup_claim_authorized",
            "geomean_headline_authorized",
            "app_specific_native_kernel_authorized",
            "hidden_v2_v3_fallback_authorized",
            "pod_authorized_by_goal4730",
        ):
            self.assertFalse(boundary[key], key)

    def test_report_and_review_debt_exist(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, REVIEW_DEBT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Non-Authorization", text)
            self.assertIn("final V4 tag", text)

    def test_next_goal_is_release_decision_not_public_tag(self) -> None:
        self.assertEqual("Goal4731", self.matrix["next_goal"]["id"])
        self.assertIn("release decision", self.matrix["next_goal"]["title"])
        self.assertIn("continue high-performance engineering", self.matrix["next_goal"]["reason"])


if __name__ == "__main__":
    unittest.main()
