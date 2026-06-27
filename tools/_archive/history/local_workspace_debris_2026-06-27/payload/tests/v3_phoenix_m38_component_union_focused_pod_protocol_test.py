import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m38_component_union_focused_pod_protocol_2026-06-23.json"
)
MD_PATH = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m38_component_union_focused_pod_protocol_2026-06-23.md"
)
REPORT_PATH = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_m38_component_union_focused_pod_protocol_2026-06-23.md"
)
CALL_PATH = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m38_component_union_focused_pod_protocol_2026-06-23.md"
)


class V3PhoenixM38ComponentUnionFocusedPodProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        cls.md = MD_PATH.read_text(encoding="utf-8")
        cls.report = REPORT_PATH.read_text(encoding="utf-8")
        cls.call = CALL_PATH.read_text(encoding="utf-8")

    def test_m38_is_protocol_only_and_blocks_claims(self):
        self.assertEqual(
            self.payload["status"],
            "m38_protocol_ready_for_review_no_pod_run",
        )
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_v3_faster_than_v2_claim_authorized",
            "true_zero_copy_claim_authorized",
            "external_embedding_or_zero_copy_claim_authorized",
            "focused_pod_spend_authorized_now",
            "all_app_pod_spend_authorized",
            "component_union_material_probe_closed",
        ):
            self.assertFalse(self.payload[key], key)
        self.assertIn("focused_pod_spend_authorized_now: false", self.md)
        self.assertIn("does not authorize POD spend", self.report)

    def test_protocol_uses_serious_component_union_row(self):
        row = self.payload["row"]
        self.assertEqual(
            row["row_id"],
            "component_union_clustered3d_262144_points_repeat5_m38_focused_probe",
        )
        self.assertEqual(row["generic_capability"], "component_union")
        self.assertEqual(row["point_count"], 262144)
        self.assertEqual(row["warmup"], 1)
        self.assertEqual(row["repeat"], 5)
        self.assertGreaterEqual(row["serious_scale_floor_points"], 262144)
        self.assertTrue(row["smoke_rows_do_not_count"])
        self.assertIn("not full DBSCAN paper reproduction", row["scope_boundary"])

    def test_variants_are_same_contract_and_require_m37_runner(self):
        variants = {item["id"]: item for item in self.payload["variants"]}
        self.assertEqual(
            set(variants),
            {
                "embree_same_contract_component_union_control",
                "legacy_optix_grouped_stream_component_labels",
                "productized_prepared_execution_runner",
            },
        )
        runner = variants["productized_prepared_execution_runner"]
        for variant in variants.values():
            self.assertEqual(
                variant["harness_status"],
                "required_before_pod_run_not_yet_authorized_by_m38_packet",
            )
            self.assertNotIn("command_template", variant)
            self.assertIn("proposed_m39_command_template", variant)
        self.assertEqual(
            runner["required_helper"],
            "run_radius_graph_component_union_3d_prepared_session",
        )
        must_report = "\n".join(runner["must_report"])
        self.assertIn("runtime_trunk_executes_end_to_end=true", must_report)
        self.assertIn("component_union_phase_accounting_visible=true", must_report)
        self.assertIn("component_label_columns_present=true", must_report)
        self.assertIn("component_signature_pass_executed=false", must_report)
        self.assertIn("component_labels_contract", "\n".join(variants["embree_same_contract_component_union_control"]["must_report"]))
        self.assertIn("component_labels_contract", "\n".join(variants["legacy_optix_grouped_stream_component_labels"]["must_report"]))

    def test_signature_shortcut_is_blocked(self):
        gates = "\n".join(self.payload["pre_run_gates"])
        failures = self.payload["failure_classification"]

        self.assertIn("Component-signature rows cannot replace component-union label rows", gates)
        self.assertEqual(
            failures["component_signature_substituted_for_labels"],
            "invalid run; no performance interpretation",
        )
        self.assertIn("signature-only route cannot replace", self.md)

    def test_success_bars_are_material_and_bounded(self):
        bars = self.payload["success_bars"]

        self.assertIn("component-label outputs", bars["correctness"])
        self.assertIn("runtime_trunk_executes_end_to_end=true", bars["productized_runtime"])
        self.assertIn("component_label_columns_present=true", bars["productized_runtime"])
        self.assertIn("1.20x", bars["material_set_a_candidate"])
        self.assertIn("0.98x", bars["legacy_no_regression"])
        self.assertIn("all release/public/broad V3-over-V2/V4/zero-copy flags", bars["claim_boundary"])

    def test_resource_budget_and_review_request_are_bounded(self):
        budget = self.payload["resource_budget_if_authorized_later"]

        self.assertEqual(budget["hard_cap_before_new_review_hours"], 2.0)
        self.assertEqual(budget["hard_cap_before_new_review_cost_usd"], 0.5)
        self.assertEqual(budget["all_app_pod_wall_hours"], "not authorized")
        self.assertIn("accept_m38_authorize_m39_runner_harness_no_pod", self.call)
        self.assertIn("accept_m38_authorize_one_focused_component_union_pod_after_harness_gate", self.call)
        self.assertIn("No matter the verdict", self.call)
        self.assertIn("Was I foolish?", self.report)
        self.assertIn("Was I foolish?", self.call)


if __name__ == "__main__":
    unittest.main()
