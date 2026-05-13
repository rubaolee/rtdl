from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1901_gemini_review_goal1900_partner_acceleration_boundary_2026-05-13.md"


class Goal1901GeminiReviewGoal1900PartnerAccelerationBoundaryTest(unittest.TestCase):
    def test_interim_review_accepts_with_boundary_and_blocks_release_consensus(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Gemini Flash", text)
        self.assertIn("not a final v2.0 release consensus", text)
        self.assertIn("**Verdict:** `accept-with-boundary`", text)
        self.assertIn("RTDL accelerates only explicit RTDL primitive calls", text)
        self.assertIn("does not accelerate arbitrary PyTorch/CuPy programs", text)
        self.assertIn("without premature implications of v2.0 release readiness", text)
        self.assertIn("pod testing", text)
        self.assertIn("broader external review/consensus", text)


if __name__ == "__main__":
    unittest.main()
