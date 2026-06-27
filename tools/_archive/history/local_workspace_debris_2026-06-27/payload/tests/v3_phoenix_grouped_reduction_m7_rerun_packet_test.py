import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_grouped_reduction_m7_rerun_packet.py"
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.md"


class V3PhoenixGroupedReductionM7RerunPacketTest(unittest.TestCase):
    def load(self):
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_is_not_execution_or_release_authorization(self):
        payload = self.load()
        self.assertEqual(payload["status"], "ready_for_external_review_not_executed")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized_before_run"])
        self.assertEqual(payload["summary"]["planned_independent_rows"], 8)
        self.assertEqual(payload["summary"]["all_planned_rows_warmup"], 3)

    def test_planned_rows_standardize_scales_and_warmup(self):
        rows = {row["id"]: row for row in self.load()["planned_rows"]}
        self.assertEqual(set(rows), {"m7_grouped_reduction_262144", "m7_grouped_reduction_524288"})
        self.assertEqual(rows["m7_grouped_reduction_262144"]["generated_groups"], 1024)
        self.assertEqual(rows["m7_grouped_reduction_524288"]["generated_groups"], 2048)
        for row in rows.values():
            self.assertEqual(row["modes"], ["count", "sum"])
            self.assertEqual(row["backends"], ["embree", "optix"])
            self.assertEqual(row["warmup"], 3)
            self.assertIn("warmup3", row["output"])

    def test_required_commands_include_claim_and_hardware_gates(self):
        commands = {command["id"]: command for command in self.load()["required_commands"]}
        for required in [
            "env_probe",
            "claim_boundary_gate",
            "optix_hardware_gate",
            "native_build",
            "m7_grouped_reduction_262144",
            "m7_grouped_reduction_524288",
            "post_run_intake",
            "artifact_manifest",
        ]:
            self.assertIn(required, commands)
            self.assertTrue(commands[required]["required"])
        self.assertIn("m7_promotion_authorized_before_run", commands["claim_boundary_gate"]["command"])
        self.assertIn("whole_app_speedup_claim_authorized", commands["claim_boundary_gate"]["command"])
        self.assertIn("2>&1", commands["claim_boundary_gate"]["command"])
        self.assertIn("--require-rt-hardware", commands["optix_hardware_gate"]["command"])
        self.assertIn("scripts/v3_gpu_python_env_gate.py", commands["env_probe"]["command"])
        self.assertIn("scripts/v3_phoenix_grouped_reduction_m7_feasibility.py", commands["env_probe"]["command"])
        for measure in ["m7_grouped_reduction_262144", "m7_grouped_reduction_524288"]:
            command = commands[measure]
            self.assertIn("--warmup 3", command["command"])
            self.assertIn("--include-iteration-walls", command["command"])
            self.assertEqual(command["generic_capability"], "grouped_reduction")
        intake = commands["post_run_intake"]["command"]
        self.assertIn("scripts/v3_phoenix_grouped_reduction_m7_feasibility.py", intake)
        self.assertIn("--fresh-rerun", intake)
        self.assertIn("--source m7_262144=", intake)
        self.assertIn("--source m7_524288=", intake)
        self.assertIn("--json-out", intake)
        self.assertIn("--md-out", intake)

    def test_planned_outputs_match_measure_commands(self):
        payload = self.load()
        commands = {command["id"]: command for command in payload["required_commands"]}
        for row in payload["planned_rows"]:
            self.assertIn(row["output"], commands[row["id"]]["command"])

    def test_public_contract_requires_hot_cold_repeat_context(self):
        rules = "\n".join(self.load()["prepared_query_public_contract"]["rules"])
        self.assertIn("cold/setup time", rules)
        self.assertIn("repeat count", rules)
        self.assertIn("Single-query end-to-end speedup", rules)
        self.assertIn("Whole-database or paper-reproduction wording remains false", rules)

    def test_failure_policy_forbids_backfill_from_old_warmups(self):
        policy = self.load()["failure_policy"]
        self.assertTrue(policy["preserve_failed_artifacts"])
        self.assertTrue(policy["no_scale_down_without_new_packet"])
        self.assertTrue(policy["no_public_claim_from_partial_success"])
        self.assertTrue(policy["no_merge_with_old_warmup1_or_warmup2_rows"])
        self.assertIn("do not backfill", policy["if_524288_sum_exceeds_time_budget"])

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "rerun.json"
            md_out = Path(tmp) / "rerun.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            rebuilt = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(rebuilt["summary"], self.load()["summary"])
            self.assertEqual(rebuilt["required_commands"], self.load()["required_commands"])
            self.assertIn("ready for external review, not executed", md_out.read_text(encoding="utf-8"))

    def test_report_keeps_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "not executed",
            "release_authorized: false",
            "public_speedup_claim_authorized: false",
            "m7_promotion_authorized_before_run: false",
            "fresh M7-designated grouped_reduction rerun",
            "warmup 3",
            "No public wording is written",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
