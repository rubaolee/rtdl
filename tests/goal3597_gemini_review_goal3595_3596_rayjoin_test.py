from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3597_gemini_review_goal3595_3596_rayjoin_public_cdb_stability_pip_audit_2026-06-06.md"


class Goal3597GeminiReviewGoal3595And3596RayJoinTest(unittest.TestCase):
    def test_review_accepts_with_boundary_and_names_next_step(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")
        for phrase in (
            "Verdict: accept-with-boundary",
            "independent Gemini review",
            "distinct from Codex",
            "Git-Cleanliness Concern Addressed",
            "PIP Route Conclusion Supported by Probes",
            "Robust Avoidance of Overclaiming Authority",
            "generic exact point-in-closed-shape count primitive",
            "not a RayJoin-specific native path",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
