from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4667_hausdorff_multiblock_argmax_20260625" / "summary.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4667_hausdorff_adaptive_argmax_focused_gate_2026-06-25.md"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
HAUSDORFF_APP = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_distance_app.py"
)


class V4Goal4667HausdorffAdaptiveArgmaxTest(unittest.TestCase):
    def setUp(self) -> None:
        self.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_focused_gate_passes_without_release_authorization(self) -> None:
        self.assertEqual(
            "goal4667_hausdorff_adaptive_argmax_focused_gate_passed_no_release_authorization",
            self.summary["status"],
        )
        self.assertEqual(
            "hausdorff_focused_gate_passes_after_generic_adaptive_argmax__not_release_yet",
            self.summary["decision"]["label"],
        )
        self.assertTrue(self.summary["decision"]["may_count_as_formal_high_performance_v4_candidate_row"])
        self.assertTrue(self.summary["decision"]["may_trigger_full_all_app_rerun_request"])
        self.assertFalse(self.summary["decision"]["release_authorized"])
        self.assertFalse(self.summary["claim_boundary"]["release_authorized"])
        self.assertFalse(self.summary["claim_boundary"]["formal_high_performance_v4_authorized"])
        self.assertFalse(self.summary["claim_boundary"]["whole_app_speedup_claim_authorized"])

    def test_both_focused_rows_clear_frozen_bars(self) -> None:
        rows = {row["points_per_side"]: row for row in self.summary["rows"]}

        self.assertEqual({65536, 262144}, set(rows))
        for points, row in rows.items():
            self.assertTrue(row["passes_correctness"], points)
            self.assertTrue(row["passes_hot_bar_1_20x"], points)
            self.assertTrue(row["passes_prepare_floor_0_80x"], points)
            self.assertGreaterEqual(row["speedup_hot_over_v3_cupy"], 1.20)
            self.assertGreaterEqual(row["speedup_prepare_over_v3_cupy"], 0.80)
            self.assertEqual("global_argmax_u32_f64_partner_columns", row["v4_adaptive_argmax"]["consumer_adapter"])
            self.assertFalse(row["v4_adaptive_argmax"]["partner_synchronized_before_return"])

        self.assertEqual(
            "cupy_rawkernel_single_block_reduce",
            rows[65536]["v4_adaptive_argmax"]["consumer_reduction_strategy"],
        )
        self.assertEqual(
            "cupy_rawkernel_multiblock_reduce",
            rows[262144]["v4_adaptive_argmax"]["consumer_reduction_strategy"],
        )

    def test_large_correctness_probe_is_not_speed_claim(self) -> None:
        probe = self.summary["large_scale_correctness_probe"]

        self.assertEqual(1048576, probe["points_per_side"])
        self.assertTrue(probe["passes_correctness"])
        self.assertFalse(probe["speed_claim_authorized"])
        self.assertEqual("cupy_rawkernel_multiblock_reduce", probe["consumer_reduction_strategy"])

    def test_source_uses_generic_runtime_optimization_not_app_kernel(self) -> None:
        adapters = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        app = HAUSDORFF_APP.read_text(encoding="utf-8")

        self.assertIn("synchronize: bool = True", adapters)
        self.assertIn("rtdl_cupy_global_argmax_u32_f64_blocks", adapters)
        self.assertIn("rtdl_cupy_global_argmax_u32_f64_final", adapters)
        self.assertIn('strategy_selection": "rawkernel_single_block_for_small_rows_else_multiblock_reduce"', adapters)
        self.assertIn("synchronize=False", app)
        self.assertNotIn("_cupy_global_argmax_u32_f64_with_neighbor", app)

    def test_report_keeps_release_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("focused gate passed", text)
        self.assertIn("No Hausdorff-specific native kernel was added", text)
        self.assertIn("does not authorize", text)
        self.assertIn("not enough by", text)
        self.assertIn("itself to finish V4", text)


if __name__ == "__main__":
    unittest.main()
