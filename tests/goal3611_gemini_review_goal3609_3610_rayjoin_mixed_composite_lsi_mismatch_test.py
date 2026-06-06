from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3611_gemini_review_goal3609_3610_rayjoin_mixed_composite_lsi_mismatch_2026-06-06.md"


class Goal3611GeminiReviewGoal3609_3610RayJoinMixedCompositeLsiMismatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = REVIEW.read_text(encoding="utf-8")

    def test_review_accepts_internal_evidence_and_blocks_overclaim(self):
        self.assertIn("## Verdict: accept", self.review)
        self.assertIn("21.654x speedup", self.review)
        self.assertIn("4977 intersections", self.review)
        self.assertIn("4985", self.review)
        self.assertIn("eight specific left-id deltas", self.review)
        self.assertIn("claim boundaries", self.review)

    def test_review_endorses_same_contract_repair_direction(self):
        self.assertIn("generic robust segment-pair intersection contract", self.review)
        self.assertIn("denominator, endpoint, collinearity, and tolerance policy", self.review)


if __name__ == "__main__":
    unittest.main()
