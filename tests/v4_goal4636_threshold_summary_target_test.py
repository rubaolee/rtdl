from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_coverage_audit import V4_COVERAGE_PARTIAL_MEASURED
from rtdsl.v4_coverage_audit import v4_goal4627_coverage_rows
from rtdsl.v4_goal4636_threshold_summary_target import V4_GOAL4636_API_SURFACE
from rtdsl.v4_goal4636_threshold_summary_target import V4_GOAL4636_OPERATOR
from rtdsl.v4_goal4636_threshold_summary_target import validate_v4_goal4636_threshold_summary_target
from rtdsl.v4_goal4636_threshold_summary_decision import (
    validate_v4_goal4636_threshold_summary_decision,
)
from rtdsl.v4_operator_catalog import V4_TIER2_OPERATOR_SURFACES


class V4Goal4636ThresholdSummaryTargetTest(unittest.TestCase):
    def test_target_selects_threshold_summary_for_hausdorff(self) -> None:
        target = validate_v4_goal4636_threshold_summary_target()

        self.assertEqual(V4_GOAL4636_OPERATOR, target["operator"])
        self.assertEqual(V4_GOAL4636_API_SURFACE, target["api_surface"])
        self.assertEqual("FIXED_RADIUS_THRESHOLD_REACHED_COUNT_2D", target["generic_primitive"])
        self.assertEqual("hausdorff_xhd", target["target_coverage_row"])
        self.assertEqual("threshold_summary", target["continuation_class"])
        self.assertEqual(("rtdl_native_prepared_runner",), target["partner_scope"])
        self.assertIn("generic_prepared_optix", target["output_contract"])

    def test_target_is_not_catalog_promotion_before_pod_gate(self) -> None:
        target = validate_v4_goal4636_threshold_summary_target()

        self.assertTrue(target["pod_gate_required"])
        self.assertFalse(target["measured_catalog_promotion_authorized"])
        self.assertNotIn("fixed_radius_threshold_summary_2d", V4_TIER2_OPERATOR_SURFACES)

    def test_target_moves_existing_partial_row_only_if_gate_passes(self) -> None:
        rows_by_app = {row.app: row for row in v4_goal4627_coverage_rows()}
        target = validate_v4_goal4636_threshold_summary_target()

        self.assertEqual(V4_COVERAGE_PARTIAL_MEASURED, rows_by_app["hausdorff_xhd"].coverage_status)
        self.assertEqual("partial_measured_operator_coverage", target["coverage_effect_if_gate_passes"]["from"])
        self.assertEqual("strong_measured_operator_coverage", target["coverage_effect_if_gate_passes"]["to"])
        self.assertIn("without adding a Hausdorff-native kernel", target["coverage_effect_if_gate_passes"]["reason"])

    def test_promotion_gate_is_material_and_residency_checked(self) -> None:
        gate = validate_v4_goal4636_threshold_summary_target()["promotion_gate"]

        self.assertEqual(262_144, gate["copies"])
        self.assertEqual(1_048_576, gate["points_per_side_floor"])
        self.assertEqual(0.4, gate["threshold"])
        self.assertEqual(5, gate["repeat"])
        self.assertTrue(gate["requires_rt_hardware"])
        self.assertGreaterEqual(gate["runner_vs_embree_phase_total_floor"], 1.20)
        self.assertGreaterEqual(gate["runner_vs_embree_wrapper_wall_floor"], 1.20)
        self.assertGreaterEqual(gate["runner_vs_legacy_phase_total_floor"], 0.98)
        self.assertGreaterEqual(gate["runner_vs_legacy_wrapper_wall_floor"], 0.98)
        self.assertTrue(gate["requires_all_variants_ok"])
        self.assertTrue(gate["requires_oracle_match_all_variants"])
        self.assertTrue(gate["requires_runtime_trunk_end_to_end"])
        self.assertTrue(gate["requires_both_directed_legs_runtime_executed"])
        self.assertTrue(gate["forbids_threshold_rows_materialized_on_host"])
        self.assertTrue(gate["requires_internal_device_residency_between_rtdl_phases"])
        self.assertTrue(gate["requires_step3_audit_ready"])

    def test_target_preserves_non_authorization_boundaries(self) -> None:
        target = validate_v4_goal4636_threshold_summary_target()

        for flag in (
            "release_claim_authorized",
            "broad_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "app_specific_native_kernel_authorized",
            "true_zero_copy_claim_authorized",
            "cupy_performance_claim_authorized",
            "c_abi_or_embedding_claim_authorized",
        ):
            self.assertFalse(target[flag])

    def test_pod_gate_failure_rejects_promotion_despite_embree_win(self) -> None:
        decision = validate_v4_goal4636_threshold_summary_decision()
        gate = decision["same_contract_gate"]

        self.assertEqual(
            "reject_threshold_summary_promotion_keep_hausdorff_partial",
            decision["decision"],
        )
        self.assertEqual("fail", gate["status"])
        self.assertIn("runner_regressed_vs_legacy_phase_total", gate["failed_checks"])
        self.assertGreaterEqual(
            gate["runner_vs_embree_phase_total_speedup"],
            gate["runner_vs_embree_phase_total_floor"],
        )
        self.assertGreaterEqual(
            gate["runner_vs_embree_wrapper_wall_speedup"],
            gate["runner_vs_embree_wrapper_wall_floor"],
        )
        self.assertLess(
            gate["runner_vs_legacy_phase_total_speedup"],
            gate["runner_vs_legacy_phase_total_floor"],
        )
        self.assertEqual("partial_measured_operator_coverage", decision["coverage_effect"]["to"])
        self.assertFalse(decision["measured_catalog_promotion_authorized"])
        self.assertFalse(decision["release_authorized"])


if __name__ == "__main__":
    unittest.main()
