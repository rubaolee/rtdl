from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2292_rayjoin_current_prepared_comparison_2026-05-17.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2294_rayjoin_current_prepared_comparison_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2293_gemini_review_goal2292_current_rayjoin_comparison_2026-05-17.md"


class Goal2294RayJoinCurrentPreparedComparison2AiConsensusTest(unittest.TestCase):
    def test_consensus_cites_gemini_acceptance(self) -> None:
        consensus = CONSENSUS.read_text(encoding="utf-8")
        review = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Codex verdict: `accept`", consensus)
        self.assertIn("Gemini/Antigravity verdict: `accept`", consensus)
        self.assertIn("**`accept`**", review)
        self.assertIn("Goal2292 report, script, and artifact are consistent", review)

    def test_consensus_marks_current_routes_without_release_overclaim(self) -> None:
        consensus = CONSENSUS.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("prepared segment-pair intersection with a prepacked left/query batch", consensus)
        self.assertIn("prepared closed-shape membership with prepacked points", consensus)
        self.assertIn("Status: accepted with Goal2294 2-AI consensus.", report)
        self.assertIn("Not allowed", consensus)
        self.assertIn("RTDL beats RayJoin", consensus)
        self.assertIn("true zero-copy", consensus)
        self.assertIn("v2.0 release readiness", consensus)


if __name__ == "__main__":
    unittest.main()
