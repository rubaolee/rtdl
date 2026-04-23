from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "rtx_cloud_single_session_runbook.md"


class Goal829RtxCloudSingleSessionRunbookTest(unittest.TestCase):
    def test_runbook_enforces_local_readiness_before_pod(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("goal824_pre_cloud_rtx_readiness_gate.py", text)
        self.assertIn('"valid": true', text)
        self.assertIn("Do not start a pod for one app at a time.", text)

    def test_runbook_uses_one_shot_runner_and_artifact_audit(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("goal769_rtx_pod_one_shot.py", text)
        self.assertIn("goal762_rtx_cloud_artifact_report_latest.json", text)
        self.assertIn("cloud_claim_contract", text)
        self.assertIn("required_phase_groups", text)
        self.assertIn("needs_attention", text)

    def test_runbook_has_deferred_batch_controls_and_shutdown_rule(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("--include-deferred", text)
        self.assertIn("--only service_coverage_gaps", text)
        self.assertIn("--only event_hotspot_screening", text)
        self.assertIn("After copying artifacts back, stop or terminate the pod.", text)
        self.assertIn("does not authorize public RTX speedup claims", text)


if __name__ == "__main__":
    unittest.main()
