from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal3029_gemini_review_goal3025_3028_hausdorff_tuning_2026-06-02.md"
HANDOFF = REPO_ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL3025_3028_HAUSDORFF_TUNING_REVIEW_2026-06-02.md"


class Goal3029GeminiReviewGoal3025To3028HausdorffTuningTest(unittest.TestCase):
    def test_review_has_required_verdict_and_scope(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")
        for phrase in (
            "Verdict: accept",
            "Goal 3025",
            "Goal 3026",
            "Goal 3028",
            "raw row-view",
            "no crossover occurs",
            "No public speedup, v2.6 release, or broad RT-core claims are made",
            "independent Gemini review distinct from Codex authoring",
        ):
            self.assertIn(phrase, text)

    def test_handoff_pins_allowed_verdict_values_and_release_boundary(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        for phrase in (
            "Verdict: accept",
            "Verdict: accept-with-boundary",
            "Verdict: needs-more-evidence",
            "Verdict: reject",
            "This is not a release review",
            "must not authorize v2.6 release",
            "speedup claims",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
