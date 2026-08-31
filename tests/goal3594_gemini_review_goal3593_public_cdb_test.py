from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3594_gemini_review_goal3593_rayjoin_public_cdb_cupy_same_contract_2026-06-06.md"


class Goal3594GeminiReviewGoal3593PublicCdbTest(unittest.TestCase):
    def test_review_accepts_with_boundaries_and_names_independence(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")
        for phrase in (
            "Verdict: accept-with-boundary",
            "independent Gemini review",
            "distinct from Codex",
            "Consistent Same-Contract Comparison Boundary",
            "Strong Claim Boundaries",
            "Git Cleanliness for Artifact Generation",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
