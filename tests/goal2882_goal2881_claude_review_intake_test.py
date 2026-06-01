from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2882_goal2881_claude_review_intake_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2881_claude_review_v2_5_residual_closure_and_current_packet_2026-05-31.md"


class Goal2882Goal2881ClaudeReviewIntakeTest(unittest.TestCase):
    def test_review_is_indexed_by_readiness_packet(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        review_path = str(REVIEW.relative_to(ROOT)).replace("\\", "/")

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["external_review_presence"][review_path])
        self.assertEqual((), packet["missing_external_reviews"])
        self.assertIn(
            "triage_goal2881_claude_review_before_any_release_packet",
            packet["allowed_next_actions"],
        )

    def test_review_accepts_with_boundary_and_keeps_release_block(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "accept-with-boundary",
            "Release boundary",
            "does not authorize v2.5 release",
            "automatic Triton preview selection",
            "app-specific native engine logic",
            "fresh 3-AI release consensus",
        ):
            self.assertIn(phrase, text)

    def test_review_preserves_residual_release_watch_items(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "Torch carrier is provenance-hardened, not removed",
            "metadata/contract, not runtime dataflow",
            "Goal2877",
            "release_conformance_complete: false",
            "\"7/7 pass\" parity over-read risk persists",
        ):
            self.assertIn(phrase, text)

    def test_readiness_redlines_remain_blocked(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        for blocked in (
            "v2_5_release",
            "release_tag_action",
            "public_speedup_wording",
            "broad_rt_core_speedup_wording",
            "whole_app_speedup_wording",
            "true_zero_copy_wording",
            "package_install_wording",
            "triton_preview_auto_selection",
            "native_app_specific_engine_logic",
        ):
            self.assertIn(blocked, packet["blocked_actions"])
        for value in packet["claim_authorization"].values():
            self.assertFalse(value)

    def test_report_records_intake_without_release_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2882",
            "Goal2881 Claude review",
            "triage_goal2881_claude_review_before_any_release_packet",
            "not a v2.5 release authorization",
            "not true-zero-copy wording",
            "fresh 3-AI release consensus",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
