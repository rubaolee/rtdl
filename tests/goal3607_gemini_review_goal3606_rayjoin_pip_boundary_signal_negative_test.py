from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3607_gemini_review_goal3606_rayjoin_pip_boundary_signal_negative_2026-06-06.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL3606_RAYJOIN_PIP_BOUNDARY_SIGNAL_NEGATIVE_REVIEW_2026-06-06.md"


class Goal3607GeminiReviewGoal3606RayJoinPipBoundarySignalNegativeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = REVIEW.read_text(encoding="utf-8")
        cls.handoff = HANDOFF.read_text(encoding="utf-8")

    def test_review_is_independent_gemini_acceptance(self):
        self.assertTrue(self.review.startswith("Verdict: accept"))
        self.assertIn("independent Gemini review", self.review)
        self.assertIn("distinct from Codex", self.review)

    def test_review_confirms_signal_fails_all_tested_tolerances(self):
        self.assertIn("fails to achieve exactness", self.review)
        self.assertIn("0, 1e-6, 1e-5, 1e-4, 1e-3", self.review)
        self.assertIn("all_tolerances_match_exact: false", self.review)

    def test_review_blocks_default_route_and_reaffirms_guidance(self):
        self.assertIn("blocks the boundary-event signal family from default-route promotion", self.review)
        self.assertIn("CuPy dense for public-CDB PIP scalar count", self.review)
        self.assertIn("prepared OptiX exact", self.review)
        self.assertIn("future fused generic closed-shape membership/count primitive", self.review)

    def test_review_and_handoff_keep_claim_boundaries(self):
        self.assertIn("claim boundaries", self.review)
        self.assertIn("all its boolean fields set to `false`", self.review)
        self.assertIn("Do not edit source", self.handoff)


if __name__ == "__main__":
    unittest.main()
