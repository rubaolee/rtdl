from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2148_gemini_review_goal2147_rayjoin_scale_harness_2026-05-16.md"


class Goal2148GeminiReviewGoal2147RayjoinScaleHarnessTest(unittest.TestCase):
    def test_review_records_independence_and_acceptance(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "independent Gemini review",
            "distinct from Codex",
            "overlay_pair_dependency_rows_with_lsi_pip_flags",
            "progress logs are sufficient",
            "RT-core speedup claims",
            "accept",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
