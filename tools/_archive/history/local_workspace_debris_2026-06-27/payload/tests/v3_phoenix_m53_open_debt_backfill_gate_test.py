import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V3PhoenixM53OpenDebtBackfillGateTest(unittest.TestCase):
    def test_m53_claude_backfill_is_recorded_without_authorization(self) -> None:
        review = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m53_open_debt_backfill_recorded_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_phoenix_v3_m53_open_debt_backfill_2ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")
        debt = (
            ROOT
            / "docs"
            / "reviews"
            / "phoenix_v3_claude_review_debt_register_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn("accept_m53_open_debt_backfill_no_authorization_continue_m54", review)
        self.assertIn("accept_m53_open_debt_backfill_no_authorization_continue_m54", consensus)
        for label in (
            "M43: accept",
            "M44-scorecard: accept",
            "M45: accept",
            "M46: accept",
            "M47: accept",
            "M48: accept",
            "M49: accept",
            "M50: accept",
            "M51: accept",
            "M52: accept",
        ):
            self.assertIn(label, review)

        self.assertIn("no focused POD spend", consensus)
        self.assertIn("M53 does not complete the active goal by itself", debt)
        self.assertIn("Backfilled by M53", debt)

    def test_m53_completion_audit_has_3ai_consensus_no_authorization(self) -> None:
        audit = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m53_goal_completion_audit_pending_3ai_2026-06-23.md"
        ).read_text(encoding="utf-8")
        prompt = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_prompt_phoenix_v3_m53_goal_completion_audit_2026-06-23.txt"
        ).read_text(encoding="utf-8")
        handoff = (
            ROOT
            / "docs"
            / "handoff"
            / "PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md"
        ).read_text(encoding="utf-8")
        blocked = (
            ROOT
            / "docs"
            / "reviews"
            / "external_review_blocked_phoenix_v3_m53_completion_gemini_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m53_goal_completion_audit_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m53_goal_completion_3ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn("m53_goal_complete_3ai_consensus_obtained_no_authorization", audit)
        self.assertIn("accept_m53_goal_complete_pending_no_authorization", audit)
        self.assertIn("This is a completion audit only", prompt)
        self.assertIn("no paid POD spend", prompt)
        self.assertIn("codex_claude_antigravity_phoenix_v3_m53_goal_completion_3ai_consensus", handoff)
        self.assertIn("completion is now satisfied", handoff)
        self.assertIn("external_review_blocked_gemini_ineligible", blocked)
        self.assertIn("not consensus", blocked)
        self.assertIn("accept_m53_goal_complete_pending_no_authorization", antigravity)
        self.assertIn("m53_goal_complete_3ai_consensus_obtained_no_authorization", consensus)
        self.assertIn("no focused POD spend", consensus)

    def test_m53_p1_items_are_carried_into_m54_packet(self) -> None:
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_phoenix_v3_m53_open_debt_backfill_2ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")
        m54 = (
            ROOT
            / "docs"
            / "reviews"
            / "call_for_review_phoenix_v3_m54_one_focused_librts_stability_pod_authorization_2026-06-23.md"
        ).read_text(encoding="utf-8")

        for text in (
            "real V2.14 root",
            "explicit Linux/POD Python paths",
            "M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED",
        ):
            self.assertIn(text, consensus)
            self.assertIn(text, m54)

        self.assertIn("draft_review_packet_not_authorized", m54)
        self.assertIn("does not authorize execution by itself", m54)
        self.assertIn("no all-app benchmark run", m54)
        self.assertIn("no broad paid POD campaign", m54)
        self.assertIn("no V3 release", m54)


if __name__ == "__main__":
    unittest.main()
