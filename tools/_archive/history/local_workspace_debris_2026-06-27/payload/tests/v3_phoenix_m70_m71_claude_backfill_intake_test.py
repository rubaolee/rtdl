import tempfile
import unittest
import subprocess
import sys
from pathlib import Path

from scripts import v3_phoenix_m70_m71_claude_backfill_intake as intake


NON_AUTH = (
    "no V3 release; no all-app benchmark run; no POD spend; "
    "no paid POD spend; no focused POD spend; no runbook execution; "
    "no benchmark execution; no public speedup wording; "
    "no broad V3-over-V2 wording; no whole-app speedup wording; "
    "no paper reproduction wording; no RT-core speedup wording; "
    "no V4 work; no embedding; no C ABI; no true-zero-copy claim; "
    "no automatic partner selection; no route-specific RTNN app tuning; no watch-row closure."
)


class V3PhoenixM70M71ClaudeBackfillIntakeTest(unittest.TestCase):
    def test_missing_explicit_review_paths_are_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            payload = intake.build_payload(root / "missing_m70.md", root / "missing_m71.md")

        self.assertEqual(payload["tool"], "v3_phoenix_m70_m71_claude_backfill_intake")
        self.assertEqual(payload["status"], "pending_claude_backfill")
        self.assertEqual(payload["missing_review_count"], 2)
        self.assertEqual(payload["accepted_review_count"], 0)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["all_app_authorized"])
        self.assertFalse(payload["pod_spend_authorized"])
        self.assertFalse(payload["benchmark_execution_authorized"])
        self.assertFalse(payload["goal_completion_authorized_by_intake_alone"])
        self.assertEqual(payload["next_action"], "run_claude_backfill_helper")

    def test_accepts_two_bounded_claude_reviews_without_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            m70 = root / "claude_m70.md"
            m71 = root / "claude_m71.md"
            m70.write_text(
                "# Claude M70 Review\n\n"
                "Reviewer: Claude\n\n"
                "Verdict: `accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod`\n\n"
                "The frozen RTNN shapes and same-contract incumbents are named. "
                "The uniform evidence boundary, per-distribution requirement, "
                "full-batch self-query constraint, and 0.988781x hot-query boundary "
                f"are preserved. {NON_AUTH}\n",
                encoding="utf-8",
            )
            m71.write_text(
                "# Claude M71 Review\n\n"
                "Reviewer: Claude\n\n"
                "Verdict: `accept_m71_local_dry_run_gate_continue_no_execution_no_pod`\n\n"
                "The dry-run packet covers 7 shape groups and 14 rows. "
                "Telemetry includes input_load, input_pack, hot_query_median, and "
                f"signature_match_status. {NON_AUTH}\n",
                encoding="utf-8",
            )

            payload = intake.build_payload(m70, m71)

        self.assertEqual(payload["status"], "claude_backfill_intake_accept_no_authorization")
        self.assertEqual(payload["missing_review_count"], 0)
        self.assertEqual(payload["accepted_review_count"], 2)
        self.assertEqual(payload["next_action"], "draft_3ai_consensus_if_all_reviews_accepted")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["benchmark_execution_authorized"])
        self.assertFalse(payload["goal_completion_authorized_by_intake_alone"])

    def test_blocks_missing_required_terms_or_release_ready_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            m70 = root / "claude_m70_bad.md"
            m71 = root / "claude_m71_good.md"
            m70.write_text(
                "# Claude M70 Review\n\n"
                "Reviewer: Claude\n\n"
                "Verdict: `accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod`\n\n"
                "release_ready\n",
                encoding="utf-8",
            )
            m71.write_text(
                "# Claude M71 Review\n\n"
                "Reviewer: Claude\n\n"
                "Verdict: `accept_m71_local_dry_run_gate_continue_no_execution_no_pod`\n\n"
                "dry-run input_load input_pack hot_query_median signature_match_status 7 14 "
                f"{NON_AUTH}\n",
                encoding="utf-8",
            )

            payload = intake.build_payload(m70, m71)

        self.assertEqual(payload["status"], "claude_backfill_intake_blocked_or_revise")
        bad = payload["reviews"][0]
        self.assertFalse(bad["accepted"])
        self.assertIn("contains_release_ready_label", bad["reasons"])
        self.assertIn("missing_required_answer_terms", bad["reasons"])

    def test_non_accept_verdict_labels_are_recognized_but_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            m70 = root / "claude_m70_revise.md"
            m71 = root / "claude_m71_reject.md"
            m70.write_text(
                "# Claude M70 Review\n\n"
                "Reviewer: Claude\n\n"
                "Verdict: `accept_m70_protocol_shape_but_revise_before_harness`\n\n"
                "frozen same-contract uniform per-distribution full-batch self-query 0.988781x "
                f"{NON_AUTH}\n",
                encoding="utf-8",
            )
            m71.write_text(
                "# Claude M71 Review\n\n"
                "Reviewer: Claude\n\n"
                "Verdict: `reject_m71_dry_run_gate_oversteps_no_execution_boundary`\n\n"
                "dry-run input_load input_pack hot_query_median signature_match_status 7 14 "
                f"{NON_AUTH}\n",
                encoding="utf-8",
            )

            payload = intake.build_payload(m70, m71)

        self.assertEqual(payload["status"], "claude_backfill_intake_blocked_or_revise")
        self.assertEqual(payload["accepted_review_count"], 0)
        for item in payload["reviews"]:
            self.assertIn("non_accept_verdict_requires_revision_or_blocks", item["reasons"])

    def test_cli_fails_closed_unless_non_accepted_is_explicitly_allowed(self) -> None:
        script = intake.ROOT / "scripts" / "v3_phoenix_m70_m71_claude_backfill_intake.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            missing_m70 = root / "missing_m70.md"
            missing_m71 = root / "missing_m71.md"

            blocked = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--m70-review",
                    str(missing_m70),
                    "--m71-review",
                    str(missing_m71),
                ],
                cwd=intake.ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn('"status": "pending_claude_backfill"', blocked.stdout)

            allowed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--m70-review",
                    str(missing_m70),
                    "--m71-review",
                    str(missing_m71),
                    "--allow-non-accepted",
                ],
                cwd=intake.ROOT,
                capture_output=True,
                text=True,
            )
        self.assertEqual(allowed.returncode, 0)
        self.assertIn('"status": "pending_claude_backfill"', allowed.stdout)


if __name__ == "__main__":
    unittest.main()
