import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2310_bounded_probe_scale_smoke_2ai_consensus_2026-05-17.md"
REPORT = ROOT / "docs" / "reports" / "goal2308_bounded_probe_scale_smoke_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2309_gemini_review_goal2308_bounded_probe_scale_smoke_2026-05-17.md"


class Goal2310BoundedProbeScaleSmoke2AIConsensusTest(unittest.TestCase):
    def test_consensus_references_codex_and_gemini(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertTrue(REPORT.exists())
        self.assertTrue(GEMINI.exists())
        self.assertIn("Codex report", text)
        self.assertIn("Gemini independent review", text)
        self.assertIn("accept-with-boundary", text)

    def test_consensus_preserves_smoke_scope(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("one synthetic point inside one synthetic closed shape", text)
        self.assertIn("No broad coordinate-scale validation", text)
        self.assertIn("No broad performance validation", text)
        self.assertIn("No RayJoin reproduction", text)
        self.assertIn("No v2.0 release authorization", text)


if __name__ == "__main__":
    unittest.main()
