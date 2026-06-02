from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal3065_v2_6_native_tutorial_validation_3ai_consensus_2026-06-02.md"
CODEX_REPORT = ROOT / "docs" / "reports" / "goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal3063_claude_review_goal3062_v2_6_native_tutorial_validation_2026-06-02.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal3064_gemini_review_goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.md"


class Goal3065V26NativeTutorialValidation3AiConsensusTest(unittest.TestCase):
    def test_consensus_records_three_distinct_ai_inputs(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertTrue(CODEX_REPORT.exists())
        self.assertTrue(CLAUDE_REVIEW.exists())
        self.assertTrue(GEMINI_REVIEW.exists())

        for name in ["Codex", "Claude", "Gemini"]:
            self.assertIn(name, text)

        self.assertIn(CODEX_REPORT.name, text)
        self.assertIn(CLAUDE_REVIEW.name, text)
        self.assertIn(GEMINI_REVIEW.name, text)

    def test_consensus_accepts_native_validation_with_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Consensus Verdict", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("21/21", text)
        self.assertIn("Ran 17 tests ... OK", text)
        self.assertIn("Ran 35 tests ...", text)
        self.assertIn("No overclaim was found", claude)
        self.assertIn("accept-with-boundary", gemini)

        blocked = [
            "tagging or publishing v2.6",
            "package-install claims",
            "broad RT-core or whole-app speedup claims",
            "automatic partner-selection claims",
            "general zero-copy/device-residency claims",
        ]
        for phrase in blocked:
            self.assertIn(phrase, text)

    def test_remaining_release_decision_is_explicit(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("press the v2.6 release button", text)
        self.assertIn("final release consensus packet", text)
        self.assertIn("does not authorize", text)
        self.assertNotIn("release authorized", text.lower())


if __name__ == "__main__":
    unittest.main()
