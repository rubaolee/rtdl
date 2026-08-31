from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3997_claude_review_goal3996_grouped_union_extended_telemetry_sweep_2026-06-08.md"


class Goal3997ClaudeReviewGoal3996GroupedUnionSweepTest(unittest.TestCase):
    def test_claude_review_accepts_with_boundary_and_scope(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("simple grouped-union mode toggles are exhausted", review)
        self.assertIn("dense candidate enumeration/root-read", review)
        self.assertIn("clustered3d", review)
        self.assertIn("no release/performance/zero-copy", review)
        self.assertIn("profile/scale", review)


if __name__ == "__main__":
    unittest.main()
