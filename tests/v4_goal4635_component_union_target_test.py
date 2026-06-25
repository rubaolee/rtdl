from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_coverage_audit import V4_COVERAGE_STRONG_MEASURED
from rtdsl.v4_coverage_audit import v4_goal4627_coverage_rows
from rtdsl.v4_goal4635_component_union_promotion_decision import (
    validate_v4_goal4635_component_union_promotion_decision,
)
from rtdsl.v4_goal4635_component_union_target import V4_GOAL4635_API_SURFACE
from rtdsl.v4_goal4635_component_union_target import V4_GOAL4635_OPERATOR
from rtdsl.v4_goal4635_component_union_target import validate_v4_goal4635_component_union_target
from rtdsl.v4_operator_catalog import V4_TIER2_OPERATOR_SURFACES


class V4Goal4635ComponentUnionTargetTest(unittest.TestCase):
    def test_target_selects_generic_component_union_for_rtdbscan(self) -> None:
        target = validate_v4_goal4635_component_union_target()

        self.assertEqual(V4_GOAL4635_OPERATOR, target["operator"])
        self.assertEqual(V4_GOAL4635_API_SURFACE, target["api_surface"])
        self.assertEqual("FIXED_RADIUS_GRAPH_COMPONENT_UNION_3D", target["generic_primitive"])
        self.assertEqual("rt_dbscan", target["target_coverage_row"])
        self.assertEqual("component_union", target["continuation_class"])
        self.assertEqual(("numba",), target["partner_scope"])
        self.assertIn("generic_prepared_optix_numba", target["output_contract"])

    def test_target_predeclared_gate_is_now_backed_by_measured_catalog_row(self) -> None:
        target = validate_v4_goal4635_component_union_target()
        decision = validate_v4_goal4635_component_union_promotion_decision()

        self.assertTrue(target["pod_gate_required"])
        self.assertFalse(target["measured_catalog_promotion_authorized"])
        self.assertIn("fixed_radius_graph_component_union_3d", V4_TIER2_OPERATOR_SURFACES)
        self.assertEqual(
            "promote_component_union_to_measured_tier2_operator_coverage_not_release",
            decision["decision"],
        )
        self.assertEqual(("numba",), decision["measured_partners"])

    def test_target_moves_existing_partial_row_only_if_gate_passes(self) -> None:
        rows_by_app = {row.app: row for row in v4_goal4627_coverage_rows()}
        target = validate_v4_goal4635_component_union_target()

        self.assertEqual(V4_COVERAGE_STRONG_MEASURED, rows_by_app["rt_dbscan"].coverage_status)
        self.assertEqual("partial_measured_operator_coverage", target["coverage_effect_if_gate_passes"]["from"])
        self.assertEqual("strong_measured_operator_coverage", target["coverage_effect_if_gate_passes"]["to"])
        self.assertIn("without adding a DBSCAN-native kernel", target["coverage_effect_if_gate_passes"]["reason"])
        self.assertIn(
            "v4_fixed_radius_graph_component_union_3d_device_arrays",
            rows_by_app["rt_dbscan"].mapped_v4_operators,
        )

    def test_promotion_gate_is_material_and_forbids_signature_shortcut(self) -> None:
        gate = validate_v4_goal4635_component_union_target()["promotion_gate"]

        self.assertEqual(262_144, gate["point_count_floor"])
        self.assertEqual(5, gate["repeat"])
        self.assertTrue(gate["requires_rt_hardware"])
        self.assertGreaterEqual(gate["runner_vs_embree_hot_floor"], 1.20)
        self.assertGreaterEqual(gate["runner_vs_embree_wall_floor"], 1.20)
        self.assertGreaterEqual(gate["runner_vs_legacy_wall_floor"], 0.98)
        self.assertTrue(gate["requires_canonical_component_signature_match"])
        self.assertTrue(gate["requires_component_label_columns"])
        self.assertTrue(gate["forbids_component_signature_substitution"])
        self.assertTrue(gate["requires_runtime_trunk_end_to_end"])
        self.assertTrue(gate["forbids_hot_path_host_materialization"])

    def test_promotion_decision_records_material_gate_pass_without_release_claims(self) -> None:
        decision = validate_v4_goal4635_component_union_promotion_decision()
        gate = decision["same_contract_gate"]

        self.assertEqual("pass", gate["status"])
        self.assertEqual((), gate["failed_checks"])
        self.assertTrue(gate["all_variant_canonical_component_signatures_match"])
        self.assertGreaterEqual(gate["runner_vs_embree_hot_speedup"], gate["runner_vs_embree_hot_floor"])
        self.assertGreaterEqual(gate["runner_vs_embree_wall_speedup"], gate["runner_vs_embree_wall_floor"])
        self.assertGreaterEqual(gate["runner_vs_legacy_wall_speedup"], gate["runner_vs_legacy_wall_floor"])
        self.assertFalse(decision["whole_app_speedup_claim_authorized"])
        self.assertFalse(decision["release_authorized"])

    def test_target_preserves_non_authorization_boundaries(self) -> None:
        target = validate_v4_goal4635_component_union_target()

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


if __name__ == "__main__":
    unittest.main()
