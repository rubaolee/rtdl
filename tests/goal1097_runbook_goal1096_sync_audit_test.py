from __future__ import annotations

import unittest

from scripts.goal1097_runbook_goal1096_sync_audit import build_audit
from scripts.goal1097_runbook_goal1096_sync_audit import to_markdown


class Goal1097RunbookGoal1096SyncAuditTest(unittest.TestCase):
    def test_runbook_points_to_current_combined_intake(self) -> None:
        audit = build_audit()

        self.assertTrue(audit["valid"])
        self.assertTrue(audit["checks"]["copies_goal1084_dir"])
        self.assertTrue(audit["checks"]["copies_goal1093_dir"])
        self.assertTrue(audit["checks"]["runs_goal1096_intake"])
        self.assertTrue(audit["checks"]["tests_goal1096_intake"])

    def test_runbook_preserves_claim_boundary_and_removes_stale_placeholder(self) -> None:
        checks = build_audit()["checks"]

        self.assertTrue(checks["states_engineering_evidence_only"])
        self.assertTrue(checks["preserves_no_claim_boundary"])
        self.assertTrue(checks["removes_pending_goal1084_intake_placeholder"])

    def test_markdown_mentions_boundary(self) -> None:
        markdown = to_markdown(build_audit())

        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("runs_goal1096_intake", markdown)


if __name__ == "__main__":
    unittest.main()
