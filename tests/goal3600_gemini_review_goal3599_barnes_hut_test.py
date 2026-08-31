from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs/reviews/goal3600_gemini_review_goal3599_barnes_hut_resident_repeat_2026-06-06.md"
HANDOFF = ROOT / "docs/handoff/HANDOFF_GEMINI_GOAL3599_BARNES_HUT_RESIDENT_REPEAT_REVIEW_2026-06-06.md"


class Goal3600GeminiReviewGoal3599BarnesHutTest(unittest.TestCase):
    def test_review_exists_with_independent_verdict(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Verdict: accept-with-boundary", text)
        self.assertIn("independent Gemini review, distinct from Codex", text)
        self.assertIn("Goal3599 genuinely closes", text)
        self.assertIn("silent-partial-row issue", text)

    def test_review_keeps_comparison_and_claim_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "decision not to publish a v2.9-vs-v2.3 speedup ratio is correct",
            "direct, comparable v2.3 baseline remains impossible",
            "claim boundaries are strong",
            "public release",
            "speedup",
            "true zero-copy",
            "automatic-dispatch",
        ):
            self.assertIn(phrase, text)

    def test_handoff_names_required_files_and_questions(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        for phrase in (
            "docs/reports/goal3599_barnes_hut_node_coverage_resident_repeat_2026-06-06.md",
            "tests/goal3599_barnes_hut_node_coverage_resident_repeat_test.py",
            "Does Goal3599 genuinely close",
            "Are the claim boundaries strong enough",
            "Do not edit source or report files except for writing the review file",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
