from __future__ import annotations

import unittest

from scripts.goal1123_public_wording_review_after_goal1121 import build_packet
from scripts.goal1123_public_wording_review_after_goal1121 import to_markdown


class Goal1123PublicWordingReviewAfterGoal1121Test(unittest.TestCase):
    def test_packet_proposes_two_reviewed_rows_and_keeps_robot_blocked(self) -> None:
        payload = build_packet()
        by_app = {row["app"]: row for row in payload["rows"]}

        self.assertEqual(payload["candidate_reviewed_count"], 2)
        self.assertEqual(payload["blocked_count"], 1)
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertEqual(by_app["facility_knn_assignment"]["status_to_apply"], "public_wording_reviewed")
        self.assertEqual(by_app["barnes_hut_force_app"]["status_to_apply"], "public_wording_reviewed")
        self.assertEqual(by_app["robot_collision_screening"]["status_to_apply"], "public_wording_blocked")
        self.assertIn("same-scale", by_app["robot_collision_screening"]["boundary"])

    def test_ratios_and_timing_floor_are_current_goal1142_values(self) -> None:
        payload = build_packet()
        by_app = {row["app"]: row for row in payload["rows"]}

        self.assertGreaterEqual(by_app["facility_knn_assignment"]["rtx_median_query_sec"], 0.1)
        self.assertAlmostEqual(by_app["facility_knn_assignment"]["fastest_baseline_ratio"], 80.60, places=2)
        self.assertGreaterEqual(by_app["robot_collision_screening"]["rtx_median_query_sec"], 0.1)
        self.assertGreater(by_app["robot_collision_screening"]["diagnostic_normalized_ratio_not_public"], 500.0)
        self.assertAlmostEqual(by_app["barnes_hut_force_app"]["fastest_baseline_ratio"], 240.56, places=2)

    def test_markdown_keeps_boundaries_visible(self) -> None:
        markdown = to_markdown(build_packet())

        self.assertIn("not itself edit public docs", markdown)
        self.assertIn("whole-app speedup", markdown)
        self.assertIn("No public RTX speedup wording is authorized for robot_collision_screening yet.", markdown)
        self.assertIn("same-scale or accepted normalized baseline review", markdown)


if __name__ == "__main__":
    unittest.main()
