import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CALL = ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m70_m71_claude_backfill_2026-06-24.md"
PROMPT = ROOT / "scratch" / "claude_prompt_phoenix_v3_m70_m71_backfill_2026-06-24.txt"
HELPER = ROOT / "scripts" / "run_claude_phoenix_v3_m70_m71_backfill_2026_06_24.ps1"
POST_CLAUDE_HELPER = ROOT / "scripts" / "run_phoenix_v3_m70_m71_post_claude_local_validation_2026_06_24.ps1"
REGISTER = ROOT / "docs" / "reviews" / "phoenix_v3_claude_review_debt_register_2026-06-23.md"
STATUS = ROOT / "docs" / "reports" / "phoenix_v3_m70_m71_backfill_packet_and_register_status_2026-06-24.md"


class V3PhoenixM70M71ClaudeBackfillPacketGateTest(unittest.TestCase):
    def test_backfill_packet_names_required_outputs_and_inputs(self) -> None:
        call = CALL.read_text(encoding="utf-8")

        for required in (
            "claude_phoenix_v3_m70_rtnn_focused_protocol_recorded_review_2026-06-23.md",
            "claude_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_recorded_review_2026-06-23.md",
            "call_for_review_phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md",
            "phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.json",
            "antigravity_phoenix_v3_m70_rtnn_focused_protocol_review_2026-06-23.md",
            "call_for_review_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md",
            "phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.json",
            "antigravity_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_review_2026-06-23.md",
            "phoenix_v3_m70_m71_backfill_packet_and_register_status_2026-06-24.md",
            "antigravity_phoenix_v3_m70_m71_backfill_packet_intake_review_2026-06-24.md",
            "v3_phoenix_m70_m71_claude_backfill_intake.py",
            "v3_phoenix_m70_m71_goal_completion_audit.py",
        ):
            self.assertIn(required, call)

    def test_backfill_packet_has_narrow_verdicts_and_boundaries(self) -> None:
        call = CALL.read_text(encoding="utf-8")
        prompt = PROMPT.read_text(encoding="utf-8")

        for text in (call, prompt):
            self.assertIn("accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod", text)
            self.assertIn("blocked_m70_missing_same_contract_or_phase_boundaries", text)
            self.assertIn("accept_m71_local_dry_run_gate_continue_no_execution_no_pod", text)
            self.assertIn("reject_m71_dry_run_gate_oversteps_no_execution_boundary", text)
            normalized = " ".join(text.split())
            self.assertIn("no V3 release", normalized)
            self.assertIn("no all-app", normalized)
            self.assertIn("no POD", normalized)
            self.assertIn("no runbook", normalized)
            self.assertIn("no benchmark execution", normalized)
            self.assertIn("no public speedup", normalized)
            self.assertIn("no broad V3-over-V2", normalized)
            self.assertIn("no V4", normalized)
            self.assertIn("no embedding", normalized)
            self.assertIn("no C ABI", normalized)
            self.assertIn("no true-zero-copy", normalized)
            self.assertIn("no route-specific RTNN app tuning", normalized)
            self.assertNotIn("release_ready", text)
            self.assertIn("accept_m70_m71_backfill_packet_intake_continue_wait_for_claude", text)
            self.assertIn("--allow-non-accepted", text)

    def test_helper_invokes_claude_with_repo_add_dir(self) -> None:
        helper = HELPER.read_text(encoding="utf-8")

        self.assertIn("claude_prompt_phoenix_v3_m70_m71_backfill_2026-06-24.txt", helper)
        self.assertIn(".local\\bin\\claude.exe", helper)
        self.assertIn("--print", helper)
        self.assertIn("--permission-mode bypassPermissions", helper)
        self.assertIn("--add-dir $Repo", helper)

    def test_post_claude_helper_runs_intake_audit_and_rebuild_fail_closed(self) -> None:
        helper = POST_CLAUDE_HELPER.read_text(encoding="utf-8")

        self.assertIn("v3_phoenix_m70_m71_claude_backfill_intake.py", helper)
        self.assertNotIn("--allow-non-accepted", helper)
        self.assertIn("v3_phoenix_m70_m71_goal_completion_audit.py", helper)
        self.assertIn("v3_phoenix_m70_m71_final_3ai_consensus.py", helper)
        self.assertIn("tests.v3_phoenix_m70_m71_final_3ai_consensus_test", helper)
        self.assertIn("tests.v3_phoenix_m70_m71_goal_completion_audit_test", helper)
        self.assertIn("tests.v3_phoenix_m70_m71_claude_backfill_intake_test", helper)
        self.assertIn("run_test_matrix.py", helper)
        self.assertIn("phoenix_v3_m70_m71_final_3ai_consensus_after_claude_2026-06-24.json", helper)
        self.assertIn("phoenix_v3_m70_m71_after_claude_v3_rebuild_2026-06-24.json", helper)

    def test_review_debt_register_tracks_m70_m71_backfill(self) -> None:
        register = REGISTER.read_text(encoding="utf-8")

        self.assertIn("m70_m71_claude_backfill_obtained_goal_complete_no_execution_no_pod", register)
        self.assertIn("call_for_review_phoenix_v3_m70_m71_claude_backfill_2026-06-24.md", register)
        self.assertIn("claude_phoenix_v3_m70_rtnn_focused_protocol_recorded_review_2026-06-23.md", register)
        self.assertIn("claude_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_recorded_review_2026-06-23.md", register)
        self.assertIn("run_claude_phoenix_v3_m70_m71_backfill_2026_06_24.ps1", register)
        for phrase in (
            "no V3 release",
            "no all-app benchmark run",
            "no POD spend",
            "no runbook execution",
            "no benchmark execution",
            "no public speedup wording",
            "no broad V3-over-V2 wording",
            "no V4 work",
            "no embedding",
            "no C ABI",
            "no true-zero-copy claim",
            "no route-specific RTNN app tuning",
        ):
            self.assertIn(phrase, register)

    def test_status_report_records_backfilled_goal_complete_state(self) -> None:
        status = STATUS.read_text(encoding="utf-8")

        self.assertIn("m70_m71_backfill_obtained_goal_complete_no_execution_no_pod_no_release", status)
        self.assertIn("module_count=148", status)
        self.assertIn("Ran 751 tests", status)
        self.assertIn("phoenix_v3_m70_m71_final_3ai_consensus_v3_rebuild_2026-06-24.json", status)
        self.assertIn("v3_phoenix_m70_m71_claude_backfill_intake.py", status)
        self.assertIn("v3_phoenix_m70_m71_claude_backfill_intake_test.py", status)
        self.assertIn("phoenix_v3_m70_m71_claude_backfill_intake_pending_2026-06-24.json", status)
        self.assertIn("phoenix_v3_m70_m71_claude_backfill_intake_pending_2026-06-24.md", status)
        self.assertIn("v3_phoenix_m70_m71_goal_completion_audit.py", status)
        self.assertIn("v3_phoenix_m70_m71_goal_completion_audit_test.py", status)
        self.assertIn("phoenix_v3_m70_m71_goal_completion_audit_pending_2026-06-24.json", status)
        self.assertIn("phoenix_v3_m70_m71_goal_completion_audit_pending_2026-06-24.md", status)
        self.assertIn("run_phoenix_v3_m70_m71_post_claude_local_validation_2026_06_24.ps1", status)
        self.assertIn("v3_phoenix_m70_m71_final_3ai_consensus.py", status)
        self.assertIn("v3_phoenix_m70_m71_final_3ai_consensus_test.py", status)
        self.assertIn("phoenix_v3_m70_m71_final_3ai_consensus_pending_2026-06-24.json", status)
        self.assertIn("phoenix_v3_m70_m71_final_3ai_consensus_pending_2026-06-24.md", status)
        self.assertIn("external_review_blocked_phoenix_v3_m70_m71_claude_session_limit_2026-06-24.md", status)
        self.assertIn("antigravity_phoenix_v3_m70_m71_backfill_packet_intake_review_2026-06-24.md", status)
        self.assertIn("accept_m70_m71_backfill_packet_intake_continue_wait_for_claude", status)
        self.assertIn("--allow-non-accepted", status)
        self.assertIn("claude_phoenix_v3_m70_rtnn_focused_protocol_recorded_review_2026-06-23.md", status)
        self.assertIn("claude_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_recorded_review_2026-06-23.md", status)
        self.assertIn("Goal-Level Decision Audit", status)
        self.assertIn("no benchmark execution", status)
        self.assertIn("no public speedup wording", status)
        self.assertIn("no V4 work", status)
        self.assertIn("no embedding", status)
        self.assertIn("no C ABI", status)
        self.assertIn("no true-zero-copy claim", status)


if __name__ == "__main__":
    unittest.main()
