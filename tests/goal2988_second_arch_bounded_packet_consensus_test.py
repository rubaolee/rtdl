from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = (
    ROOT
    / "docs"
    / "reports"
    / "goal2988_goal2984_2985_second_arch_bounded_packet_consensus_2026-06-01.md"
)
GEMINI_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2986_gemini_review_goal2984_2985_second_arch_bounded_packet_2026-06-01.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2987_claude_review_goal2984_2985_second_arch_bounded_packet_2026-06-01.md"
)


class Goal2988SecondArchBoundedPacketConsensusTest(unittest.TestCase):
    def test_external_reviews_accept_with_boundary(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")

        for text in (gemini, claude):
            self.assertIn("accept-with-boundary", text)
            self.assertIn("7/7", text)
            self.assertIn("second_arch_bounded", text)
            self.assertIn("does not authorize", text)

    def test_consensus_records_carry_forward_conditions(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "Consensus verdict: **accept-with-boundary**",
            "Goal2984",
            "Goal2985",
            "Goal2977 gap is closed",
            "8192-body Embree CPU baseline remains unmeasured",
            "Validation scope",
            "does not authorize",
            "3-AI release consensus",
        ):
            self.assertIn(phrase, text)

    def test_readiness_indexes_reviews_and_keeps_claims_blocked(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2988_goal2984_2985_second_arch_bounded_packet_consensus_2026-06-01.md"
            ]
        )
        self.assertTrue(
            packet["external_review_presence"][
                "docs/reviews/goal2986_gemini_review_goal2984_2985_second_arch_bounded_packet_2026-06-01.md"
            ]
        )
        self.assertTrue(
            packet["external_review_presence"][
                "docs/reviews/goal2987_claude_review_goal2984_2985_second_arch_bounded_packet_2026-06-01.md"
            ]
        )
        self.assertIn(
            "use_goal2988_second_arch_bounded_packet_consensus_before_release_packet",
            packet["allowed_next_actions"],
        )
        self.assertEqual("accept", validation["status"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])


if __name__ == "__main__":
    unittest.main()
