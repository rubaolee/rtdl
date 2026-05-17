from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2287_packed_left_segment_pair_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2286_gemini_review_goal2284_2285_packed_left_2026-05-17.md"


class Goal2287PackedLeftSegmentPair2AiConsensusTest(unittest.TestCase):
    def test_consensus_cites_distinct_external_review(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        review = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Gemini/Antigravity verdict: `accept`", text)
        self.assertIn("**Reviewer:** Gemini (Antigravity)", review)
        self.assertIn("**Outcome:** accept", review)
        self.assertIn("Codex verdict: `accept`", text)

    def test_consensus_keeps_narrow_packed_left_claim(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("one recorded RTX A5000 pod", text)
        self.assertIn("RayJoin-exported 100k LSI stream", text)
        self.assertIn("about `20x`", text)
        self.assertIn("not a new engine specialization", text)

    def test_consensus_preserves_not_allowed_claims(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Not allowed", text)
        self.assertIn("whole RayJoin application speedup", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("true zero-copy", text)
        self.assertIn("claim that all workloads get a 20x gain", text)


if __name__ == "__main__":
    unittest.main()
