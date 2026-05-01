from __future__ import annotations

import unittest

from scripts.goal1095_rtx_cloud_runbook_current_audit import build_audit
from scripts.goal1095_rtx_cloud_runbook_current_audit import to_markdown


class Goal1095RtxCloudRunbookCurrentAuditTest(unittest.TestCase):
    def test_runbook_audit_validates_current_pod_plan(self) -> None:
        audit = build_audit()

        self.assertTrue(audit["valid"])
        self.assertTrue(audit["checks"]["mentions_current_post_goal1094"])
        self.assertTrue(audit["checks"]["runs_goal1084_facility"])
        self.assertTrue(audit["checks"]["runs_goal1093_barnes"])
        self.assertTrue(audit["checks"]["robot_is_not_cloud_gpu_task"])

    def test_runbook_audit_preserves_barnes_validation_timing_boundary(self) -> None:
        checks = build_audit()["checks"]

        self.assertTrue(checks["barnes_validation_no_skip"])
        self.assertTrue(checks["barnes_timing_skip"])
        self.assertTrue(checks["marks_goal1072_historical"])
        self.assertTrue(checks["marks_goal1076_historical"])
        self.assertTrue(checks["no_public_claim_boundary"])

    def test_markdown_preserves_no_claim_boundary(self) -> None:
        markdown = to_markdown(build_audit())

        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("runs_goal1093_barnes", markdown)


if __name__ == "__main__":
    unittest.main()
