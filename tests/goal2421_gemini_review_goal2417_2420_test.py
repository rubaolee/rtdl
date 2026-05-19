from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2421_gemini_review_goal2417_2420_rt_dbscan_prepared_grid_2026-05-19.md"


class Goal2421GeminiReviewGoal2417To2420Test(unittest.TestCase):
    def test_gemini_review_accepts_prepared_grid_work_with_boundaries(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("## Verdict", review)
        self.assertIn("accept", review)
        self.assertIn("no DBSCAN-specific native ABI", review)
        self.assertIn("prepared mode is consistently faster", review)
        self.assertIn("scale crossover", review)
        self.assertIn("no paper reproduction", review)
        self.assertIn("no broad DBSCAN acceleration claim", review)
        self.assertIn("hidden magic dispatcher", review)


if __name__ == "__main__":
    unittest.main()
