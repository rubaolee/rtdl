from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2983_claude_review_intake_goal2981_v2_5_closeout_2026-06-01.md"
)
REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2981_claude_review_v2_5_closeout_positioning_and_external_review_packet_2026-06-01.md"
)


class Goal2983ClaudeReviewIntakeTest(unittest.TestCase):
    def test_claude_review_accepts_closeout_with_release_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "accept-with-boundary",
            "primitive-first fast path",
            "partners only for unfused continuations",
            "neutral seam scoped out",
            "no release/speedup/zero-copy/Triton/paper-reproduction overclaim",
            "Barnes-Hut Embree baseline gap",
            "fresh 3-AI consensus",
        ):
            self.assertIn(phrase, text)

    def test_intake_report_carries_forward_release_gate_findings(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2983",
            "Claude verdict: `accept-with-boundary`",
            "Barnes-Hut 8192-body Embree baseline",
            "RT-core ratios internal-only",
            "neutral-seam fix as deferred work",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_readiness_indexes_claude_review_and_keeps_claims_blocked(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2983_claude_review_intake_goal2981_v2_5_closeout_2026-06-01.md"
            ]
        )
        self.assertTrue(
            packet["external_review_presence"][
                "docs/reviews/goal2981_claude_review_v2_5_closeout_positioning_and_external_review_packet_2026-06-01.md"
            ]
        )
        self.assertIn("triage_goal2983_claude_review_before_release_packet", packet["allowed_next_actions"])
        self.assertEqual("accept", validation["status"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertFalse(packet["claim_authorization"]["public_speedup_claim_authorized"])
        self.assertFalse(packet["claim_authorization"]["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
