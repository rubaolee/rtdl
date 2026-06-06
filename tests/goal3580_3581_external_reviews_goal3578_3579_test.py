from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "docs" / "reviews" / "goal3580_claude_review_goal3578_3579_raydb_mode_diagnostic_2026-06-06.md"
GEMINI = ROOT / "docs" / "reviews" / "goal3581_gemini_review_goal3578_3579_raydb_mode_diagnostic_2026-06-06.md"


class Goal3580Goal3581ExternalReviewsGoal3578Goal3579Test(unittest.TestCase):
    def test_claude_accepts_diagnostic_and_ratio(self) -> None:
        text = CLAUDE.read_text(encoding="utf-8")
        self.assertIn("Reviewer: Claude", text)
        self.assertIn("Verdict: **accept**", text)
        self.assertIn("integration-only evidence", text)
        self.assertIn("native_launch_count: 1", text)
        self.assertIn("3.604830411x", text)
        self.assertIn("No unauthorized claim language was found", text)

    def test_gemini_accepts_diagnostic_and_ratio(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Independent Gemini Review", text)
        self.assertIn("**accept**", text)
        self.assertIn("integration-only evidence", text)
        self.assertIn("single native launch", text)
        self.assertIn("3.604830411x", text)
        self.assertIn("Boundary Adherence", text)


if __name__ == "__main__":
    unittest.main()
