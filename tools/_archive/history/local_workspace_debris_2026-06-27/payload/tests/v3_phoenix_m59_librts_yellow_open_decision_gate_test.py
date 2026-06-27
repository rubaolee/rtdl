import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_m59_librts_yellow_open_decision_2026-06-23.md"
)
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m59_librts_yellow_open_decision_2026-06-23.md"
)


class V3PhoenixM59LibRTSYellowOpenDecisionGateTest(unittest.TestCase):
    def test_m59_decision_classifies_librts_as_set_b_yellow_open(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn(
            "m59_librts_set_b_yellow_open_limit_not_step2_gap_pending_external_review",
            report,
        )
        self.assertIn("Set-B yellow/open control limitation", report)
        self.assertIn("not treated as a new Step-2 runtime optimization gap", report)
        self.assertIn("set_a_probe_candidate=false", report)
        self.assertIn("set_b_control_candidate=true", report)
        self.assertIn("yellow_stability_boundary_watch_row_open", report)
        self.assertIn("OptiX cold single-shot row remains weak", report)

    def test_m59_preserves_non_authorization_and_no_closure(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW):
            text = path.read_text(encoding="utf-8")
            self.assertIn("no V3 release", text)
            self.assertIn("no all-app benchmark run", text)
            self.assertIn("no broad paid POD campaign", text)
            self.assertIn("no additional LibRTS POD run", text)
            self.assertIn("no public speedup wording", text)
            self.assertIn("no broad V3-over-V2 claim", text)
            self.assertIn("no V4 work", text)
            self.assertIn("no embedding", text)
            self.assertIn("no C ABI", text)
            self.assertIn("no true-zero-copy claim", text)
            self.assertIn("no watch-row closure", text)
            self.assertNotIn("release_ready", text)

    def test_m59_review_request_keeps_next_action_on_set_a_step2(self) -> None:
        review = CALL_FOR_REVIEW.read_text(encoding="utf-8")

        self.assertIn(
            "accept_m59_librts_set_b_yellow_open_limit_continue_set_a_step2",
            review,
        )
        self.assertIn("request_m59_changes_before_decision", review)
        self.assertIn(
            "reject_m59_classification_librts_requires_runtime_gap_work_now",
            review,
        )
        self.assertIn("return Step 2 to a Set-A runtime family", review)
        self.assertIn("Set-B release risk", review)
        self.assertNotIn("authorize_all_app", review)

    def test_m59_external_reviews_and_consensus_close_goal_not_release(self) -> None:
        claude = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m59_librts_yellow_open_decision_recorded_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m59_librts_yellow_open_decision_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m59_librts_yellow_open_decision_3ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")
        audit = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m59_goal_completion_audit_2026-06-23.md"
        ).read_text(encoding="utf-8")

        for text in (claude, antigravity, consensus, audit):
            self.assertIn(
                "accept_m59_librts_set_b_yellow_open_limit_continue_set_a_step2",
                text,
            )
            self.assertIn("no V3 release", text)
            self.assertIn("no all-app benchmark run", text)
            self.assertIn("no additional LibRTS POD run", text)
            self.assertIn("no watch-row closure", text)
            self.assertNotIn("release_ready", text)

        self.assertIn("m59_librts_set_b_yellow_open_limit_continue_set_a_step2_no_release", consensus)
        self.assertIn("weak stripped median", consensus)
        self.assertIn("m59_goal_complete_3ai_accept_continue_set_a_step2", audit)


if __name__ == "__main__":
    unittest.main()
