from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1954_gemini_review_goal1953_rawkernel_control_apps_2026-05-13.md"


class Goal1954GeminiReviewGoal1953RawKernelControlAppsTest(unittest.TestCase):
    def test_review_accepts_rawkernel_control_app_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal1954", text)
        self.assertIn("Goal1953", text)
        self.assertIn("RawKernel", text)
        self.assertIn("database_analytics", text)
        self.assertIn("graph_analytics", text)
        self.assertIn("polygon_pair_overlap_area_rows", text)
        self.assertIn("polygon_set_jaccard", text)
        self.assertIn("CPU fallback", text)
        self.assertIn("pod timing", text)
        self.assertIn("Final Verdict", text)
        self.assertIn("**accept**", text)


if __name__ == "__main__":
    unittest.main()
