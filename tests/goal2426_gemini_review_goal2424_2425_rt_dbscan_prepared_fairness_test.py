from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2426_gemini_review_goal2424_2425_rt_dbscan_prepared_fairness_2026-05-19.md"


class Goal2426GeminiReviewGoal2424_2425RtDbscanPreparedFairnessTest(unittest.TestCase):
    def test_gemini_review_accepts_fairness_correction_with_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Reviewer:** Gemini", text)
        self.assertIn("Goal2424 clearly identifies", text)
        self.assertIn("prepared RT wins clustered3d at 65k and above", text)
        self.assertIn("prepared pure CuPy wins ngsim_dense through 262k", text)
        self.assertIn("not a hidden dispatcher", text)
        self.assertIn("avoid broad DBSCAN", text)
        self.assertIn("**`accept`**", text)


if __name__ == "__main__":
    unittest.main()
