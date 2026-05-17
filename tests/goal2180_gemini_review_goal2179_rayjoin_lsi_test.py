from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL2179_RAYJOIN_LSI_REVIEW_2026-05-16.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2180_gemini_review_goal2179_rayjoin_lsi_2026-05-16.md"


class Goal2180GeminiReviewGoal2179RayjoinLsiTest(unittest.TestCase):
    def test_review_accepts_lsi_evidence(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Gemini Review: Goal2179", text)
        self.assertIn("Gemini Agent", text)
        self.assertIn("`accept`", text)
        self.assertIn("transcribed from `scratch/gemini_goal2180.out`", text)
        self.assertIn("19a090702c0ea32eee247866743cd44afeb2ede1", text)
        self.assertIn("lsi_county256_soil256_count512", text)

    def test_review_verifies_numbers_and_interpretation(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("136411275", text)
        self.assertIn("0.003221943974494934", text)
        self.assertIn("0.040767318569123745", text)
        self.assertIn("62.472x", text)
        self.assertIn("12.653x", text)
        self.assertIn("sparse true-hit LSI", text)
        self.assertIn("hot-repeat median", text)

    def test_review_and_handoff_block_broad_claims(self) -> None:
        review_text = REVIEW.read_text(encoding="utf-8")
        handoff_text = HANDOFF.read_text(encoding="utf-8")

        for text in (review_text, handoff_text):
            self.assertIn("full RayJoin paper reproduction", text)
            self.assertIn("broad RT-core speedup", text)
            self.assertIn("v2.0 release authorization", text)
            self.assertIn("whole-app RayJoin speedup", text)
            self.assertIn("spatial-indexed baselines", text)
            self.assertIn("cold-start OptiX", text)


if __name__ == "__main__":
    unittest.main()
