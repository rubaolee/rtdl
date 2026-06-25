from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts import v3_0_m30_librts_prepared_all_ops_refresh as aabb_runner
from rtdsl.v4_coverage_audit import V4_COVERAGE_STRONG_MEASURED
from rtdsl.v4_coverage_audit import v4_goal4627_coverage_rows
from rtdsl.v4_goal4636_aabb_index_decision import V4_GOAL4636C_DECISION
from rtdsl.v4_goal4636_aabb_index_decision import validate_v4_goal4636_aabb_index_decision
from rtdsl.v4_goal4636_aabb_index_target import V4_GOAL4636C_API_SURFACE
from rtdsl.v4_goal4636_aabb_index_target import V4_GOAL4636C_OPERATOR
from rtdsl.v4_goal4636_aabb_index_target import validate_v4_goal4636_aabb_index_target
from rtdsl.v4_operator_catalog import V4_TIER2_OPERATOR_SURFACES


class V4Goal4636AabbIndexTargetTest(unittest.TestCase):
    def test_target_selects_aabb_index_for_librts_row(self) -> None:
        target = validate_v4_goal4636_aabb_index_target()

        self.assertEqual(V4_GOAL4636C_OPERATOR, target["operator"])
        self.assertEqual(V4_GOAL4636C_API_SURFACE, target["api_surface"])
        self.assertEqual("AABB_INDEX_QUERY_2D", target["generic_primitive"])
        self.assertEqual("librts_spatial_index", target["target_coverage_row"])
        self.assertEqual("aabb_index_all_ops_count", target["continuation_class"])
        self.assertEqual(("rtdl_native_prepared_runner",), target["scope"])
        self.assertEqual("generic_prepared_aabb_index_query_2d_family", target["output_contract"])
        self.assertEqual("generic_prepared_aabb_index_query_2d", target["accepted_contract_family"])
        self.assertIn("generic_prepared_aabb_index_query_2d_count", target["accepted_contracts"])
        self.assertIn(
            "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
            target["accepted_contracts"],
        )

    def test_target_is_not_catalog_promotion_before_pod_gate(self) -> None:
        target = validate_v4_goal4636_aabb_index_target()

        self.assertTrue(target["pod_gate_required"])
        self.assertFalse(target["measured_catalog_promotion_authorized"])
        self.assertIn("aabb_index_query_2d_all_ops_count", V4_TIER2_OPERATOR_SURFACES)

    def test_target_moves_deferred_row_only_if_gate_passes(self) -> None:
        rows_by_app = {row.app: row for row in v4_goal4627_coverage_rows()}
        target = validate_v4_goal4636_aabb_index_target()

        self.assertEqual(V4_COVERAGE_STRONG_MEASURED, rows_by_app["librts_spatial_index"].coverage_status)
        self.assertEqual("deferred_or_uncovered_v4_0", target["coverage_effect_if_gate_passes"]["from"])
        self.assertEqual("strong_measured_operator_coverage", target["coverage_effect_if_gate_passes"]["to"])
        self.assertIn("without adding a LibRTS-native kernel", target["coverage_effect_if_gate_passes"]["reason"])

    def test_promotion_gate_is_large_all_ops_and_material(self) -> None:
        gate = validate_v4_goal4636_aabb_index_target()["promotion_gate"]

        self.assertEqual(1_000_000, gate["box_count"])
        self.assertEqual(1_000, gate["query_count"])
        self.assertEqual("all", gate["operation"])
        self.assertEqual({"embree": 240, "optix": 240}, gate["repeat_overrides"])
        self.assertTrue(gate["requires_rt_hardware"])
        self.assertTrue(gate["requires_cross_backend_count_match"])
        self.assertTrue(gate["requires_same_contract"])
        self.assertTrue(gate["requires_same_contract_family"])
        self.assertTrue(gate["requires_primitive_first_no_partner"])
        self.assertTrue(gate["cpu_reference_skipped_acknowledged"])
        self.assertEqual("cross_backend_count_match_same_fixture", gate["correctness_oracle"])
        self.assertGreaterEqual(gate["embree_over_optix_query_median_floor"], 10.0)
        self.assertGreaterEqual(gate["embree_over_optix_query_total_floor"], 10.0)
        self.assertEqual("operator_coverage_only_not_librts_paper_or_authors_code", gate["promotion_scope"])
        self.assertTrue(gate["catalog_surface_addition_requires_frontdoor_goal"])

    def test_target_preserves_non_authorization_boundaries(self) -> None:
        target = validate_v4_goal4636_aabb_index_target()

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

    def test_runner_accepts_base_and_optix_qualified_contract_family(self) -> None:
        fixture = {
            "box_count": 1_000_000,
            "point_query_count": 1_000,
            "box_query_count": 1_000,
        }
        rows = [
            {
                "backend": "embree",
                "generic_primitive": "AABB_INDEX_QUERY_2D",
                "primitive_contract": "generic_prepared_aabb_index_query_2d_count",
                "counts_signature": "{\"point_contains\": 1}",
                "fixture": fixture,
                "query_median_sec": 10.0,
                "query_total_sec": 240.0,
                "query_repeat": 240,
                "partner_continuation_required": False,
                "public_speedup_claim_authorized": False,
            },
            {
                "backend": "optix",
                "generic_primitive": "AABB_INDEX_QUERY_2D",
                "primitive_contract": "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
                "counts_signature": "{\"point_contains\": 1}",
                "fixture": fixture,
                "query_median_sec": 1.0,
                "query_total_sec": 24.0,
                "query_repeat": 240,
                "partner_continuation_required": False,
                "public_speedup_claim_authorized": False,
            },
        ]

        comparison = aabb_runner._compare_rows(rows)
        pair = comparison["same_contract_backend_pair"]

        self.assertTrue(comparison["all_same_contract"])
        self.assertTrue(comparison["all_same_contract_family"])
        self.assertEqual("generic_prepared_aabb_index_query_2d", comparison["accepted_contract_family"])
        self.assertTrue(pair["same_contract"])
        self.assertTrue(pair["same_contract_family"])
        self.assertEqual(10.0, pair["embree_over_optix_query_median"])

    def test_pod_gate_decision_accepts_gate_but_requires_frontdoor_goal(self) -> None:
        decision = validate_v4_goal4636_aabb_index_decision()
        gate = decision["same_contract_gate"]

        self.assertEqual(V4_GOAL4636C_DECISION, decision["decision"])
        self.assertEqual("pass", gate["status"])
        self.assertTrue(gate["all_counts_match_cross_backend"])
        self.assertTrue(gate["all_same_contract_family"])
        self.assertEqual(gate["embree_repeat"], gate["optix_repeat"])
        self.assertGreaterEqual(
            gate["embree_over_optix_query_median"],
            gate["embree_over_optix_query_median_floor"],
        )
        self.assertGreaterEqual(
            gate["embree_over_optix_query_total"],
            gate["embree_over_optix_query_total_floor"],
        )
        self.assertFalse(decision["measured_catalog_promotion_authorized"])
        self.assertTrue(decision["frontdoor_catalog_goal_required"])
        self.assertFalse(decision["release_authorized"])


if __name__ == "__main__":
    unittest.main()
