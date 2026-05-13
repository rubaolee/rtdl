from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1920_gemini_followup_goal1912_post_pod_review_correction_2026-05-13.md"


class Goal1920GeminiFollowupGoal1912PostPodReviewCorrectionTest(unittest.TestCase):
    def test_followup_corrects_flash_and_fixed_radius_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Gemini Flash", text)
        self.assertIn("does not fulfill the requirement for a Claude-or-Pro-class review", text)
        self.assertIn("Fixed-radius artifacts", text)
        self.assertIn("do not", text)
        self.assertIn("`partner_output_columns_true_zero_copy_authorized: true`", text)
        self.assertIn("segment/polygon", text)
        self.assertIn("road-hazard", text)
        self.assertIn("`needs-more-evidence`", text)


if __name__ == "__main__":
    unittest.main()
