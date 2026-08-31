from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal3566_claude_review_goal3563_3565_v29_raydb_sum_fastpath_2026-06-06.md"
)
HANDOFF = (
    ROOT
    / "docs"
    / "handoff"
    / "HANDOFF_CLAUDE_GOAL3563_3565_V29_RAYDB_SUM_FASTPATH_REVIEW_2026-06-06.md"
)


class Goal3566ClaudeReviewGoal3563To3565Test(unittest.TestCase):
    def test_review_exists_with_accepted_boundary_verdict(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Reviewer: Claude", text)
        self.assertIn("Verdict: **accept-with-boundary**", text)
        self.assertIn("Goal3563", text)
        self.assertIn("Goal3564", text)
        self.assertIn("Goal3565", text)

    def test_review_names_remaining_packet_refresh_requirement(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Update the v2.9 summary packet", text)
        self.assertIn("stale Goal3558 RayDB sum value", text)
        self.assertIn("1.586x", text)
        self.assertIn("No unauthorized claims", text)

    def test_handoff_requested_read_only_external_review(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("read-only external review", text)
        self.assertIn("docs/reviews/goal3566_claude_review_goal3563_3565", text)
        self.assertIn("Do not edit source files", text)


if __name__ == "__main__":
    unittest.main()
