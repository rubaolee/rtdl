from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2806_v2_5_internal_readiness_packet_2026-05-31.md"
CONSENSUS = (
    ROOT
    / "docs"
    / "reports"
    / "goal2806_v2_5_internal_readiness_packet_consensus_2026-05-31.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2806_claude_review_v2_5_internal_readiness_packet_2026-05-31.md"
)
GEMINI_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2806_gemini_review_v2_5_internal_readiness_packet_2026-05-31.md"
)


class Goal2806V25InternalReadinessPacketTest(unittest.TestCase):
    def test_internal_readiness_packet_validates_current_v2_5_state(self) -> None:
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["benchmark_app_count"], 10)
        self.assertEqual(validation["tier_counts"], {"A": 3, "B": 4, "C": 3})
        self.assertEqual(validation["tier_b_clean_artifact_count"], 4)
        self.assertEqual(validation["broad_clean_pod_gate_result"], "OK")
        self.assertEqual(validation["errors"], ())

    def test_packet_indexes_required_reports_reviews_and_clean_artifacts(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual(packet["status"], "internal_evidence_packet_coherent_not_release_ready")
        self.assertEqual(packet["missing_required_reports"], ())
        self.assertEqual(packet["missing_external_reviews"], ())
        for app_id, artifact in packet["tier_b_clean_artifacts"].items():
            with self.subTest(app_id=app_id):
                self.assertEqual(artifact["status"], "pass")
                self.assertRegex(artifact["source_commit"], r"^[0-9a-f]{40}$")
                self.assertEqual(artifact["source_dirty"], [])
                self.assertIn("NVIDIA", artifact["gpu"])

    def test_packet_preserves_false_release_and_claim_flags(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        for flag, value in packet["claim_authorization"].items():
            with self.subTest(flag=flag):
                self.assertFalse(value)
        self.assertIn("v2_5_release", packet["blocked_actions"])
        self.assertIn("public_speedup_wording", packet["blocked_actions"])
        self.assertIn("true_zero_copy_wording", packet["blocked_actions"])
        self.assertIn("triton_preview_auto_selection", packet["blocked_actions"])
        self.assertIn("native_app_specific_engine_logic", packet["blocked_actions"])

    def test_public_api_and_report_document_the_internal_boundary(self) -> None:
        self.assertIn("v2_5_internal_readiness_packet", rt.__all__)
        self.assertIn("validate_v2_5_internal_readiness_packet", rt.__all__)

        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2806", text)
        self.assertIn("internal evidence packet", text)
        self.assertIn("10 benchmark apps", text)
        self.assertIn("239 tests", text)
        self.assertIn("not a v2.5 release authorization", text)
        self.assertIn("not a public speedup claim", text)
        self.assertIn("not a true-zero-copy claim", text)

    def test_external_reviews_and_consensus_are_recorded(self) -> None:
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Independent Claude Review", claude)
        self.assertIn("accept-with-boundary", claude)
        self.assertIn("Independent Gemini Review", gemini)
        self.assertIn("accept-with-boundary", gemini)
        self.assertIn("Codex + Claude + Gemini", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("does not authorize", consensus)


if __name__ == "__main__":
    unittest.main()
