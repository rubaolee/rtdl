from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3628_gemini_review_goal3627_segment_pair_residency_contract_2026-06-06.md"


class Goal3628GeminiReviewGoal3627SegmentPairResidencyContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = REVIEW.read_text(encoding="utf-8")

    def test_review_accepts_residency_contract_with_boundaries(self):
        self.assertIn("Gemini Review", self.review)
        self.assertIn("Verdict: accept", self.review)
        self.assertIn("app-agnostic", self.review)
        self.assertIn("neutral-seam", self.review)
        self.assertIn("borrowed_device_pointer_unmeasured", self.review)
        self.assertIn("true_zero_copy_authorized", self.review)


if __name__ == "__main__":
    unittest.main()
