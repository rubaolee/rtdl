from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2166_gemini_review_goal2165_count_first_optix_lsi_output_2026-05-16.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL2165_COUNT_FIRST_OPTIX_LSI_REVIEW_2026-05-16.md"


class Goal2166GeminiReviewGoal2165CountFirstOptixLsiOutputTest(unittest.TestCase):
    def test_review_records_independent_acceptance(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("distinct from Codex authoring", text)
        self.assertIn("does not by itself authorize v2.0 release", text)
        self.assertIn("`accept`", text)

    def test_review_accepts_generic_count_first_design(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("generic app-agnostic engine boundary", text)
        self.assertIn("host exact refinement", text)
        self.assertIn("speedup claims", text)
        self.assertIn("no blocking debts", text)

    def test_handoff_named_expected_review_path(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn(
            "docs/reviews/goal2166_gemini_review_goal2165_count_first_optix_lsi_output_2026-05-16.md",
            text,
        )
        self.assertIn("Goal2165", text)


if __name__ == "__main__":
    unittest.main()
