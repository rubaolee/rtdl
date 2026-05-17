from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2268_prepared_closed_shape_count_scale_probe_2ai_consensus_2026-05-17.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2267_gemini_review_goal2266_count_scale_probe_2026-05-17.md"


class Goal2268PreparedClosedShapeCountScaleProbe2AiConsensusTest(unittest.TestCase):
    def test_consensus_records_scale_table(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("1,000,000", text)
        self.assertIn("0.3518645130097866", text)
        self.assertIn("0.4656780920922756", text)
        self.assertIn("0.7555960200508284", text)

    def test_gemini_review_accepts(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("independent Gemini review", text)
        self.assertIn("Verdict:** accept", text)

    def test_boundary_stays_synthetic(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("synthetic repeated-stream diagnostic", text)
        self.assertIn("does not authorize", text)
        self.assertIn("true device-resident output-stream", text)


if __name__ == "__main__":
    unittest.main()
