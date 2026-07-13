import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5318_water_bg_exact_provenance_search.json"
)


class Goal5318WaterBgExactProvenanceSearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_search_keeps_exact_and_figure5_claims_false(self):
        boundary = self.data["claim_boundary"]
        self.assertTrue(boundary["provenance_search_complete"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_complete"])
        self.assertFalse(boundary["figure5_reproduction_complete"])
        self.assertFalse(boundary["full_paper_reproduction_complete"])
        self.assertFalse(boundary["author_vs_rtdl_performance_ratio_authorized"])
        self.assertFalse(boundary["new_author_or_rtdl_performance_run"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])

        decision = self.data["decision"]
        self.assertEqual(
            decision["exit_label"],
            "water_bg_exact_provenance_not_found_keep_level_b",
        )
        self.assertFalse(decision["water_bg_exact_paper_dataset_reproduction_claimed"])
        self.assertTrue(decision["water_bg_remains_best_geo_level_b_candidate"])

    def test_local_wkt_hashes_and_point_deltas_are_carried_forward(self):
        local = self.data["local_full_public_wkt_candidate"]
        water = local["waterbodies"]
        blockgroups = local["blockgroups"]

        self.assertEqual(
            water["sha256"],
            "0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39",
        )
        self.assertEqual(
            blockgroups["sha256"],
            "8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e",
        )

        self.assertEqual(water["paper_point_count"], 22_818_694)
        self.assertEqual(water["author_loader_point_count"], 22_824_823)
        self.assertEqual(water["point_count_delta"], 6_129)

        self.assertEqual(blockgroups["paper_point_count"], 52_271_340)
        self.assertEqual(blockgroups["author_loader_point_count"], 52_271_467)
        self.assertEqual(blockgroups["point_count_delta"], 127)

    def test_arcgis_metadata_is_same_source_not_exact_provenance(self):
        arcgis = self.data["arcgis_metadata"]

        water = arcgis["waterbodies"]
        self.assertEqual(water["service_item_id"], "48c77cbde9a0470fb371f8c8a8a7421a")
        self.assertIn("National Hydrography", water["service"]["copyrightText"])
        self.assertTrue(water["service"]["hasStaticData"])
        self.assertEqual(water["layer"]["objectIdField"], "OBJECTID")
        self.assertIsNotNone(water["linked_layer_package"])
        self.assertEqual(water["linked_layer_package"]["type"], "Layer Package")

        blockgroups = arcgis["blockgroups"]
        self.assertEqual(
            blockgroups["service_item_id"], "2f5e592494d243b0aa5c253e75e792a4"
        )
        self.assertIn("U.S. Census", blockgroups["service"]["description"])
        self.assertFalse(blockgroups["service"]["hasStaticData"])
        self.assertEqual(blockgroups["layer"]["objectIdField"], "OBJECTID")
        self.assertIn("dataLastEditDate", blockgroups["layer"]["editingInfoIso"])

        findings = self.data["provenance_findings"]
        self.assertTrue(findings["service_metadata_supports_same_source_candidate"])
        self.assertFalse(findings["service_metadata_supports_exact_claim"])
        self.assertFalse(findings["arcgis_current_snapshot_exact_equivalence_proven"])

    def test_author_hashes_and_byte_identical_regeneration_are_not_found(self):
        findings = self.data["provenance_findings"]

        self.assertFalse(findings["author_waterbodies_wkt_file_found"])
        self.assertFalse(findings["author_blockgroups_wkt_file_found"])
        self.assertFalse(findings["author_waterbodies_wkt_sha256_found"])
        self.assertFalse(findings["author_blockgroups_wkt_sha256_found"])
        self.assertFalse(findings["byte_identical_regeneration_proven"])
        self.assertFalse(findings["external_review_accepts_public_snapshot_as_exact"])

        why = "\n".join(findings["why_not_exact"])
        self.assertIn("No author-provided WKT files", why)
        self.assertIn("point-count deltas", why)
        self.assertIn("RayJoin", why)

    def test_value_evidence_remains_level_b_supporting_context(self):
        value = self.data["paper_config_value_evidence"]
        self.assertEqual(value["author_paper_config_hd_result"], 0.8964367508888245)
        self.assertEqual(value["paper_log_hd_result"], 0.8964367508888245)
        self.assertEqual(value["author_num_points_cell"], 8)
        self.assertEqual(value["same_witness_float32"], 0.8964367508888245)
        self.assertAlmostEqual(
            value["rtdl_exact_witness_float64"],
            0.8964380566690101,
        )
        self.assertEqual(value["declared_tolerance"], 2e-6)

    def test_related_rayjoin_assets_are_not_promoted_to_xhd_wkt_provenance(self):
        related = self.data["related_prior_assets"]
        self.assertTrue(related["rayjoin_cdb_assets_found"])
        self.assertEqual(related["status"], "related_not_exact_xhd_wkt_provenance")
        self.assertIn("CDB", related["reason"])


if __name__ == "__main__":
    unittest.main()
