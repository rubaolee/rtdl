from __future__ import annotations

import unittest

from scripts.goal1094_v1_rtx_readiness_status_refresh import build_status
from scripts.goal1094_v1_rtx_readiness_status_refresh import to_markdown


class Goal1094V1RtxReadinessStatusRefreshTest(unittest.TestCase):
    def test_status_refresh_has_two_pod_ready_and_one_non_cloud_ready_row(self) -> None:
        status = build_status()

        self.assertTrue(status["valid"])
        self.assertEqual(status["summary"]["row_count"], 3)
        self.assertEqual(status["summary"]["pod_ready_count"], 2)
        self.assertEqual(status["summary"]["non_cloud_ready_count"], 1)
        self.assertEqual(status["summary"]["blocked_count"], 0)
        self.assertEqual(status["summary"]["public_speedup_claim_authorized_count"], 0)

    def test_rows_point_to_current_next_actions(self) -> None:
        rows = {row["app"]: row for row in build_status()["rows"]}

        self.assertEqual(rows["facility_knn_assignment"]["status"], "ready_for_next_rtx_pod_validation")
        self.assertIn("Goal1084", rows["facility_knn_assignment"]["next_action"])
        self.assertEqual(rows["robot_collision_screening"]["status"], "ready_for_non_cloud_chunked_embree_baseline_execution")
        self.assertIn("Goal1090", rows["robot_collision_screening"]["next_action"])
        self.assertEqual(rows["barnes_hut_force_app"]["status"], "ready_for_next_rtx_pod_contract_validation")
        self.assertIn("Goal1093", rows["barnes_hut_force_app"]["next_action"])

    def test_markdown_preserves_no_claim_boundary(self) -> None:
        markdown = to_markdown(build_status())

        self.assertIn("Supersedes", markdown)
        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("ready_for_next_rtx_pod_contract_validation", markdown)


if __name__ == "__main__":
    unittest.main()
