from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3605_gemini_review_goal3604_rayjoin_pip_signal_timing_2026-06-06.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL3604_RAYJOIN_PIP_SIGNAL_TIMING_REVIEW_2026-06-06.md"


class Goal3605GeminiReviewGoal3604RayJoinPipSignalTimingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = REVIEW.read_text(encoding="utf-8")
        cls.handoff = HANDOFF.read_text(encoding="utf-8")

    def test_review_is_independent_gemini_with_accepted_verdict(self):
        self.assertTrue(self.review.startswith("Verdict: accept"))
        self.assertIn("independent Gemini review", self.review)
        self.assertIn("distinct from Codex", self.review)

    def test_review_validates_correctness_and_negative_performance_result(self):
        self.assertIn("all_boundary_event_signal_counts_match_exact: true", self.review)
        self.assertIn("geomean_boundary_event_signal_speedup_vs_cupy: 0.028x", self.review)
        self.assertIn("not performance-ready", self.review)
        self.assertIn("approximately 35 times slower", self.review)

    def test_review_accepts_route_selection_and_generic_boundary(self):
        self.assertIn("CuPy dense CUDA-core scalar count", self.review)
        self.assertIn("prepared OptiX exact count", self.review)
        self.assertIn("against promoting the boundary-event selective route", self.review)
        self.assertIn("generic and app-agnostic", self.review)

    def test_review_keeps_claim_boundary_false(self):
        self.assertIn("claim boundaries are strong", self.review)
        self.assertIn("all set to `false`", self.review)
        self.assertIn("unauthorized claims", self.review)
        self.assertIn("Do not edit source", self.handoff)


if __name__ == "__main__":
    unittest.main()
