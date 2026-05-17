from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2295_prepared_closed_shape_phase_telemetry_2026-05-17.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2297_prepared_closed_shape_phase_telemetry_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2296_gemini_review_goal2295_closed_shape_telemetry_2026-05-17.md"


class Goal2297PreparedClosedShapePhaseTelemetry2AiConsensusTest(unittest.TestCase):
    def test_consensus_cites_gemini_acceptance(self) -> None:
        consensus = CONSENSUS.read_text(encoding="utf-8")
        review = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Codex verdict: `accept`", consensus)
        self.assertIn("Gemini/Antigravity verdict: `accept`", consensus)
        self.assertIn("**accept**", review)
        self.assertIn("candidate traversal/write is the largest measured native phase", review)

    def test_consensus_keeps_diagnostic_boundary(self) -> None:
        consensus = CONSENSUS.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("This is instrumentation, not a speedup goal", consensus)
        self.assertIn("Status: accepted with Goal2297 2-AI consensus.", report)
        self.assertIn("Not allowed", consensus)
        self.assertIn("RTDL beats RayJoin", consensus)
        self.assertIn("true zero-copy", consensus)
        self.assertIn("v2.0 release readiness", consensus)


if __name__ == "__main__":
    unittest.main()
