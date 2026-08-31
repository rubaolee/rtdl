import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5428_level_b_matrix_with_water_bg_full_public.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5428_level_b_matrix_with_water_bg_full_public.py"
)


class Goal5428LevelBMatrixWithWaterBgFullPublicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_matrix_coverage_includes_full_public_geo_row(self) -> None:
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5428.level_b_matrix_with_water_bg_full_public.v1",
        )
        self.assertTrue(payload["matched"])
        coverage = payload["coverage"]
        self.assertEqual(coverage["graphics_case_count"], 3)
        self.assertEqual(coverage["graphics_route_result_count"], 6)
        self.assertEqual(coverage["bounded_geo_case_count"], 2)
        self.assertEqual(coverage["bounded_geo_route_result_count"], 2)
        self.assertEqual(coverage["full_public_geo_case_count"], 1)
        self.assertEqual(coverage["full_public_geo_route_result_count"], 1)
        self.assertEqual(coverage["total_case_count"], 6)
        self.assertEqual(coverage["total_route_result_count"], 9)

    def test_full_public_geo_row_is_level_b_not_figure5(self) -> None:
        rows = self.summary["full_public_geo_rows"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["case_id"], "geo_water_bg_full_public_paper_config")
        self.assertEqual(row["category"], "geo_full_public")
        self.assertEqual(row["input_identity_level"], "level_b_full_public_same_source_geo_not_exact_file_hash")
        self.assertEqual(row["author_denominator"], "goal5314_paper_config_n_points_cell_8")
        self.assertEqual(row["point_counts"], [22_824_823, 52_271_467])
        self.assertFalse(row["figure5_reproduction_claimed"])
        self.assertFalse(row["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(row["new_execution_claimed"])

    def test_full_public_geo_row_matches_with_declared_tolerance(self) -> None:
        row = self.summary["full_public_geo_rows"][0]
        self.assertAlmostEqual(row["author_hd_result"], 0.8964367508888245, places=12)
        self.assertAlmostEqual(row["rtdl_hd_result_float64"], 0.8964380566690101, places=12)
        self.assertAlmostEqual(row["abs_diff_vs_author"], 1.305780185645311e-06, places=15)
        self.assertLessEqual(row["abs_diff_vs_author"], row["tolerance"])
        self.assertTrue(row["matched_author"])
        self.assertTrue(row["per_source_witness_exact"])
        self.assertTrue(row["author_matches_paper_log"])
        self.assertTrue(row["distance_float32_matches_paper_log"])
        self.assertFalse(row["ratio_authorized"])

    def test_claim_boundary_and_next_recommendation(self) -> None:
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["level_b_same_pod_scalar_matrix_claimed"])
        self.assertTrue(boundary["full_public_geo_scalar_row_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_figure5_matrix_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])

        next_step = self.summary["next_recommendation"]
        self.assertTrue(next_step["strict_review_packet"])
        self.assertFalse(next_step["route_micro_optimization"])
        self.assertFalse(next_step["explicit_lb"])

    def test_remaining_blockers_are_visible(self) -> None:
        blockers = {row["blocker"] for row in self.summary["remaining_blockers"]}
        self.assertIn("exact_paper_dataset_files_or_hashes_missing", blockers)
        self.assertIn("figures_5_to_11_denominators_not_aligned", blockers)
        self.assertIn("fast_scalar_routes_are_scalar_only_when_per_source_witness_exact_false", blockers)
        self.assertIn("explicit_lb_row_identity_fail_closed", blockers)

    def test_builder_is_consolidation_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("hd_exec", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)


if __name__ == "__main__":
    unittest.main()
