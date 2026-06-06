from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3614_gemini_review_goal3612_3613_rayjoin_safe_fast_lsi_repair_2026-06-06.md"


class Goal3614GeminiReviewGoal3612_3613RayJoinSafeFastLsiRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = REVIEW.read_text(encoding="utf-8")

    def test_review_accepts_with_boundary(self):
        self.assertIn("## Verdict: accept-with-boundary", self.review)
        self.assertIn("193.939x", self.review)
        self.assertIn("188.997x", self.review)
        self.assertIn("2032.908x", self.review)
        self.assertIn("No RayJoin or CDB logic enters the engine", self.review)

    def test_review_records_remaining_public_claim_risks(self):
        self.assertIn("Float Strict Predicate vs. Host Double Exact Refinement", self.review)
        self.assertIn("Limited Dataset Diversity", self.review)
        self.assertIn("documented primitive contract", self.review)
        self.assertIn("Provenance Note", self.review)


if __name__ == "__main__":
    unittest.main()
