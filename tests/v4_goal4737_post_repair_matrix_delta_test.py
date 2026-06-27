from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4737_post_repair_app_matrix_delta_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4737_post_repair_app_matrix_delta_2026-06-26.md"


class V4Goal4737PostRepairMatrixDeltaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.rows = {row["app"]: row for row in self.payload["rows"]}

    def test_delta_counts_three_candidate_rows_but_blocks_tag(self) -> None:
        summary = self.payload["summary"]
        self.assertEqual(10, summary["app_count"])
        self.assertEqual(3, summary["candidate_rows_vs_v2_with_v3_no_regression"])
        self.assertEqual(["hausdorff_xhd", "triangle_counting", "barnes_hut"], summary["candidate_apps"])
        self.assertFalse(summary["formal_high_performance_v4_supported"])
        self.assertFalse(summary["final_tag_authorized"])

    def test_raydb_remains_blocker_and_triangle_is_cleaned(self) -> None:
        self.assertLess(self.rows["raydb_style"]["v4_vs_v3_0_2_hot"], 0.98)
        self.assertFalse(self.rows["raydb_style"]["contributes_to_candidate_count"])
        self.assertGreater(self.rows["triangle_counting"]["v4_vs_v2_14_hot"], 1.20)
        self.assertGreaterEqual(self.rows["triangle_counting"]["v4_vs_v3_0_2_hot"], 0.98)
        self.assertTrue(self.rows["triangle_counting"]["contributes_to_candidate_count"])

    def test_barnes_hut_candidate_is_bounded(self) -> None:
        barnes = self.rows["barnes_hut"]
        self.assertGreater(barnes["v4_vs_v2_14_hot"], 1.20)
        self.assertGreaterEqual(barnes["v4_vs_v3_0_2_hot"], 0.98)
        self.assertEqual(
            barnes["claim_class"],
            "complete_aggregate_workflow_candidate_not_rt_core_force_law",
        )
        self.assertTrue(barnes["contributes_to_candidate_count"])

    def test_claim_boundary_blocks_overclaiming(self) -> None:
        boundary = self.payload["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "public_speedup_claim_authorized",
            "all_benchmark_speedup_claim_authorized",
            "geomean_headline_authorized",
            "broad_v4_over_v3_wording_authorized",
            "app_specific_native_kernel_authorized",
            "true_zero_copy_wording_authorized",
        ):
            self.assertFalse(boundary[key], key)

    def test_next_goals_start_with_raydb_v3_regression(self) -> None:
        goals = self.payload["next_goals"]
        self.assertEqual("Goal4738", goals[0]["id"])
        self.assertEqual("raydb_style", goals[0]["target"])
        self.assertIn("RayDB V3 regression first", REPORT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
