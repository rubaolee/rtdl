from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl import v4
from rtdsl import v4_app_route_binding as route_binding


class V4Goal4652AppRouteBindingTest(unittest.TestCase):
    def test_all_benchmark_apps_are_bound_or_blocked_in_frozen_order(self) -> None:
        rows = v4.v4_goal4652_app_route_bindings()
        apps = tuple(row["app"] for row in rows)

        self.assertEqual(route_binding.V4_GOAL4652_APP_ORDER, apps)
        self.assertEqual(10, len(rows))
        self.assertEqual(len(rows), len(set(apps)))

    def test_summary_splits_full_routes_partial_routes_and_blockers(self) -> None:
        summary = v4.v4_goal4652_route_binding_summary()
        by_class = summary["by_route_class"]

        self.assertEqual(route_binding.V4_GOAL4652_APP_ROUTE_BINDING_STATUS, summary["status"])
        self.assertEqual(10, summary["app_count"])
        self.assertEqual(5, by_class[route_binding.V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE])
        self.assertEqual(0, by_class[route_binding.V4_ROUTE_PARTNER_MIGRATION_OR_PARITY])
        self.assertEqual(0, by_class[route_binding.V4_ROUTE_BACKEND_BOUND_PARITY_CONTROL])
        self.assertEqual(3, by_class[route_binding.V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR])
        self.assertEqual(0, by_class[route_binding.V4_ROUTE_REQUIRES_CUPY_PROMOTION])
        self.assertEqual(0, by_class[route_binding.V4_ROUTE_REQUIRES_FIXED_NUMBA_CONTINUATION])
        self.assertEqual(1, by_class[route_binding.V4_ROUTE_NO_V4_APP_ROUTE_BLOCKER])
        self.assertEqual(1, by_class[route_binding.V4_ROUTE_DEFERRED_EXCLUDED_WITH_REASON])
        self.assertEqual(5, summary["full_app_route_bound_count"])
        self.assertEqual(5, summary["partial_or_blocked_count"])
        self.assertEqual(8, summary["route_actually_uses_v4_code_count"])
        self.assertTrue(summary["no_silent_fallback_to_v2_or_v3"])

    def test_full_routes_have_v4_planner_dry_runs_and_no_claim_authorization(self) -> None:
        rows = {row["app"]: row for row in v4.v4_goal4652_app_route_bindings()}

        for app in ("rt_dbscan", "raydb_style", "triangle_counting", "librts_spatial_index", "hausdorff_xhd"):
            row = rows[app]
            self.assertTrue(row["full_app_route_bound"], app)
            self.assertTrue(row["route_actually_uses_v4_code"], app)
            self.assertTrue(row["mapped_v4_operators"], app)
            self.assertTrue(row["planner_dry_runs"], app)
            for check in row["planner_dry_runs"]:
                self.assertTrue(check["status_matches"], (app, check))
                self.assertEqual("tier2_measured_ready", check["actual_status"], (app, check))
                self.assertTrue(check["api_surface"], (app, check))
                self.assertTrue(check["generic_primitive"], (app, check))
                self.assertTrue(check["measured_partner"], (app, check))
                self.assertFalse(check["release_claim_authorized"], (app, check))
                self.assertFalse(check["broad_v4_speedup_claim_authorized"], (app, check))
                self.assertFalse(check["whole_app_speedup_claim_authorized"], (app, check))
                self.assertFalse(check["app_specific_native_kernel_authorized"], (app, check))

    def test_hausdorff_route_is_bound_with_correctness_boundary_not_speed_claim(self) -> None:
        rows = {row["app"]: row for row in v4.v4_goal4652_app_route_bindings()}
        hausdorff = rows["hausdorff_xhd"]

        self.assertEqual(route_binding.V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE, hausdorff["route_class"])
        self.assertEqual(
            "official_v4_route_with_coordinate_normalized_correctness_boundary",
            hausdorff["route_status"],
        )
        self.assertTrue(hausdorff["full_app_route_bound"])
        self.assertIn(
            "v4_point_group_nearest_witness_2d_device_arrays",
            hausdorff["mapped_v4_operators"],
        )
        self.assertIn("Goal4666 mixed-result caveat", hausdorff["next_goal4653_protocol_action"])
        self.assertIn("CuPy official route repairs the 262k hot/prepare failure", hausdorff["blocker_or_gap"])
        self.assertIn("65k row stays below bar", hausdorff["blocker_or_gap"])
        self.assertIn(
            "future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/summary.json",
            hausdorff["evidence_refs"],
        )
        self.assertIn(
            "future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/summary.json",
            hausdorff["evidence_refs"],
        )
        self.assertFalse(hausdorff["release_claim_authorized"])
        self.assertFalse(hausdorff["whole_app_speedup_claim_authorized"])

    def test_partial_routes_are_not_silently_promoted_to_whole_app_claims(self) -> None:
        rows = {row["app"]: row for row in v4.v4_goal4652_app_route_bindings()}

        for app in ("robot_collision", "contact_manifold", "rtnn"):
            row = rows[app]
            self.assertEqual(route_binding.V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR, row["route_class"])
            self.assertTrue(row["route_actually_uses_v4_code"], app)
            self.assertFalse(row["full_app_route_bound"], app)
            self.assertTrue(row["mapped_v4_operators"], app)
            self.assertIn("Freeze as", row["next_goal4653_protocol_action"])
            self.assertFalse(row["release_claim_authorized"])
            self.assertFalse(row["broad_v4_speedup_claim_authorized"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"])
            self.assertFalse(row["app_specific_native_kernel_authorized"])

    def test_rtnn_route_is_deferred_after_ranked_summary_parity(self) -> None:
        rows = {row["app"]: row for row in v4.v4_goal4652_app_route_bindings()}
        rtnn = rows["rtnn"]

        self.assertEqual(route_binding.V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR, rtnn["route_class"])
        self.assertEqual(
            "deferred_ranked_summary_parity_no_open_candidate",
            rtnn["route_status"],
        )
        self.assertIn(
            "v4_fixed_radius_ranked_summary_3d_prepared_runner",
            rtnn["mapped_v4_operators"],
        )
        self.assertIn("deferred/no-open-candidate", rtnn["next_goal4653_protocol_action"])
        self.assertIn("does not move the app-level bar", rtnn["blocker_or_gap"])
        self.assertIn(
            "future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json",
            rtnn["evidence_refs"],
        )
        dry_runs = {(row["operator"], row["partner"]): row for row in rtnn["planner_dry_runs"]}
        ranked = dry_runs[("ranked_summary", "rtdl_native")]
        self.assertEqual(
            "deferred_serious_scale_not_v4_0_release_surface",
            ranked["actual_status"],
        )
        self.assertFalse(ranked["release_claim_authorized"])
        self.assertFalse(ranked["whole_app_speedup_claim_authorized"])

    def test_no_route_and_deferred_rows_are_explicit_blockers(self) -> None:
        rows = {row["app"]: row for row in v4.v4_goal4652_app_route_bindings()}

        spatial = rows["spatial_rayjoin"]
        self.assertEqual(route_binding.V4_ROUTE_NO_V4_APP_ROUTE_BLOCKER, spatial["route_class"])
        self.assertFalse(spatial["route_actually_uses_v4_code"])
        self.assertFalse(spatial["full_app_route_bound"])
        self.assertFalse(spatial["dry_run_possible"])
        self.assertIn("no-route blocker", spatial["next_goal4653_protocol_action"])

        barnes_hut = rows["barnes_hut"]
        self.assertEqual(route_binding.V4_ROUTE_DEFERRED_EXCLUDED_WITH_REASON, barnes_hut["route_class"])
        self.assertFalse(barnes_hut["route_actually_uses_v4_code"])
        self.assertFalse(barnes_hut["full_app_route_bound"])
        self.assertFalse(barnes_hut["dry_run_possible"])
        self.assertIn("do not add a Barnes-Hut native kernel", barnes_hut["next_goal4653_protocol_action"])

    def test_validation_returns_summary_and_preserves_front_door_exports(self) -> None:
        summary = v4.validate_v4_goal4652_app_route_bindings()

        self.assertEqual(route_binding.V4_GOAL4652_APP_ROUTE_BINDING_STATUS, summary["status"])
        self.assertFalse(summary["release_claim_authorized"])
        self.assertFalse(summary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(summary["whole_app_speedup_claim_authorized"])
        self.assertFalse(summary["app_specific_native_kernel_authorized"])


if __name__ == "__main__":
    unittest.main()
