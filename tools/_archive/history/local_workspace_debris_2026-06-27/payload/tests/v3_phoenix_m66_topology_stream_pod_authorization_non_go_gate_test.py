import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts import v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner as runner


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py"
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_m66_topology_stream_pod_authorization_non_go_2026-06-23.md"
)
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m66_topology_stream_pod_authorization_non_go_2026-06-23.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_m66_topology_stream_pod_authorization_non_go_recorded_review_2026-06-23.md"
)
ANTIGRAVITY_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "antigravity_phoenix_v3_m66_topology_stream_pod_authorization_non_go_review_2026-06-23.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m66_topology_stream_pod_authorization_non_go_3ai_consensus_2026-06-23.md"
)
AUDIT = ROOT / "docs" / "reports" / "phoenix_v3_m66_goal_completion_audit_2026-06-23.md"


class V3PhoenixM66TopologyStreamPodAuthorizationNonGoGateTest(unittest.TestCase):
    def test_runner_uses_m66_token_and_preflight_before_samples(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertEqual(
            runner.AUTHORIZATION_TOKEN,
            "M66_SOURCE_SIGNATURE_GATED_TOPOLOGY_STREAM_M3_POD_AUTHORIZED",
        )
        self.assertEqual(runner.AUTHORIZED_EXECUTION_TOKENS, (runner.AUTHORIZATION_TOKEN,))
        self.assertNotIn(
            "M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED",
            runner.AUTHORIZED_EXECUTION_TOKENS,
        )
        self.assertIn("STATUS_PREFLIGHT_ONLY", text)
        self.assertIn("STATUS_FAILED", text)
        self.assertIn("current_topology_stream_source_signature", text)
        self.assertIn("runner_runs_preflight", runner.CURRENT_SOURCE_SIGNATURE_SCRIPT)
        self.assertIn(
            "tests.v3_phoenix_m65_topology_stream_step3_audit_negative_hardening_gate_test",
            runner.PREFLIGHT_TEST_MODULES,
        )

        execute_index = text.index("preflight, preflight_errors = execute_preflight(args)")
        abort_index = text.index("if preflight_errors:")
        run_index = text.index("payload = run_packet(args, preflight=preflight)")
        self.assertLess(execute_index, run_index)
        self.assertLess(abort_index, run_index)

    def test_source_signature_direct_check_passes_current_tree(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                runner.CURRENT_SOURCE_SIGNATURE_SCRIPT,
                str(ROOT),
            ],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["failed"], [])
        for check_name in (
            "point_topology_runner_present",
            "segment_topology_runner_present",
            "m3_bridge_helper_present",
            "step3_audit_bridge_gate_present",
            "rayjoin_app_emits_m3_table",
            "rayjoin_app_emits_prepared_handle",
            "runner_uses_m66_token",
            "runner_runs_preflight",
        ):
            self.assertTrue(payload["checks"][check_name], check_name)

    def test_m66_documents_record_non_go_and_redirect(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, CLAUDE_REVIEW, ANTIGRAVITY_REVIEW, CONSENSUS, AUDIT):
            text = path.read_text(encoding="utf-8")
            lower_text = text.lower()
            self.assertIn("m66", lower_text)
            self.assertTrue(
                "no pod" in lower_text
                or "no_pod" in lower_text
                or "not authorize" in lower_text
            )
            self.assertIn("v3 release", lower_text)
            self.assertIn("all-app", lower_text)
            self.assertIn("paid pod", lower_text)
            self.assertIn("focused pod", lower_text)
            self.assertIn("public speedup", lower_text)
            self.assertIn("broad v3-over-v2", lower_text)
            self.assertIn("true-zero-copy", lower_text)
            self.assertIn("watch-row closure", lower_text)
            self.assertNotIn("release_ready", text)

        verdict = (
            "accept_m66_topology_stream_pod_authorization_rejected_continue_"
            "barnes_hut_pre_audit_no_pod_no_release"
        )
        self.assertIn(verdict, CLAUDE_REVIEW.read_text(encoding="utf-8"))
        self.assertIn(verdict, ANTIGRAVITY_REVIEW.read_text(encoding="utf-8"))
        self.assertIn(verdict, CONSENSUS.read_text(encoding="utf-8"))
        self.assertIn(
            "m66_goal_complete_3ai_reject_topology_stream_pod_continue_barnes_hut_pre_audit_no_pod_no_release",
            AUDIT.read_text(encoding="utf-8"),
        )

    def test_prior_rayjoin_no_go_remains_the_controlling_reason(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (REPORT, CLAUDE_REVIEW, ANTIGRAVITY_REVIEW, CONSENSUS)
        )
        lower_combined = combined.lower()

        for ratio in ("0.973465x", "0.973754x", "0.794180x"):
            self.assertIn(ratio, combined)
        self.assertIn("structural-only", lower_combined)
        self.assertIn("same native", lower_combined)
        self.assertIn("barnes-hut", lower_combined)
        self.assertIn("phase-structure pre-audit", lower_combined)

    def test_completion_audit_keeps_four_question_decision_audit(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")

        self.assertIn("Was I foolish?", text)
        self.assertIn("If yes, what actions made the decision foolish?", text)
        self.assertIn("Was there another path?", text)
        self.assertIn("Can I now try a different path", text)
        self.assertIn("Carry-Forward", text)


if __name__ == "__main__":
    unittest.main()
