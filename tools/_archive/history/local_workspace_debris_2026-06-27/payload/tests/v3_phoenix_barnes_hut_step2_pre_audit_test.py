from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_barnes_hut_step2_pre_audit_2026-06-22.json"
AUDIT_MD = AUDIT_JSON.with_suffix(".md")


class V3PhoenixBarnesHutStep2PreAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
        cls.text = AUDIT_MD.read_text(encoding="utf-8")

    def test_pre_audit_blocks_pod_until_productized_runner_exists(self) -> None:
        payload = self.payload

        self.assertEqual(
            payload["status"],
            "conditional_go_for_step1_replacement_implementation_with_required_gates_pod_not_authorized",
        )
        self.assertEqual(payload["redesign_position"], "step_1_replacement_candidate_not_step_2_generalization")
        self.assertFalse(payload["step_1_completion_verified"])
        self.assertEqual(payload["step_1_material_evidence_count"], 0)
        self.assertFalse(payload["pre_audit_decision"]["pod_now_authorized"])
        self.assertTrue(payload["pre_audit_decision"]["runtime_implementation_authorized"])
        self.assertIn("Step 1 material-probe replacement", payload["pre_audit_decision"]["implementation_authorized_as"])
        self.assertEqual(payload["contract"], "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1")
        self.assertEqual(payload["candidate_family"], "aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda")

    def test_audit_separates_material_baseline_from_parity_control(self) -> None:
        comparisons = self.payload["required_comparisons_after_implementation"]

        self.assertIn("prepared OptiX frontier-emission", comparisons["historical_no_go_reference"])
        self.assertIn("existing app-front-door fused Numba CUDA partner", comparisons["primary_parity_control"])
        self.assertIn("must not claim the runner wrapper itself is faster", comparisons["control_interpretation"])
        self.assertEqual(
            self.payload["parity_failure_rule"]["runner_vs_existing_fused_partner_min_each_size"],
            0.95,
        )
        self.assertEqual(
            self.payload["parity_failure_rule"]["runner_vs_existing_fused_partner_target_geomean"],
            0.98,
        )

    def test_audit_records_m7_amendments_and_frozen_set_a_classification(self) -> None:
        self.assertTrue(self.payload["m7_row_amendments_incorporated"])
        amendment = self.payload["m7_row_amendment_evidence"]
        self.assertEqual(amendment["evidence_tree_structure"], "barnes_hut_theta_0.5_2d_bucketized")
        self.assertEqual(
            amendment["large_scale_validation_tier"],
            "route_parity_plus_checksum_no_independent_oracle",
        )
        self.assertTrue(amendment["primary_claim_uses_cpu_numba_fused"])
        self.assertTrue(amendment["prepared_optix_ratio_supporting_metadata_only"])

        classification = self.payload["set_ab_classification"]
        self.assertTrue(classification["classification_frozen_before_next_full_paired_run"])
        self.assertEqual(classification["barnes_hut_set"], "A")
        self.assertFalse(classification["all_app_pod_spend_authorized_now"])

    def test_audit_keeps_claim_flags_and_v3_scope_closed(self) -> None:
        guards = self.payload["hard_guards"]

        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_v3_faster_than_v2_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "full_all_app_rerun_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            self.assertFalse(guards[key], key)

    def test_markdown_states_no_shortcut_and_next_helper(self) -> None:
        for phrase in (
            "Barnes-Hut is a valid next Phoenix V3 material-probe candidate, but it is not yet Step 2 generalization.",
            "productized runner-wrapped fused partner versus the old prepared OptiX frontier-emission",
            "productized runner-wrapped fused partner versus the existing app-front-door fused Numba CUDA partner",
            "runner / existing fused partner must be at least `0.95x`",
            "Do not compare only against the slow OptiX frontier route",
            "historical no-go reference",
            "aggregate_tree_fused_weighted_vector_sum_2d",
            "This audit authorizes no release",
        ):
            self.assertIn(phrase, self.text)


if __name__ == "__main__":
    unittest.main()
