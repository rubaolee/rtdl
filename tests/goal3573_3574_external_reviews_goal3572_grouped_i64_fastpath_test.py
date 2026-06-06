from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "docs" / "reviews" / "goal3573_claude_review_goal3572_grouped_i64_fastpath_2026-06-06.md"
GEMINI = ROOT / "docs" / "reviews" / "goal3574_gemini_review_goal3572_grouped_i64_fastpath_2026-06-06.md"


class Goal3573Goal3574ExternalReviewsGoal3572Test(unittest.TestCase):
    def test_claude_review_accepts_with_boundaries(self) -> None:
        text = CLAUDE.read_text(encoding="utf-8")
        self.assertIn("Reviewer: Claude", text)
        self.assertIn("Verdict: **accept**", text)
        self.assertIn("device_column_grouped_i64_small_group_reduction_kernel", text)
        self.assertIn("stats", text)
        self.assertIn("structural", text)
        self.assertIn("0.9878x", text)
        self.assertIn("does not authorize release", text)

    def test_gemini_review_accepts_with_boundary_and_exact_artifact_numbers(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Verdict**: accept-with-boundary", text)
        self.assertIn("baseline commit**: `f5090057`", text)
        self.assertIn("candidate commit**: `bfcb943c`", text)
        self.assertIn("geomean speedup**: `1.157044x`", text)
        self.assertIn("`sum`: `0.987797x`", text)
        self.assertIn("no performance claim for `stats`", text)
        self.assertIn("public speedup claims", text)


if __name__ == "__main__":
    unittest.main()
