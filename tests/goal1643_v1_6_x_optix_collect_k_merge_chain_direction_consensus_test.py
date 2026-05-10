import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "docs" / "reviews" / "claude_goal1643_collect_k_merge_chain_direction_review_2026-05-09.md"
GEMINI = ROOT / "docs" / "reviews" / "gemini_goal1643_collect_k_merge_chain_direction_review_2026-05-09.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal1643_v1_6_x_optix_collect_k_merge_chain_direction_3ai_consensus_2026-05-09.md"


class Goal1643OptixCollectKMergeChainDirectionConsensusTest(unittest.TestCase):
    def test_external_reviews_support_merge_chain_direction(self) -> None:
        claude = CLAUDE.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")

        self.assertIn("shifting the primary optimization target to the merge chain", claude)
        self.assertIn("Capture the merge chain into a CUDA graph", claude)
        self.assertIn("focus on the merge chain itself", gemini)
        self.assertIn("Reduce the number of merge launches", gemini)

    def test_consensus_keeps_next_candidate_diagnostic_and_bounded(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("`shift_next_target_to_merge_chain`", text)
        self.assertIn("Goal1642 shows deferred merge GPU work", text)
        self.assertIn("opt-in merge-chain diagnostic", text)
        self.assertIn("not a production flag", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
