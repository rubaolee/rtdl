from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal3584_claude_review_goal3583_rayjoin_hot_promoted_routes_2026-06-06.md"
)
GEMINI_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal3585_gemini_review_goal3583_rayjoin_hot_promoted_routes_2026-06-06.md"
)


class Goal3584_3585ExternalReviewsGoal3583Test(unittest.TestCase):
    def test_distinct_external_reviews_exist(self) -> None:
        for path in (CLAUDE_REVIEW, GEMINI_REVIEW):
            with self.subTest(path=path.name):
                self.assertTrue(path.exists(), f"missing review: {path}")
                self.assertGreater(len(path.read_text(encoding="utf-8")), 1000)

    def test_claude_review_is_code_grounded_acceptance(self) -> None:
        text = CLAUDE_REVIEW.read_text(encoding="utf-8")
        self.assertIn("Verdict: **accept**", text)
        self.assertIn("All artifacts, source code, and test files were read directly", text)
        self.assertIn("phases_sec.prepared_query_sec", text)
        self.assertIn("repeat_protocol.repeat = 5", text)
        self.assertIn("full RayJoin paper reproduction", text)
        self.assertIn("full polygon overlay", text)
        self.assertIn("composite app scoring (Option 1) first", text)

    def test_gemini_review_is_distinct_acceptance_with_boundaries(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")
        self.assertIn("Reviewer: Gemini", text)
        self.assertIn("accept", text.lower())
        self.assertIn("full RayJoin paper reproduction", text)
        self.assertIn("true zero-copy", text)
        self.assertIn("external same-contract CUDA/OptiX baseline", text)


if __name__ == "__main__":
    unittest.main()
