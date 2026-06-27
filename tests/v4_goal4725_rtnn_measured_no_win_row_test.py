from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROW = ROOT / "future" / "v4" / "evidence" / "v4_goal4725_rtnn_measured_no_win_row_2026-06-26.json"
SOURCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4660_rtnn_ranked_summary_20260625" / "summary.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4725_rtnn_measured_no_win_row_2026-06-26.md"
CALL_FOR_REVIEW = (
    ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_goal4725_rtnn_measured_no_win_row_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT / "future" / "v4" / "reviews" / "v4_goal4725_rtnn_measured_no_win_row_review_debt_2026-06-26.md"
)


class V4Goal4725RtnnMeasuredNoWinRowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.row = json.loads(ROW.read_text(encoding="utf-8"))
        self.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.matrix_row = self.row["matrix_row"]

    def test_row_closes_rtnn_as_measured_no_win(self) -> None:
        self.assertEqual("rtnn", self.matrix_row["app"])
        self.assertEqual("closed_measured_no_win_row", self.matrix_row["row_status"])
        self.assertEqual("measured_no_win_candidate", self.matrix_row["goal4723_row_class"])
        self.assertEqual(
            "measured_no_win_deferred_from_v4_high_performance_release_path",
            self.matrix_row["formal_conclusion"],
        )
        self.assertTrue(self.matrix_row["contributes_to_complete_10_app_matrix"])
        self.assertFalse(self.matrix_row["contributes_to_formal_high_performance_v4"])

    def test_source_decision_matches_goal4725_conclusion(self) -> None:
        decision = self.source["decision"]
        self.assertEqual("rtnn_candidate_does_not_move_app_level_bar", decision["label"])
        self.assertFalse(decision["may_count_as_formal_high_performance_v4_evidence"])
        self.assertFalse(decision["may_trigger_full_all_app_rerun"])

    def test_serious_scales_are_parity_or_slower(self) -> None:
        rows = {row["point_count"]: row for row in self.matrix_row["all_measured_scales"]}
        self.assertEqual([262144, 1048576], self.matrix_row["serious_scale_points"])
        self.assertLess(rows[262144]["speedup_hot_median_v4_over_v2_14"], 1.01)
        self.assertLess(rows[262144]["speedup_hot_median_v4_over_v3_0_2"], 1.01)
        self.assertLess(rows[1048576]["speedup_hot_median_v4_over_v2_14"], 1.0)
        self.assertLess(rows[1048576]["speedup_hot_median_v4_over_v3_0_2"], 1.0)

    def test_runtime_executed_and_correctness_validated_without_host_hot_path(self) -> None:
        for scale in self.matrix_row["all_measured_scales"]:
            with self.subTest(point_count=scale["point_count"]):
                self.assertTrue(scale["validation_passed"])
                self.assertTrue(scale["runtime_executed"])
                self.assertFalse(scale["hot_path_host_materialization"])

    def test_denominator_boundary_is_visible(self) -> None:
        boundary = self.matrix_row["denominator_boundary"]
        self.assertFalse(boundary["old_denominator_exact_same_runner"])
        self.assertIn("closest old-version", boundary["allowed_wording"])
        self.assertIn("forbidden", "forbidden_wording")
        self.assertIn("exact same runner", boundary["forbidden_wording"])

    def test_claim_boundary_blocks_release_and_speed_claims(self) -> None:
        boundary = self.row["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "public_speedup_claim_authorized",
            "whole_app_high_performance_claim_authorized",
            "rtnn_speedup_claim_authorized",
            "broad_v4_over_v2_14_claim_authorized",
            "pod_authorized_by_goal4725",
        ):
            self.assertFalse(boundary[key], key)

    def test_report_and_review_debt_exist(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, REVIEW_DEBT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Non-Authorization", text)
            self.assertIn("final V4 tag", text)

    def test_next_goal_is_robot_collision(self) -> None:
        self.assertEqual("Goal4726", self.row["next_goal"]["id"])
        self.assertIn("robot_collision", self.row["next_goal"]["title"])


if __name__ == "__main__":
    unittest.main()
