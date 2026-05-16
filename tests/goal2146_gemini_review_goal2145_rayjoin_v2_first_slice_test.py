from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2146_gemini_review_goal2145_rayjoin_v2_first_slice_2026-05-16.md"


class Goal2146GeminiReviewGoal2145RayjoinV2FirstSliceTest(unittest.TestCase):
    def test_review_records_independence_verdict_and_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        required = (
            "independent Gemini review",
            "distinct from the Codex validation",
            "result_mode=\"positive_hits\"",
            "Full RayJoin paper reproduction",
            "OptiX/RT-core speedup evidence",
            "v2.0 release authorization",
            "accept-with-boundary",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
