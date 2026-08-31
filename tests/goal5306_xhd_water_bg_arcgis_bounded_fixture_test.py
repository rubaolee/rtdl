import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "data"
    / "generated"
    / "goal5306_arcgis_water_bg_bounded"
)
MANIFEST = FIXTURE_DIR / "manifest.json"
WATER_WKT = FIXTURE_DIR / "USADetailedWaterBodies_arcgis_bounded.wkt"
BLOCKGROUP_WKT = FIXTURE_DIR / "USACensusBlockGroupBoundaries_arcgis_bounded.wkt"


class Goal5306XhdWaterBgArcgisBoundedFixtureTest(unittest.TestCase):
    def _manifest(self) -> dict:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_records_second_figure5_wkt_pair_contract(self) -> None:
        payload = self._manifest()

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5306.arcgis_water_bg_bounded_fixture.v1",
        )
        self.assertEqual(payload["goal"], "Goal5306")
        self.assertEqual(
            payload["source_contract"]["paper_pair"],
            "USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt",
        )
        self.assertIn("USA_Detailed_Water_Bodies", payload["source_contract"]["waterbodies_service"])
        self.assertIn("USA_Census_BlockGroups", payload["source_contract"]["blockgroup_service"])
        self.assertEqual(payload["source_contract"]["query_order"], "OBJECTID")
        self.assertEqual(payload["source_contract"]["out_sr"], 4326)
        self.assertEqual(payload["author_loader_contract"]["input_type"], "wkt")
        self.assertEqual(payload["author_loader_contract"]["n_dims"], 2)
        self.assertFalse(payload["author_loader_contract"]["normalize"])
        self.assertTrue(payload["author_loader_contract"]["polygon_outer_ring_only_for_author_point_count"])

    def test_generated_wkt_hashes_counts_and_point_estimates_are_stable(self) -> None:
        payload = self._manifest()
        water = payload["outputs"]["waterbodies"]
        block = payload["outputs"]["blockgroups"]

        self.assertTrue(WATER_WKT.exists())
        self.assertTrue(BLOCKGROUP_WKT.exists())
        self.assertEqual(water["feature_count"], 5)
        self.assertEqual(block["feature_count"], 5)
        self.assertEqual(water["line_count"], 5)
        self.assertEqual(block["line_count"], 5)
        self.assertEqual(water["geometry_types"], {"Polygon": 5})
        self.assertEqual(block["geometry_types"], {"Polygon": 5})
        self.assertEqual(water["object_ids"], [1, 2, 3, 4, 5])
        self.assertEqual(block["object_ids"], [1, 2, 3, 4, 5])
        self.assertEqual(water["outer_ring_point_count_author_loader_estimate"], 124)
        self.assertEqual(block["outer_ring_point_count_author_loader_estimate"], 894)
        self.assertEqual(water["sha256"], "3dda7b9df0655e0070f129625c4cfb7ab9cb40b22c8b71da3994faf0283c1dcb")
        self.assertEqual(block["sha256"], "01ec10a1cdd3520f3bcc5742a6c7a6430c7e9dbe45f170ec35a5d70d4f7455b9")

    def test_claim_boundary_remains_fixture_only(self) -> None:
        payload = self._manifest()
        boundary = payload["claim_boundary"]

        self.assertTrue(boundary["level_b_same_source_fixture"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["geo_correctness_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(payload["comparison_readiness"]["author_hd_exec_ready"])
        self.assertFalse(payload["comparison_readiness"]["rtdl_route_ready"])


if __name__ == "__main__":
    unittest.main()
