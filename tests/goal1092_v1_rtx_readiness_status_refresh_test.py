from __future__ import annotations

import unittest

from scripts.goal1092_v1_rtx_readiness_status_refresh import build_status
from scripts.goal1092_v1_rtx_readiness_status_refresh import to_markdown


class Goal1092V1RtxReadinessStatusRefreshTest(unittest.TestCase):
    def test_status_refresh_tracks_current_three_rows(self) -> None:
        status = build_status()

        self.assertTrue(status["valid"])
        self.assertEqual(status["summary"]["row_count"], 3)
        self.assertEqual(status["summary"]["public_speedup_claim_authorized_count"], 0)
        self.assertTrue(status["summary"]["facility_ready_for_pod"])
        self.assertTrue(status["summary"]["robot_ready_for_non_cloud_baseline"])
        self.assertTrue(status["summary"]["barnes_hut_blocked"])

    def test_rows_reference_latest_local_evidence(self) -> None:
        rows = {row["app"]: row for row in build_status()["rows"]}

        self.assertIn("Goal1084", rows["facility_knn_assignment"]["next_action"])
        self.assertIn("Goal1090", rows["robot_collision_screening"]["next_action"])
        self.assertIn("Goal1086", rows["robot_collision_screening"]["next_action"])
        self.assertIn("goal1091_robot_pose_offset_smoke_intake", " ".join(rows["robot_collision_screening"]["latest_evidence"]))
        self.assertEqual(rows["barnes_hut_force_app"]["status"], "blocked_pending_contract_supersession")

    def test_markdown_preserves_no_claim_boundary(self) -> None:
        markdown = to_markdown(build_status())

        self.assertIn("Supersedes", markdown)
        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("ready_for_non_cloud_chunked_embree_baseline_execution", markdown)


if __name__ == "__main__":
    unittest.main()
