import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "docs" / "reviews" / "claude_goal1639_collect_k_graph_direction_review_2026-05-09.md"
GEMINI = ROOT / "docs" / "reviews" / "gemini_goal1639_collect_k_graph_direction_review_2026-05-09.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal1639_v1_6_x_optix_collect_k_graph_direction_3ai_consensus_2026-05-09.md"


class Goal1639OptixCollectKGraphDirectionConsensusTest(unittest.TestCase):
    def test_external_reviews_are_recorded(self) -> None:
        claude = CLAUDE.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Do not revive the existing compact-level CUDA graph replay path", claude)
        self.assertIn("prepared end-to-end stable-topology graph", claude)
        self.assertIn("avoid", gemini)
        self.assertIn("prepared end-to-end stable-topology graph", gemini)

    def test_consensus_records_narrow_next_probe_and_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("`do_not_revive_old_per_level_graph_replay`", text)
        self.assertIn("Goal1637 shows the final-pair mark kernel is small", text)
        self.assertIn("Goal1638 shows a small positive graph replay signal", text)
        self.assertIn("segment_capacity=131072", text)
        self.assertIn("prepared stable-topology CUDA graph", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
