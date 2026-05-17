from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2265_exact_prepared_closed_shape_count_2ai_consensus_2026-05-17.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2264_gemini_review_goal2262_2263_exact_count_2026-05-17.md"


class Goal2265ExactPreparedClosedShapeCount2AiConsensusTest(unittest.TestCase):
    def test_consensus_records_exact_count_evidence(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("0.04043779522180557", text)
        self.assertIn("0.055270278826355934", text)
        self.assertIn("8,686", text)
        self.assertIn("1.37x", text)
        self.assertIn("1.04x", text)

    def test_gemini_review_accepts(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("`accept`", text)

    def test_boundary_stays_narrow(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("does not authorize", text)
        self.assertIn("RTDL-beats-RayJoin", text)
        self.assertIn("true device-resident output-stream", text)


if __name__ == "__main__":
    unittest.main()
