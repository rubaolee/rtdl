from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2857_v2_5_readiness_indexes_packet_runner_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2858_gemini_review_goal2857_v2_5_readiness_packet_runner_index_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2858_goal2857_v2_5_readiness_packet_runner_index_consensus_2026-05-31.md"


class Goal2857V25ReadinessIndexesPacketRunnerTest(unittest.TestCase):
    def test_readiness_indexes_goal2855_runner_and_goal2856_consensus(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(7, validation["current_canonical_runner_artifact_count"])
        for path in (
            "docs/reports/goal2855_v2_5_current_canonical_harness_packet_runner_2026-05-31.md",
            "docs/reports/goal2856_goal2855_v2_5_canonical_packet_runner_consensus_2026-05-31.md",
        ):
            self.assertTrue(packet["required_report_presence"][path], path)
        self.assertTrue(
            packet["external_review_presence"][
                "docs/reviews/"
                "goal2856_gemini_review_goal2855_v2_5_canonical_packet_runner_2026-05-31.md"
            ]
        )

    def test_current_canonical_runner_metadata_is_clean_and_bounded(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        runner = packet["current_canonical_runner"]

        self.assertEqual("pass", runner["status"])
        self.assertTrue(runner["all_pass"])
        self.assertEqual(7, runner["artifact_count"])
        self.assertEqual(7, runner["expected_artifact_count"])
        self.assertEqual({}, runner["dirty_artifacts"])
        self.assertEqual({}, runner["claim_boundary_violations"])
        self.assertIn("goal2855", runner["summary_path"])
        self.assertIn("operational readiness guard", runner["claim_boundary"])

    def test_allowed_next_actions_point_at_goal2855_runner(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual(
            "keep_goal2855_current_canonical_packet_runner_green",
            packet["allowed_next_actions"][0],
        )
        self.assertNotIn(
            "keep_current_canonical_harness_and_observability_guards_green",
            packet["allowed_next_actions"],
        )

    def test_report_records_metadata_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal2857",
            "Goal2855",
            "Goal2856",
            "current_canonical_runner",
            "metadata-only",
            "not a release authorization",
            "keep_goal2855_current_canonical_packet_runner_green",
        ):
            self.assertIn(phrase, text)

    def test_review_and_consensus_accept_with_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "independent Gemini review",
            "accept-with-boundary",
            "current_canonical_runner",
            "Goal2847 full artifact set",
        ):
            self.assertIn(phrase, review)

        for phrase in (
            "Consensus verdict: **accept-with-boundary**",
            "Codex",
            "Gemini",
            "not final v2.5 release consensus",
            "keep_goal2855_current_canonical_packet_runner_green",
        ):
            self.assertIn(phrase, consensus)


if __name__ == "__main__":
    unittest.main()
