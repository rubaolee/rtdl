from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2158_gemini_review_goal2157_rayjoin_nonzero_lsi_2026-05-16.md"


class Goal2158GeminiReviewGoal2157RayjoinNonzeroLsiTest(unittest.TestCase):
    def test_review_records_independence_verdict_and_caveats(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "independent Gemini review, distinct from Codex",
            "does not authorize v2.0 release by itself",
            "`accept-with-boundary`",
            "bounded derived inputs, not exact RayJoin paper-scale inputs",
            "5.18x speedup over CPU",
            "committed reusable runner",
            "CUDA/CuPy non-RT baselines",
            "not release evidence by itself",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
