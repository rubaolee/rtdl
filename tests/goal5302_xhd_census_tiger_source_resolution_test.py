import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MATRIX_PATH = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5302_census_tiger_source_resolution_plan_2026-07-09.json"
)


class Goal5302XhdCensusTigerSourceResolutionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with MATRIX_PATH.open("r", encoding="utf-8") as handle:
            cls.matrix = json.load(handle)

    def test_author_geo_contract_is_extracted_from_scripts_and_logs(self):
        contract = self.matrix["author_geo_contract"]
        pairs = {(item["input1"], item["input2"]) for item in contract["run_fig5_geo_pairs"]}
        self.assertIn(("dtl_cnty.wkt", "uszipcode.wkt"), pairs)
        self.assertIn(
            ("USADetailedWaterBodies.wkt", "USACensusBlockGroupBoundaries.wkt"),
            pairs,
        )

        for item in contract["run_fig5_geo_pairs"]:
            self.assertEqual(item["input_type"], "wkt")
            self.assertEqual(item["n_dims"], 2)
            self.assertFalse(item["normalize"])

        loader = contract["wkt_loader_semantics"]
        self.assertIn("MULTIPOLYGON", loader["accepted_geometry_prefixes"])
        self.assertIn("outer ring vertices only", loader["polygon_handling"])
        self.assertIn("author loader point counts", loader["implication"])

    def test_official_source_probes_include_county_zcta_and_sharded_bg_water(self):
        probes = {item["url"]: item for item in self.matrix["head_probe_results"]}
        self.assertEqual(
            probes[
                "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
            ]["status"],
            200,
        )
        self.assertEqual(
            probes[
                "https://www2.census.gov/geo/tiger/TIGER2023/ZCTA520/tl_2023_us_zcta520.zip"
            ]["status"],
            200,
        )
        self.assertEqual(
            probes[
                "https://www2.census.gov/geo/tiger/TIGER2023/BG/tl_2023_01_bg.zip"
            ]["status"],
            200,
        )
        self.assertEqual(
            probes[
                "https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/tl_2023_01001_areawater.zip"
            ]["status"],
            200,
        )
        self.assertEqual(
            probes[
                "https://www2.census.gov/geo/tiger/TIGER2023/BG/tl_2023_us_bg.zip"
            ]["status"],
            "timeout",
        )

    def test_dataset_resolution_keeps_exact_and_level_b_boundaries(self):
        datasets = {item["author_basename"]: item for item in self.matrix["dataset_resolution"]}

        county = datasets["dtl_cnty.wkt"]
        self.assertEqual(county["author_log_points"], 9438045)
        self.assertIn("TIGER2023", county["preferred_level_b_candidate"])
        self.assertIn("ArcGIS", county["alternative_name_matched_source"])

        zipcode = datasets["uszipcode.wkt"]
        self.assertEqual(zipcode["author_log_points"], 43952878)
        self.assertIn("ZCTA520", zipcode["preferred_level_b_candidate"])
        self.assertIn("ZCTA vs commercial ZIP boundary distinction", zipcode["unresolved"])

        water = datasets["USADetailedWaterBodies.wkt"]
        self.assertIn("AREAWATER", water["official_tiger_alternative_pattern"])
        self.assertIn("ArcGIS vs TIGER source identity", water["unresolved"])

        block_group = datasets["USACensusBlockGroupBoundaries.wkt"]
        self.assertIn("<state_fips>", block_group["preferred_url_pattern"])
        self.assertIn("national aggregation of state BG shards", block_group["unresolved"])

    def test_first_executable_candidate_and_forbidden_claims_are_explicit(self):
        conversion = self.matrix["conversion_plan"]
        self.assertEqual(
            conversion["first_executable_candidate"],
            "dtl_cnty.wkt -> uszipcode.wkt from TIGER2023 COUNTY + ZCTA520 or name-matched ArcGIS exports",
        )
        self.assertEqual(
            conversion["first_gate_type"],
            "Level-B same-source representative only, not exact paper dataset reproduction",
        )

        decisions = self.matrix["decisions"]
        self.assertEqual(
            decisions["recommended_next_goal"],
            "Goal5303_county_zcta_conversion_probe_plan_or_bounded_fixture",
        )
        self.assertTrue(decisions["do_not_run_pod_yet"])
        self.assertTrue(decisions["do_not_claim_exact"])

        boundary = self.matrix["claim_boundary"]
        self.assertFalse(boundary["executable_input_artifact_created"])
        self.assertFalse(boundary["author_rtdl_geo_comparison_claimed"])
        self.assertIn("Geo Figure 5 is reproduced", boundary["forbidden_summaries"])


if __name__ == "__main__":
    unittest.main()
