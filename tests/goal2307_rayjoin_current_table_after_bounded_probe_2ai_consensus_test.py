import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2307_rayjoin_current_table_after_bounded_probe_2ai_consensus_2026-05-17.md"
REPORT = ROOT / "docs" / "reports" / "goal2305_rayjoin_current_prepared_comparison_after_bounded_probe_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2306_gemini_review_goal2305_current_rayjoin_table_2026-05-17.md"


class Goal2307RayjoinCurrentTableAfterBoundedProbe2AIConsensusTest(unittest.TestCase):
    def test_consensus_has_codex_and_gemini_inputs(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertTrue(REPORT.exists())
        self.assertTrue(GEMINI.exists())
        self.assertIn("Codex report", text)
        self.assertIn("Gemini independent review", text)
        self.assertIn("accept-with-boundary", text)

    def test_consensus_records_current_table_values(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for value in ("0.008976681", "0.008994997", "0.023158047", "0.009362523"):
            self.assertIn(value, text)
        self.assertIn("8921", text)
        self.assertIn("8686", text)

    def test_consensus_preserves_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("RayJoin paper reproduction", text)
        self.assertIn("RTDL-beats-RayJoin", text)
        self.assertIn("whole-app speedup", text)
        self.assertIn("True zero-copy", text)
        self.assertIn("v2.0 release readiness", text)
        self.assertIn("validated only on the current", text)


if __name__ == "__main__":
    unittest.main()
