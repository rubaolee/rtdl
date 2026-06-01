from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2922_gemini_review_goal2920_2921_rtnn_hausdorff_stability_2026-06-01.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2923_goal2920_2921_stability_review_consensus_2026-06-01.md"


class Goal2923Goal2920Goal2921StabilityReviewConsensusTest(unittest.TestCase):
    def test_gemini_review_accepts_with_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Reviewer", text)
        self.assertIn("Gemini", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("target `4096`", text)
        self.assertIn("app-agnostic native-engine boundary", text)
        self.assertIn("residual risks", text)

    def test_consensus_records_codex_gemini_and_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Codex and Gemini agree", text)
        self.assertIn("Goal2921 proves the seven-app packet remains clean", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("does not authorize v2.5 release", text)
        self.assertIn("fresh 3-AI release review", text)


if __name__ == "__main__":
    unittest.main()
