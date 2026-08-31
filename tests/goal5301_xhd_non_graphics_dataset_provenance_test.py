import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MATRIX_PATH = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json"
)


class Goal5301XhdNonGraphicsDatasetProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with MATRIX_PATH.open("r", encoding="utf-8") as handle:
            cls.matrix = json.load(handle)

    def test_exact_dataset_rule_rejects_statistics_as_exact_identity(self):
        rule = self.matrix["exact_dataset_rule"]
        self.assertFalse(rule["count_or_gini_match_is_sufficient"])
        self.assertIn("actual dataset file hash provenance", rule["exact_requires"])
        self.assertIn("Level-B same-source representative", rule["public_reconstruction_without_hash_is_level"])

    def test_non_graphics_family_priorities_and_blockers_are_explicit(self):
        families = {item["family_id"]: item for item in self.matrix["families"]}

        brats = families["brats_2020"]
        self.assertEqual(brats["access_status"], "registration_or_license_required")
        self.assertEqual(brats["current_pod_assets"], "absent")
        self.assertIn("author_image_list", brats["exact_paper_identity_status"])

        census = families["census_tiger_geo"]
        self.assertEqual(census["priority"], "highest_non_graphics_next")
        self.assertEqual(census["access_status"], "public_source_likely_available")
        self.assertIn("WKT conversion", census["next_action"])
        self.assertFalse(census["pod_needed_now"])

        osm = families["osm_geospatial"]
        self.assertEqual(osm["priority"], "defer_until_census_tiger_resolved")
        self.assertIn("snapshot", osm["exact_paper_identity_status"])
        self.assertFalse(osm["pod_needed_now"])

    def test_pod_is_not_the_current_blocker_for_non_graphics_inputs(self):
        scope = self.matrix["scope"]
        self.assertFalse(scope["this_goal_uses_pod"])
        self.assertIn("input provenance", scope["reason_no_pod"])

        blocked = self.matrix["figure_paths_blocked"]
        self.assertFalse(blocked["pod_root_exists"])
        self.assertEqual(blocked["pod_root"], "/local/storage/shared/HDDatasets")
        self.assertIn("geo/all_nodes.wkt", blocked["figure10_required"])

    def test_claim_boundary_forbids_full_reproduction_or_ratios(self):
        boundary = self.matrix["claim_boundary"]
        self.assertFalse(boundary["claims_full_paper_reproduction"])
        self.assertFalse(boundary["claims_exact_dataset_recovery"])
        self.assertFalse(boundary["claims_performance_ratio"])
        self.assertIn("Count/Gini matching proves exact paper inputs", boundary["forbidden_summaries"])

        decisions = self.matrix["decisions"]
        self.assertFalse(decisions["full_paper_reproduction_complete"])
        self.assertFalse(decisions["exact_paper_datasets_available"])
        self.assertEqual(
            decisions["non_graphics_next_goal"],
            "Goal5302_census_tiger_public_source_resolution_plan",
        )


if __name__ == "__main__":
    unittest.main()
