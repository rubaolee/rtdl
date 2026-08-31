import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json"
)


class Goal5317Figure5ExactInputGapMatrixTest(unittest.TestCase):
    def setUp(self):
        self.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.rows = {row["row_id"]: row for row in self.matrix["rows"]}

    def test_global_boundary_keeps_goal_as_acquisition_plan_not_reproduction(self):
        boundary = self.matrix["claim_boundary"]
        self.assertEqual(
            self.matrix["schema"],
            "rtdl.paper_reproduction.xhd.goal5317.figure5_exact_input_acquisition_gap_matrix.v1",
        )
        self.assertFalse(boundary["figure5_reproduction_complete"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_complete"])
        self.assertFalse(boundary["full_paper_reproduction_complete"])
        self.assertFalse(boundary["author_vs_rtdl_performance_ratio_authorized"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertTrue(boundary["dataset_acquisition_plan_claimed"])

    def test_all_input_references_exist(self):
        for ref in self.matrix["inputs"]:
            self.assertTrue((ROOT / ref).exists(), ref)

    def test_exact_dataset_rule_rejects_statistics_and_hdresult_only(self):
        rule = self.matrix["exact_dataset_rule"]
        self.assertIn("author-provided input files or archives", rule["level_c_requires_one_of"])
        self.assertIn("matching point counts", rule["not_sufficient"])
        self.assertIn("matching MBRs", rule["not_sufficient"])
        self.assertIn("matching HDResult alone", rule["not_sufficient"])
        self.assertIn("paper-log path names without bytes or hashes", rule["not_sufficient"])

    def test_expected_rows_and_no_exact_status_anywhere(self):
        expected = {
            "brats2020_validation",
            "graphics_stanford",
            "geo_county_zcta",
            "geo_waterbodies_blockgroups",
            "geo_osm_lakes_parks_allnodes",
        }
        self.assertEqual(set(self.rows), expected)
        for row in self.rows.values():
            self.assertNotEqual(row["exact_input_status"], "available")
            self.assertNotIn("Figure-5 reproduction", row.get("current_level", ""))

    def test_graphics_row_keeps_level_b_and_dragon_asian_no_go(self):
        row = self.rows["graphics_stanford"]
        self.assertEqual(row["current_level"], "level_b_public_same_source_candidates")
        self.assertEqual(row["exact_input_status"], "not_proven")
        self.assertIn("dragon.ply -> happy_buddha.ply", row["value_matched_level_b_pairs"])
        self.assertIn("dragon.ply -> asian_dragon_scaled_1e-3.ply", row["no_go_pairs"])
        missing = " ".join(row["missing_for_exact"])
        self.assertIn("hashes or bytes", missing)
        self.assertIn("Stanford public files are exact paper inputs", row["forbidden_claim"])

    def test_geo_county_zcta_blocks_route_work_on_point_count_mismatch(self):
        row = self.rows["geo_county_zcta"]
        probe = row["full_public_probe"]
        self.assertEqual(row["exact_input_status"], "blocked")
        self.assertEqual(row["level_b_status"], "bounded_match_only")
        self.assertEqual(probe["county_point_count_delta"], 3039134)
        self.assertGreater(probe["county_relative_delta"], 0.32)
        self.assertIn("alternate County source", row["candidate_next_action"])
        self.assertIn("point-count no-go", row["why_not_next_default"])

    def test_water_bg_is_ranked_first_but_not_exact(self):
        row = self.rows["geo_waterbodies_blockgroups"]
        probe = row["full_public_probe"]
        self.assertEqual(row["exact_input_status"], "not_proven")
        self.assertEqual(row["level_b_status"], "strongest_geo_candidate")
        self.assertEqual(probe["waterbodies_point_count_delta"], 6129)
        self.assertEqual(probe["blockgroups_point_count_delta"], 127)
        evidence = " ".join(row["available_evidence"])
        self.assertIn("Goal5313 author rerun with n_points_cell=8", evidence)
        self.assertIn("Goal5314 RTDL exact-witness", evidence)
        self.assertIn("exact snapshots", " ".join(row["missing_for_exact"]))
        self.assertEqual(self.matrix["ranked_next_actions"][0]["row_id"], "geo_waterbodies_blockgroups")
        self.assertEqual(self.matrix["recommended_next_goal"]["goal"], "Goal5318")

    def test_brats_and_osm_are_not_immediate_route_targets(self):
        brats = self.rows["brats2020_validation"]
        osm = self.rows["geo_osm_lakes_parks_allnodes"]
        self.assertFalse(brats["pod_expected"])
        self.assertFalse(osm["pod_expected"])
        self.assertIn("Access/licensing", brats["why_not_next_default"])
        self.assertIn("No snapshot/filter provenance", osm["why_not_next_default"])


if __name__ == "__main__":
    unittest.main()
