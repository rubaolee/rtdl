from __future__ import annotations

import unittest

from scripts.goal1088_v1_rtx_readiness_status_audit import build_audit
from scripts.goal1088_v1_rtx_readiness_status_audit import to_markdown


class Goal1088V1RtxReadinessStatusAuditTest(unittest.TestCase):
    def test_audit_tracks_three_remaining_rows_without_authorized_claims(self) -> None:
        audit = build_audit()

        self.assertTrue(audit["valid"])
        self.assertEqual(audit["summary"]["row_count"], 3)
        self.assertEqual(audit["summary"]["public_speedup_claim_authorized_count"], 0)
        self.assertEqual({row["app"] for row in audit["rows"]}, {
            "facility_knn_assignment",
            "robot_collision_screening",
            "barnes_hut_force_app",
        })
        self.assertTrue(all(not row["public_speedup_claim_authorized"] for row in audit["rows"]))

    def test_statuses_point_to_distinct_next_actions(self) -> None:
        rows = {row["app"]: row for row in build_audit()["rows"]}

        self.assertEqual(rows["facility_knn_assignment"]["current_status"], "pending_next_rtx_pod_validation")
        self.assertIn("Goal1084", rows["facility_knn_assignment"]["next_action"])
        self.assertEqual(rows["robot_collision_screening"]["current_status"], "pending_non_cloud_embree_baseline_execution")
        self.assertIn("Goal1085", rows["robot_collision_screening"]["next_action"])
        self.assertEqual(rows["barnes_hut_force_app"]["current_status"], "pending_contract_supersession")
        self.assertIn("20M validation/intake", rows["barnes_hut_force_app"]["next_action"])

    def test_markdown_preserves_boundary(self) -> None:
        markdown = to_markdown(build_audit())

        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("facility_knn_assignment", markdown)
        self.assertIn("robot_collision_screening", markdown)
        self.assertIn("barnes_hut_force_app", markdown)


if __name__ == "__main__":
    unittest.main()
