import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1762_v1_8_final_release_prep_consensus_2026-05-12.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal1760_claude_review_goal1759_v1_8_release_prep_2026-05-12.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal1761_gemini_review_goal1759_v1_8_release_prep_2026-05-12.md"
CLAUDE_DOC_REVIEW = ROOT / "docs" / "reviews" / "goal1766_claude_review_goal1763_1765_release_docs_audit_2026-05-12.md"
GEMINI_DOC_REVIEW = ROOT / "docs" / "reviews" / "goal1767_gemini_review_goal1763_1765_release_docs_audit_2026-05-12.md"


class Goal1762V18FinalReleasePrepConsensusTest(unittest.TestCase):
    def test_consensus_declares_ready_pending_user_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1_8_release_prep_consensus_ready_pending_user_release_authorization", text)
        self.assertIn("does not authorize a tag", text)
        self.assertIn("explicit user authorization", text)
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "v1.8")

    def test_consensus_records_distinct_external_reviews(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertTrue(CLAUDE_REVIEW.exists())
        self.assertTrue(GEMINI_REVIEW.exists())
        self.assertIn("goal1760_claude_review_goal1759_v1_8_release_prep_2026-05-12.md", text)
        self.assertIn("Verdict: `accept-with-boundary`", text)
        self.assertIn("goal1761_gemini_review_goal1759_v1_8_release_prep_2026-05-12.md", text)
        self.assertIn("Verdict: `accept`", text)

    def test_consensus_records_docs_audit_learner_followup_reviews(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertTrue(CLAUDE_DOC_REVIEW.exists())
        self.assertTrue(GEMINI_DOC_REVIEW.exists())
        self.assertIn("Goals1763-1768 extend this consensus", text)
        self.assertIn("goal1766_claude_review_goal1763_1765_release_docs_audit_2026-05-12.md", text)
        self.assertIn("goal1767_gemini_review_goal1763_1765_release_docs_audit_2026-05-12.md", text)
        self.assertIn("goal1768_v1_8_release_authorization_readiness_after_docs_audit_2026-05-12.md", text)
        self.assertIn("v1_8_release_authorization_packet_ready_pending_user_go", text)

    def test_consensus_records_goal1758_resolution_and_gate(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal1758 migrated the remaining older Apple RT / HIPRT / Oracle / Vulkan", text)
        self.assertIn("native engine boundary", text)
        self.assertIn("app-agnostic in source and exported ABI terminology", text)
        self.assertIn("Ran 129 tests", text)
        self.assertIn("OK", text)

    def test_consensus_blocks_public_overclaims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "package-install support",
            "public speedup wording",
            "broad RTX/GPU acceleration wording",
            "whole-application acceleration",
            "universal backend support",
            "Python+partner+RTDL completion",
            "PyTorch/CuPy integration",
            "true zero-copy support",
            "recovered v1.0 Embree app-level rows",
        ):
            self.assertIn(phrase, text)

    def test_consensus_protects_local_files(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz", text)
        self.assertIn("id_ed25519_rtdl_codex", text)
        self.assertIn("rtdl_v0_4.tar.gz", text)
        self.assertIn("scratch/", text)


if __name__ == "__main__":
    unittest.main()
