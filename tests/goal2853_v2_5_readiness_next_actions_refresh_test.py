from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2853_v2_5_readiness_next_actions_refresh_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2854_gemini_review_goal2853_v2_5_readiness_next_actions_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2854_goal2853_v2_5_readiness_next_actions_consensus_2026-05-31.md"


class Goal2853V25ReadinessNextActionsRefreshTest(unittest.TestCase):
    def test_readiness_indexes_barnes_hut_observability_hardening(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        for path in (
            "docs/reports/goal2851_barnes_hut_harness_progress_logging_2026-05-31.md",
            "docs/reports/goal2852_goal2851_barnes_hut_progress_logging_consensus_2026-05-31.md",
        ):
            with self.subTest(path=path):
                self.assertTrue(packet["required_report_presence"][path])

        review_path = (
            "docs/reviews/"
            "goal2852_gemini_review_goal2851_barnes_hut_progress_logging_2026-05-31.md"
        )
        self.assertTrue(packet["external_review_presence"][review_path])

    def test_allowed_next_actions_no_longer_point_at_old_goal2806_review(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual(
            (
                "keep_current_canonical_harness_and_observability_guards_green",
                "continue_internal_v2_5_hardening_or_prepare_user_requested_release_packet",
                "request_fresh_3ai_release_review_only_if_user_requests_release",
            ),
            packet["allowed_next_actions"],
        )
        self.assertNotIn(
            "request_external_review_of_goal2806_packet",
            packet["allowed_next_actions"],
        )

    def test_report_records_metadata_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal2853",
            "allowed next actions",
            "Goal2851",
            "Goal2852",
            "metadata-only",
            "not a release authorization",
        ):
            self.assertIn(phrase, text)

    def test_review_and_consensus_accept_with_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "independent Gemini review",
            "accept-with-boundary",
            "metadata-only boundary",
            "No. Upon reviewing all relevant files",
        ):
            self.assertIn(phrase, review)

        for phrase in (
            "Consensus verdict: **accept-with-boundary**",
            "Codex",
            "Gemini",
            "metadata-only readiness refresh",
            "not final v2.5 release consensus",
        ):
            self.assertIn(phrase, consensus)


if __name__ == "__main__":
    unittest.main()
