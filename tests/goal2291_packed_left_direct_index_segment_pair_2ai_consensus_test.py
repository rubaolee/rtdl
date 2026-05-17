from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2291_packed_left_direct_index_segment_pair_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2290_gemini_review_goal2289_direct_index_packed_left_2026-05-17.md"


class Goal2291PackedLeftDirectIndexSegmentPair2AiConsensusTest(unittest.TestCase):
    def test_consensus_cites_codex_and_gemini_verdicts(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        review = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Codex verdict: `accept-with-boundary`", text)
        self.assertIn("Gemini/Antigravity verdict: `accept-with-boundary`", text)
        self.assertIn("# Goal2290: Gemini Review For Goal2289", review)
        self.assertIn("**Verdict:** `accept-with-boundary`", review)

    def test_consensus_keeps_goal2280_rejection_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("This does not overturn Goal2280", text)
        self.assertIn("tuple-input direct-index experiment remains", text)
        self.assertIn("Not allowed", text)
        self.assertIn("Goal2280's tuple-input rejection is overturned", text)

    def test_consensus_keeps_narrow_measured_claim(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("one recorded RTX A5000 pod", text)
        self.assertIn("RayJoin-exported 100k LSI stream", text)
        self.assertIn("prepacked-left contract", text)
        self.assertIn("1.095x", text)
        self.assertIn("1.252x", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("true zero-copy", text)


if __name__ == "__main__":
    unittest.main()
