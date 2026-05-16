from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2149_gemini_review_goal2147_linux_evidence_addendum_2026-05-16.md"


class Goal2149GeminiReviewGoal2147LinuxEvidenceAddendumTest(unittest.TestCase):
    def test_review_accepts_linux_evidence_addendum_with_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "independent Gemini review",
            "distinct from Codex",
            "accept",
            "dirty primary Linux checkout",
            "rt_core_speedup_claim_authorized",
            "cold-start outlier",
            "without exceeding the defined claims",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
