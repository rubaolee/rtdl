import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2073_final_v2_0_release_consensus_2026-05-15.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2070_gemini_review_goal2068_2069_final_v2_gate_2026-05-15.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal2071_claude_review_goal2068_2069_final_v2_gate_2026-05-15.md"


class Goal2073FinalV20ReleaseConsensusTest(unittest.TestCase):
    def test_external_reviews_exist_and_accept_with_boundary(self):
        self.assertTrue(GEMINI.exists())
        self.assertTrue(CLAUDE.exists())
        self.assertIn("accept-with-boundary", GEMINI.read_text(encoding="utf-8").lower())
        self.assertIn("accept-with-boundary", CLAUDE.read_text(encoding="utf-8").lower())

    def test_consensus_records_distinct_ai_reviewers(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Codex",
            "Gemini",
            "Claude",
            "distinct external AI families",
            "Codex+Codex does not count",
            "`accept-with-boundary`",
        ):
            self.assertIn(phrase, text)

    def test_consensus_preserves_release_claim_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "explicit user-requested release action missing",
            "all apps are faster in v2.0",
            "broad RT-core speedup",
            "whole-app speedup",
            "arbitrary PyTorch/CuPy program acceleration",
            "package-install support",
            "full witness-row materialization solved",
            "arbitrary polygon overlay solved",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
