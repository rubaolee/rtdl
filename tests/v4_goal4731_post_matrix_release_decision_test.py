from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "future" / "v4" / "evidence" / "v4_goal4731_post_matrix_release_decision_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4731_post_matrix_release_decision_2026-06-26.md"
CALL_FOR_REVIEW = (
    ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_goal4731_post_matrix_release_decision_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT / "future" / "v4" / "reviews" / "v4_goal4731_post_matrix_release_decision_review_debt_2026-06-26.md"
)


class V4Goal4731PostMatrixReleaseDecisionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_decision_blocks_tag_and_selects_engineering(self) -> None:
        decision = self.decision["decision"]
        self.assertFalse(decision["formal_high_performance_v4_supported_now"])
        self.assertTrue(decision["bounded_operator_v4_release_possible_but_not_user_mandate"])
        self.assertFalse(decision["public_tag_authorized_now"])
        self.assertEqual("continue_high_performance_engineering", decision["selected_path"])

    def test_next_goals_are_ordered_measured_blockers_first(self) -> None:
        goals = self.decision["next_goals"]
        self.assertEqual(["Goal4732", "Goal4733", "Goal4734", "Goal4735"], [goal["id"] for goal in goals])
        self.assertEqual("raydb_style", goals[0]["target_app"])
        self.assertEqual("triangle_counting", goals[1]["target_app"])
        self.assertEqual("rt_dbscan", goals[2]["target_app"])
        self.assertEqual("spatial_rayjoin_or_barnes_hut", goals[3]["target_app"])
        self.assertIn("below the 0.98 no-regression floor", goals[0]["current_fact"])

    def test_non_goals_prevent_process_churn_and_overclaiming(self) -> None:
        non_goals = set(self.decision["non_goals"])
        self.assertIn("no docs-only milestone as progress", non_goals)
        self.assertIn("no all-app rerun before a named blocker moves", non_goals)
        self.assertIn("no geomean headline", non_goals)
        self.assertIn("no app-specific native kernels", non_goals)
        self.assertIn("no public tag without external release authorization", non_goals)

    def test_claim_boundary_blocks_release_pod_and_speed_claims(self) -> None:
        boundary = self.decision["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "public_speedup_claim_authorized",
            "whole_app_high_performance_claim_authorized",
            "all_benchmark_speedup_claim_authorized",
            "pod_authorized_by_goal4731",
        ):
            self.assertFalse(boundary[key], key)

    def test_report_and_review_debt_exist(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, REVIEW_DEBT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Non-Authorization", text)
            self.assertIn("final V4 tag", text)


if __name__ == "__main__":
    unittest.main()
