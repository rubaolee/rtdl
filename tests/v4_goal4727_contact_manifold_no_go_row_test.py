from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROW = ROOT / "future" / "v4" / "evidence" / "v4_goal4727_contact_manifold_no_go_row_2026-06-26.json"
SOURCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4683_contact_witness_design_audit_2026-06-25.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4727_contact_manifold_no_go_row_2026-06-26.md"
CALL_FOR_REVIEW = (
    ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_goal4727_contact_manifold_no_go_row_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT / "future" / "v4" / "reviews" / "v4_goal4727_contact_manifold_no_go_row_review_debt_2026-06-26.md"
)


class V4Goal4727ContactManifoldNoGoRowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.row = json.loads(ROW.read_text(encoding="utf-8"))
        self.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.matrix_row = self.row["matrix_row"]

    def test_row_closes_contact_manifold_as_no_go(self) -> None:
        self.assertEqual("contact_manifold", self.matrix_row["app"])
        self.assertEqual("closed_no_go_for_current_high_performance_path", self.matrix_row["row_status"])
        self.assertEqual("route_gap_requires_generic_operator", self.matrix_row["goal4723_row_class"])
        self.assertEqual(
            "partial_operator_exists_no_go_prior_for_rebranded_collect_k",
            self.matrix_row["goal4724_gap_class"],
        )
        self.assertTrue(self.matrix_row["contributes_to_complete_10_app_matrix"])
        self.assertFalse(self.matrix_row["contributes_to_formal_high_performance_v4"])

    def test_goal4683_source_is_no_go_and_kills_target(self) -> None:
        self.assertEqual("no_go", self.source["decision"])
        self.assertTrue(self.source["target_killed_for_v4_0_performance_path"])
        self.assertFalse(self.source["implementation_authorized"])
        self.assertFalse(self.source["pod_authorized"])
        self.assertEqual(self.source["status"], self.matrix_row["goal4683_status"])

    def test_preexisting_v2_14_and_current_surfaces_are_visible(self) -> None:
        self.assertIn("rtdl_optix_collect_k_bounded_i64", self.matrix_row["v2_14_preexisting_surfaces"])
        self.assertIn("rtdl_embree_collect_k_bounded_i64", self.matrix_row["v2_14_preexisting_surfaces"])
        self.assertIn(
            "segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns",
            self.matrix_row["current_preexisting_surfaces"],
        )
        self.assertIn(
            "bounded_collect_finalize_i64_partner_columns",
            self.matrix_row["current_preexisting_surfaces"],
        )

    def test_interpretation_blocks_rebranded_collect_k(self) -> None:
        interpretation = self.matrix_row["interpretation"]
        self.assertFalse(interpretation["complete_v4_app_route_bound"])
        self.assertFalse(interpretation["fresh_generic_v4_lever_identified"])
        self.assertFalse(interpretation["same_primitive_v4_over_v2_14_improvement_proved"])
        self.assertFalse(interpretation["app_level_high_performance_candidate"])
        self.assertIn("rebrand", interpretation["reason"])

    def test_claim_boundary_blocks_release_pod_and_speed_credit(self) -> None:
        boundary = self.row["claim_boundary"]
        for key in (
            "implementation_authorized",
            "release_authorized",
            "final_v4_tag_authorized",
            "pod_authorized_by_goal4727",
            "public_speedup_claim_authorized",
            "whole_app_high_performance_claim_authorized",
            "contact_manifold_speedup_claim_authorized",
            "broad_v4_over_v2_14_claim_authorized",
            "partner_migration_speed_credit_authorized",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(boundary[key], key)

    def test_report_and_review_debt_exist(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, REVIEW_DEBT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Non-Authorization", text)
            self.assertIn("final V4 tag", text)

    def test_next_goal_is_spatial_rayjoin(self) -> None:
        self.assertEqual("Goal4728", self.row["next_goal"]["id"])
        self.assertIn("spatial_rayjoin", self.row["next_goal"]["title"])


if __name__ == "__main__":
    unittest.main()
