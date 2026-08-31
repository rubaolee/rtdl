from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL3926_REVIEW_GOAL3924_3925_NUMBA_COVERAGE_2026-06-08.md"
REVIEW = ROOT / "docs" / "reviews" / "goal3926_gemini_review_goal3924_3925_numba_coverage_2026-06-08.md"


class Goal3926GeminiReviewGoal3924_3925NumbaCoverageTest(unittest.TestCase):
    def test_review_records_accept_verdict_and_answers_required_questions(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("**Verdict:** `accept`", text)
        for phrase in (
            "functional readiness only",
            "not release performance evidence",
            "primitive-first apps",
            "requiring Numba references",
            "avoid any CuPy-only",
            "await A5000 timing",
            "automatic-partner-selection overclaims",
        ):
            self.assertIn(phrase, text)

    def test_handoff_and_review_state_read_only_limitations(self) -> None:
        handoff = HANDOFF.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("read-only review", handoff)
        self.assertIn("No tests were executed", review)
        self.assertIn("before the next pod performance packet", review)


if __name__ == "__main__":
    unittest.main()
