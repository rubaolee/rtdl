import tempfile
import unittest
from pathlib import Path

from scripts import v3_phoenix_m70_m71_final_3ai_consensus as consensus


class V3PhoenixM70M71Final3AIConsensusTest(unittest.TestCase):
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

    def test_missing_explicit_review_paths_are_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            payload = consensus.build_payload(root / "missing_m70.md", root / "missing_m71.md")

        self.assertEqual(payload["tool"], "v3_phoenix_m70_m71_final_3ai_consensus")
        self.assertEqual(payload["status"], "m70_m71_final_3ai_consensus_pending")
        self.assertFalse(payload["claude_ready"])
        self.assertTrue(payload["antigravity_ready"])
        self.assertFalse(payload["audit_ready"])
        self.assertFalse(payload["goal_completion_authorized_by_builder"])
        self.assertFalse(payload["goal_completion_ready_for_human_record"])
        self.assertFalse(payload["release_authorized"])
        self.assertEqual(payload["reviewers"], ["codex", "claude", "antigravity"])

    def test_current_default_ready_after_claude_backfill_but_not_authorized(self) -> None:
        payload = consensus.build_payload()

        self.assertEqual(
            payload["status"],
            "m70_m71_final_3ai_consensus_ready_to_record_no_authorization",
        )
        self.assertTrue(payload["claude_ready"])
        self.assertTrue(payload["antigravity_ready"])
        self.assertTrue(payload["audit_ready"])
        self.assertFalse(payload["goal_completion_authorized_by_builder"])
        self.assertTrue(payload["goal_completion_ready_for_human_record"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["pod_spend_authorized"])
        self.assertFalse(payload["benchmark_execution_authorized"])

    def test_valid_claude_reviews_make_consensus_ready_but_not_self_authorized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            m70, m71 = self._write_valid_reviews(Path(tmpdir))
            payload = consensus.build_payload(m70, m71)

        self.assertEqual(
            payload["status"],
            "m70_m71_final_3ai_consensus_ready_to_record_no_authorization",
        )
        self.assertTrue(payload["claude_ready"])
        self.assertTrue(payload["antigravity_ready"])
        self.assertTrue(payload["audit_ready"])
        self.assertFalse(payload["goal_completion_authorized_by_builder"])
        self.assertTrue(payload["goal_completion_ready_for_human_record"])
        self.assertFalse(payload["pod_spend_authorized"])
        self.assertFalse(payload["benchmark_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
