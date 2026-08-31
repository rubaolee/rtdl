from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2981_v2_5_closeout_positioning_and_external_review_packet_2026-06-01.md"
)
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_EXTERNAL_REVIEW_GOAL2981_V2_5_CLOSEOUT_2026-06-01.md"


class Goal2981V25CloseoutPositioningTest(unittest.TestCase):
    def test_closeout_report_states_delivered_and_not_delivered_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2981",
            "primitive-first native RTDL",
            "Delivered In v2.5",
            "Not Delivered In v2.5",
            "Full partner-neutral composition",
            "True zero-copy",
            "Triton performance win",
            "Goal2981 does not authorize",
            "fresh 3-AI consensus",
        ):
            self.assertIn(phrase, text)

    def test_readiness_indexes_closeout_report_without_release_claim(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2981_v2_5_closeout_positioning_and_external_review_packet_2026-06-01.md"
            ]
        )
        self.assertIn("request_external_review_for_goal2981_before_release_packet", packet["allowed_next_actions"])
        self.assertEqual("accept", validation["status"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertFalse(packet["claim_authorization"]["public_speedup_claim_authorized"])
        self.assertFalse(packet["claim_authorization"]["true_zero_copy_claim_authorized"])
        self.assertIn("v2_5_release", packet["blocked_actions"])

    def test_closeout_is_consistent_with_c1_c2_c3_decisions(self) -> None:
        doctrine = rt.v2_5_primitive_first_selection_doctrine()
        seam = rt.v2_5_neutral_seam_closeout_decision()

        self.assertEqual("accept", rt.validate_v2_5_primitive_first_selection_doctrine(doctrine)["status"])
        self.assertEqual("accept", rt.validate_v2_5_neutral_seam_closeout_decision(seam)["status"])
        self.assertFalse(doctrine["automatic_triton_selection_allowed"])
        self.assertFalse(seam["multi_partner_composition_delivered"])
        self.assertFalse(seam["true_zero_copy_authorized"])

    def test_external_review_handoff_is_specific_and_non_authorizing(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        for phrase in (
            "Goal2981 v2.5 Closeout",
            "docs/reports/goal2981_v2_5_closeout_positioning_and_external_review_packet_2026-06-01.md",
            "Goal2979",
            "Goal2980",
            "not itself a release authorization",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
