from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl import v4
from rtdsl import v4_app_benchmark_protocol as protocol
from rtdsl import v4_app_route_binding as routes


GOAL4663_SUMMARY = (
    ROOT
    / "future"
    / "v4"
    / "evidence"
    / "v4_goal4663_app_level_protocol_refresh_after_changed_routes_2026-06-25.json"
)


class V4Goal4653AppLevelProtocolTest(unittest.TestCase):
    def test_protocol_covers_all_apps_in_goal4652_order(self) -> None:
        rows = v4.v4_goal4653_protocol_rows()
        apps = tuple(row["app"] for row in rows)

        self.assertEqual(routes.V4_GOAL4652_APP_ORDER, apps)
        self.assertEqual(10, len(rows))
        self.assertEqual(10, len(set(apps)))

    def test_summary_freezes_class_aware_protocol_shape(self) -> None:
        summary = v4.v4_goal4653_protocol_summary()
        by_type = summary["by_protocol_row_type"]

        self.assertEqual(protocol.V4_GOAL4653_PROTOCOL_STATUS, summary["status"])
        self.assertEqual(5, by_type[protocol.V4_PROTOCOL_FULL_APP_CANDIDATE])
        self.assertEqual(3, by_type[protocol.V4_PROTOCOL_PARTIAL_CONTROL_ONLY])
        self.assertEqual(1, by_type[protocol.V4_PROTOCOL_NO_ROUTE_BLOCKER])
        self.assertEqual(1, by_type[protocol.V4_PROTOCOL_DEFERRED_EXCLUDED])
        self.assertEqual(5, summary["full_app_v4_speed_row_count"])
        self.assertEqual(3, summary["partial_control_count"])
        self.assertEqual(2, summary["visible_blocker_or_deferred_count"])
        self.assertTrue(summary["all_rows_have_pre_frozen_bars"])
        self.assertTrue(summary["no_naive_whole_suite_geomean_trigger"])
        self.assertTrue(summary["posthoc_app_exclusion_forbidden"])
        self.assertFalse(summary["pod_spend_authorized_by_this_goal"])

    def test_full_app_rows_freeze_numeric_speed_bars_and_correctness(self) -> None:
        rows = {row["app"]: row for row in v4.v4_goal4653_protocol_rows()}

        for app in ("rt_dbscan", "raydb_style", "triangle_counting", "librts_spatial_index"):
            row = rows[app]
            bar = row["pass_fail_bar"]
            self.assertEqual(protocol.V4_PROTOCOL_FULL_APP_CANDIDATE, row["protocol_row_type"])
            self.assertTrue(row["v4_run_required_in_goal4654"], app)
            self.assertTrue(row["contributes_to_formal_high_performance"], app)
            self.assertEqual(1.20, bar["v4_vs_v2_14_wall_speedup_min"])
            self.assertEqual(1.05, bar["v4_vs_v3_wall_speedup_min"])
            self.assertEqual(0.98, bar["no_regression_floor"])
            self.assertTrue(bar["correctness_parity_required"])
            self.assertFalse(bar["partner_migration_counts_as_win"])
            self.assertIn("same-app V2.14", row["denominator"])
            self.assertIn("correctness_parity", row["metric_windows"])

        hausdorff = rows["hausdorff_xhd"]
        hausdorff_bar = hausdorff["pass_fail_bar"]
        self.assertEqual(protocol.V4_PROTOCOL_FULL_APP_CANDIDATE, hausdorff["protocol_row_type"])
        self.assertTrue(hausdorff["v4_run_required_in_goal4654"])
        self.assertTrue(hausdorff["contributes_to_formal_high_performance"])
        self.assertEqual(1.20, hausdorff_bar["v4_vs_v3_hot_speedup_min"])
        self.assertEqual(0.80, hausdorff_bar["prepare_no_regression_floor_where_comparable"])
        self.assertTrue(hausdorff_bar["coordinate_normalized_1m_correctness_probe_required"])
        self.assertFalse(hausdorff_bar["partner_migration_counts_as_win"])
        self.assertIn("Goal4667 focused rows", hausdorff["dataset_scale"])
        self.assertIn("V3.0.2 CuPy", hausdorff["denominator"])
        self.assertIn("focused_true_v4_runtime_candidate", hausdorff["claim_class_if_pass"])

    def test_partial_rows_are_controls_not_formal_speed_rows(self) -> None:
        rows = {row["app"]: row for row in v4.v4_goal4653_protocol_rows()}

        for app in ("robot_collision", "contact_manifold"):
            row = rows[app]
            bar = row["pass_fail_bar"]
            self.assertEqual(protocol.V4_PROTOCOL_PARTIAL_CONTROL_ONLY, row["protocol_row_type"])
            self.assertFalse(row["v4_run_required_in_goal4654"], app)
            self.assertFalse(row["contributes_to_formal_high_performance"], app)
            self.assertTrue(bar["operator_control_only"], app)
            self.assertEqual(0.98, bar["if_measured_no_regression_floor"])
            self.assertFalse(bar["whole_app_speedup_claim_authorized"], app)
            self.assertIn("operator-control denominator only", row["denominator"])

        rtnn = rows["rtnn"]
        self.assertEqual(protocol.V4_PROTOCOL_PARTIAL_CONTROL_ONLY, rtnn["protocol_row_type"])
        self.assertEqual(routes.V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR, rtnn["route_class"])
        self.assertFalse(rtnn["v4_run_required_in_goal4654"])
        self.assertFalse(rtnn["contributes_to_formal_high_performance"])
        self.assertIn("not exact same-runner", rtnn["denominator"])
        self.assertIn("does_not_move_app_level_bar", rtnn["claim_class_if_pass"])
        self.assertIn("v4_fixed_radius_ranked_summary_3d_prepared_runner", rtnn["mapped_v4_operators"])
        self.assertFalse(rtnn["pass_fail_bar"]["whole_app_speedup_claim_authorized"])

    def test_blocked_and_deferred_rows_are_visible_and_not_hidden_exclusions(self) -> None:
        rows = {row["app"]: row for row in v4.v4_goal4653_protocol_rows()}

        spatial = rows["spatial_rayjoin"]
        self.assertEqual(protocol.V4_PROTOCOL_NO_ROUTE_BLOCKER, spatial["protocol_row_type"])
        self.assertFalse(spatial["v4_run_required_in_goal4654"])
        self.assertTrue(spatial["pass_fail_bar"]["count_as_visible_blocker"])
        self.assertTrue(spatial["pass_fail_bar"]["posthoc_exclusion_forbidden"])

        barnes_hut = rows["barnes_hut"]
        self.assertEqual(protocol.V4_PROTOCOL_DEFERRED_EXCLUDED, barnes_hut["protocol_row_type"])
        self.assertFalse(barnes_hut["v4_run_required_in_goal4654"])
        self.assertTrue(barnes_hut["pass_fail_bar"]["count_as_visible_blocker"])
        self.assertIn("app-identity", barnes_hut["blocker_or_gap"])

    def test_protocol_stays_in_sync_with_goal4652_route_matrix(self) -> None:
        protocol_rows = {row["app"]: row for row in v4.v4_goal4653_protocol_rows()}
        route_rows = {row["app"]: row for row in v4.v4_goal4652_app_route_bindings()}

        for app, protocol_row in protocol_rows.items():
            route_row = route_rows[app]
            self.assertEqual(route_row["route_class"], protocol_row["route_class"], app)
            self.assertEqual(tuple(route_row["mapped_v4_operators"]), tuple(protocol_row["mapped_v4_operators"]), app)

    def test_validation_preserves_all_non_authorization_flags(self) -> None:
        summary = v4.validate_v4_goal4653_protocol()

        self.assertFalse(summary["release_claim_authorized"])
        self.assertFalse(summary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(summary["whole_app_speedup_claim_authorized"])
        self.assertFalse(summary["app_specific_native_kernel_authorized"])
        self.assertFalse(summary["silent_v2_v3_fallback_authorized"])

    def test_goal4663_refresh_does_not_trigger_full_all_app_rerun(self) -> None:
        summary = json.loads(GOAL4663_SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(
            "goal4663_app_level_protocol_refreshed_after_goal4659_4661",
            summary["status"],
        )
        self.assertEqual(
            "protocol_refreshed__no_full_all_app_rerun_triggered",
            summary["decision"]["label"],
        )
        self.assertFalse(summary["decision"]["goal4664_focused_changed_app_rerun_needed"])
        self.assertTrue(summary["decision"]["goal4664_focused_changed_app_evidence_already_available"])
        self.assertFalse(summary["decision"]["goal4665_full_all_app_go"])
        self.assertFalse(summary["claim_boundary"]["full_all_app_rerun_authorized"])
        self.assertFalse(summary["claim_boundary"]["formal_high_performance_v4_authorized"])
        self.assertEqual(
            "official_route_recorded_but_kept_out_of_formal_speed_row_until_coordinate_normalized_denominator_is_public",
            summary["changed_rows"]["hausdorff_xhd"]["changed_row_decision"],
        )
        self.assertEqual(
            "candidate_route_recorded_but_performance_failed_and_kept_out_of_formal_speed_rows",
            summary["changed_rows"]["rtnn"]["changed_row_decision"],
        )


if __name__ == "__main__":
    unittest.main()
