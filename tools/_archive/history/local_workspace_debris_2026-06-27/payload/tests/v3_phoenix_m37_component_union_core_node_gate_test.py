import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m37_component_union_core_node_and_adapter_metadata_gate_2026-06-23.md"
CALL_FOR_REVIEW = ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m37_component_union_core_node_2026-06-23.md"
LEDGER = ROOT / "docs" / "reports" / "phoenix_v3_m37_prepared_session_step4_surface_ledger_2026-06-23.md"


class V3PhoenixM37ComponentUnionCoreNodeGateTest(unittest.TestCase):
    def test_m37_report_preserves_non_release_runtime_boundary(self):
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Status: `m37_component_union_core_node_local_ready_not_release`",
            "run_radius_graph_component_union_3d_prepared_session",
            "prepared_execution_session_runner",
            "generic_fixed_radius_graph_component_union_3d",
            "generic_prepared_optix_numba_grouped_stream_component_labels_3d",
            "component_union_phase_accounting_visible",
            "component_signature_accounting_split",
            "component_signature_pass_executed",
            "public_helper_count: 13",
            "step4_ready: 9",
            "blocked_set_a_seed: 1",
            "blocked_set_b_control: 3",
            "not a benchmark result",
            "not a release",
            "Non-Authorization",
        ):
            self.assertIn(phrase, text)

        self.assertNotIn("release_authorized: true", text)
        self.assertNotIn("all_app_pod_spend_authorized: true", text)
        self.assertNotIn("v4_work_authorized: true", text)

    def test_m37_ledger_lists_component_union_helper_once(self):
        text = LEDGER.read_text(encoding="utf-8")

        self.assertEqual(text.count("`run_radius_graph_component_union_3d_prepared_session`"), 1)
        self.assertIn("M37 generic component-union helper", text)
        self.assertIn("nine runner-callable continuation", text)
        self.assertIn("not performance evidence", text)

    def test_call_for_review_is_bounded(self):
        text = CALL_FOR_REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "Status: `request_m37_component_union_core_node_review_not_release`",
            "accept_m37_component_union_core_node_continue",
            "accept_with_amendments",
            "blocked_needs_code_or_ledger_changes",
            "reject_wrong_boundary_or_app_specific",
            "Explicit Non-Authorization Block",
        ):
            self.assertIn(phrase, text)

        self.assertNotIn("release_authorized: true", text)
        self.assertNotIn("public_speedup_claim_authorized: true", text)

    def test_referenced_paths_exist(self):
        for path in (REPORT, CALL_FOR_REVIEW, LEDGER):
            text = path.read_text(encoding="utf-8")
            paths = sorted(set(re.findall(r"`([^`]+\.(?:md|json|txt|py|ps1))`", text)))
            missing = [item for item in paths if not (ROOT / item).exists()]
            self.assertEqual(missing, [], path.name)


if __name__ == "__main__":
    unittest.main()
