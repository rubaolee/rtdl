import tempfile
import unittest
from pathlib import Path

from scripts import v3_phoenix_m70_m71_goal_completion_audit as audit


class V3PhoenixM70M71GoalCompletionAuditTest(unittest.TestCase):
    def _write_valid_reviews(self, root: Path) -> tuple[Path, Path]:
        non_auth = (
            "no V3 release; no all-app benchmark run; no POD spend; "
            "no paid POD spend; no focused POD spend; no runbook execution; "
            "no benchmark execution; no public speedup wording; "
            "no broad V3-over-V2 wording; no whole-app speedup wording; "
            "no paper reproduction wording; no RT-core speedup wording; "
            "no V4 work; no embedding; no C ABI; no true-zero-copy claim; "
            "no automatic partner selection; no route-specific RTNN app tuning; "
            "no watch-row closure."
        )
        m70 = root / "claude_m70.md"
        m71 = root / "claude_m71.md"
        m70.write_text(
            "# Claude M70 Review\n\n"
            "Reviewer: Claude\n\n"
            "Verdict: `accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod`\n\n"
            "frozen same-contract uniform per-distribution full-batch self-query 0.988781x "
            f"{non_auth}\n",
            encoding="utf-8",
        )
        m71.write_text(
            "# Claude M71 Review\n\n"
            "Reviewer: Claude\n\n"
            "Verdict: `accept_m71_local_dry_run_gate_continue_no_execution_no_pod`\n\n"
            "dry-run input_load input_pack hot_query_median signature_match_status 7 14 "
            f"{non_auth}\n",
            encoding="utf-8",
        )
        return m70, m71

    def test_current_default_ready_for_3ai_consensus_but_not_authorized(self) -> None:
        # Claude backfill is complete; intake now accepts both reviews.
        # Goal completion is ready for final 3AI consensus but still not authorized.
        payload = audit.build_payload()

        self.assertEqual(payload["tool"], "v3_phoenix_m70_m71_goal_completion_audit")
        self.assertEqual(
            payload["status"],
            "m70_m71_goal_completion_ready_for_final_3ai_consensus_no_authorization",
        )
        self.assertEqual(payload["intake_status"], "claude_backfill_intake_accept_no_authorization")
        self.assertTrue(payload["intake_ready"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["benchmark_execution_authorized"])
        self.assertFalse(payload["goal_completion_authorized"])
        self.assertTrue(payload["goal_completion_ready_for_final_3ai_consensus"])
        self.assertIn("was_i_foolish", payload["decision_audit"])

    def test_valid_claude_reviews_make_packet_ready_but_not_self_authorized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            m70, m71 = self._write_valid_reviews(Path(tmpdir))
            payload = audit.build_payload(m70, m71)

        self.assertEqual(
            payload["status"],
            "m70_m71_goal_completion_ready_for_final_3ai_consensus_no_authorization",
        )
        self.assertTrue(payload["intake_ready"])
        self.assertFalse(payload["missing_support"])
        self.assertFalse(payload["goal_completion_authorized"])
        self.assertTrue(payload["goal_completion_ready_for_final_3ai_consensus"])
        self.assertFalse(payload["release_authorized"])


if __name__ == "__main__":
    unittest.main()
