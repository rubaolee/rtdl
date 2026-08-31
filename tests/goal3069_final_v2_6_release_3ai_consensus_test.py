from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal3069_final_v2_6_release_3ai_consensus_2026-06-02.md"
CODEX_REPORT = ROOT / "docs" / "reports" / "goal3066_v2_6_release_action_2026-06-02.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal3067_claude_final_v2_6_release_review_2026-06-02.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal3068_gemini_final_v2_6_release_review_2026-06-02.md"
RELEASE_README = ROOT / "docs" / "release_reports" / "v2_6" / "README.md"


class Goal3069FinalV26Release3AiConsensusTest(unittest.TestCase):
    def test_consensus_records_three_distinct_ai_inputs(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertTrue(CODEX_REPORT.exists())
        self.assertTrue(CLAUDE_REVIEW.exists())
        self.assertTrue(GEMINI_REVIEW.exists())

        for name in ("Codex", "Claude", "Gemini"):
            self.assertIn(name, text)

        self.assertIn(CODEX_REPORT.name, text)
        self.assertIn(CLAUDE_REVIEW.name, text)
        self.assertIn(GEMINI_REVIEW.name, text)

    def test_consensus_authorizes_v2_6_tag_with_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("final 3-AI consensus authorizing the `v2.6` source-tree release tag", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("committed tree is ready to tag as", text)
        self.assertIn("Ran 18 tests in 0.733s", text)
        self.assertIn("Ran 21 tests", text)
        self.assertIn("may be tagged `v2.6`", claude)
        self.assertIn("acceptable to proceed", gemini)

        blocked = [
            "package-install or PyPI claims",
            "broad RT-core speedup claims",
            "whole-application speedup claims",
            "arbitrary PyTorch, CuPy, Numba, or Triton acceleration claims",
            "automatic partner-selection claims",
            "general zero-copy/device-residency claims",
        ]
        for phrase in blocked:
            self.assertIn(phrase, text)

    def test_release_package_and_version_marker_align(self) -> None:
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "v2.6")

        package = RELEASE_README.read_text(encoding="utf-8")
        self.assertIn("Version marker: `v2.6`", package)
        self.assertIn("released source-tree", package)
        self.assertIn("not a package-install release", package)


if __name__ == "__main__":
    unittest.main()
