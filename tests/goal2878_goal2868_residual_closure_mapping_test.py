from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2878_goal2868_residual_closure_map_after_conformance_2026-05-31.md"
CLAUDE_REVIEW = ROOT / "docs/reviews/goal2868_claude_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md"
GOAL2877_HANDOFF = ROOT / "docs/handoff/CALL_FOR_REVIEW_GOAL2877_V2_5_CONFORMANCE_CLOSURE_AND_CURRENT_PACKET_2026-05-31.md"


class Goal2878Goal2868ResidualClosureMappingTest(unittest.TestCase):
    def test_goal2868_residuals_are_present_in_source_review(self) -> None:
        text = CLAUDE_REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "Legacy torch carrier is bounded and labeled, not removed",
            "\"7/7 harnesses pass\" must not be readable as Tier A/B parity",
            "CuPy \"conformance\" role is declared",
            "kernel-level tie-break enforcement is unproven",
        ):
            self.assertIn(phrase, text)

    def test_closure_report_maps_each_residual_to_newer_goal_evidence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2871",
            "Goal2872",
            "Goal2873",
            "Goal2874",
            "Goal2875",
            "Goal2876",
            "Goal2877",
            "Partially closed for internal readiness",
            "Closed as wording/metadata guard",
            "Closed for preview-runtime conformance bookkeeping",
            "Closed for the current high-risk Triton preview rows",
        ):
            self.assertIn(phrase, text)

    def test_partner_conformance_and_readiness_validate_post_closure(self) -> None:
        conformance = rt.validate_v2_5_partner_conformance_matrix()
        readiness = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", conformance["status"])
        self.assertEqual(0, conformance["runtime_conformance_gap_count"])
        self.assertEqual(0, conformance["release_blocker_count"])
        self.assertFalse(rt.v2_5_partner_conformance_matrix()["release_conformance_complete"])

        self.assertEqual("accept", readiness["status"])
        self.assertEqual(
            "docs/reports/goal2876_current_packet_after_conformance_pod/goal2855_summary.json",
            packet["current_canonical_runner"]["summary_path"],
        )
        self.assertTrue(packet["required_report_presence"][str(REPORT.relative_to(ROOT)).replace("\\", "/")])
        self.assertIn(
            "request_goal2877_external_review_for_goal2873_to_goal2876_conformance_closure",
            packet["allowed_next_actions"],
        )

    def test_goal2877_handoff_targets_newer_conformance_closure(self) -> None:
        text = GOAL2877_HANDOFF.read_text(encoding="utf-8")

        for phrase in (
            "Goals2873-2876",
            "partner x operation conformance matrix",
            "Numba/Triton/CuPy evidence boundaries",
            "clean seven-app Goal2876 packet",
            "without authorizing v2.5 release",
        ):
            self.assertIn(phrase, text)

    def test_goal2878_boundary_blocks_release_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "not a v2.5 release authorization",
            "not a public speedup claim",
            "not a broad RT-core claim",
            "not a whole-app speedup claim",
            "not true-zero-copy wording",
            "not package-install wording",
            "fresh 3-AI release consensus",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
