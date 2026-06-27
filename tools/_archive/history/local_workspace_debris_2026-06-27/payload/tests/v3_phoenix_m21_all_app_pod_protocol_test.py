import json
import os
import unittest
from pathlib import Path

from scripts import goal2626_benchmark_embree_optix_baseline as goal2626
from scripts.v3_phoenix_m21_all_app_protocol_gate import build_payload as build_gate_payload


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m21_all_app_pod_protocol_2026-06-23.json"
)
MD_PATH = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md"
)
CALL_PATH = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md"
)
RUNNER_PATH = ROOT / "scripts" / "phoenix_v3_serious_paired_v2x_runner.sh"
GATE_SCRIPT_PATH = ROOT / "scripts" / "v3_phoenix_m21_all_app_protocol_gate.py"
GOAL2626_SCRIPT_PATH = ROOT / "scripts" / "goal2626_benchmark_embree_optix_baseline.py"


class V3PhoenixM21AllAppPODProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        cls.markdown = MD_PATH.read_text(encoding="utf-8")
        cls.call = CALL_PATH.read_text(encoding="utf-8")
        cls.runner = RUNNER_PATH.read_text(encoding="utf-8")
        cls.gate_script = GATE_SCRIPT_PATH.read_text(encoding="utf-8")

    def test_protocol_blocks_run_and_release_until_external_verdict(self):
        self.assertEqual(
            self.payload["status"],
            "protocol_prepared_external_review_required_no_run",
        )
        authorizations = self.payload["authorizations"]
        self.assertTrue(authorizations["protocol_preparation_authorized_by_m20"])
        for key in (
            "external_m21_run_authorization_obtained",
            "all_app_pod_run_authorized_now",
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_v3_faster_than_v2_claim_authorized",
            "release_based_on_all_app_run_outcome",
        ):
            self.assertFalse(authorizations[key], key)
        self.assertIn("all_app_pod_run_authorized_now: false", self.markdown)
        self.assertIn("Unless your verdict is exactly `authorize_m21_one_all_app_pod_run`", self.call)

    def test_required_fail_closed_bars_are_preregistered(self):
        bars = {bar["id"]: bar for bar in self.payload["fail_closed_bars"]}
        self.assertEqual(bars["barnes_hut_app_geomean_floor"]["fail_if"], "< 0.90")
        self.assertEqual(bars["librts_embree_aabb_index_row_floor"]["fail_if"], "< 0.95")
        self.assertEqual(
            bars["librts_embree_aabb_index_row_floor"]["row_id"],
            "goal2626_large|librts_spatial_index|aabb_index_all_count_only|embree|librts_embree_aabb_index",
        )
        self.assertEqual(bars["set_b_geomean_floor"]["fail_if"], "< 0.98")
        self.assertEqual(bars["new_app_level_severe_regression_floor"]["fail_if"], "< 0.90")
        self.assertTrue(all(bar["protocol_fail"] for bar in bars.values()))
        documented = self.payload["documented_not_pass_fail_for_this_evidence_run"]
        self.assertIn("set_a_geomean_v3_vs_v2", documented)
        self.assertIn("set_a_apps_over_1_05x", documented)
        self.assertIn("These values must be reported exactly", self.markdown)
        self.assertEqual(
            self.payload["protocol_gate_script"],
            "scripts/v3_phoenix_m21_all_app_protocol_gate.py",
        )
        self.assertIn("protocol_gate_command_after_analysis", self.payload)

    def test_frozen_case_whitelist_and_watch_row_are_recorded(self):
        whitelist = self.payload["frozen_case_id_whitelist"]
        self.assertTrue(whitelist["classification_frozen_before_run"])
        self.assertTrue(whitelist["case_id_whitelist_frozen"])
        self.assertEqual(whitelist["unknown_case_id_policy"], "protocol_fail_out_of_scope")
        self.assertEqual(whitelist["app_classification"]["triangle_counting"], "A")
        self.assertIn(
            "triangle_counting_embree_rt_graph_2a1_cliques_80000",
            whitelist["approved_case_ids_by_app"]["triangle_counting"],
        )
        watch = self.payload["watch_rows"][0]
        self.assertEqual(watch["id"], "librts_optix_aabb_index_watch_row")
        self.assertEqual(watch["alert_if"], "< 0.95")
        self.assertIn("watch", watch["status"])
        self.assertIn("not_current_blocking_row", watch["status"])

    def test_hardware_interpreter_and_correctness_gates_are_fail_closed(self):
        hardware = self.payload["hardware_gate"]
        self.assertEqual(hardware["required_gpu_name"], "NVIDIA RTX 4000 Ada Generation")
        self.assertEqual(hardware["required_driver_version"], "550.127.05")
        self.assertEqual(hardware["required_compute_capability"], "8.9")
        self.assertIn("id_ed25519_rtdl_codex_current_pod", hardware["pod_access_hint"])
        self.assertEqual(hardware["runner_fail_exit_code_on_mismatch"], 67)
        self.assertTrue(hardware["fail_if_gpu_or_driver_differs_without_new_review"])
        preflight = self.payload["latest_no_benchmark_pod_preflight"]
        self.assertEqual(preflight["status"], "pass")
        self.assertFalse(preflight["all_app_pod_run_started"])
        self.assertEqual(preflight["python"], "/root/rtdl_v3_rebuild_20260620/.venv/bin/python")

        interpreter = self.payload["interpreter_preflight"]
        self.assertEqual(
            interpreter["required_project_venv_python"],
            "/root/rtdl_v3_rebuild_20260620/.venv/bin/python",
        )
        self.assertTrue(interpreter["fail_closed_if_any_check_fails"])
        self.assertEqual(interpreter["fail_exit_codes"]["missing_or_not_executable"], 65)
        self.assertEqual(interpreter["fail_exit_codes"]["sys_executable_mismatch"], 66)
        self.assertEqual(interpreter["fail_exit_codes"]["required_import_failure"], 68)
        self.assertEqual(interpreter["fail_exit_codes"]["benchmark_child_interpreter_mismatch"], 69)

        correctness = self.payload["correctness_oracle_gate"]
        self.assertTrue(correctness["all_required_suites_must_exit_zero"])
        self.assertTrue(correctness["primary_metric_source_mismatch_count_must_equal_zero"])
        self.assertTrue(correctness["performance_rows_accepted_only_after_correctness"])

    def test_runner_uses_project_venv_python_explicitly(self):
        self.assertIn('python_bin="${PYTHON_BIN:-$base/.venv/bin/python}"', self.runner)
        self.assertIn("sys.executable", self.runner)
        self.assertIn("exit 65", self.runner)
        self.assertIn("exit 66", self.runner)
        self.assertIn("exit 67", self.runner)
        self.assertIn("exit 68", self.runner)
        self.assertIn("exit 69", self.runner)
        self.assertIn("required_import_preflight", self.runner)
        self.assertIn("child_interpreter_preflight", self.runner)
        self.assertIn("goal2626_child", self.runner)
        self.assertIn("goal3828_child", self.runner)
        self.assertIn("gpu_preflight_name", self.runner)
        self.assertIn('"$python_bin" scripts/goal2626_benchmark_embree_optix_baseline.py', self.runner)
        self.assertIn('"$python_bin" scripts/goal2636_strengthen_benchmark_rows.py', self.runner)
        self.assertIn('"$python_bin" scripts/goal3828_current_benchmark_scale_profile_runner.py', self.runner)
        self.assertNotIn("run_cmd \"$tree\" goal2626_large \\\n    python3", self.runner)

    def test_goal2626_child_commands_inherit_selected_python(self):
        script = GOAL2626_SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn('return ("python3", path', script)

        old_python_bin = os.environ.get("PYTHON_BIN")
        try:
            os.environ["PYTHON_BIN"] = "/tmp/rtdl-test-venv/bin/python"
            self.assertEqual(
                goal2626._py("examples/current/research_benchmarks/app.py")[0],
                "/tmp/rtdl-test-venv/bin/python",
            )
        finally:
            if old_python_bin is None:
                os.environ.pop("PYTHON_BIN", None)
            else:
                os.environ["PYTHON_BIN"] = old_python_bin

    def test_resource_estimate_and_goal_decision_audit_are_present(self):
        budget = self.payload["resource_budget_estimate_if_later_authorized"]
        self.assertEqual(budget["expected_hours_low"], 5.5)
        self.assertEqual(budget["expected_hours_high"], 7.0)
        self.assertEqual(budget["hard_cap_hours_before_new_review"], 8.0)
        self.assertEqual(budget["hard_cap_cost_usd"], 2.0)
        audit = self.payload["goal_level_decision_audit"]
        self.assertIn("was_i_foolish", audit)
        self.assertIn("foolish_actions", audit)
        self.assertIn("other_path", audit)
        self.assertIn("different_path_now", audit)
        self.assertIn("Was I foolish?", self.markdown)
        self.assertIn("v3_phoenix_m21_all_app_protocol_gate.py", self.call)
        self.assertIn("v3_phoenix_m21_all_app_protocol_gate", self.gate_script)

    def test_protocol_gate_fails_the_current_old_scorecard_baseline(self):
        gate_payload = build_gate_payload()
        self.assertEqual(gate_payload["status"], "protocol_fail_invalid_or_out_of_scope")
        self.assertFalse(gate_payload["release_authorized"])
        failure_ids = {failure["bar"] for failure in gate_payload["protocol_failures"]}
        self.assertIn("barnes_hut_app_geomean_floor", failure_ids)
        self.assertIn("librts_embree_aabb_index_row_floor", failure_ids)
        self.assertIn("new_app_level_severe_regression_floor", failure_ids)
        self.assertEqual(gate_payload["scope_failures"], [])
        self.assertGreaterEqual(len(gate_payload["correctness_failures"]), 1)
        documented = gate_payload["documented_values"]
        self.assertAlmostEqual(documented["overall_geomean_v3_vs_v2"], 1.0117790403434224)
        self.assertAlmostEqual(documented["set_a_geomean_v3_vs_v2"], 1.0129340100769488)


if __name__ == "__main__":
    unittest.main()
