from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_coverage_audit import V4_COVERAGE_PARTIAL_MEASURED
from rtdsl.v4_coverage_audit import v4_goal4627_coverage_rows
from rtdsl.v4_goal4636_grouped_any_hit_decision import (
    validate_v4_goal4636_grouped_any_hit_decision,
)
from rtdsl.v4_goal4636_grouped_any_hit_target import V4_GOAL4636B_API_SURFACE
from rtdsl.v4_goal4636_grouped_any_hit_target import V4_GOAL4636B_OPERATOR
from rtdsl.v4_goal4636_grouped_any_hit_target import validate_v4_goal4636_grouped_any_hit_target
from rtdsl.v4_operator_catalog import V4_TIER2_OPERATOR_SURFACES


class V4Goal4636GroupedAnyHitTargetTest(unittest.TestCase):
    def test_target_selects_grouped_any_hit_for_robot_collision(self) -> None:
        target = validate_v4_goal4636_grouped_any_hit_target()

        self.assertEqual(V4_GOAL4636B_OPERATOR, target["operator"])
        self.assertEqual(V4_GOAL4636B_API_SURFACE, target["api_surface"])
        self.assertEqual("RAY_TRIANGLE_GROUPED_ANY_HIT_FLAGS_3D", target["generic_primitive"])
        self.assertEqual("robot_collision", target["target_coverage_row"])
        self.assertEqual("grouped_any_hit_flag_stream", target["continuation_class"])
        self.assertEqual(("rtdl_native_prepared_runner",), target["scope"])
        self.assertIn("grouped_segment_any_hit_flags", target["output_contract"])

    def test_target_is_not_catalog_promotion_before_pod_gate(self) -> None:
        target = validate_v4_goal4636_grouped_any_hit_target()

        self.assertTrue(target["pod_gate_required"])
        self.assertFalse(target["measured_catalog_promotion_authorized"])
        self.assertNotIn("ray_triangle_grouped_any_hit_flags_3d", V4_TIER2_OPERATOR_SURFACES)

    def test_target_moves_existing_partial_row_only_if_gate_passes(self) -> None:
        rows_by_app = {row.app: row for row in v4_goal4627_coverage_rows()}
        target = validate_v4_goal4636_grouped_any_hit_target()

        self.assertEqual(V4_COVERAGE_PARTIAL_MEASURED, rows_by_app["robot_collision"].coverage_status)
        self.assertEqual("partial_measured_operator_coverage", target["coverage_effect_if_gate_passes"]["from"])
        self.assertEqual("strong_measured_operator_coverage", target["coverage_effect_if_gate_passes"]["to"])
        self.assertIn("without adding a robot collision native kernel", target["coverage_effect_if_gate_passes"]["reason"])

    def test_promotion_gate_is_material_not_trivial_parity(self) -> None:
        gate = validate_v4_goal4636_grouped_any_hit_target()["promotion_gate"]

        self.assertEqual(8_192, gate["pose_count"])
        self.assertEqual(2_048, gate["obstacle_count"])
        self.assertEqual(5, gate["sample_count"])
        self.assertEqual(101, gate["timed_repeats"])
        self.assertTrue(gate["requires_rt_hardware"])
        self.assertGreaterEqual(gate["tail_total_mean_embree_over_optix_floor"], 3.0)
        self.assertGreaterEqual(gate["traversal_mean_embree_over_optix_floor"], 3.0)
        self.assertGreaterEqual(gate["wrapper_mean_embree_over_optix_floor"], 1.10)
        self.assertGreaterEqual(gate["wrapper_min_embree_over_optix_floor"], 1.00)
        self.assertTrue(gate["requires_probe_reference_disabled_for_timed_rows"])
        self.assertTrue(gate["requires_validation_and_timed_signature_overlap"])
        self.assertTrue(gate["requires_same_contract_shape_signature_counts"])
        self.assertTrue(gate["timed_status_is_correctness_gate_only"])
        self.assertTrue(gate["requires_post_pod_performance_floor_review"])
        self.assertTrue(gate["requires_traversal_ratio_evaluable"])
        self.assertEqual("operator_coverage_only_not_robot_app_wall_time", gate["promotion_scope"])
        self.assertTrue(gate["catalog_surface_addition_requires_separate_frontdoor_goal"])

    def test_target_preserves_non_authorization_boundaries(self) -> None:
        target = validate_v4_goal4636_grouped_any_hit_target()

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

    def test_pod_gate_decision_rejects_promotion_on_wrapper_floor_failure(self) -> None:
        decision = validate_v4_goal4636_grouped_any_hit_decision()
        gate = decision["same_contract_gate"]

        self.assertEqual(
            "reject_grouped_any_hit_promotion_keep_robot_collision_partial",
            decision["decision"],
        )
        self.assertEqual("pass", gate["validation_status"])
        self.assertEqual("pass", gate["timed_status"])
        self.assertEqual("fail", gate["performance_floor_status"])
        self.assertGreaterEqual(
            gate["tail_total_mean_embree_over_optix"],
            gate["tail_total_mean_embree_over_optix_floor"],
        )
        self.assertGreaterEqual(
            gate["traversal_mean_embree_over_optix"],
            gate["traversal_mean_embree_over_optix_floor"],
        )
        self.assertLess(
            gate["wrapper_mean_embree_over_optix"],
            gate["wrapper_mean_embree_over_optix_floor"],
        )
        self.assertLess(
            gate["wrapper_min_embree_over_optix"],
            gate["wrapper_min_embree_over_optix_floor"],
        )
        self.assertEqual("partial_measured_operator_coverage", decision["coverage_effect"]["to"])
        self.assertFalse(decision["measured_catalog_promotion_authorized"])
        self.assertFalse(decision["release_authorized"])


if __name__ == "__main__":
    unittest.main()
