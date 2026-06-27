from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_release_decision import V4_GOAL4632_DECISION
from rtdsl.v4_release_decision import V4_AUTHORIZED_RELEASE_LABEL
from rtdsl.v4_release_decision import validate_v4_goal4632_release_decision
from rtdsl.v4_release_decision import v4_goal4632_release_decision


class V4Goal4632ReleaseDecisionTest(unittest.TestCase):
    def test_decision_records_goal4720_release_candidate_with_legacy_app_boundary(self) -> None:
        decision = validate_v4_goal4632_release_decision()

        self.assertEqual(V4_GOAL4632_DECISION, decision["decision"])
        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["formal_release_authorized"])
        self.assertTrue(decision["bounded_operator_surface_available"])
        self.assertFalse(decision["app_level_high_performance_authorized"])
        self.assertTrue(decision["v4_python_edsl_release_candidate_supported"])
        self.assertTrue(decision["operator_pushdown_workflow_high_performance_supported"])
        self.assertFalse(decision["legacy_all_app_high_performance_supported"])
        self.assertEqual(
            "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim",
            decision["current_app_level_decision_label"],
        )
        self.assertEqual(
            V4_AUTHORIZED_RELEASE_LABEL,
            decision["authorized_release_label"],
        )
        self.assertTrue(decision["release_candidate_authorized"])
        self.assertTrue(decision["performance_preview_authorized"])
        self.assertFalse(decision["development_state_authorized"])
        self.assertIn("Python eDSL/operator-pushdown release candidate", decision["public_wording"])
        self.assertIn("custom predicate early-exit", decision["public_wording"])
        self.assertIn("complete 10-app", decision["public_wording"])

    def test_all_scorecard_gates_are_recorded(self) -> None:
        decision = v4_goal4632_release_decision()
        gates = {gate["gate"]: gate for gate in decision["gates"]}

        self.assertEqual(
            set(gates),
            {
                "G1_fixed_radius_anchor",
                "G2_operator_coverage_audit",
                "G3_second_tier2_same_contract_gate",
                "G4_weighted_sum_candidate",
                "G5_pushdown_recognizer",
                "G6_tier3_boundary",
                "G7_aabb_index_frontdoor_catalog",
                "G8_formal_release_scorecard_freeze",
                "G9_serious_release_scorecard_pod_gate",
                "G10_clean_tree_reproducibility",
                "G11_final_release_authorization",
                "G12_custom_predicate_early_exit_workflow",
                "G13_public_docs_current_frontdoor_cleanup",
                "G14_full_v4_local_gate_after_current_frontdoor_cleanup",
            },
        )
        self.assertTrue(gates["G1_fixed_radius_anchor"]["passed_for_release"])
        self.assertTrue(gates["G2_operator_coverage_audit"]["passed_for_release"])
        self.assertTrue(gates["G3_second_tier2_same_contract_gate"]["passed_for_release"])
        self.assertTrue(gates["G4_weighted_sum_candidate"]["passed_for_release"])
        self.assertTrue(gates["G5_pushdown_recognizer"]["passed_for_release"])
        self.assertTrue(gates["G6_tier3_boundary"]["passed_for_release"])
        self.assertTrue(gates["G7_aabb_index_frontdoor_catalog"]["passed_for_release"])
        self.assertTrue(gates["G8_formal_release_scorecard_freeze"]["passed_for_release"])
        self.assertIn("formal release scorecard freeze", gates["G8_formal_release_scorecard_freeze"]["note"])
        self.assertTrue(gates["G9_serious_release_scorecard_pod_gate"]["passed_for_release"])
        self.assertTrue(gates["G10_clean_tree_reproducibility"]["passed_for_release"])
        self.assertTrue(gates["G11_final_release_authorization"]["passed_for_release"])
        self.assertIn("Goal4756", gates["G11_final_release_authorization"]["note"])
        self.assertTrue(gates["G12_custom_predicate_early_exit_workflow"]["passed_for_release"])
        self.assertIn("4.633x", gates["G12_custom_predicate_early_exit_workflow"]["note"])
        self.assertTrue(gates["G13_public_docs_current_frontdoor_cleanup"]["passed_for_release"])
        self.assertTrue(gates["G14_full_v4_local_gate_after_current_frontdoor_cleanup"]["passed_for_release"])

    def test_external_review_blocker_and_scope_limitations_are_preserved(self) -> None:
        decision = v4_goal4632_release_decision()

        self.assertIn(
            "external_3ai_review_debt_open_for_goal4743_goal4744_current_release_candidate",
            decision["release_blockers"],
        )
        self.assertIn("legacy_all_app_speedup_wording_not_authorized", decision["scope_limitations"])
        self.assertIn("arbitrary_python_callback_not_supported", decision["scope_limitations"])
        self.assertIn("raw_optix_callback_not_supported", decision["scope_limitations"])
        self.assertIn("public_tier3_deferred_not_supported", decision["scope_limitations"])
        self.assertIn("no_true_zero_copy_public_claim_authorized", decision["scope_limitations"])
        self.assertIn("no_c_abi_embedding_or_non_python_host_scope", decision["scope_limitations"])

    def test_surface_counts_and_coverage_summary_are_explicit(self) -> None:
        decision = v4_goal4632_release_decision()
        coverage = decision["coverage_summary"]

        self.assertEqual(10, decision["measured_surfaces_count"])
        self.assertEqual(0, decision["candidate_surfaces_count"])
        self.assertEqual(
            "promote_component_union_to_measured_tier2_operator_coverage_not_release",
            decision["component_union_promotion"]["decision"],
        )
        self.assertEqual(
            "reject_threshold_summary_promotion_keep_hausdorff_partial",
            decision["threshold_summary_decision"]["decision"],
        )
        self.assertEqual(
            "reject_grouped_any_hit_promotion_keep_robot_collision_partial",
            decision["grouped_any_hit_decision"]["decision"],
        )
        self.assertEqual(
            "accept_aabb_index_pod_gate_require_frontdoor_catalog_goal",
            decision["aabb_index_decision"]["decision"],
        )
        self.assertTrue(decision["aabb_index_decision"]["frontdoor_catalog_goal_required"])
        self.assertEqual(
            "promote_aabb_index_to_measured_v4_frontdoor_catalog_not_release",
            decision["aabb_frontdoor_decision"]["decision"],
        )
        self.assertTrue(decision["aabb_frontdoor_decision"]["frontdoor_catalog_surface_added"])
        self.assertEqual(
            "accept_catalog_regression_gpu_gate_after_aabb_not_release",
            decision["catalog_regression_supporting_evidence"]["decision"],
        )
        self.assertEqual(11, decision["catalog_regression_supporting_evidence"]["example_count"])
        self.assertEqual((), decision["catalog_regression_supporting_evidence"]["failed_examples"])
        self.assertEqual(
            "freeze_v4_release_scorecard_before_goal4639_pod_run",
            decision["formal_scorecard_freeze"]["decision"],
        )
        self.assertTrue(decision["formal_scorecard_freeze"]["requires_external_review_before_goal4639"])
        self.assertEqual(
            "accept_release_scorecard_continue_to_docs_clean_tree_and_3ai",
            decision["release_scorecard_decision"]["decision"],
        )
        self.assertEqual(8, decision["release_scorecard_decision"]["measured_surfaces_passed"])
        self.assertEqual(4, decision["release_scorecard_decision"]["strong_families_passed"])
        self.assertEqual(
            "complete_public_v4_docs_cleanup_pending_external_review",
            decision["public_docs_cleanup_decision"]["decision"],
        )
        self.assertTrue(decision["public_docs_cleanup_decision"]["public_docs_current"])
        self.assertTrue(decision["public_docs_cleanup_decision"]["v3_current_doc_archived"])
        self.assertEqual(
            "complete_clean_tree_reproducibility_gate_pending_external_review",
            decision["clean_tree_reproducibility_decision"]["decision"],
        )
        self.assertTrue(decision["clean_tree_reproducibility_decision"]["full_v4_tests_passed"])
        self.assertTrue(decision["clean_tree_reproducibility_decision"]["catalog_dry_run_passed"])
        self.assertTrue(decision["clean_tree_reproducibility_decision"]["quickstart_passed"])
        self.assertEqual("partial_measured_operator_coverage", decision["grouped_any_hit_decision"]["coverage_effect"]["to"])
        self.assertEqual(10, coverage["row_count"])
        self.assertEqual(4, coverage["by_status"]["strong_measured_operator_coverage"])
        self.assertEqual(4, coverage["by_status"]["partial_measured_operator_coverage"])
        self.assertEqual(0, coverage["by_status"]["candidate_not_measured_release_coverage"])
        self.assertEqual(2, coverage["by_status"]["deferred_or_uncovered_v4_0"])

    def test_forbidden_claims_and_flags_stay_false(self) -> None:
        decision = v4_goal4632_release_decision()

        for claim in (
            "broad V4 speedup",
            "whole-application speedup",
            "Tier-3 callback support",
            "CuPy performance",
            "C ABI / embedding / non-Python host",
            "Barnes-Hut new V4-over-V3 speedup",
            "Spatial RayJoin speedup",
            "LibRTS paper reproduction",
            "raw OptiX callback support",
        ):
            self.assertIn(claim, decision["forbidden_claims"])

        self.assertNotIn("V4 release", decision["forbidden_claims"])

        for flag in (
            "release_claim_authorized",
            "broad_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "all_benchmark_speedup_claim_authorized",
            "measured_catalog_promotion_authorized",
            "true_zero_copy_claim_authorized",
            "tier3_callback_claim_authorized",
            "raw_optix_callback_claim_authorized",
            "cupy_performance_claim_authorized",
            "c_abi_or_embedding_claim_authorized",
            "non_python_host_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(decision[flag])


if __name__ == "__main__":
    unittest.main()
