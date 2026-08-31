from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3630_gemini_review_goal3629_segment_pair_oracle_2026-06-06.md"


class Goal3630GeminiReviewGoal3629SegmentPairOracleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = REVIEW.read_text(encoding="utf-8")

    def test_review_accepts_same_contract_oracle(self):
        self.assertIn("Gemini Review", self.review)
        self.assertIn("Verdict: accept", self.review)
        self.assertIn("segment_pair_left_id_dense_counts_reference", self.review)
        self.assertIn("strict-v0 predicate", self.review)
        self.assertIn("not a performance path", self.review)
        self.assertIn("does not authorize public claims", self.review)


if __name__ == "__main__":
    unittest.main()
