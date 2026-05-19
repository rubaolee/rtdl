from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_CLAUDE_GOAL2415_RT_DBSCAN_MICROCELL_NEGATIVE_REVIEW_2026-05-19.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2416_claude_review_goal2415_rt_dbscan_microcell_negative_2026-05-19.md"


class Goal2416ClaudeReviewGoal2415RtDbscanMicrocellNegativeTest(unittest.TestCase):
    def test_handoff_requested_bounded_negative_review(self) -> None:
        handoff = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("correctness-valid but performance-negative", handoff)
        self.assertIn("prepared CuPy grid continuation hardening", handoff)
        self.assertIn("Do not recommend DBSCAN-specific native ABI", handoff)

    def test_claude_accepts_negative_result_and_pivot(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Verdict: **accept**", review)
        self.assertIn("performance-negative", review)
        self.assertIn("prepared CuPy grid continuation hardening", review)
        self.assertIn("No anomalies were found", review)
        self.assertIn("does not authorize a release claim", review)


if __name__ == "__main__":
    unittest.main()
