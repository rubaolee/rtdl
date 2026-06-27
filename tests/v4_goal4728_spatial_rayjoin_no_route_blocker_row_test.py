from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROW = ROOT / "future" / "v4" / "evidence" / "v4_goal4728_spatial_rayjoin_no_route_blocker_row_2026-06-26.json"
SOURCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4681_shape_pair_serious_2026-06-25" / "summary.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4728_spatial_rayjoin_no_route_blocker_row_2026-06-26.md"
CALL_FOR_REVIEW = (
    ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_goal4728_spatial_rayjoin_no_route_blocker_row_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT / "future" / "v4" / "reviews" / "v4_goal4728_spatial_rayjoin_no_route_blocker_row_review_debt_2026-06-26.md"
)


class V4Goal4728SpatialRayjoinNoRouteBlockerRowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.row = json.loads(ROW.read_text(encoding="utf-8"))
        self.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.matrix_row = self.row["matrix_row"]

    def test_row_closes_spatial_rayjoin_as_no_route_blocker(self) -> None:
        self.assertEqual("spatial_rayjoin", self.matrix_row["app"])
        self.assertEqual("closed_no_current_v4_app_route_blocker", self.matrix_row["row_status"])
        self.assertEqual("no_v4_route_blocker", self.matrix_row["goal4723_row_class"])
        self.assertEqual("no_current_v4_relation_topology_route", self.matrix_row["goal4724_gap_class"])
        self.assertFalse(self.matrix_row["current_v4_full_app_route_bound"])
        self.assertTrue(self.matrix_row["contributes_to_complete_10_app_matrix"])
        self.assertFalse(self.matrix_row["contributes_to_formal_high_performance_v4"])

    def test_shape_pair_subprobe_failed_speed_credit_bars(self) -> None:
        subprobe = self.matrix_row["subprobe_result"]
        self.assertTrue(subprobe["correctness_companion_ok"])
        self.assertTrue(subprobe["serious_active_count_parity"])
        self.assertFalse(subprobe["v4_host_row_stream_materialization_in_hot_path"])
        self.assertFalse(subprobe["goal4681_speed_credit_pass"])
        self.assertLess(subprobe["v4_hot_over_v2_14_same_primitive"], 1.20)
        self.assertLess(subprobe["v4_wall_over_v2_14_same_primitive"], 1.10)
        self.assertLess(subprobe["v4_hot_over_v3_0_2_control"], 0.98)
        self.assertEqual(
            self.source["ratios"]["v4_hot_over_v2_14_same_primitive"],
            subprobe["v4_hot_over_v2_14_same_primitive"],
        )

    def test_interpretation_blocks_subprobe_as_full_app_result(self) -> None:
        interpretation = self.matrix_row["interpretation"]
        self.assertFalse(interpretation["subprobe_is_complete_spatial_rayjoin_app_row"])
        self.assertFalse(interpretation["subprobe_supports_v4_speed_credit"])
        self.assertFalse(interpretation["v2_v3_fallback_allowed"])
        self.assertFalse(interpretation["app_level_high_performance_candidate"])
        self.assertIn("not a complete spatial_rayjoin app route", interpretation["reason"])

    def test_claim_boundary_blocks_release_pod_rayjoin_claims_and_fallback(self) -> None:
        boundary = self.row["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "pod_authorized_by_goal4728",
            "public_speedup_claim_authorized",
            "whole_app_high_performance_claim_authorized",
            "spatial_rayjoin_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "broad_v4_over_v2_14_claim_authorized",
            "app_specific_native_kernel_authorized",
            "hidden_v2_v3_fallback_authorized",
        ):
            self.assertFalse(boundary[key], key)

    def test_report_and_review_debt_exist(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, REVIEW_DEBT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Non-Authorization", text)
            self.assertIn("final V4 tag", text)

    def test_next_goal_is_barnes_hut(self) -> None:
        self.assertEqual("Goal4729", self.row["next_goal"]["id"])
        self.assertIn("barnes_hut", self.row["next_goal"]["title"])


if __name__ == "__main__":
    unittest.main()
