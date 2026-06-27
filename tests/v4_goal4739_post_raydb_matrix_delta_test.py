from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4739_post_raydb_repair_app_matrix_delta_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4739_post_raydb_repair_app_matrix_delta_2026-06-26.md"


class V4Goal4739PostRaydbMatrixDeltaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.rows = {row["app"]: row for row in self.payload["rows"]}

    def test_matrix_keeps_three_candidates_and_blocks_tag(self) -> None:
        summary = self.payload["summary"]
        self.assertEqual(10, summary["app_count"])
        self.assertEqual(3, summary["candidate_rows_vs_v2_with_v3_no_regression"])
        self.assertEqual(["hausdorff_xhd", "triangle_counting", "barnes_hut"], summary["candidate_apps"])
        self.assertTrue(summary["raydb_regression_removed"])
        self.assertFalse(summary["formal_high_performance_v4_supported"])
        self.assertFalse(summary["final_tag_authorized"])

    def test_raydb_is_repaired_but_not_promoted(self) -> None:
        raydb = self.rows["raydb_style"]
        self.assertGreaterEqual(raydb["v4_vs_v2_14_hot"], 0.98)
        self.assertGreaterEqual(raydb["v4_vs_v3_0_2_hot"], 0.98)
        self.assertLess(raydb["v4_vs_v3_0_2_hot"], 1.20)
        self.assertFalse(raydb["contributes_to_candidate_count"])
        self.assertFalse(raydb["host_materialization_in_hot_path"])
        self.assertEqual(raydb["claim_class"], "modest_device_output_hot_path_win_below_formal_bar")

    def test_candidate_rows_remain_bounded(self) -> None:
        for app in ("hausdorff_xhd", "triangle_counting", "barnes_hut"):
            self.assertTrue(self.rows[app]["contributes_to_candidate_count"], app)
            self.assertGreater(self.rows[app]["v4_vs_v2_14_hot"], 1.20)
            self.assertGreaterEqual(self.rows[app]["v4_vs_v3_0_2_hot"], 0.98)
        self.assertIn("not_rt_core_force_law", self.rows["barnes_hut"]["claim_class"])

    def test_next_goal_targets_robot_before_spatial_churn(self) -> None:
        goals = self.payload["next_goals"]
        self.assertEqual("Goal4740", goals[0]["id"])
        self.assertEqual("robot_collision", goals[0]["target"])
        self.assertIn("wrapper-wall failure", REPORT.read_text(encoding="utf-8"))

    def test_claim_boundary_blocks_release_overclaims(self) -> None:
        boundary = self.payload["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "public_speedup_claim_authorized",
            "all_benchmark_speedup_claim_authorized",
            "geomean_headline_authorized",
            "broad_v4_over_v3_wording_authorized",
            "app_specific_native_kernel_authorized",
            "arbitrary_callback_support_authorized",
            "raw_optix_callback_support_authorized",
            "true_zero_copy_wording_authorized",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
