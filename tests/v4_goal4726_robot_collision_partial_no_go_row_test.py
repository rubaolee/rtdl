from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROW = ROOT / "future" / "v4" / "evidence" / "v4_goal4726_robot_collision_partial_no_go_row_2026-06-26.json"
SOURCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25" / "summary.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4726_robot_collision_partial_no_go_row_2026-06-26.md"
CALL_FOR_REVIEW = (
    ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_goal4726_robot_collision_partial_no_go_row_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT / "future" / "v4" / "reviews" / "v4_goal4726_robot_collision_partial_no_go_row_review_debt_2026-06-26.md"
)


class V4Goal4726RobotCollisionPartialNoGoRowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.row = json.loads(ROW.read_text(encoding="utf-8"))
        self.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.matrix_row = self.row["matrix_row"]

    def test_row_closes_robot_collision_as_partial_no_go(self) -> None:
        self.assertEqual("robot_collision", self.matrix_row["app"])
        self.assertEqual(
            "closed_partial_operator_no_go_for_current_high_performance_path",
            self.matrix_row["row_status"],
        )
        self.assertEqual("route_gap_requires_generic_operator", self.matrix_row["goal4723_row_class"])
        self.assertEqual(
            "partial_operator_exists_full_app_missing",
            self.matrix_row["goal4724_gap_class"],
        )
        self.assertFalse(self.matrix_row["contributes_to_formal_high_performance_v4"])
        self.assertTrue(self.matrix_row["contributes_to_complete_10_app_matrix"])

    def test_v2_14_denominator_is_same_core_primitive(self) -> None:
        self.assertEqual(
            "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1",
            self.matrix_row["v2_14_primitive_contract"],
        )
        self.assertIn("NumPy vectorized query lowering", self.matrix_row["v2_14_route"])

    def test_source_gate_failed_wrapper_floor(self) -> None:
        source_ratios = self.source["comparison"]["aggregate_ratios"]
        gate = self.matrix_row["same_contract_gate"]
        self.assertEqual("pass", gate["validation_status"])
        self.assertEqual("pass", gate["timed_status"])
        self.assertEqual("fail", gate["performance_floor_status"])
        self.assertGreaterEqual(gate["tail_total_mean_embree_over_optix"], gate["tail_total_mean_embree_over_optix_floor"])
        self.assertGreaterEqual(gate["traversal_mean_embree_over_optix"], gate["traversal_mean_embree_over_optix_floor"])
        self.assertLess(gate["wrapper_mean_embree_over_optix"], gate["wrapper_mean_embree_over_optix_floor"])
        self.assertLess(gate["wrapper_min_embree_over_optix"], gate["wrapper_min_embree_over_optix_floor"])
        self.assertEqual(source_ratios["wrapper_elapsed_embree_over_optix_mean"], gate["wrapper_mean_embree_over_optix"])

    def test_interpretation_does_not_turn_traversal_win_into_app_win(self) -> None:
        interpretation = self.matrix_row["interpretation"]
        self.assertTrue(interpretation["native_traversal_win_exists"])
        self.assertFalse(interpretation["wrapper_wall_win_exists"])
        self.assertTrue(interpretation["correctness_validated"])
        self.assertFalse(interpretation["complete_v4_app_route_bound"])
        self.assertFalse(interpretation["same_primitive_v4_over_v2_14_improvement_proved"])
        self.assertFalse(interpretation["app_level_high_performance_candidate"])

    def test_claim_boundary_blocks_release_pod_and_speed_claims(self) -> None:
        boundary = self.row["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "public_speedup_claim_authorized",
            "whole_app_high_performance_claim_authorized",
            "robot_collision_speedup_claim_authorized",
            "broad_v4_over_v2_14_claim_authorized",
            "measured_catalog_promotion_authorized",
            "pod_authorized_by_goal4726",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(boundary[key], key)

    def test_report_and_review_debt_exist(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, REVIEW_DEBT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Non-Authorization", text)
            self.assertIn("final V4 tag", text)

    def test_next_goal_is_contact_manifold(self) -> None:
        self.assertEqual("Goal4727", self.row["next_goal"]["id"])
        self.assertIn("contact_manifold", self.row["next_goal"]["title"])


if __name__ == "__main__":
    unittest.main()
