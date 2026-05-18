import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2314_prepared_closed_shape_raw_row_view_2ai_consensus_2026-05-17.md"
CODEX = ROOT / "docs" / "reports" / "goal2312_prepared_closed_shape_raw_row_view_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2313_gemini_review_goal2312_raw_row_view_rayjoin_perf_2026-05-17.md"


class Goal2314PreparedClosedShapeRawRowView2AiConsensusTest(unittest.TestCase):
    def test_consensus_artifacts_exist_and_use_allowed_verdicts(self) -> None:
        self.assertTrue(CODEX.exists())
        self.assertTrue(GEMINI.exists())
        text = CONSENSUS.read_text(encoding="utf-8")
        review = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Goal2314", text)
        self.assertIn("Codex", text)
        self.assertIn("Gemini", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("accept-with-boundary", review)

    def test_consensus_records_bounded_perf_claim_and_release_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("0.008657", text)
        self.assertIn("0.008476", text)
        self.assertIn("8,686", text)
        self.assertIn("RTDL beats the RayJoin paper implementation", text)
        self.assertIn("v2.0 release authorization", text)
        self.assertIn("row-stream / continuation", text)


if __name__ == "__main__":
    unittest.main()
