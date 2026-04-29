from __future__ import annotations

import unittest

from scripts.goal1109_v1_rtx_readiness_status_after_baselines import build_status
from scripts.goal1109_v1_rtx_readiness_status_after_baselines import to_markdown


class Goal1109V1RtxReadinessStatusAfterBaselinesTest(unittest.TestCase):
    def test_status_promotes_three_apps_to_engineering_review_ready(self) -> None:
        payload = build_status()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 3)
        self.assertEqual(payload["summary"]["engineering_comparison_ready_count"], 3)
        self.assertEqual(payload["summary"]["non_cloud_ready_count"], 0)
        self.assertEqual(payload["summary"]["public_speedup_claim_authorized_count"], 0)
        by_app = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(
            by_app["facility_knn_assignment"]["status"],
            "engineering_review_ready_needs_public_wording_review",
        )
        self.assertEqual(
            by_app["barnes_hut_force_app"]["status"],
            "engineering_review_ready_needs_public_wording_review",
        )
        self.assertEqual(
            by_app["robot_collision_screening"]["status"],
            "engineering_review_ready_needs_public_wording_review",
        )
        self.assertIn("goal1121_two_ai_consensus", " ".join(by_app["facility_knn_assignment"]["latest_evidence"]))
        self.assertIn("robot_prepared_pose_flags_64m_timing_goal1121", " ".join(by_app["robot_collision_screening"]["latest_evidence"]))
        self.assertIn("barnes_hut_depth8_20m_timing", " ".join(by_app["barnes_hut_force_app"]["latest_evidence"]))

    def test_rows_keep_no_public_claim_boundary_and_next_actions(self) -> None:
        payload = build_status()

        for row in payload["rows"]:
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertIn("next_action", row)
        self.assertIn("public wording review remains required", payload["boundary"])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_markdown_mentions_supersession_and_ratios(self) -> None:
        markdown = to_markdown(build_status())

        self.assertIn("Supersedes:", markdown)
        self.assertIn("87.24x vs CPU oracle", markdown)
        self.assertIn("64M-pose timing crossed", markdown)
        self.assertIn("222.19x vs Embree", markdown)
        self.assertIn("public wording review remains required", markdown)


if __name__ == "__main__":
    unittest.main()
