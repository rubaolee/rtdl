from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3626_gemini_review_goal3625_segment_pair_contract_foundation_2026-06-06.md"


class Goal3626GeminiReviewGoal3625SegmentPairContractFoundationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = REVIEW.read_text(encoding="utf-8")

    def test_review_accepts_contract_foundation_with_boundaries(self):
        self.assertIn("Reviewer: Gemini", self.review)
        self.assertIn("Verdict: accept", self.review)
        self.assertIn("app-agnostic contract foundation", self.review)
        self.assertIn("candidate_behavior", self.review)
        self.assertIn("does not authorize release", self.review)
        self.assertIn("3-AI consensus has not yet been achieved", self.review)


if __name__ == "__main__":
    unittest.main()
