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
from rtdsl import v4_ranked_summary


class V4Goal4678RankedSummaryDispositionTest(unittest.TestCase):
    def test_decision_defers_ranked_summary_and_removes_candidate_frontdoor(self) -> None:
        decision = v4.v4_goal4678_ranked_summary_disposition().as_dict()

        self.assertEqual(
            "goal4678_defer_ranked_summary_no_open_candidate_no_release",
            decision["status"],
        )
        self.assertTrue(decision["deferred"])
        self.assertTrue(decision["removed_from_candidate_frontdoor"])
        self.assertEqual("v4_fixed_radius_ranked_summary_3d_prepared_runner", decision["surface"])
        self.assertEqual("rtnn_candidate_does_not_move_app_level_bar", decision["decision_label"])
        self.assertLess(decision["serious_scale_ratios"]["262144"]["v4_over_v2_14_hot"], 1.01)
        self.assertLess(decision["serious_scale_ratios"]["262144"]["v4_over_v3_0_2_hot"], 1.01)
        self.assertLess(decision["serious_scale_ratios"]["1048576"]["v4_over_v2_14_hot"], 1.0)
        self.assertLess(decision["serious_scale_ratios"]["1048576"]["v4_over_v3_0_2_hot"], 1.0)
        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["public_speedup_claim_authorized"])

    def test_validation_passes(self) -> None:
        validation = v4.validate_v4_goal4678_ranked_summary_disposition()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(validation["release_authorized"])

    def test_frontdoor_has_no_open_candidate_surfaces(self) -> None:
        boundary = v4.claim_boundary_v4()

        self.assertEqual((), boundary["candidate_surfaces"])
        self.assertEqual([], v4.candidate_operator_catalog_v4())
        gate = v4.v4_0_scope_gate().as_dict()
        self.assertEqual((), gate["candidate_surfaces"])
        self.assertEqual("v4_python_edsl_operator_pushdown_scope_goal4756_complete_rt_core_matrix", gate["status"])
        self.assertEqual(
            "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim",
            boundary["current_app_level_decision_label"],
        )

    def test_planner_returns_deferred_for_ranked_summary(self) -> None:
        plan = catalog.plan_v4_operator_request("ranked_summary", partner="rtdl_native")

        self.assertEqual("deferred_serious_scale_not_v4_0_release_surface", plan.status)
        self.assertEqual("deferred_v4_x_or_research", plan.tier)
        self.assertIsNone(plan.api_surface)
        self.assertFalse(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertIn("serious-scale rows did not meet the V4.0 surface bar", plan.guidance)

    def test_ranked_summary_claim_boundary_is_deferred_not_candidate(self) -> None:
        boundary = v4_ranked_summary.fixed_radius_ranked_summary_3d_prepared_runner_claim_boundary_v4()

        self.assertEqual("deferred_serious_scale_not_v4_0_release_surface", boundary["status"])
        self.assertFalse(boundary["candidate_surface"])
        self.assertTrue(boundary["deferred_surface"])
        self.assertFalse(boundary["measured_v4_release_surface"])
        self.assertIn("does not move the RTNN app-level bar", boundary["goal4678_no_go_reason"])
        self.assertFalse(boundary["release_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
