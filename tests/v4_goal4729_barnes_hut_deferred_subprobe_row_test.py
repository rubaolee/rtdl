from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROW = ROOT / "future" / "v4" / "evidence" / "v4_goal4729_barnes_hut_deferred_subprobe_row_2026-06-26.json"
SOURCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4676_serious_2026-06-25" / "summary.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4729_barnes_hut_deferred_subprobe_row_2026-06-26.md"
CALL_FOR_REVIEW = (
    ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_goal4729_barnes_hut_deferred_subprobe_row_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT / "future" / "v4" / "reviews" / "v4_goal4729_barnes_hut_deferred_subprobe_row_review_debt_2026-06-26.md"
)


class V4Goal4729BarnesHutDeferredSubprobeRowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.row = json.loads(ROW.read_text(encoding="utf-8"))
        self.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.matrix_row = self.row["matrix_row"]

    def test_row_closes_barnes_hut_as_deferred_subprobe(self) -> None:
        self.assertEqual("barnes_hut", self.matrix_row["app"])
        self.assertEqual("closed_deferred_subprobe_not_complete_app_route", self.matrix_row["row_status"])
        self.assertEqual("deferred_no_app_identity_route", self.matrix_row["goal4723_row_class"])
        self.assertEqual(
            "aggregate_frontier_subprobe_not_complete_app_route",
            self.matrix_row["goal4724_gap_class"],
        )
        self.assertTrue(self.matrix_row["contributes_to_complete_10_app_matrix"])
        self.assertFalse(self.matrix_row["contributes_to_formal_high_performance_v4"])

    def test_aggregate_frontier_subprobe_preserves_real_v2_14_win_and_v3_caveat(self) -> None:
        subprobe = self.matrix_row["subprobe_result"]
        self.assertTrue(subprobe["goal4676_pass"])
        self.assertTrue(subprobe["correctness_companion_ok"])
        self.assertFalse(subprobe["partner_migration_counted_as_speed"])
        self.assertFalse(subprobe["v4_host_frontier_materialization_in_hot_path"])
        self.assertGreater(subprobe["v4_full_hot_over_v2_14"], 100.0)
        self.assertGreater(subprobe["v4_full_wall_over_v2_14"], 100.0)
        self.assertLess(subprobe["v4_full_hot_over_v3_0_2_control"], 1.01)
        self.assertEqual(
            self.source["ratios"]["v4_full_hot_over_v3_0_2_control"],
            subprobe["v4_full_hot_over_v3_0_2_control"],
        )

    def test_fused_weighted_vector_contract_blocks_rt_core_claim(self) -> None:
        boundary = self.matrix_row["fused_weighted_vector_contract_boundary"]
        self.assertEqual(
            "implemented_cuda_device_accumulation_not_rt_core",
            boundary["implemented_runtime_status"],
        )
        self.assertFalse(boundary["uses_optix_trace"])
        self.assertTrue(boundary["device_resident_output_columns"])
        self.assertFalse(boundary["hot_path_host_materialization"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])

    def test_interpretation_blocks_full_app_and_rt_core_claims(self) -> None:
        interpretation = self.matrix_row["interpretation"]
        self.assertTrue(interpretation["real_v4_operator_win_vs_v2_14_host_frontier"])
        self.assertFalse(interpretation["clean_v4_over_v3_speed_win"])
        self.assertFalse(interpretation["complete_barnes_hut_app_route_bound"])
        self.assertFalse(interpretation["force_vector_workflow_measured_as_complete_app"])
        self.assertFalse(interpretation["rt_core_speedup_proved"])
        self.assertFalse(interpretation["app_identity_kernel_allowed"])

    def test_claim_boundary_blocks_release_pod_and_barnes_claims(self) -> None:
        boundary = self.row["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "pod_authorized_by_goal4729",
            "public_speedup_claim_authorized",
            "whole_app_high_performance_claim_authorized",
            "barnes_hut_speedup_claim_authorized",
            "broad_v4_over_v2_14_claim_authorized",
            "v4_over_v3_speed_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "paper_reproduction_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(boundary[key], key)

    def test_report_and_review_debt_exist(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, REVIEW_DEBT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Non-Authorization", text)
            self.assertIn("final V4 tag", text)

    def test_next_goal_is_complete_matrix(self) -> None:
        self.assertEqual("Goal4730", self.row["next_goal"]["id"])
        self.assertIn("10-app", self.row["next_goal"]["title"])


if __name__ == "__main__":
    unittest.main()
