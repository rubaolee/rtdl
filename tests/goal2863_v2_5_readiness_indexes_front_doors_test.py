from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2863_v2_5_readiness_indexes_front_doors_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2864_gemini_review_goal2863_readiness_front_door_index_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2864_goal2863_readiness_front_door_index_consensus_2026-05-31.md"


class Goal2863V25ReadinessIndexesFrontDoorsTest(unittest.TestCase):
    def test_readiness_packet_indexes_goal2861_reports_and_review(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        for path in (
            "docs/reports/goal2861_v2_5_generic_partner_front_door_completion_2026-05-31.md",
            "docs/reports/goal2862_goal2861_generic_front_door_completion_consensus_2026-05-31.md",
        ):
            self.assertTrue(packet["required_report_presence"][path], path)
        self.assertTrue(
            packet["external_review_presence"][
                "docs/reviews/"
                "goal2862_gemini_review_goal2861_generic_front_door_completion_2026-05-31.md"
            ]
        )

    def test_readiness_packet_fails_closed_on_front_door_regression(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        coverage = packet["front_door_coverage"]

        self.assertEqual(10, coverage["benchmark_app_count"])
        self.assertEqual(10, coverage["fully_front_door_ready_count"])
        for row in coverage["apps"]:
            self.assertEqual("adapter_front_door_ready", row["front_door_status"], row["app_id"])
            self.assertEqual((), row["dispatcher_only_operations"], row["app_id"])
            self.assertEqual((), row["missing_operations"], row["app_id"])
        self.assertIn("not CUDA pod evidence", coverage["claim_boundary"])

    def test_report_review_and_consensus_record_metadata_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "Goal2863",
            "front_door_coverage",
            "Goal2861",
            "metadata-only",
            "not a release authorization",
        ):
            self.assertIn(phrase, report)
        self.assertIn("accept-with-boundary", review)
        self.assertIn("accept-with-boundary", consensus)


if __name__ == "__main__":
    unittest.main()
