from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL2181_RAYJOIN_PIP_REVIEW_2026-05-16.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2182_gemini_review_goal2181_rayjoin_pip_2026-05-16.md"


class Goal2182GeminiReviewGoal2181RayjoinPipTest(unittest.TestCase):
    def test_review_accepts_pip_boundary_evidence(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal2182 Gemini Review", text)
        self.assertIn("`accept`", text)
        self.assertIn("173a12bca288a9bbddff4386fb1417c4d388be75", text)
        self.assertIn("pip_county512", text)
        self.assertIn("512", text)
        self.assertIn("481", text)
        self.assertIn("246272", text)
        self.assertIn("1430", text)

    def test_review_verifies_boundary_interpretation(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Embree and OptiX both beat CPU/native-oracle", text)
        self.assertIn("Embree is slightly faster than OptiX", text)
        self.assertIn("OptiX does not win every RayJoin subproblem", text)
        self.assertIn("valuable boundary result", text)

    def test_review_and_handoff_block_broad_claims(self) -> None:
        review_text = REVIEW.read_text(encoding="utf-8")
        handoff_text = HANDOFF.read_text(encoding="utf-8")

        for text in (review_text, handoff_text):
            self.assertIn("full RayJoin paper reproduction", text)
            self.assertIn("broad RT-core speedup", text)
            self.assertIn("v2.0 release authorization", text)
            self.assertIn("whole-app RayJoin speedup", text)
            self.assertIn("OptiX wins every RayJoin subproblem", text)


if __name__ == "__main__":
    unittest.main()
