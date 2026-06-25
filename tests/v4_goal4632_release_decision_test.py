from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_release_decision import V4_GOAL4632_DECISION
from rtdsl.v4_release_decision import validate_v4_goal4632_release_decision
from rtdsl.v4_release_decision import v4_goal4632_release_decision


class V4Goal4632ReleaseDecisionTest(unittest.TestCase):
    def test_final_decision_is_development_state_not_release(self) -> None:
        decision = validate_v4_goal4632_release_decision()

        self.assertEqual(V4_GOAL4632_DECISION, decision["decision"])
        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["release_candidate_authorized"])
        self.assertTrue(decision["performance_preview_authorized"])
        self.assertTrue(decision["development_state_authorized"])
        self.assertIn("scorecard passed", decision["public_wording"])

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
                "G10_final_release_authorization",
            },
        )
        self.assertTrue(gates["G1_fixed_radius_anchor"]["passed_for_release"])
        self.assertFalse(gates["G2_operator_coverage_audit"]["passed_for_release"])
        self.assertTrue(gates["G3_second_tier2_same_contract_gate"]["passed_for_release"])
        self.assertTrue(gates["G4_weighted_sum_candidate"]["passed_for_release"])
        self.assertTrue(gates["G5_pushdown_recognizer"]["passed_for_release"])
        self.assertTrue(gates["G6_tier3_boundary"]["passed_for_release"])
        self.assertTrue(gates["G7_aabb_index_frontdoor_catalog"]["passed_for_release"])
        self.assertTrue(gates["G8_formal_release_scorecard_freeze"]["passed_for_release"])
        self.assertIn("formal release scorecard freeze", gates["G8_formal_release_scorecard_freeze"]["note"])
        self.assertTrue(gates["G9_serious_release_scorecard_pod_gate"]["passed_for_release"])
        self.assertFalse(gates["G10_final_release_authorization"]["passed_for_release"])

    def test_release_blockers_include_candidate_coverage_review_debt_and_no_all_app(self) -> None:
        decision = v4_goal4632_release_decision()

        self.assertNotIn("operator_coverage_still_incomplete_not_broad_app_coverage", decision["release_blockers"])
        self.assertNotIn("weighted_sum_remains_candidate_not_measured", decision["release_blockers"])
        self.assertIn("tier3_deferred_not_supported", decision["release_blockers"])
        self.assertIn(
            "external_review_debt_remains_for_antigravity_goal4633_backfill",
            decision["release_blockers"],
        )
        self.assertIn(
            "external_review_debt_remains_for_goal4635_component_union_completion",
            decision["release_blockers"],
        )
        self.assertNotIn(
            "goal4636_threshold_summary_gate_failed_need_next_generic_coverage_target",
            decision["release_blockers"],
        )
        self.assertNotIn(
            "goal4636b_grouped_any_hit_gate_failed_need_next_generic_coverage_target",
            decision["release_blockers"],
        )
        self.assertIn(
            "external_review_debt_remains_for_goal4637_aabb_frontdoor_catalog_completion",
            decision["release_blockers"],
        )
        self.assertIn(
            "external_review_debt_antigravity_goal4638_formal_scorecard_freeze",
            decision["release_blockers"],
        )
        self.assertIn(
            "external_review_debt_antigravity_goal4639_serious_release_scorecard",
            decision["release_blockers"],
        )
        self.assertIn(
            "goal4642_final_3ai_release_authorization_not_done",
            decision["release_blockers"],
        )
        self.assertIn("external_review_debt_goal4640_public_docs_cleanup", decision["release_blockers"])
        self.assertNotIn("goal4640_user_docs_cleanup_not_done", decision["release_blockers"])
        self.assertNotIn(
            "goal4636c_aabb_index_gate_passed_pending_frontdoor_catalog_goal",
            decision["release_blockers"],
        )
        self.assertIn("whole_app_speedup_wording_still_requires_final_3ai_authorization", decision["release_blockers"])
        self.assertIn("cupy_performance_unmeasured", decision["release_blockers"])

    def test_surface_counts_and_coverage_summary_are_explicit(self) -> None:
        decision = v4_goal4632_release_decision()
        coverage = decision["coverage_summary"]

        self.assertEqual(8, decision["measured_surfaces_count"])
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
        self.assertEqual("partial_measured_operator_coverage", decision["grouped_any_hit_decision"]["coverage_effect"]["to"])
        self.assertEqual(10, coverage["row_count"])
        self.assertEqual(4, coverage["by_status"]["strong_measured_operator_coverage"])
        self.assertEqual(4, coverage["by_status"]["partial_measured_operator_coverage"])
        self.assertEqual(0, coverage["by_status"]["candidate_not_measured_release_coverage"])
        self.assertEqual(2, coverage["by_status"]["deferred_or_uncovered_v4_0"])

    def test_forbidden_claims_and_flags_stay_false(self) -> None:
        decision = v4_goal4632_release_decision()

        for claim in (
            "V4 release",
            "broad V4 speedup",
            "whole-application speedup",
            "Tier-3 callback support",
            "CuPy performance",
            "C ABI / embedding / non-Python host",
        ):
            self.assertIn(claim, decision["forbidden_claims"])

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
