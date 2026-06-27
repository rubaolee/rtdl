import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V3PhoenixReviewDebtAndCompletionGateTest(unittest.TestCase):
    def test_claude_review_debt_register_covers_m43_through_m47_and_completion(self) -> None:
        debt = (
            ROOT
            / "docs"
            / "reviews"
            / "phoenix_v3_claude_review_debt_register_2026-06-23.md"
        ).read_text(encoding="utf-8")

        for heading in (
            "Debt 1: M43 Grouped Reduction CuPy Warp Prepared Runner",
            "Debt 2: M44 Step-2 Scorecard Sync After M43",
            "Debt 3: M45 Barnes-Hut Blocker Reaudit",
            "Debt 4: M46 LibRTS Watch-Row Status",
            "Debt 5: M47 LibRTS Stability / Cold-Start Protocol And Dry-Run Harness",
            "Debt 6: M44 Goal Completion Audit",
            "Debt 7: M48 LibRTS Stability Harness Execution Safety",
            "Debt 8: M49 Current Blocker Queue After M48",
            "Debt 9: M50 Spatial Topology-Stream Runner Fail-Closed Gate",
            "Debt 10: M51 LibRTS Authorized-Run Runbook",
            "Debt 11: M52 POD Runner Authorization Surface Audit",
        ):
            self.assertIn(heading, debt)

        for helper in (
            "run_claude_phoenix_v3_m43_grouped_reduction_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m44_scorecard_sync_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m45_barnes_hut_reaudit_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m46_librts_watch_rows_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m47_librts_stability_protocol_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m44_goal_completion_audit_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m48_librts_harness_execution_safety_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m49_current_blocker_queue_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m50_spatial_topology_runner_fail_closed_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m51_librts_authorized_runbook_review_2026_06_23.ps1",
            "run_claude_phoenix_v3_m52_pod_surface_audit_review_2026_06_23.ps1",
        ):
            self.assertIn(helper, debt)

        self.assertIn(
            "run_claude_phoenix_v3_review_debt_backfill_2026_06_23.ps1",
            debt,
        )

        self.assertIn("no V3 release", debt)
        self.assertIn("no all-app benchmark run", debt)
        self.assertIn("no paid POD spend", debt)

    def test_refresh_allows_saved_antigravity_review_as_external_ai_but_not_subagents(self) -> None:
        refresh = (
            ROOT / "docs" / "handoff" / "REFRESH_LOCAL_2026-04-13.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Codex plus two external AIs", refresh)
        self.assertIn("Antigravity", refresh)
        self.assertIn("Codex calls Claude first", refresh)
        self.assertIn("Do not call Gemini", refresh)
        self.assertIn("until the user restores it", refresh)
        self.assertIn(r"C:\Users\Lestat\AppData\Local\agy\bin\agy.exe", refresh)
        self.assertIn("Prefer the installed `agy.exe` CLI", refresh)
        self.assertIn("temporary GUI", refresh)
        self.assertIn("fallback", refresh)
        self.assertIn("occasional user-forwarded GUI fallback", refresh)
        self.assertIn("saved file is in the repo", refresh)
        self.assertIn("An internal Codex subagent does not satisfy", refresh)
        self.assertIn("goal-completion audit must have `3-AI`", refresh)

    def test_m44_completion_audit_has_3ai_consensus_and_guardrails(self) -> None:
        audit_path = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m44_goal_completion_audit_pending_3ai_2026-06-23.md"
        )
        prompt_path = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_prompt_phoenix_v3_m44_goal_completion_audit_2026-06-23.txt"
        )
        antigravity_review_path = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m44_goal_completion_audit_review_2026-06-23.md"
        )
        interim_consensus_path = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_antigravity_phoenix_v3_m44_goal_completion_audit_interim_2ai_consensus_2026-06-23.md"
        )
        claude_review_path = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m44_goal_completion_audit_recorded_review_2026-06-23.md"
        )
        final_consensus_path = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m44_goal_completion_3ai_consensus_2026-06-23.md"
        )
        blocked_review_path = (
            ROOT
            / "docs"
            / "reviews"
            / "external_review_blocked_phoenix_v3_m44_completion_claude_gemini_2026-06-23.md"
        )
        handoff = (
            ROOT
            / "docs"
            / "handoff"
            / "PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md"
        ).read_text(encoding="utf-8")
        audit = audit_path.read_text(encoding="utf-8")
        prompt = prompt_path.read_text(encoding="utf-8")
        antigravity_review = antigravity_review_path.read_text(encoding="utf-8")
        interim_consensus = interim_consensus_path.read_text(encoding="utf-8")
        claude_review = claude_review_path.read_text(encoding="utf-8")
        final_consensus = final_consensus_path.read_text(encoding="utf-8")
        blocked_review = blocked_review_path.read_text(encoding="utf-8")

        self.assertIn(
            "m44_goal_complete_3ai_consensus_obtained_pending_claude_debt_backfill_not_release",
            audit,
        )
        self.assertIn("3-AI", audit)
        self.assertIn(prompt_path.name, audit)
        self.assertIn(antigravity_review_path.name, audit)
        self.assertIn(interim_consensus_path.name, audit)
        self.assertIn(claude_review_path.name, audit)
        self.assertIn(final_consensus_path.name, audit)
        self.assertIn(prompt_path.name, handoff)
        self.assertIn(antigravity_review_path.name, handoff)
        self.assertIn(interim_consensus_path.name, handoff)
        self.assertIn(claude_review_path.name, handoff)
        self.assertIn(final_consensus_path.name, handoff)
        self.assertIn(blocked_review_path.name, handoff)
        self.assertIn("This is a completion audit only", prompt)
        self.assertIn("Does M52 correctly audit current vs historical POD runner authorization?", prompt)
        self.assertIn("older M47-only completion shape", handoff)
        self.assertIn("no paid POD", prompt)
        self.assertIn("no all-app", prompt)
        self.assertIn(
            "accept_m44_substantively_done_but_do_not_mark_complete_until_3ai",
            antigravity_review,
        )
        self.assertIn(
            "accept_m44_substantively_done_but_do_not_mark_complete_until_3ai",
            interim_consensus,
        )
        self.assertIn("accept_m44_goal_complete_pending_claude_debt_backfill", claude_review)
        self.assertIn("accept_m44_goal_complete_pending_claude_debt_backfill", final_consensus)
        self.assertIn("no V3 release", final_consensus)
        self.assertIn("Claude debt items M43-M52 must still be backfilled", final_consensus)
        self.assertIn("Claude", interim_consensus)
        self.assertIn("external_review_blocked_claude_quota_gemini_ineligible", blocked_review)
        self.assertIn("not consensus", blocked_review)


if __name__ == "__main__":
    unittest.main()
