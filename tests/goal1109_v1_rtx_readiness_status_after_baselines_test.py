from __future__ import annotations

import unittest

from scripts.goal1109_v1_rtx_readiness_status_after_baselines import build_status
from scripts.goal1109_v1_rtx_readiness_status_after_baselines import to_markdown


class Goal1109V1RtxReadinessStatusAfterBaselinesTest(unittest.TestCase):
    def test_status_reflects_goal1146_promotion(self) -> None:
        payload = build_status()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 3)
        self.assertEqual(payload["summary"]["engineering_comparison_ready_count"], 1)
        self.assertEqual(payload["summary"]["public_wording_reviewed_count"], 2)
        self.assertEqual(payload["summary"]["non_cloud_ready_count"], 0)
        self.assertEqual(payload["summary"]["public_speedup_claim_authorized_count"], 2)
        by_app = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(
            by_app["facility_knn_assignment"]["status"],
            "public_wording_reviewed",
        )
        self.assertEqual(
            by_app["barnes_hut_force_app"]["status"],
            "public_wording_reviewed",
        )
        self.assertEqual(
            by_app["robot_collision_screening"]["status"],
            "engineering_review_ready_needs_public_wording_review",
        )
        self.assertIn("goal1142_current_source_rtx_rerun_intake", " ".join(by_app["facility_knn_assignment"]["latest_evidence"]))
        self.assertIn("robot_prepared_pose_flags_64m_timing_goal1142", " ".join(by_app["robot_collision_screening"]["latest_evidence"]))
        self.assertIn("barnes_hut_depth8_20m_timing", " ".join(by_app["barnes_hut_force_app"]["latest_evidence"]))
        self.assertIn("goal1146_two_ai_public_wording_promotion_consensus", " ".join(by_app["facility_knn_assignment"]["latest_evidence"]))

    def test_rows_keep_no_public_claim_boundary_and_next_actions(self) -> None:
        payload = build_status()

        by_app = {row["app"]: row for row in payload["rows"]}
        self.assertTrue(by_app["facility_knn_assignment"]["public_speedup_claim_authorized"])
        self.assertTrue(by_app["barnes_hut_force_app"]["public_speedup_claim_authorized"])
        self.assertFalse(by_app["robot_collision_screening"]["public_speedup_claim_authorized"])
        for row in payload["rows"]:
            self.assertIn("next_action", row)
        self.assertIn("Robot remains engineering-ready but blocked", payload["boundary"])
        self.assertIn("does not authorize release", payload["boundary"])

    def test_markdown_mentions_supersession_and_ratios(self) -> None:
        markdown = to_markdown(build_status())

        self.assertIn("Supersedes:", markdown)
        self.assertIn("80.60x vs CPU oracle", markdown)
        self.assertIn("64M-pose timing crossed", markdown)
        self.assertIn("Goal1146", markdown)
        self.assertIn("240.56x vs Embree", markdown)
        self.assertIn("reviewed narrow prepared coverage-threshold", markdown)
        self.assertIn("reviewed narrow prepared node-coverage", markdown)
        self.assertIn("blocked for public speedup wording", markdown)


if __name__ == "__main__":
    unittest.main()
