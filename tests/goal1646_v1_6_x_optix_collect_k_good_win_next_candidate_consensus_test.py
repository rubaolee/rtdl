import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "docs" / "reviews" / "claude_goal1645_collect_k_next_good_win_candidate_2026-05-09.md"
GEMINI = ROOT / "docs" / "reviews" / "gemini_goal1645_collect_k_next_good_win_candidate_2026-05-09.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal1646_v1_6_x_optix_collect_k_good_win_next_candidate_3ai_consensus_2026-05-09.md"


class Goal1646OptixCollectKGoodWinNextCandidateConsensusTest(unittest.TestCase):
    def test_external_reviews_are_recorded(self) -> None:
        claude = CLAUDE.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Cooperative-kernel fused merge chain", claude)
        self.assertIn("128-bit Vector Loads", gemini)

    def test_consensus_selects_merge_chain_restructure_after_negatives(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("`next_good_win_requires_merge_chain_restructure`", text)
        self.assertIn("vector-load candidate preserved parity but regressed performance", text)
        self.assertIn("cooperative or multi-level merge-chain probe", text)
        self.assertIn("do not enable it by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
