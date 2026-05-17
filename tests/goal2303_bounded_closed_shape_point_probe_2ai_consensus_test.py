import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2303_bounded_closed_shape_point_probe_2ai_consensus_2026-05-17.md"
CODEX = ROOT / "docs" / "reports" / "goal2301_bounded_closed_shape_point_probe_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2302_gemini_review_goal2301_bounded_closed_shape_probe_2026-05-17.md"


class Goal2303BoundedClosedShapePointProbe2AIConsensusTest(unittest.TestCase):
    def test_consensus_references_distinct_codex_and_gemini_inputs(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertTrue(CODEX.exists())
        self.assertTrue(GEMINI.exists())
        self.assertIn("Codex implementation/report", text)
        self.assertIn("Gemini independent review", text)
        self.assertIn("accept-with-boundary", text)

    def test_consensus_preserves_narrow_performance_claim(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("100,000-query", text)
        self.assertIn("8686", text)
        self.assertIn("2.808x", text)
        self.assertIn("4.885x", text)

    def test_consensus_keeps_release_and_generality_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("fixed `0.5` half-length", text)
        self.assertIn("current RayJoin-exported", text)
        self.assertIn("coordinate scale only", text)
        self.assertIn("does not authorize a RayJoin paper reproduction claim", text)
        self.assertIn("does not authorize an RTDL-beats-RayJoin claim", text)
        self.assertIn("does not authorize broad whole-app speedup", text)
        self.assertIn("true zero-copy", text)
        self.assertIn("v2.0", text)
        self.assertIn("release readiness", text)


if __name__ == "__main__":
    unittest.main()
