from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal3061_v2_6_doc_total_audit_3ai_consensus_2026-06-02.md"
CODEX_REPORT = ROOT / "docs" / "reports" / "goal3058_v2_6_release_candidate_doc_total_audit_2026-06-02.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal3059_claude_review_goal3058_v2_6_doc_total_audit_2026-06-02.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal3060_gemini_review_goal3058_v2_6_doc_total_audit_2026-06-02.md"


class Goal3061V26DocTotalAudit3AiConsensusTest(unittest.TestCase):
    def test_consensus_records_three_distinct_ai_inputs(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertTrue(CODEX_REPORT.exists())
        self.assertTrue(CLAUDE_REVIEW.exists())
        self.assertTrue(GEMINI_REVIEW.exists())

        self.assertIn("Codex", text)
        self.assertIn("Claude", text)
        self.assertIn("Gemini", text)
        self.assertIn("goal3058_v2_6_release_candidate_doc_total_audit_2026-06-02.md", text)
        self.assertIn("goal3059_claude_review_goal3058_v2_6_doc_total_audit_2026-06-02.md", text)
        self.assertIn("goal3060_gemini_review_goal3058_v2_6_doc_total_audit_2026-06-02.md", text)

    def test_consensus_accepts_with_release_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Consensus Verdict", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("No blocking findings", claude)
        self.assertIn("No blocking findings", gemini)
        self.assertIn("ALL_PORTABLE_SMOKE_OK", text)
        self.assertIn("103 checked / 0 broken", text)

        blocked = [
            "tagging or publishing v2.6",
            "package-install claims",
            "broad RT-core or whole-app speedup claims",
            "automatic partner-selection claims",
            "general zero-copy/device-residency claims",
        ]
        for phrase in blocked:
            self.assertIn(phrase, text)

    def test_remaining_release_gates_are_explicit(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Run native tutorial and example commands", text)
        self.assertIn("including Embree and OptiX", text)
        self.assertIn("final v2.6 release consensus record", text)
        self.assertNotIn("release authorized", text.lower())


if __name__ == "__main__":
    unittest.main()
