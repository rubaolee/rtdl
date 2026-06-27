import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_m70_rtnn_focused_protocol.py"
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.json"
PACKET_MD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md"
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md"
CALL_FOR_REVIEW = ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md"
ANTIGRAVITY_REVIEW = (
    ROOT / "docs" / "reviews" / "antigravity_phoenix_v3_m70_rtnn_focused_protocol_review_2026-06-23.md"
)
CLAUDE_BLOCKED = (
    ROOT / "docs" / "reviews" / "external_review_blocked_phoenix_v3_m70_claude_session_limit_2026-06-23.md"
)
PROVISIONAL_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_antigravity_phoenix_v3_m70_provisional_2ai_consensus_pending_claude_2026-06-23.md"
)
PENDING_STATUS = ROOT / "docs" / "reports" / "phoenix_v3_m70_status_pending_claude_backfill_2026-06-23.md"


class V3PhoenixM70RtnnFocusedProtocolGateTest(unittest.TestCase):
    def load(self) -> dict:
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_m70_is_protocol_only_and_authorizes_nothing(self) -> None:
        payload = self.load()

        self.assertEqual(
            payload["status"],
            "m70_rtnn_focused_protocol_draft_ready_for_review_no_execution_no_pod_no_release",
        )
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["protocol_scope"]["execution_authorized_now"])
        self.assertFalse(payload["protocol_scope"]["runbook_authorized_now"])
        self.assertFalse(payload["protocol_scope"]["pod_authorized_now"])
        self.assertFalse(payload["protocol_scope"]["all_app_authorized_now"])
        self.assertFalse(payload["protocol_scope"]["release_authorized_now"])
        for value in payload["non_authorization"].values():
            self.assertFalse(value)

    def test_all_frozen_shapes_and_same_contract_incumbents_are_named(self) -> None:
        payload = self.load()
        shapes = payload["frozen_shapes"]
        rows = [row for shape in shapes for row in shape["rows"]]

        self.assertEqual(len(shapes), 7)
        self.assertEqual(len(rows), 14)
        self.assertEqual({shape["distribution"] for shape in shapes}, {"uniform", "clustered", "shell"})
        self.assertEqual({shape["point_count"] for shape in shapes}, {65536, 262144})
        self.assertTrue(all(shape["query_role"] == "full_batch_self_query" for shape in shapes))
        self.assertTrue(all(row["same_contract_incumbent"] for row in rows))
        self.assertIn(
            "legacy_app_front_door_prepared_optix_ranked_summary",
            {row["same_contract_incumbent"]["incumbent_id"] for row in rows},
        )
        self.assertIn(
            "frozen_v2_14_embree_ranked_summary_row",
            {row["same_contract_incumbent"]["incumbent_id"] for row in rows},
        )

    def test_m69_carry_forward_and_phase_metrics_are_explicit(self) -> None:
        payload = self.load()
        carry = "\n".join(payload["m69_carry_forward"])
        metrics = payload["phase_metric_contract"]

        self.assertIn("uniform-distribution evidence only", carry)
        self.assertIn("per-distribution phase bounds", carry)
        self.assertIn("full-batch self-queries", carry)
        self.assertIn("0.988781x", carry)
        self.assertTrue(metrics["must_keep_separate"])
        for metric in (
            "input_load_sec",
            "input_pack_sec",
            "input_load_pack_sec",
            "execution_prepare_sec",
            "runner_after_input_load_pack_sec",
            "hot_query_median_sec",
            "runner_wall_sec",
            "signature_match_status",
        ):
            self.assertIn(metric, metrics["required_metric_names"])
        self.assertAlmostEqual(
            metrics["m69_uniform_repeat50_reference"]["hot_query_speedup_vs_legacy"],
            0.9887810047298636,
        )

    def test_future_harness_requirements_have_no_commands_or_token(self) -> None:
        payload = self.load()
        future = payload["future_harness_requirements"]
        text = json.dumps(payload, sort_keys=True)

        self.assertEqual(future["status"], "requirements_only_no_execution")
        self.assertFalse(future["commands_present"])
        self.assertFalse(future["authorization_token_present"])
        self.assertNotIn("command_template", text)
        self.assertNotIn("--execute", text)
        self.assertIn(">=1.20x", future["future_material_candidate_bar_if_separately_authorized"]["runner_wall_speedup_vs_same_contract_incumbent"])
        self.assertIn(">=0.98x", future["future_material_candidate_bar_if_separately_authorized"]["hot_query_speedup_vs_same_contract_incumbent"])

    def test_docs_and_call_for_review_preserve_boundaries(self) -> None:
        for path in (PACKET_MD, REPORT, CALL_FOR_REVIEW):
            text = path.read_text(encoding="utf-8")
            normalized = " ".join(text.split())
            self.assertIn("M70", text)
            self.assertIn("RTNN", text)
            self.assertIn("no V3 release", normalized)
            self.assertIn("no all-app", normalized)
            self.assertIn("no POD", normalized)
            self.assertIn("no runbook", normalized)
            self.assertIn("no public speedup", normalized)
            self.assertIn("no broad V3-over-V2", normalized)
            self.assertIn("no V4", normalized)
            self.assertIn("no embedding", normalized)
            self.assertIn("no C ABI", normalized)
            self.assertIn("no true-zero-copy", normalized)
            self.assertIn("no route-specific RTNN app tuning", normalized)
            self.assertNotIn("release_ready", text)

        call = CALL_FOR_REVIEW.read_text(encoding="utf-8")
        for verdict in (
            "accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod",
            "accept_m70_protocol_shape_but_revise_before_harness",
            "blocked_m70_missing_same_contract_or_phase_boundaries",
            "reject_m70_protocol_repeats_leaf_first_or_overclaims",
        ):
            self.assertIn(verdict, call)

    def test_external_review_state_is_provisional_pending_claude(self) -> None:
        antigravity = ANTIGRAVITY_REVIEW.read_text(encoding="utf-8")
        blocked = CLAUDE_BLOCKED.read_text(encoding="utf-8")
        consensus = PROVISIONAL_CONSENSUS.read_text(encoding="utf-8")
        status = PENDING_STATUS.read_text(encoding="utf-8")

        self.assertIn(
            "accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod",
            antigravity,
        )
        self.assertIn("blocked_pending_claude_backfill_m70_review", blocked)
        self.assertIn(
            "m70_protocol_draft_2ai_accept_pending_claude_backfill_no_completion_no_execution_no_pod",
            consensus,
        )
        self.assertIn(
            "m70_pending_claude_backfill_not_goal_complete_no_execution_no_pod",
            status,
        )
        normalized_blocked = " ".join(blocked.split())
        normalized_consensus = " ".join(consensus.split())
        self.assertIn("not a 3AI completion seat", normalized_blocked)
        self.assertIn("not a 3AI goal-completion consensus", normalized_consensus)
        normalized_status = " ".join(status.split())
        self.assertIn("M70 is not 3AI-complete", normalized_status)
        self.assertIn("no-execution M71 local harness design", consensus)
        self.assertNotIn("goal_complete_3ai", consensus)

        for text in (antigravity, blocked, consensus, status):
            normalized = " ".join(text.split())
            normalized_lower = normalized.lower()
            self.assertIn("no v3 release", normalized_lower)
            self.assertIn("no all-app", normalized_lower)
            self.assertIn("no pod", normalized_lower)
            self.assertIn("no runbook", normalized_lower)
            self.assertIn("no public speedup", normalized_lower)
            self.assertIn("no broad v3-over-v2", normalized_lower)
            self.assertIn("no route-specific rtnn app tuning", normalized_lower)

    def test_script_rebuilds_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            packet_md_out = Path(tmp) / "packet.md"
            report_md_out = Path(tmp) / "report.md"
            call_out = Path(tmp) / "call.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--packet-md-out",
                    str(packet_md_out),
                    "--report-md-out",
                    str(report_md_out),
                    "--call-out",
                    str(call_out),
                    "--pretty",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertIn("Phoenix V3 M70", packet_md_out.read_text(encoding="utf-8"))
            self.assertIn("Call For Review", call_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
