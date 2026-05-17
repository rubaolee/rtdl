from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL2161_RAYJOIN_CUPY_NON_RT_BASELINE_REVIEW_2026-05-16.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2162_gemini_review_goal2161_rayjoin_cupy_non_rt_baseline_2026-05-16.md"


class Goal2162GeminiReviewGoal2161RayjoinCupyNonRtBaselineTest(unittest.TestCase):
    def test_review_records_independent_accept_verdict(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("distinct from Codex", text)
        self.assertIn("does not authorize v2.0 release by itself", text)
        self.assertIn("Verdict", text)
        self.assertIn("accept", text)

    def test_review_accepts_negative_result_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("non-RT CUDA-core baseline", text)
        self.assertIn("CuPy baseline outperforms OptiX", text)
        self.assertIn("strong claim boundaries", text)

    def test_handoff_names_expected_review_output(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("goal2162_gemini_review_goal2161_rayjoin_cupy_non_rt_baseline_2026-05-16.md", text)
        self.assertIn("cupy_lsi_bruteforce", text)


if __name__ == "__main__":
    unittest.main()
