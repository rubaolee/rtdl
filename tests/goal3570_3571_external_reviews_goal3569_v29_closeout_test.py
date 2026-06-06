from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_EXTERNAL_REVIEW_GOAL3569_V29_INTERNAL_CLOSEOUT_2026-06-06.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal3570_claude_review_goal3569_v29_internal_closeout_2026-06-06.md"
GEMINI = ROOT / "docs" / "reviews" / "goal3571_gemini_review_goal3569_v29_internal_closeout_2026-06-06.md"
REPORT = ROOT / "docs" / "reports" / "goal3569_v2_9_internal_performance_closeout_2026-06-06.md"


class Goal3570And3571ExternalReviewsGoal3569Test(unittest.TestCase):
    def test_handoff_requested_both_reviews(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("External Review for Goal3569", text)
        self.assertIn("goal3570_claude_review_goal3569_v29_internal_closeout", text)
        self.assertIn("goal3571_gemini_review_goal3569_v29_internal_closeout", text)
        self.assertIn("Do not edit source files", text)

    def test_claude_accepts_internal_closeout(self) -> None:
        text = CLAUDE.read_text(encoding="utf-8")

        self.assertIn("Reviewer: Claude", text)
        self.assertIn("Verdict: **accept**", text)
        self.assertIn("v2.9 is accepted as an internally closed performance version", text)
        self.assertIn("No unauthorized claims", text)

    def test_gemini_accepts_internal_closeout(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Reviewer: Gemini", text)
        self.assertIn("Verdict: **accept**", text)
        self.assertIn("The decision to close v2.9 as an internal performance version is accepted", text)
        self.assertIn("claim boundaries", text)

    def test_closeout_report_references_direct_external_acceptance(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal3570", text)
        self.assertIn("Goal3571", text)
        self.assertIn("Claude and Gemini both accepted this closeout report directly", text)


if __name__ == "__main__":
    unittest.main()
