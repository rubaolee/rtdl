from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2156_gemini_review_goal2155_embree_endpoint_fix_2026-05-16.md"


class Goal2156GeminiReviewGoal2155EmbreeEndpointFixTest(unittest.TestCase):
    def test_review_records_independence_verdict_and_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "independent Gemini review, distinct from Codex",
            "does not authorize v2.0 release by itself",
            "`accept-with-boundary`",
            "not RayJoin app customization",
            "shared-endpoint segment hits",
            "all_parity_vs_cpu_python_reference: true",
            "v2.0 release authorization",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
