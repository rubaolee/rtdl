from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1935_gemini_review_goal1933_1934_large_scale_perf_2026-05-13.md"


class Goal1935GeminiReviewGoal1933Goal1934LargeScalePerfTest(unittest.TestCase):
    def test_review_accepts_large_scale_perf_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal1935 Gemini Review", text)
        self.assertIn("fixed_radius_524288.json", text)
        self.assertIn("Verdict:** `accept`", text)
        self.assertIn("sub-second", text)
        self.assertIn("control evidence", text)
        self.assertIn("does not authorize v2.0 release", text)
        self.assertIn("whole-app speedup", text)
        self.assertIn("arbitrary PyTorch/CuPy acceleration", text)

    def test_review_does_not_upgrade_release_claims(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertNotIn("v2.0 release authorized", text.lower())
        self.assertIn("v2_0_release_authorized", text)
        self.assertIn("false", text.lower())


if __name__ == "__main__":
    unittest.main()
