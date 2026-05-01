from __future__ import annotations

import unittest

from scripts.goal1099_post_pod_readiness_status_refresh import build_status
from scripts.goal1099_post_pod_readiness_status_refresh import to_markdown


class Goal1099PostPodReadinessStatusRefreshTest(unittest.TestCase):
    def test_status_refresh_moves_two_rows_from_pod_ready_to_evidence_intaked(self) -> None:
        status = build_status()

        self.assertTrue(status["valid"])
        self.assertEqual(status["summary"]["row_count"], 3)
        self.assertEqual(status["summary"]["pod_ready_count"], 0)
        self.assertEqual(status["summary"]["evidence_intaked_count"], 2)
        self.assertEqual(status["summary"]["non_cloud_ready_count"], 1)
        self.assertEqual(status["summary"]["blocked_count"], 0)
        self.assertEqual(status["summary"]["public_speedup_claim_authorized_count"], 0)

    def test_facility_and_barnes_rows_require_baseline_and_public_wording_review(self) -> None:
        rows = {row["app"]: row for row in build_status()["rows"]}

        self.assertEqual(
            rows["facility_knn_assignment"]["status"],
            "rtx_pod_evidence_intaked_needs_same_semantics_baseline_and_public_wording_review",
        )
        self.assertIn("goal1084_facility_recentered_rtx_pod_packet", " ".join(rows["facility_knn_assignment"]["latest_evidence"]))
        self.assertIn("same-semantics baseline", rows["facility_knn_assignment"]["next_action"])
        self.assertFalse(rows["facility_knn_assignment"]["public_speedup_claim_authorized"])

        self.assertEqual(
            rows["barnes_hut_force_app"]["status"],
            "rtx_pod_evidence_intaked_needs_same_semantics_baseline_and_public_wording_review",
        )
        self.assertIn("barnes_hut_depth8_20m_timing", " ".join(rows["barnes_hut_force_app"]["latest_evidence"]))
        self.assertIn("public wording review", rows["barnes_hut_force_app"]["next_action"])
        self.assertFalse(rows["barnes_hut_force_app"]["public_speedup_claim_authorized"])

    def test_robot_row_remains_non_cloud_embree_baseline_ready(self) -> None:
        rows = {row["app"]: row for row in build_status()["rows"]}

        self.assertEqual(
            rows["robot_collision_screening"]["status"],
            "ready_for_non_cloud_chunked_embree_baseline_execution",
        )
        self.assertIn("Goal1090", rows["robot_collision_screening"]["next_action"])
        self.assertFalse(rows["robot_collision_screening"]["public_speedup_claim_authorized"])

    def test_markdown_preserves_claim_boundary(self) -> None:
        markdown = to_markdown(build_status())

        self.assertIn("Supersedes", markdown)
        self.assertIn("Same-semantics baselines", markdown)
        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("rtx_pod_evidence_intaked_needs_same_semantics_baseline", markdown)


if __name__ == "__main__":
    unittest.main()
