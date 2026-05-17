from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2172_gemini_review_goal2171_rayjoin_overlay_seed_baseline_2026-05-16.md"


class Goal2172GeminiReviewGoal2171RayjoinOverlaySeedBaselineTest(unittest.TestCase):
    def test_review_records_independent_acceptance_with_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("`accept`", text)
        self.assertIn("independent Gemini review", text)
        self.assertIn("does not, by itself, authorize a v2.0 release", text)
        self.assertIn("0.15251125488430262", text)
        self.assertIn("0.02216548379510641", text)
        self.assertIn("0.025159044191241264", text)
        self.assertIn("OptiX is RT-core-accelerated but still slower than Embree", text)
        self.assertIn("prepared/reused generic OptiX shape-pair relation", text)
        self.assertIn("block unauthorized broader claims", text)


if __name__ == "__main__":
    unittest.main()
