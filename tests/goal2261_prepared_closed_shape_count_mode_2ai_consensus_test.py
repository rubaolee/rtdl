from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2261_prepared_closed_shape_count_mode_2ai_consensus_2026-05-17.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2260_gemini_review_goal2258_2259_count_mode_2026-05-17.md"


class Goal2261PreparedClosedShapeCountMode2AiConsensusTest(unittest.TestCase):
    def test_consensus_records_count_evidence(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("0.041955990716814995", text)
        self.assertIn("0.05280204117298126", text)
        self.assertIn("8,686", text)
        self.assertIn("1.26x", text)

    def test_gemini_review_accepts(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("Verdict:** accept", text)

    def test_boundary_stays_narrow(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("does not authorize", text)
        self.assertIn("RTDL-beats-RayJoin", text)
        self.assertIn("true device-resident output-stream", text)


if __name__ == "__main__":
    unittest.main()
