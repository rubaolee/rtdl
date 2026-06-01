from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2931_goal2929_tier_c_10_benchmark_consensus_2026-06-01.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2930_gemini_review_goal2929_tier_c_10_benchmark_foundation_2026-06-01.md"


class Goal2931TierCTenBenchmarkConsensusTest(unittest.TestCase):
    def test_consensus_records_goal2929_codex_gemini_acceptance(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "Goal2931",
            "Goal2929",
            "Codex + Gemini 2-AI consensus",
            "accept-with-boundary",
            "seven apps in the current canonical packet",
            "same-contract performance gate",
            "Tier C no-regression smoke",
            "does not authorize v2.5 release",
            "Fresh 3-AI release consensus remains required",
        ):
            self.assertIn(phrase, text)

    def test_gemini_review_accepts_internal_scope_and_boundaries(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("**Verdict:** `accept`", text)
        self.assertIn("Codex + Gemini 2-AI consensus is appropriate", text)
        self.assertIn("does NOT authorize v2.5 release", text)
        self.assertIn("Tier C no-regression", text)
        self.assertIn("No issues found", text)


if __name__ == "__main__":
    unittest.main()
