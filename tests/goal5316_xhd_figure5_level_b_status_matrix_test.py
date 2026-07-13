import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5316_figure5_level_b_status_matrix.json"
)


class Goal5316Figure5LevelBStatusMatrixTest(unittest.TestCase):
    def setUp(self):
        self.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.rows = {row["row_id"]: row for row in self.matrix["rows"]}

    def test_global_claim_boundary_forbids_figure5_and_ratio_claims(self):
        boundary = self.matrix["claim_boundary"]
        self.assertEqual(
            self.matrix["schema"],
            "rtdl.paper_reproduction.xhd.goal5316.figure5_level_b_status_matrix.v1",
        )
        self.assertFalse(boundary["figure5_reproduction_complete"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_complete"])
        self.assertFalse(boundary["full_paper_reproduction_complete"])
        self.assertFalse(boundary["author_vs_rtdl_performance_ratio_authorized"])
        self.assertTrue(boundary["level_b_status_matrix_claimed"])
        self.assertIn("Figure 5 is reproduced.", self.matrix["forbidden_summaries"])
        self.assertEqual(self.matrix["matrix_summary"]["rows_with_exact_paper_input_provenance"], [])
        self.assertEqual(self.matrix["matrix_summary"]["rows_with_denominator_aligned_performance_ratio"], [])

    def test_expected_row_set_and_primary_artifacts_exist(self):
        expected = {
            "graphics_dragon_happy_full_public",
            "graphics_dragon_asian_scaled_author_no_go",
            "graphics_thai_happy_scaled",
            "graphics_thai_asian_scaled",
            "geo_county_zcta_bounded",
            "geo_county_zcta_full_public_probe",
            "geo_water_bg_bounded",
            "geo_water_bg_full_public_corrected",
        }
        self.assertEqual(set(self.rows), expected)
        self.assertEqual(self.matrix["matrix_summary"]["row_count"], len(expected))
        for row in self.matrix["rows"]:
            for artifact in row["primary_artifacts"]:
                self.assertTrue((ROOT / artifact).exists(), artifact)

    def test_dragon_happy_is_level_b_exact_value_only_not_exact_dataset(self):
        row = self.rows["graphics_dragon_happy_full_public"]
        self.assertFalse(row["exact_paper_input_available"])
        self.assertTrue(row["same_source_public_candidate_available"])
        self.assertTrue(row["rtdl_scalar"]["matched_author_rerun"])
        self.assertAlmostEqual(
            row["rtdl_scalar"]["abs_diff_vs_author_rerun"],
            2.3848857610975216e-09,
            places=18,
        )
        self.assertTrue(row["rtdl_scalar"]["global_bound_early_break"])
        self.assertFalse(row["rtdl_scalar"]["per_source_witness_exact"])
        self.assertEqual(row["performance_denominator_status"], "not_aligned_no_ratio")
        self.assertIn("exact-value-only", row["allowed_claim"])

    def test_dragon_asian_author_precheck_is_no_go_before_rtdl_timing(self):
        row = self.rows["graphics_dragon_asian_scaled_author_no_go"]
        self.assertFalse(row["author_paper_config_scalar"]["matched_paper_log_within_tolerance"])
        self.assertAlmostEqual(
            row["author_paper_config_scalar"]["author_rerun_vs_paper_log_abs_diff"],
            8.715689182281494e-05,
            places=15,
        )
        self.assertFalse(row["rtdl_scalar"]["available"])
        self.assertEqual(
            row["performance_denominator_status"],
            "not_applicable_author_value_no_go",
        )

    def test_thai_graphics_rows_match_author_but_keep_witness_boundary(self):
        thai_happy = self.rows["graphics_thai_happy_scaled"]
        thai_asian = self.rows["graphics_thai_asian_scaled"]
        self.assertTrue(thai_happy["rtdl_scalar"]["matched_author_rerun"])
        self.assertTrue(thai_asian["rtdl_scalar"]["matched_author_rerun"])
        self.assertFalse(thai_happy["rtdl_scalar"]["fast_scalar_per_source_witness_exact"])
        self.assertFalse(thai_asian["rtdl_scalar"]["fast_scalar_per_source_witness_exact"])
        self.assertTrue(thai_happy["rtdl_scalar"]["exact_witness_per_source_witness_exact"])
        self.assertTrue(thai_asian["rtdl_scalar"]["exact_witness_per_source_witness_exact"])
        self.assertLess(thai_happy["rtdl_scalar"]["fast_scalar_route_wall_sec"], 2.0)
        self.assertGreater(
            thai_asian["rtdl_scalar"]["fast_scalar_route_wall_sec"],
            thai_asian["rtdl_scalar"]["exact_witness_route_wall_sec"],
        )

    def test_geo_bounded_rows_are_not_promoted_to_full_public(self):
        county = self.rows["geo_county_zcta_bounded"]
        water = self.rows["geo_water_bg_bounded"]
        for row in (county, water):
            self.assertTrue(row["bounded_fixture_available"])
            self.assertFalse(row["exact_paper_input_available"])
            self.assertFalse(row["same_source_public_candidate_available"])
            self.assertTrue(row["rtdl_scalar"]["matched_author"])
            self.assertEqual(row["performance_denominator_status"], "not_aligned_no_ratio")
            self.assertIn("Bounded", row["allowed_claim"])

    def test_county_zcta_full_public_probe_blocks_exact_claim(self):
        row = self.rows["geo_county_zcta_full_public_probe"]
        probe = row["input_probe"]
        self.assertFalse(row["exact_paper_input_available"])
        self.assertFalse(row["rtdl_scalar"]["available"])
        self.assertEqual(probe["county_point_count_delta"], 3039134)
        self.assertGreater(probe["county_point_count_relative_delta"], 0.32)
        self.assertEqual(
            row["performance_denominator_status"],
            "not_applicable_input_provenance_blocked",
        )
        self.assertIn("point count differs", row["allowed_claim"])

    def test_water_bg_full_public_corrected_denominator_and_numeric_boundary(self):
        row = self.rows["geo_water_bg_full_public_corrected"]
        author = row["author_paper_config_scalar"]
        rtdl = row["rtdl_scalar"]
        self.assertFalse(row["exact_paper_input_available"])
        self.assertTrue(row["same_source_public_candidate_available"])
        self.assertEqual(author["num_points_cell"], 8)
        self.assertTrue(author["matched_paper_log_with_paper_config"])
        self.assertAlmostEqual(author["author_paper_config_vs_paper_log_abs_diff"], 0.0)
        self.assertTrue(rtdl["matched_author_at_declared_tolerance"])
        self.assertFalse(rtdl["matches_at_1e_6"])
        self.assertEqual(rtdl["declared_tolerance"], 2e-06)
        self.assertAlmostEqual(
            rtdl["same_witness_float32_distance"],
            author["author_paper_config_n_points_cell_8_hd_result"],
        )
        self.assertIn("n_points_cell=8", row["allowed_claim"])


if __name__ == "__main__":
    unittest.main()
