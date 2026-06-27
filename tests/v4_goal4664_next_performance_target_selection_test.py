from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4664_next_performance_target_selection_2026-06-25.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4664_next_performance_target_selection_2026-06-25.md"


class V4Goal4664NextPerformanceTargetSelectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_selects_hausdorff_not_parity_targets(self) -> None:
        self.assertEqual(
            "goal4664_select_hausdorff_xhd_for_focused_formal_candidate_protocol",
            self.summary["status"],
        )
        self.assertEqual("hausdorff_xhd", self.summary["selected_app"])
        self.assertEqual(
            "select_hausdorff_for_goal4665_focused_formal_candidate_run",
            self.summary["decision"]["label"],
        )
        self.assertEqual(
            "RTNN serious rows are parity/slower and would be fake progress.",
            self.summary["decision"]["why_not_rtnn"],
        )
        self.assertFalse(self.summary["decision"]["full_all_app_rerun_authorized"])
        self.assertFalse(self.summary["decision"]["public_speed_claim_authorized"])
        self.assertFalse(self.summary["decision"]["release_authorized"])

    def test_frozen_goal4665_protocol_has_numeric_bars_and_denominator(self) -> None:
        protocol = self.summary["frozen_goal4665_protocol"]

        self.assertEqual("hausdorff_xhd", protocol["app"])
        self.assertIn("official V4 point-group", protocol["route"])
        self.assertEqual("no Hausdorff-specific native kernel", protocol["forbidden_shortcut"])
        self.assertEqual([65536, 262144], protocol["scales"])
        self.assertTrue(protocol["correctness_required"])
        self.assertEqual("hot_device_sec for prepared/reuse route", protocol["primary_metric"])
        self.assertEqual(1.20, protocol["minimum_bars"]["v4_vs_v3_0_2_hot_speedup_min"])
        self.assertEqual(1.20, protocol["minimum_bars"]["v4_vs_v2_14_primary_metric_speedup_min"])
        self.assertEqual(0.80, protocol["minimum_bars"]["no_regression_floor_for_prepare_where_comparable"])
        self.assertIn("V2.14 Embree", protocol["denominator_boundary"])
        self.assertIn("V3.0.2 CuPy", protocol["denominator_boundary"])
        self.assertIn("V4 Torch", protocol["denominator_boundary"])

    def test_report_blocks_release_and_full_all_app_rerun(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Why not RTNN", text)
        self.assertIn("would be fake progress", text)
        self.assertIn("Why not full all-app", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("no Hausdorff-specific native kernel", text)


if __name__ == "__main__":
    unittest.main()
