from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4
import rtdsl.v4_operator_catalog as catalog
from rtdsl import v4_partner_promotion_contract as contracts


class V4Goal4648PartnerPromotionContractTest(unittest.TestCase):
    def test_cupy_contract_freezes_numeric_bars_and_claim_boundaries(self) -> None:
        contract = contracts.v4_partner_promotion_contract("cupy")

        self.assertEqual("cupy", contract["partner"])
        self.assertEqual("device_array_frontdoor_certification", contract["contract_class"])
        self.assertEqual(1.0, contract["correctness_parity_required"])
        self.assertEqual(1.20, contract["representative_speedup_floor"])
        self.assertEqual(0.98, contract["partner_parity_floor"])
        self.assertIn("host_materialization_in_hot_path", contract["telemetry_required"])
        self.assertIn("stream_mode", contract["telemetry_required"])
        self.assertIn("output_ownership", contract["telemetry_required"])
        self.assertIn("cupy_grouped_reduction_device_columns_262144", contract["candidate_ids"])
        self.assertIn("cupy_grouped_reduction_device_columns_524288", contract["candidate_ids"])
        self.assertFalse(contract["partner_migration_counts_as_v4_speed_win"])
        self.assertFalse(contract["partner_parity_counts_as_v4_speed_win"])
        self.assertFalse(contract["cupy_performance_claim_authorized"])
        self.assertFalse(contract["broad_v4_speedup_claim_authorized"])
        self.assertFalse(contract["whole_app_speedup_claim_authorized"])
        self.assertFalse(contract["release_claim_authorized"])

    def test_fixed_numba_contract_blocks_arbitrary_callback_claims(self) -> None:
        contract = contracts.v4_partner_promotion_contract("numba", fixed=True)

        self.assertEqual("numba", contract["partner"])
        self.assertEqual("fixed_continuation_certification", contract["contract_class"])
        self.assertTrue(contract["fixed_operator_only"])
        self.assertFalse(contract["arbitrary_callback_supported"])
        self.assertFalse(contract["arbitrary_numba_callback_claim_authorized"])
        self.assertFalse(contract["partner_parity_counts_as_v4_speed_win"])
        self.assertIn("compile_time_seconds", contract["telemetry_required"])
        self.assertIn("cache_hit", contract["telemetry_required"])
        self.assertIn(
            "fixed_radius_graph_component_union_3d(device columns) -> component labels",
            contract["accepted_signatures"],
        )
        self.assertEqual("compile_time_excluded_from_hot_path_but_reported_as_phase_telemetry", contract["compile_cache_timing_boundary"])

    def test_unsupported_contract_requests_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "partner promotion contract must be one of"):
            contracts.v4_partner_promotion_contract("torch")

        with self.assertRaisesRegex(ValueError, "partner promotion contract must be one of"):
            contracts.v4_partner_promotion_contract("numba")

        self.assertFalse(
            contracts.v4_partner_promotion_candidate_allowed(
                "barnes_hut_aggregate_tree_numba_cuda_fused",
                partner="numba",
            )
        )
        self.assertFalse(
            contracts.v4_partner_promotion_candidate_allowed(
                "cupy_grouped_reduction_device_columns_262144",
                partner="torch",
            )
        )
        self.assertFalse(
            contracts.v4_partner_promotion_candidate_allowed(
                "numba_component_union_current_v4_surface",
                partner="torch",
            )
        )
        self.assertFalse(
            contracts.v4_partner_promotion_candidate_allowed(
                "cupy_grouped_reduction_device_columns_262144",
                partner="unknown",
            )
        )

    def test_candidate_allowlist_matches_goal4647_outputs(self) -> None:
        self.assertTrue(
            contracts.v4_partner_promotion_candidate_allowed(
                "cupy_grouped_reduction_device_columns_262144",
                partner="cupy",
            )
        )
        self.assertTrue(
            contracts.v4_partner_promotion_candidate_allowed(
                "cupy_segment_polygon_hitcount_prepared_scaling",
                partner="cupy",
            )
        )
        self.assertTrue(
            contracts.v4_partner_promotion_candidate_allowed(
                "numba_component_union_current_v4_surface",
                partner="numba",
            )
        )
        self.assertFalse(
            contracts.v4_partner_promotion_candidate_allowed(
                "tier3_numba_ptx_spike",
                partner="numba",
            )
        )

    def test_current_planner_still_fails_closed_for_unmeasured_cupy_until_goal4649(self) -> None:
        plan = catalog.plan_v4_operator_request("grouped_i64", partner="cupy")

        self.assertEqual("tier2_declared_unmeasured_partner", plan.status)
        self.assertIsNone(plan.api_surface)
        self.assertFalse(plan.measured_partner)
        self.assertFalse(plan.cupy_performance_claim_authorized)
        self.assertFalse(plan.broad_v4_speedup_claim_authorized)

    def test_v4_frontdoor_exports_contracts_without_authorizing_release_claims(self) -> None:
        rows = v4.v4_partner_promotion_contracts()
        by_partner = {row["partner"]: row for row in rows}

        self.assertEqual({"cupy", "numba"}, set(by_partner))
        self.assertEqual(
            v4.V4_GOAL4648_PARTNER_PROMOTION_CONTRACT_STATUS,
            by_partner["cupy"]["status"],
        )
        self.assertTrue(
            v4.v4_partner_promotion_candidate_allowed(
                "cupy_hausdorff_witness_continuation",
                partner="cupy",
            )
        )
        for row in rows:
            self.assertFalse(row["release_claim_authorized"])
            self.assertFalse(row["partner_migration_counts_as_v4_speed_win"])
            self.assertFalse(row["partner_parity_counts_as_v4_speed_win"])


if __name__ == "__main__":
    unittest.main()
