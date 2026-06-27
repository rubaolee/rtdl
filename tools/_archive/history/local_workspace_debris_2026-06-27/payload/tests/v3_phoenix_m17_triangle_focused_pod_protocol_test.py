import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.json"
)
REPORT_PATH = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.md"
)
CALL_PATH = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.md"
)


class V3PhoenixM17TriangleFocusedPodProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        cls.report = REPORT_PATH.read_text(encoding="utf-8")
        cls.call = CALL_PATH.read_text(encoding="utf-8")

    def test_m17_is_protocol_only_and_blocks_claims(self):
        self.assertEqual(self.payload["status"], "m17_protocol_ready_for_review_no_pod_run")
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(self.payload["focused_pod_spend_authorized_now"])
        self.assertFalse(self.payload["all_app_pod_spend_authorized"])
        self.assertFalse(self.payload["third_strict_set_a_material_probe_closed"])
        self.assertIn("focused_pod_spend_authorized_now: false", self.report)

    def test_m17_consensus_authorizes_m18_harness_only(self):
        consensus = self.payload["m17_2ai_consensus"]
        self.assertEqual(
            consensus["bernoulli_verdict"],
            "accept_m17_authorize_m18_runner_harness_no_pod",
        )
        self.assertTrue(consensus["m17_protocol_sufficient_for_m18_harness_only"])
        self.assertTrue(consensus["runner_harness_is_pre_run_blocker"])
        self.assertFalse(consensus["focused_pod_spend_authorized_now"])
        self.assertFalse(consensus["all_app_pod_spend_authorized"])
        self.assertEqual(consensus["next_step"], "m18_local_triangle_runner_harness_no_pod")
        self.assertIn("2-AI verdict: `accept_m17_authorize_m18_runner_harness_no_pod`", self.report)

    def test_protocol_uses_serious_exact_triangle_row(self):
        row = self.payload["row"]
        self.assertEqual(row["workload"], "Generated K4 clique ladder, 80,000 cliques")
        self.assertEqual(row["edge_count"], 480000)
        self.assertEqual(row["oracle_triangle_count"], 320000)
        self.assertGreaterEqual(row["serious_scale_floor_cliques"], 80000)
        self.assertTrue(row["smoke_rows_do_not_count"])
        self.assertIn("not RT-Graph paper reproduction", self.report)

    def test_variants_include_controls_and_runner_harness_blocker(self):
        variants = {item["id"]: item for item in self.payload["variants"]}
        self.assertEqual(
            set(variants),
            {
                "embree_same_contract_control",
                "legacy_app_front_door_optix",
                "productized_prepared_execution_runner",
            },
        )
        self.assertIn("--backend embree", variants["embree_same_contract_control"]["command"])
        self.assertIn("--backend optix", variants["legacy_app_front_door_optix"]["command"])
        runner = variants["productized_prepared_execution_runner"]
        self.assertEqual(
            runner["required_helper"],
            "run_ray_triangle_weighted_summary_device_output_stream_prepared_session",
        )
        self.assertIn("required_before_pod_run", runner["harness_status"])
        self.assertIn("prepared_execution_session_runner", "\n".join(runner["must_report"]))

    def test_success_bars_are_material_and_not_broad_release(self):
        bars = self.payload["success_bars"]
        self.assertIn("320000", bars["correctness"])
        self.assertIn("runtime_trunk_executes_end_to_end=true", bars["productized_runtime"])
        self.assertIn("1.20x", bars["material_set_a_candidate"])
        self.assertIn("0.98x", bars["legacy_no_regression"])
        self.assertIn("all release/public/broad V3-over-V2/V4/zero-copy flags", bars["claim_boundary"])
        self.assertIn("runner OptiX must beat Embree", self.report)

    def test_resource_budget_and_review_request_are_bounded(self):
        budget = self.payload["resource_budget_if_authorized_later"]
        self.assertEqual(budget["hard_cap_before_new_review_hours"], 2.0)
        self.assertEqual(budget["hard_cap_before_new_review_cost_usd"], 0.5)
        self.assertEqual(budget["all_app_pod_wall_hours"], "not authorized")
        self.assertIn("accept_m17_authorize_m18_runner_harness_no_pod", self.call)
        self.assertIn("accept_m17_authorize_one_focused_triangle_pod_after_harness_gate", self.call)
        self.assertIn("runner harness is a pre-run blocker", self.call)
        self.assertIn("Was I foolish?", self.report)
        self.assertIn("Was I foolish?", self.call)


if __name__ == "__main__":
    unittest.main()
