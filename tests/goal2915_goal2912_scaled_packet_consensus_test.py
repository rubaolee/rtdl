import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = (
    ROOT
    / "docs"
    / "reports"
    / "goal2915_goal2912_scaled_v2_5_packet_external_review_consensus_2026-06-01.md"
)
GEMINI = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2913_gemini_review_goal2907_2912_scaled_v2_5_perf_packet_2026-05-31.md"
)
CLAUDE = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2914_claude_review_goal2907_2912_scaled_v2_5_perf_packet_2026-05-31.md"
)


class Goal2915Goal2912ScaledPacketConsensusTest(unittest.TestCase):
    def test_external_reviews_exist_and_accept_with_boundary(self) -> None:
        gemini = GEMINI.read_text(encoding="utf-8")
        claude = CLAUDE.read_text(encoding="utf-8")

        self.assertIn("Reviewer: Gemini", gemini)
        self.assertIn("Reviewer: Claude", claude)
        self.assertIn("accept-with-boundary", gemini)
        self.assertIn("accept-with-boundary", claude)

    def test_consensus_records_distinct_external_reviewers(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Codex, Gemini, and Claude agree", text)
        self.assertIn("Goal2912 packet is internally coherent", text)
        self.assertIn("no active performance targets", text)
        self.assertIn("benchmark stabilization", text)
        self.assertIn("no app-specific native engine logic was added", text)

    def test_consensus_keeps_release_boundary_blocked(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("not a v2.5 release consensus", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("fresh 3-AI release review", text)


if __name__ == "__main__":
    unittest.main()
