import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5423_level_b_matrix_consolidation_after_geo.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5423_level_b_matrix_consolidation_after_geo.py"
)


class Goal5423LevelBMatrixConsolidationAfterGeoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_consolidates_graphics_and_bounded_geo_coverage(self):
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5423.level_b_matrix_consolidation_after_geo.v1",
        )
        self.assertTrue(payload["matched"])
        coverage = payload["coverage"]
        self.assertEqual(coverage["graphics_case_count"], 3)
        self.assertEqual(coverage["graphics_route_result_count"], 6)
        self.assertEqual(coverage["bounded_geo_case_count"], 2)
        self.assertEqual(coverage["bounded_geo_route_result_count"], 2)
        self.assertEqual(coverage["total_case_count"], 5)

        self.assertEqual(
            [row["case_id"] for row in payload["graphics_rows"]],
            ["dragon_happy", "thai_happy_scaled", "thai_asian_scaled"],
        )
        self.assertEqual(
            [row["case_id"] for row in payload["bounded_geo_rows"]],
            ["county_zcta_bounded", "water_bg_bounded"],
        )

    def test_graphics_and_geo_rows_remain_level_b_only(self):
        for row in self.summary["graphics_rows"]:
            self.assertEqual(row["input_identity_level"], "level_b_same_source_public_graphics")
            self.assertTrue(row["author_rerun_matches_paper_log"])
            self.assertTrue(row["all_routes_match_author"])
            self.assertFalse(row["ratio_authorized"])
            self.assertFalse(row["figure5_reproduction_claimed"])

        for row in self.summary["bounded_geo_rows"]:
            self.assertEqual(row["input_identity_level"], "level_b_bounded_geo_fixture")
            self.assertTrue(row["matched_author"])
            self.assertLessEqual(row["abs_diff_vs_author"], row["tolerance"])
            self.assertFalse(row["ratio_authorized"])
            self.assertFalse(row["figure5_reproduction_claimed"])

    def test_claim_boundary_and_stop_loss_gate(self):
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["level_b_same_pod_scalar_matrix_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_figure5_matrix_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])

        gate = self.summary["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertIn("Goal5128", gate["gate_non_app_consumer"])
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

    def test_remaining_blockers_and_next_recommendation_are_not_micro_optimization(self):
        blockers = {row["blocker"] for row in self.summary["remaining_blockers"]}
        self.assertIn("exact_paper_dataset_files_or_hashes_missing", blockers)
        self.assertIn("figures_5_to_11_denominators_not_aligned", blockers)
        self.assertIn("explicit_lb_row_identity_fail_closed", blockers)
        self.assertIn("fast_scalar_routes_are_scalar_only_when_per_source_witness_exact_false", blockers)

        next_step = self.summary["next_recommendation"]
        self.assertTrue(next_step["strict_review_packet"])
        self.assertFalse(next_step["route_micro_optimization"])
        self.assertFalse(next_step["explicit_lb"])

    def test_builder_is_consolidation_only(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn(".run(", source)
        self.assertNotIn(".Popen(", source)


if __name__ == "__main__":
    unittest.main()
