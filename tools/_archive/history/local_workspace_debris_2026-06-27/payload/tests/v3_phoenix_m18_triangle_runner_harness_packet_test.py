import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m18_triangle_runner_harness_2026-06-22.json"
)
REPORT_PATH = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_m18_triangle_runner_harness_2026-06-22.md"
)
CALL_PATH = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m18_triangle_runner_harness_2026-06-22.md"
)


class V3PhoenixM18TriangleRunnerHarnessPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        cls.report = REPORT_PATH.read_text(encoding="utf-8")
        cls.call = CALL_PATH.read_text(encoding="utf-8")

    def test_m18_harness_packet_blocks_release_and_pod(self):
        self.assertEqual(
            self.payload["status"],
            "m19_env_corrected_triangle_focused_pod_accepted_third_strict_set_a_probe",
        )
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_v3_faster_than_v2_claim_authorized",
            "focused_pod_spend_authorized_now",
            "all_app_pod_spend_authorized",
        ):
            self.assertFalse(self.payload[key], key)
        self.assertTrue(self.payload["third_strict_set_a_material_probe_closed"])
        self.assertIn("replacement_run_authorized_now: false", self.report)

    def test_harness_uses_m16_device_output_runner_shape(self):
        impl = self.payload["implementation"]
        self.assertEqual(impl["script"], "scripts/v3_phoenix_triangle_runner_m18_pod_ab.py")
        self.assertEqual(
            impl["m16_helper"],
            "run_ray_triangle_weighted_summary_device_output_stream_prepared_session",
        )
        self.assertEqual(
            impl["device_output_executor"],
            "prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor",
        )
        self.assertIn("productized_prepared_execution_runner", impl["variants"])
        self.assertIn("heartbeat", impl)

    def test_initial_review_blocker_and_revision_are_recorded(self):
        review = self.payload["initial_m18_review"]
        revision = self.payload["m18_revision"]
        self.assertEqual(review["verdict"], "revise_m18_harness")
        self.assertIn("weighted_hit_sum_out.get()", review["blocking_issue"])
        self.assertEqual(revision["status"], "hot_path_scalar_materialization_boundary_fixed")
        self.assertIn("finalize_weighted_summary", revision["prepared_execution_helper_change"])
        self.assertIn("after measured repeats", revision["runner_change"])
        self.assertIn("Initial Review And Fix", self.report)

    def test_second_review_blockers_and_revision_are_recorded(self):
        review = self.payload["second_m18_review"]
        revision = self.payload["m18_revision_2"]
        self.assertEqual(review["verdict"], "revise_m18_harness")
        self.assertIn("Embree and legacy controls", " ".join(review["blocking_issues"]))
        self.assertIn("checksum", " ".join(review["blocking_issues"]))
        self.assertEqual(revision["status"], "control_oracle_and_edge_checksum_fail_closed")
        self.assertIn("sha256", revision["edge_file_change"])
        self.assertIn("oracle_triangle_count", revision["oracle_change"])
        self.assertIn("Second-review blockers", self.report)

    def test_dry_run_and_pod_command_are_bounded(self):
        dry = self.payload["dry_run_artifact"]
        self.assertEqual(dry["comparisons"], "dry_run_no_performance_interpretation")
        self.assertFalse(dry["pod_run_authorized_by_m18"])
        command = self.payload["focused_pod_command_if_later_2ai_authorized"]
        self.assertIn("--require-rt-hardware", command)
        self.assertIn("--generate-edge-file", command)
        self.assertIn("--repeat 5", command)
        self.assertIn("/root/rtdl_v3_rebuild_20260620/.venv/bin/python", command)
        self.assertEqual(
            self.payload["resource_budget_if_authorized_by_review"]["hard_cap_before_new_review_hours"],
            2.0,
        )
        self.assertIn("accept_m18_authorize_one_focused_triangle_pod", self.call)
        self.assertIn("focused POD authorization now: yes/no", self.call)

    def test_consumed_pod_attempt_and_environment_failure_are_recorded(self):
        authorization = self.payload["final_m18_pod_authorization"]
        self.assertEqual(authorization["verdict"], "accept_m18_authorize_one_focused_triangle_pod")
        self.assertEqual(authorization["status"], "authorization_consumed_by_attempt_1")

        attempt = self.payload["pod_run_attempt_1"]
        self.assertEqual(attempt["status"], "failed_wrong_interpreter_no_performance_evidence")
        self.assertEqual(attempt["remote_command_interpreter"], "/usr/bin/python3")
        self.assertEqual(attempt["failed_check_count"], 6)
        self.assertEqual(attempt["edge_file_preflight_status"], "pass")
        self.assertEqual(attempt["rt_hardware_gate_status"], "pass")
        self.assertTrue(attempt["embree_same_contract_control"]["triangle_count_matches_oracle"])
        self.assertIn("No module named 'cupy'", attempt["legacy_app_front_door_optix"]["failure"])
        self.assertFalse(attempt["comparisons_available"])

        diagnosis = self.payload["pod_environment_diagnosis"]
        self.assertEqual(diagnosis["verified_interpreter"], "/root/rtdl_v3_rebuild_20260620/.venv/bin/python")
        self.assertEqual(diagnosis["verified_packages"]["cupy"], "present")
        self.assertEqual(diagnosis["verified_packages"]["numba"], "present")
        self.assertEqual(diagnosis["remote_no_benchmark_smoke"]["status"], "pass")
        self.assertIn("no benchmark run", diagnosis["remote_no_benchmark_smoke"]["command_scope"])
        self.assertIn("failed_wrong_interpreter_no_performance_evidence", self.report)

    def test_m19_env_corrected_result_is_recorded_without_release_claims(self):
        authorization = self.payload["m19_external_authorization"]
        self.assertEqual(
            authorization["verdict"],
            "authorize_m19_one_env_corrected_triangle_replacement_pod",
        )
        self.assertEqual(authorization["prelaunch_subprocess_interpreter_check"], "pass")

        result = self.payload["m19_env_corrected_pod_result"]
        self.assertEqual(
            result["status"],
            "focused_triangle_productized_runner_pod_accepted_third_strict_set_a_probe",
        )
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["failed_check_count"], 0)
        self.assertTrue(result["all_variant_oracle_checks_passed"])
        self.assertEqual(result["productized_execution_path"], "prepared_execution_session_runner")
        self.assertTrue(result["runtime_executed"])
        self.assertTrue(result["runtime_trunk_executes_end_to_end"])
        self.assertGreaterEqual(result["comparisons"]["runner_vs_embree_hot_speedup"], 1.20)
        self.assertGreaterEqual(result["comparisons"]["runner_vs_embree_wall_speedup"], 1.20)
        self.assertGreaterEqual(result["comparisons"]["runner_vs_legacy_wall_speedup"], 0.98)
        self.assertEqual(
            result["third_strict_set_a_material_probe_interpretation"],
            "closed_by_claude_result_review",
        )
        self.assertTrue(result["third_strict_set_a_material_probe_closed"])
        self.assertFalse(result["another_focused_triangle_rerun_authorized"])
        self.assertTrue(self.payload["third_strict_set_a_material_probe_closed"])
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_v3_faster_than_v2_claim_authorized",
            "all_app_pod_spend_authorized",
        ):
            self.assertFalse(result[key], key)

    def test_success_bars_remain_strict(self):
        gates = self.payload["implementation"]["real_run_fail_closed_gates"]
        self.assertIn("K4 edge-file sha256/edge-count/byte-count preflight before real variants", gates)
        self.assertIn("all three variants match oracle_triangle_count", gates)
        bars = self.payload["success_bars_carried_from_m17"]
        self.assertIn("320000", bars["correctness"])
        self.assertIn("runtime_trunk_executes_end_to_end=true", bars["productized_runtime"])
        self.assertIn(">=1.20x", bars["material_set_a_candidate"])
        self.assertIn(">=0.98x", bars["legacy_no_regression"])
        self.assertIn("all-app flags remain false", bars["claim_boundary"])
        self.assertIn("Was I foolish?", self.report)
        self.assertIn("Was I foolish?", self.call)


if __name__ == "__main__":
    unittest.main()
