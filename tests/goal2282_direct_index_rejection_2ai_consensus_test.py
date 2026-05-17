from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2282_direct_index_rejection_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2281_gemini_review_goal2280_direct_index_negative_probe_2026-05-17.md"
SUMMARY = ROOT / "docs" / "reports" / "goal2280_direct_index_ab_same_pod_summary_2026-05-17.json"


class Goal2282DirectIndexRejection2AiConsensusTest(unittest.TestCase):
    def test_consensus_cites_distinct_external_review(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        review = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Gemini/Antigravity verdict: `accept`", text)
        self.assertIn("independent review by Gemini/Antigravity", review)
        self.assertIn("Codex verdict: `accept`", text)

    def test_consensus_uses_canonical_same_pod_numbers(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn(str(SUMMARY.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn("raw witness rows regressed", text)
        self.assertIn("`0.944x`", text)
        self.assertIn("`1.004x`", text)

    def test_consensus_preserves_claim_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("direct-index host exact refinement is not an accepted v2.0 performance win", text)
        self.assertIn("without RayJoin-specific native", text)
        self.assertIn("engine logic", text)
        self.assertIn("Not allowed", text)
        self.assertIn("RTDL beats RayJoin claim", text)


if __name__ == "__main__":
    unittest.main()
