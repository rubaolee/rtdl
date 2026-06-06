from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal3568_gemini_review_goal3567_v29_composite_packet_2026-06-06.md"
)
HANDOFF = (
    ROOT
    / "docs"
    / "handoff"
    / "HANDOFF_GEMINI_GOAL3567_V29_COMPOSITE_PACKET_REVIEW_2026-06-06.md"
)


class Goal3568GeminiReviewGoal3567Test(unittest.TestCase):
    def test_review_exists_with_accept_with_boundary_verdict(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Reviewer: Gemini", text)
        self.assertIn("Verdict: **accept-with-boundary**", text)
        self.assertIn("Goal3567", text)

    def test_review_accepts_composite_packet_and_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("9 rows are reused from Goal3558", text)
        self.assertIn("2 RayDB rows are replaced with Goal3565", text)
        self.assertIn("not a raw all-row rerun", text)
        self.assertIn("All RayDB replacements are numerically and semantically sound", text)
        self.assertIn("internal benchmark evidence only", text)

    def test_handoff_asked_for_read_only_review(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("read-only external review", text)
        self.assertIn("docs/reviews/goal3568_gemini_review_goal3567", text)
        self.assertIn("Do not edit source files", text)


if __name__ == "__main__":
    unittest.main()
