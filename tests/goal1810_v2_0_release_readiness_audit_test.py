from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "reports" / "goal1810_v2_0_release_readiness_audit_2026-05-13.md"
GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"


class Goal1810V20ReleaseReadinessAuditTest(unittest.TestCase):
    def test_audit_answers_when_v2_0_is_done(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")
        self.assertIn("When is v2.0 done?", text)
        self.assertIn("protocol-first", text)
        self.assertIn("PyTorch is the primary/reference partner", text)
        self.assertIn("CuPy is the lightweight conformance partner", text)
        self.assertIn("RTX-class hardware evidence exists", text)
        self.assertIn("final release consensus is recorded", text)

    def test_audit_records_evidence_chain_and_hardware_packet(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")
        for phrase in (
            "Goal1777 implements and tests the v2.0 partner protocol baseline",
            "Goal1799 adds the public dispatch",
            "Goal1802 adds the learner-facing partner any-hit example and tutorial",
            "Goal1808 records RTX-class pod execution",
            "`torch-cuda`",
            "`cupy-cuda`",
            "`host_stage`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_audit_keeps_claim_boundary(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")
        for phrase in (
            "Do not claim",
            "true zero-copy",
            "direct device-pointer handoff",
            "broad RT-core speedup",
            "whole-application acceleration",
            "packaging/install support beyond source-tree execution",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_audit_records_external_final_consensus_but_is_superseded(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")
        self.assertIn("Claude review of Goal1810", text)
        self.assertIn("Gemini review of Goal1810", text)
        self.assertIn("Goal1813 records final 3-AI release-readiness", text)
        self.assertIn("Goal1814 supersedes", text)
        self.assertIn("v2.0 is not release-ready until the", text)
        self.assertIn("stricter blockers are resolved", text)

    def test_gate_links_latest_evidence_but_still_blocks_overclaims(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        self.assertIn("Goal1808 v2.0 Partner OptiX Pod Hardware Evidence", text)
        self.assertIn("Goal1809 Gemini Review of Goal1808", text)
        self.assertIn("Goal1813 3-AI Consensus for v2.0 Release Readiness", text)
        self.assertIn("Goal1814 v2.0 Strict Birth Gate", text)
        self.assertIn("RTDL has general true zero-copy support", text)
        self.assertIn("RTDL accelerates arbitrary PyTorch/CuPy programs", text)
        self.assertIn("RTDL v2.0 is released", text)


if __name__ == "__main__":
    unittest.main()
