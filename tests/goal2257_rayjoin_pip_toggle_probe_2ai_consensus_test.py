from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2257_rayjoin_pip_toggle_probe_2ai_consensus_2026-05-17.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2256_gemini_review_goal2255_rayjoin_pip_toggle_probe_2026-05-17.md"


class Goal2257RayjoinPipToggleProbe2AiConsensusTest(unittest.TestCase):
    def test_consensus_records_toggle_ratios(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("0.06666836328804493", text)
        self.assertIn("0.5072881113737822", text)
        self.assertIn("0.09405476413667202", text)
        self.assertIn("7.61x", text)
        self.assertIn("1.41x", text)

    def test_gemini_review_accepts(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("Verdict:** accept", text)

    def test_boundary_remains_diagnostic(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("diagnostic only", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.0 release readiness", text)


if __name__ == "__main__":
    unittest.main()
