from __future__ import annotations

import unittest

from scripts.goal1109_v1_rtx_readiness_status_after_baselines import build_status
from scripts.goal1109_v1_rtx_readiness_status_after_baselines import to_markdown


class Goal1109V1RtxReadinessStatusAfterBaselinesTest(unittest.TestCase):
    def test_status_promotes_facility_and_barnes_to_engineering_comparison_ready(self) -> None:
        payload = build_status()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 3)
        self.assertEqual(payload["summary"]["engineering_comparison_ready_count"], 3)
        self.assertEqual(payload["summary"]["non_cloud_ready_count"], 0)
        self.assertEqual(payload["summary"]["public_speedup_claim_authorized_count"], 0)
        by_app = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(
            by_app["facility_knn_assignment"]["status"],
            "engineering_comparison_ready_needs_same_source_rtx_rerun_and_public_wording_review",
        )
        self.assertEqual(
            by_app["barnes_hut_force_app"]["status"],
            "engineering_comparison_ready_needs_same_source_rtx_rerun_and_public_wording_review",
        )
        self.assertEqual(
            by_app["robot_collision_screening"]["status"],
            "engineering_comparison_ready_needs_same_source_rtx_rerun_and_public_wording_review",
        )

    def test_rows_keep_no_public_claim_boundary_and_next_actions(self) -> None:
        payload = build_status()

        for row in payload["rows"]:
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertIn("next_action", row)
        self.assertIn("same-source RTX reruns", payload["boundary"])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_markdown_mentions_supersession_and_ratios(self) -> None:
        markdown = to_markdown(build_status())

        self.assertIn("Supersedes:", markdown)
        self.assertIn("66.61x vs CPU oracle", markdown)
        self.assertIn("Robot non-OptiX baseline complete", markdown)
        self.assertIn("231.82x vs Embree", markdown)
        self.assertIn("same-source RTX reruns", markdown)


if __name__ == "__main__":
    unittest.main()
