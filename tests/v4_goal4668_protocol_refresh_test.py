from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4668_protocol_refresh_after_goal4667_2026-06-25.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4668_protocol_refresh_after_hausdorff_focused_pass_2026-06-25.md"


class V4Goal4668ProtocolRefreshTest(unittest.TestCase):
    def setUp(self) -> None:
        self.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_protocol_refresh_goes_to_full_app_rerun_not_release(self) -> None:
        self.assertEqual(
            "goal4668_protocol_refreshed_after_hausdorff_focused_pass",
            self.summary["status"],
        )
        self.assertEqual(
            "protocol_refreshed__full_app_rerun_go_after_hausdorff_focused_pass__no_release",
            self.summary["decision"]["label"],
        )
        self.assertTrue(self.summary["decision"]["full_app_rerun_go"])
        self.assertFalse(self.summary["decision"]["release_authorized"])
        self.assertFalse(self.summary["decision"]["formal_high_performance_v4_authorized"])
        self.assertTrue(self.summary["claim_boundary"]["pod_spend_authorized_by_protocol"])
        self.assertFalse(self.summary["claim_boundary"]["whole_app_speedup_claim_authorized"])

    def test_protocol_counts_promote_only_hausdorff(self) -> None:
        protocol = self.summary["protocol_summary"]

        self.assertEqual(5, protocol["full_app_v4_speed_row_count"])
        self.assertEqual(3, protocol["partial_control_count"])
        self.assertEqual(2, protocol["visible_blocker_or_deferred_count"])

        hausdorff = self.summary["changed_rows"]["hausdorff_xhd"]["protocol"]
        self.assertEqual("full_app_v4_speed_row_candidate", hausdorff["protocol_row_type"])
        self.assertTrue(hausdorff["contributes_to_formal_high_performance"])
        self.assertTrue(hausdorff["v4_run_required_in_goal4654"])
        self.assertIn("adaptive CuPy", hausdorff["v4_route"])

    def test_hausdorff_bar_is_frozen_and_claim_bounded(self) -> None:
        hausdorff = self.summary["changed_rows"]["hausdorff_xhd"]["protocol"]
        bar = hausdorff["pass_fail_bar"]

        self.assertEqual(1.20, bar["v4_vs_v2_14_wall_speedup_min"])
        self.assertEqual(1.20, bar["v4_vs_v3_hot_speedup_min"])
        self.assertEqual(0.80, bar["prepare_no_regression_floor_where_comparable"])
        self.assertTrue(bar["coordinate_normalized_1m_correctness_probe_required"])
        self.assertFalse(bar["partner_migration_counts_as_win"])
        self.assertFalse(bar["app_specific_native_kernel_authorized"])

    def test_report_keeps_next_step_and_boundary_clear(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("full app rerun Go", text)
        self.assertIn("does not authorize V4 release", text)
        self.assertIn("Goal4669 should run", text)
        self.assertIn("Release remains unauthorized", text)


if __name__ == "__main__":
    unittest.main()
