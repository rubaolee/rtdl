from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4
import rtdsl.v4_operator_catalog as catalog


class V4Goal4677AggregateFrontierPromotionTest(unittest.TestCase):
    def test_goal4677_decision_promotes_only_bounded_measured_route(self) -> None:
        decision = v4.v4_goal4677_aggregate_frontier_promotion_decision().as_dict()

        self.assertEqual(
            "goal4677_promote_aggregate_frontier_device_columns_measured_route_no_release",
            decision["status"],
        )
        self.assertTrue(decision["promoted"])
        self.assertEqual(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            decision["promoted_surface"],
        )
        self.assertEqual(("rtdl_native", "cupy"), decision["measured_partners"])
        self.assertGreaterEqual(decision["ratios"]["v4_frontier_only_hot_over_v2_14"], 1.20)
        self.assertGreaterEqual(decision["ratios"]["v4_full_hot_over_v2_14"], 1.20)
        self.assertGreaterEqual(decision["ratios"]["v4_full_wall_over_v2_14"], 1.10)
        self.assertGreaterEqual(decision["ratios"]["v4_full_hot_over_v3_0_2_control"], 0.98)
        self.assertIn("does not prove a V4-over-V3 speedup", decision["v3_0_2_caveat"])
        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["whole_app_speedup_claim_authorized"])
        self.assertFalse(decision["cupy_performance_claim_authorized"])

    def test_goal4677_validation_passes(self) -> None:
        validation = v4.validate_v4_goal4677_aggregate_frontier_promotion()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(validation["release_authorized"])

    def test_catalog_promotes_aggregate_frontier_out_of_candidate_list(self) -> None:
        rows = catalog.measured_v4_tier2_operator_catalog()
        row_by_operator = {row["operator"]: row for row in rows}

        self.assertIn("aggregate_frontier_device_columns_2d", row_by_operator)
        promoted = row_by_operator["aggregate_frontier_device_columns_2d"]
        self.assertEqual(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            promoted["api_surface"],
        )
        self.assertEqual(("rtdl_native", "cupy"), promoted["measured_partners"])
        self.assertEqual(("torch", "numba"), promoted["declared_unmeasured_partners"])
        self.assertGreaterEqual(promoted["runner_vs_v2_14_full_hot_speedup"], 1.20)
        self.assertGreaterEqual(promoted["runner_vs_v2_14_full_wall_speedup"], 1.10)
        self.assertGreaterEqual(promoted["runner_vs_v3_0_2_full_hot_ratio"], 0.98)
        self.assertIn("V3.0.2", promoted["performance_caveat"])
        self.assertFalse(promoted["release_claim_authorized"])
        self.assertFalse(promoted["whole_app_speedup_claim_authorized"])

        candidate_names = {row["operator"] for row in catalog.candidate_v4_tier2_operator_catalog()}
        self.assertNotIn("aggregate_frontier_device_columns_2d", candidate_names)

    def test_planner_recognizes_measured_cupy_and_native_routes_but_not_torch_or_numba(self) -> None:
        cupy_plan = catalog.plan_v4_operator_request("aggregate_frontier_device_columns", partner="cupy")
        self.assertEqual("tier2_measured_ready", cupy_plan.status)
        self.assertEqual("tier2_fused_operator", cupy_plan.tier)
        self.assertTrue(cupy_plan.measured_partner)
        self.assertFalse(cupy_plan.release_claim_authorized)

        native_plan = catalog.plan_v4_operator_request("aggregate_frontier", partner="rtdl_native")
        self.assertEqual("tier2_measured_ready", native_plan.status)
        self.assertTrue(native_plan.measured_partner)

        torch_plan = catalog.plan_v4_operator_request("aggregate_frontier", partner="torch")
        self.assertEqual("tier2_declared_unmeasured_partner", torch_plan.status)
        self.assertIsNone(torch_plan.api_surface)

        numba_plan = catalog.plan_v4_operator_request("aggregate_frontier", partner="numba")
        self.assertEqual("tier2_declared_unmeasured_partner", numba_plan.status)
        self.assertIsNone(numba_plan.api_surface)

    def test_scope_gate_counts_promoted_surface_as_measured_not_candidate(self) -> None:
        gate = v4.v4_0_scope_gate().as_dict()

        self.assertEqual(10, len(gate["included_surfaces"]))
        self.assertEqual(0, len(gate["candidate_surfaces"]))
        self.assertIn(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            gate["included_surfaces"],
        )
        self.assertNotIn(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            gate["candidate_surfaces"],
        )
        self.assertFalse(gate["release_authorized"])


if __name__ == "__main__":
    unittest.main()
