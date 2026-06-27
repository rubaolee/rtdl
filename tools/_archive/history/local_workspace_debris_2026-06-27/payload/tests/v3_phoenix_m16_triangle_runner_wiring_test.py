import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m16_triangle_runner_wiring_2026-06-22.json"
)
REPORT_PATH = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_m16_triangle_runner_wiring_2026-06-22.md"
)
CALL_PATH = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m16_triangle_runner_wiring_2026-06-22.md"
)


class V3PhoenixM16TriangleRunnerWiringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        cls.report = REPORT_PATH.read_text(encoding="utf-8")
        cls.call = CALL_PATH.read_text(encoding="utf-8")

    def test_m16_is_local_runner_wiring_not_probe_close(self):
        self.assertEqual(
            self.payload["status"],
            "m16_local_triangle_runner_wiring_validated_not_pod",
        )
        self.assertFalse(self.payload["third_strict_set_a_material_probe_closed"])
        self.assertEqual(
            self.payload["source_verdict"]["m15_verdict"],
            "accept_m15_triangle_m16_local_runner_wiring_no_pod",
        )
        self.assertIn("third_strict_set_a_material_probe_closed: false", self.report)

    def test_m16_two_ai_consensus_keeps_next_step_protocol_only(self):
        consensus = self.payload["m16_2ai_consensus"]
        self.assertEqual(
            consensus["bernoulli_verdict"],
            "accept_m16_prepare_m17_focused_pod_protocol_no_run",
        )
        self.assertTrue(consensus["m16_closes_local_runner_wiring"])
        self.assertFalse(consensus["triangle_counts_as_third_strict_set_a_material_probe_now"])
        self.assertFalse(consensus["focused_pod_spend_authorized_now"])
        self.assertFalse(consensus["all_app_pod_spend_authorized"])
        self.assertEqual(
            consensus["next_step"],
            "m17_focused_triangle_pod_protocol_review_no_run",
        )
        self.assertIn("2-AI verdict: `accept_m16_prepare_m17_focused_pod_protocol_no_run`", self.report)

    def test_helper_is_generic_and_productized(self):
        impl = self.payload["implementation"]
        self.assertEqual(
            impl["helper"],
            "run_ray_triangle_weighted_summary_device_output_stream_prepared_session",
        )
        self.assertEqual(impl["primitive"], "ray_triangle_weighted_summary_device_output_stream")
        self.assertEqual(impl["output_contract"], "generic_ray_triangle_weighted_any_hit_summary_device_output_stream_v1")
        self.assertEqual(impl["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(impl["backend_scope"], "optix")
        self.assertIn("explicit", impl["partner_scope"])

    def test_local_contract_metadata_closes_wiring_only(self):
        result = self.payload["local_contract_result"]
        self.assertTrue(result["runtime_executed"])
        self.assertTrue(result["runtime_trunk_executes_end_to_end"])
        self.assertTrue(result["repeat5_material_probe_candidate"])
        self.assertTrue(result["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(result["hot_path_host_materialization"])
        self.assertFalse(result["m113_graph_capture_claim_authorized"])
        self.assertFalse(result["m113_cuda_graph_capture_validated"])
        self.assertTrue(result["old_triangle_row_does_not_count_as_current_third_probe"])

    def test_claims_and_pod_stay_blocked(self):
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_v3_faster_than_v2_claim_authorized",
            "true_zero_copy_claim_authorized",
            "external_embedding_or_zero_copy_claim_authorized",
            "focused_pod_spend_authorized_now",
            "all_app_pod_spend_authorized",
        ):
            self.assertFalse(self.payload[key], key)
        self.assertIn("focused POD authorization now: yes/no", self.call)
        self.assertIn("all-app POD authorization now: yes/no", self.call)
        self.assertIn("release/public/broad V3-over-V2 wording", self.call)

    def test_review_request_keeps_m17_protocol_separate(self):
        self.assertIn("accept_m16_prepare_m17_focused_pod_protocol_no_run", self.call)
        self.assertIn("Triangle counts as the third strict Set-A material probe now", self.call)
        self.assertIn("Please be strict", self.call)
        self.assertIn("Was I foolish?", self.report)
        self.assertIn("Was I foolish?", self.call)


if __name__ == "__main__":
    unittest.main()
