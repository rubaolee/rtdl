import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_m71_rtnn_local_harness_dry_run_gate.py"
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.json"
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md"
CALL_FOR_REVIEW = ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md"
RTNN_APP = ROOT / "examples" / "current" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
ANTIGRAVITY_REVIEW = (
    ROOT / "docs" / "reviews" / "antigravity_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_review_2026-06-23.md"
)
PROVISIONAL_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_antigravity_phoenix_v3_m71_local_dry_run_gate_provisional_2ai_consensus_pending_claude_2026-06-23.md"
)
STATUS_REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m71_status_provisional_2ai_pending_claude_2026-06-23.md"


class V3PhoenixM71RtnnLocalHarnessDryRunGateTest(unittest.TestCase):
    def load(self) -> dict:
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_m71_is_dry_run_only_and_authorizes_nothing(self) -> None:
        payload = self.load()

        self.assertEqual(payload["status"], "m71_rtnn_local_harness_dry_run_gate_ready_no_execution_no_pod")
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertTrue(payload["scope"]["dry_run_gate_only"])
        self.assertFalse(payload["scope"]["benchmark_execution_authorized"])
        self.assertFalse(payload["scope"]["runbook_authorized"])
        self.assertFalse(payload["scope"]["pod_authorized"])
        self.assertFalse(payload["scope"]["release_authorized"])
        self.assertFalse(payload["scope"]["commands_generated"])
        self.assertFalse(payload["scope"]["authorization_token_present"])
        for value in payload["non_authorization"].values():
            self.assertFalse(value)

    def test_shape_plan_covers_m70_without_commands(self) -> None:
        plan = self.load()["dry_run_plan"]
        rows = [row for shape in plan for row in shape["rows"]]

        self.assertEqual(len(plan), 7)
        self.assertEqual(len(rows), 14)
        self.assertEqual({shape["distribution"] for shape in plan}, {"uniform", "clustered", "shell"})
        self.assertTrue(all(shape["dry_run_only"] for shape in plan))
        self.assertTrue(all(shape["command_present"] is False for shape in plan))
        self.assertTrue(all(shape["query_batch_size"] == shape["point_count"] for shape in plan))
        self.assertTrue(all(shape["query_role"] == "full_batch_self_query" for shape in plan))

    def test_source_surface_has_required_telemetry_fields(self) -> None:
        payload = self.load()
        surface = payload["source_surface"]

        self.assertTrue(surface["productized_mode_present"])
        self.assertTrue(surface["generic_helper_call_present"])
        self.assertTrue(surface["generic_helper_defined"])
        self.assertTrue(surface["full_batch_self_query_constraint_present"])
        self.assertTrue(surface["telemetry_split_helper_present"])
        self.assertTrue(surface["required_timing_fields_present"])
        self.assertTrue(surface["required_metadata_fields_present"])
        self.assertTrue(payload["summary"]["telemetry_contract_ready"])

        timing = surface["timing_fields"]
        for field in (
            "input_load",
            "input_pack",
            "input_load_pack",
            "runner_after_input_load_pack",
            "hot_query_median",
            "runner_wall",
            "runner_measured_total",
            "runner_measured_median",
        ):
            self.assertTrue(timing[field], field)

        self.assertEqual(surface["metadata_fields_missing"], [])
        self.assertIn("release_authorized", surface["metadata_fields_present"])
        self.assertNotIn("metadata_fields", surface)

        encoded_surface = json.dumps(surface, sort_keys=True)
        self.assertNotIn('"release_authorized": true', encoded_surface)
        self.assertNotIn('"public_speedup_claim_authorized": true', encoded_surface)
        self.assertNotIn('"broad_v3_faster_than_v2_claim_authorized": true', encoded_surface)

    def test_rtnn_app_change_is_telemetry_only(self) -> None:
        source = RTNN_APP.read_text(encoding="utf-8")

        self.assertIn("def _load_rtnn_csv_xyz_records", source)
        self.assertIn("input_load_sec", source)
        self.assertIn("input_pack_sec", source)
        self.assertIn('"input_load"', source)
        self.assertIn('"input_pack"', source)
        self.assertIn('"hot_query_median"', source)
        self.assertIn('"signature_match_status"', source)
        self.assertIn("rt.run_fixed_radius_ranked_summary_3d_prepared_session", source)
        self.assertNotIn("command_template", source)

    def test_docs_preserve_boundaries(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW):
            text = path.read_text(encoding="utf-8")
            normalized = " ".join(text.split())
            self.assertIn("M71", text)
            self.assertIn("RTNN", text)
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

        call = CALL_FOR_REVIEW.read_text(encoding="utf-8")
        for verdict in (
            "accept_m71_local_dry_run_gate_continue_no_execution_no_pod",
            "revise_m71_dry_run_gate_before_any_harness_work",
            "reject_m71_dry_run_gate_oversteps_no_execution_boundary",
        ):
            self.assertIn(verdict, call)

    def test_external_review_state_is_provisional_and_non_authorizing(self) -> None:
        antigravity = ANTIGRAVITY_REVIEW.read_text(encoding="utf-8")
        consensus = PROVISIONAL_CONSENSUS.read_text(encoding="utf-8")
        status = STATUS_REPORT.read_text(encoding="utf-8")

        self.assertIn("accept_m71_local_dry_run_gate_continue_no_execution_no_pod", antigravity)
        self.assertIn(
            "m71_local_dry_run_gate_2ai_accept_pending_claude_backfill_no_completion_no_execution_no_pod",
            consensus,
        )
        self.assertIn("m71_provisional_2ai_accept_not_goal_complete_no_execution_no_pod", status)
        self.assertIn("M70 Claude review debt must be backfilled", antigravity)
        self.assertIn("does not mark any goal complete", consensus)
        self.assertIn("Claude M70 recorded review", status)

        for text in (antigravity, consensus, status):
            normalized_lower = " ".join(text.split()).lower()
            self.assertIn("no v3 release", normalized_lower)
            self.assertIn("no all-app", normalized_lower)
            self.assertIn("no pod", normalized_lower)
            self.assertIn("no runbook", normalized_lower)
            self.assertIn("no benchmark execution", normalized_lower)
            self.assertIn("no public speedup", normalized_lower)
            self.assertIn("no broad v3-over-v2", normalized_lower)
            self.assertIn("no route-specific rtnn app tuning", normalized_lower)

    def test_script_rebuilds_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
            call_out = Path(tmp) / "call.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
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
            self.assertIn("Phoenix V3 M71", md_out.read_text(encoding="utf-8"))
            self.assertIn("Call For Review", call_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
