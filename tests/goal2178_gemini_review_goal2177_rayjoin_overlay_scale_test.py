from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL2177_RAYJOIN_OVERLAY_SCALE_REVIEW_2026-05-16.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2178_gemini_review_goal2177_rayjoin_overlay_scale_2026-05-16.md"


class Goal2178GeminiReviewGoal2177RayjoinOverlayScaleTest(unittest.TestCase):
    def test_review_accepts_goal2177_scale_evidence(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Gemini Review: Goal2177", text)
        self.assertIn("Gemini Agent", text)
        self.assertIn("`accept`", text)
        self.assertIn("f161c8aafdfc0a469c4e23f92859b810e9f9b8be", text)
        self.assertIn("overlay_county384_soil384", text)
        self.assertIn("overlay_county512_soil512", text)

    def test_review_verifies_scale_numbers_and_trend(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("130320", text)
        self.assertIn("233766", text)
        self.assertIn("0.1776761505752802", text)
        self.assertIn("0.3221710389479995", text)
        self.assertIn("2.619x", text)
        self.assertIn("3.688x", text)
        self.assertIn("advantage widens", text)
        self.assertIn("not the fastest path", text)

    def test_review_and_handoff_block_broad_claims(self) -> None:
        review_text = REVIEW.read_text(encoding="utf-8")
        handoff_text = HANDOFF.read_text(encoding="utf-8")

        for text in (review_text, handoff_text):
            self.assertIn("full RayJoin paper reproduction", text)
            self.assertIn("broad RT-core speedup", text)
            self.assertIn("v2.0 release authorization", text)
            self.assertIn("whole-app RayJoin speedup", text)
            self.assertIn("stronger CUDA/CuPy spatial-prefilter baselines", text)


if __name__ == "__main__":
    unittest.main()
