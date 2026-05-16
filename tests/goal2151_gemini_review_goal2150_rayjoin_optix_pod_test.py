from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2151_gemini_review_goal2150_rayjoin_optix_pod_2026-05-16.md"


class Goal2151GeminiReviewGoal2150RayjoinOptixPodTest(unittest.TestCase):
    def test_review_records_independence_verdict_and_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "independent Gemini review",
            "distinct from Codex",
            "accept-with-boundary",
            "OptiX fix is app-agnostic",
            "pod artifacts fully support",
            "broad RT-core speedup claims",
            "does not authorize general release claims",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
