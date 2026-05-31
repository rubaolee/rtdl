import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_2026-05-31.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reports"
    / "goal2870_goal2868_last_day_review_intake_consensus_2026-05-31.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2868_claude_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md"
)
GEMINI_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2868_gemini_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md"
)
RUNNER_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal2880_current_packet_after_seam_provenance_pod"
    / "goal2855_summary.json"
)


class Goal2870V25LastDayReviewIntakeAndRunnerFailClosedHardeningTest(unittest.TestCase):
    def test_readiness_packet_indexes_goal2868_reviews_and_goal2870_reports(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        for path in (
            "docs/reviews/goal2868_claude_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md",
            "docs/reviews/goal2868_gemini_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md",
        ):
            self.assertTrue(packet["external_review_presence"][path], path)
        for path in (
            "docs/reports/goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_2026-05-31.md",
            "docs/reports/goal2870_goal2868_last_day_review_intake_consensus_2026-05-31.md",
        ):
            self.assertTrue(packet["required_report_presence"][path], path)
        self.assertEqual((), packet["missing_external_reviews"])
        self.assertEqual((), packet["missing_required_reports"])

    def test_current_runner_metadata_fails_closed_on_child_status_fields(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        runner = packet["current_canonical_runner"]
        summary = json.loads(RUNNER_SUMMARY.read_text(encoding="utf-8"))

        self.assertTrue(summary["returncode_ok"])
        self.assertTrue(summary["artifact_status_ok"])
        self.assertTrue(summary["source_commit_consistent"])
        self.assertTrue(runner["returncode_ok"])
        self.assertTrue(runner["artifact_status_ok"])
        self.assertTrue(runner["source_commit_consistent"])
        self.assertEqual("pass", runner["status"])

    def test_external_reviews_preserve_accept_with_boundary_and_release_block(self) -> None:
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")

        for text in (claude, gemini):
            self.assertIn("accept-with-boundary", text)
            self.assertIn("release", text.lower())
            self.assertIn("blocked", text.lower())
        self.assertIn("legacy torch carrier", claude.lower())
        self.assertIn("per-op", claude.lower())
        self.assertIn("performance gap", gemini.lower())
        self.assertIn("tie-break", gemini.lower())

    def test_report_and_consensus_record_review_findings_without_authorizing_release(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "Goal2870",
            "Goal2868",
            "accept-with-boundary",
            "returncode_ok",
            "artifact_status_ok",
            "not a v2.5 release authorization",
        ):
            self.assertIn(phrase, report)
        for phrase in (
            "Codex + Claude + Gemini",
            "accept-with-boundary",
            "final release remains blocked",
            "not v2.5 release consensus",
        ):
            self.assertIn(phrase, consensus)


if __name__ == "__main__":
    unittest.main()
