from __future__ import annotations

import unittest

from scripts.goal1208_public_wording_decision_after_goal1206 import build_packet, to_markdown


class Goal1208PublicWordingDecisionAfterGoal1206Test(unittest.TestCase):
    def test_goal1206_decisions_are_bounded(self):
        payload = build_packet()
        by_app = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(by_app["road_hazard_screening"]["status_to_apply"], "public_wording_reviewed")
        self.assertEqual(by_app["database_analytics"]["status_to_apply"], "public_wording_blocked")
        self.assertEqual(by_app["polygon_set_jaccard"]["status_to_apply"], "public_correctness_ready_speedup_blocked")
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_database_below_threshold_not_promoted(self):
        payload = build_packet()
        row = next(row for row in payload["rows"] if row["app"] == "database_analytics")
        self.assertLess(row["raw_ratio_embree_over_optix"], payload["min_public_ratio"])
        self.assertIn("below the 1.2x public speedup threshold", row["candidate_public_wording"])

    def test_markdown_preserves_no_release_boundary(self):
        text = to_markdown(build_packet())
        self.assertIn("does not edit public docs", text)
        self.assertIn("does not", text)
        self.assertIn("whole-app speedup", text)

    def test_road_hazard_wording_contains_measured_values(self):
        payload = build_packet()
        row = next(row for row in payload["rows"] if row["app"] == "road_hazard_screening")
        self.assertIn("0.230652 s", row["candidate_public_wording"])
        self.assertIn("3.53x", row["candidate_public_wording"])
        self.assertIn("40k copies", row["candidate_public_wording"])
        self.assertEqual(payload["public_speedup_claims_applied_by_this_packet"], 0)


if __name__ == "__main__":
    unittest.main()
