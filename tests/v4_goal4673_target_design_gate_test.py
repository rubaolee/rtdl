from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4673_target_design_gate_2026-06-25.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4673_target_design_gate_2026-06-25.md"


class V4Goal4673TargetDesignGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_selects_aggregate_frontier_device_columns_without_pod_authorization(self) -> None:
        self.assertEqual(
            "select_aggregate_frontier_device_columns_as_conditional_goal4674_target__pod_not_authorized",
            self.payload["decision_label"],
        )
        target = self.payload["selected_target"]
        self.assertEqual("AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D", target["operator"])
        self.assertEqual("new_generic_runtime_lever_absent_from_v2_14", target["work_class"])
        self.assertEqual("barnes_hut", target["selected_app_probe"])
        self.assertFalse(self.payload["claim_boundary"]["pod_run_authorized_by_this_artifact"])
        self.assertFalse(self.payload["claim_boundary"]["whole_app_high_performance_claim_authorized"])

    def test_v2_14_denominator_distinguishes_logical_family_from_device_columns(self) -> None:
        denominator = self.payload["v2_14_denominator"]
        self.assertTrue(denominator["same_logical_family_existed_in_v2_14"])
        self.assertFalse(denominator["same_device_column_primitive_existed_in_v2_14"])
        self.assertIn("rtdl_optix_collect_aggregate_frontier_2d", denominator["v2_14_symbols_confirmed_present"])
        self.assertIn(
            "rtdl_optix_run_aggregate_frontier_device_columns_2d",
            denominator["v2_14_symbols_confirmed_absent"],
        )

    def test_pre_pod_gate_blocks_claims_and_requires_numeric_bars(self) -> None:
        gate = self.payload["goal4674_pre_pod_gate"]
        self.assertFalse(gate["pod_authorized_by_goal4673"])
        self.assertIn("frozen numeric material-speed bars before any hardware run", gate["required_before_pod"])
        self.assertEqual(1.2, gate["if_pod_later_authorized_primary_bars"]["aggregate_frontier_hot_v4_over_v2_14_min"])
        self.assertFalse(gate["if_pod_later_authorized_primary_bars"]["host_frontier_materialization_in_hot_path_allowed"])
        self.assertIn(
            "the only app-level win requires Barnes-Hut or force-law identity in the engine",
            gate["kill_conditions"],
        )

    def test_rejected_targets_preserve_v2_14_primitive_audit(self) -> None:
        by_target = {row["target"]: row for row in self.payload["rejected_or_deferred_targets"]}
        self.assertEqual(
            "defer_as_same_primitive_or_new_route_design",
            by_target["spatial_rayjoin_segment_pair_or_point_location"]["decision"],
        )
        self.assertIn("V2.14 already had", by_target["robot_collision_any_hit_flags"]["reason"])
        self.assertEqual(
            "reject_as_v4_public_target_as_is",
            by_target["aggregate_tree_fused_weighted_vector_sum_as_is"]["decision"],
        )

    def test_report_records_hard_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal4673 selects `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D`", text)
        self.assertIn("This does not promote the old aggregate-tree fused weighted-vector sum", text)
        self.assertIn("Goal4674 Pre-POD Gate", text)
        self.assertIn("Host frontier materialization in hot path", text)
        self.assertIn("Non-Authorization", text)


if __name__ == "__main__":
    unittest.main()
