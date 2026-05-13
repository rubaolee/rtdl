from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reviews" / "goal1818_3ai_consensus_goal1814_strict_v2_birth_gate_2026-05-13.md"
REPORT = ROOT / "docs" / "reports" / "goal1814_v2_0_strict_birth_gate_2026-05-13.md"
GEMINI = ROOT / "docs" / "reviews" / "goal1817_gemini_followup_review_goal1814_strict_v2_birth_gate_2026-05-13.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal1816_claude_review_goal1814_strict_v2_birth_gate_2026-05-13.md"


class Goal1818StrictV2BirthGateConsensusTest(unittest.TestCase):
    def test_consensus_accepts_strict_gate_and_blocks_release(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("Verdict: `accept-with-boundary`", text)
        self.assertIn("Goal1814 is now the governing v2.0 release gate", text)
        self.assertIn("It is not a v2.0", text)
        self.assertIn("release. v2.0 is born only after the six blockers", text)
        self.assertIn("v2.0 is born only after the six blockers", text)

    def test_consensus_counts_substantive_external_reviews(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("Goal1815 is recorded but not counted", text)
        self.assertIn("Goal1816 and Goal1817 are the", text)
        self.assertIn("substantive external reviews", text)
        self.assertIn("Claude and Gemini are distinct from Codex", text)
        self.assertIn("Codex+Codex is invalid", text)
        self.assertIn("accept-with-boundary", CLAUDE.read_text(encoding="utf-8"))
        self.assertIn("Verdict: `accept`", GEMINI.read_text(encoding="utf-8"))

    def test_report_incorporates_review_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("positive rule for what RTDL does", text)
        self.assertIn("3-AI-ratified release statement", text)
        self.assertIn("Goal1815 is preserved as a non-substantive", text)


if __name__ == "__main__":
    unittest.main()
