from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2982_gemini_review_intake_goal2981_v2_5_closeout_2026-06-01.md"
)
REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "gemini_goal2981_v2_5_closeout_positioning_and_external_review_packet_review_2026-06-01.md"
)


class Goal2982GeminiReviewIntakeTest(unittest.TestCase):
    def test_gemini_review_accepts_with_boundary_and_blocks_release(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "accept-with-boundary",
            "not release-authorizing",
            "Primitive-first",
            "Neutral-seam-scope-out",
            "28.5x to 175.1x slowdown",
            "3.8x to 4.9x speedup",
            "zero overclaims",
            "does **NOT** authorize a v2.5 release",
        ):
            self.assertIn(phrase, text)

    def test_intake_report_records_remaining_release_work(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2982",
            "Gemini verdict: `accept-with-boundary`",
            "Goal2977 second-architecture packet gap",
            "Barnes-Hut 8192-body Embree CPU baseline bottleneck",
            "final 3-AI consensus pass",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_readiness_indexes_review_and_keeps_claims_blocked(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2982_gemini_review_intake_goal2981_v2_5_closeout_2026-06-01.md"
            ]
        )
        self.assertTrue(
            packet["external_review_presence"][
                "docs/reviews/gemini_goal2981_v2_5_closeout_positioning_and_external_review_packet_review_2026-06-01.md"
            ]
        )
        self.assertIn("triage_goal2982_gemini_review_before_release_packet", packet["allowed_next_actions"])
        self.assertEqual("accept", validation["status"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertFalse(packet["claim_authorization"]["public_speedup_claim_authorized"])
        self.assertFalse(packet["claim_authorization"]["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
