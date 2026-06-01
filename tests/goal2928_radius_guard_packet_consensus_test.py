from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2928_goal2924_2925_radius_guard_packet_consensus_2026-06-01.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2926_gemini_review_goal2924_2925_radius_guard_packet_2026-06-01.md"


class Goal2928RadiusGuardPacketConsensusTest(unittest.TestCase):
    def test_consensus_records_codex_gemini_acceptance_and_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "Goal2928",
            "Goal2924",
            "Goal2925",
            "Codex + Gemini 2-AI consensus",
            "accept-with-boundary",
            "rtdl_optix_ptx_compiler = \"nvcc\"",
            "near-parity, not a speedup claim",
            "does not authorize v2.5 release",
            "fresh 3-AI release consensus",
        ):
            self.assertIn(phrase, text)

    def test_gemini_review_is_saved_and_accepts_scope(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Verdict: accept", text)
        self.assertIn("Codex + Gemini 2-AI consensus", text)
        self.assertIn("does not authorize v2.5 release", text)
        self.assertIn("rtdl_optix_ptx_compiler = \"nvcc\"", text)


if __name__ == "__main__":
    unittest.main()
