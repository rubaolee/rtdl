from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5320_county_zcta_source_conversion_investigation.json"
)


class Goal5320CountyZctaSourceConversionInvestigationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_goal5320_keeps_claim_boundary_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertTrue(boundary["source_conversion_investigation_claimed"])

    def test_county_public_candidates_do_not_match_paper_count(self) -> None:
        candidates = {
            row["candidate_id"]: row for row in self.payload["county_candidates"]
        }
        paper = self.payload["paper_target"]["author_log_points"]["dtl_cnty.wkt"]
        self.assertEqual(paper, 9_438_045)

        arcgis = candidates["arcgis_usa_census_counties_current_service"]
        self.assertEqual(arcgis["author_loader_point_count"], 12_477_179)
        self.assertEqual(arcgis["point_count_delta"], 3_039_134)
        self.assertGreater(arcgis["relative_delta"], 0.32)
        self.assertEqual(
            arcgis["classification"], "not_exact__too_many_points_current_service"
        )

        tiger_all = candidates["census_tiger2023_county_direct_zip_all_records"]
        self.assertEqual(tiger_all["points_all_parts"], 8_201_082)
        self.assertLess(tiger_all["point_count_delta"], 0)
        self.assertEqual(
            tiger_all["classification"],
            "not_exact__too_few_points_and_extent_includes_territories",
        )

        tiger_50dc = candidates[
            "census_tiger2023_county_direct_zip_50_states_dc_filter"
        ]
        self.assertEqual(tiger_50dc["records"], 3_144)
        self.assertEqual(tiger_50dc["points_all_parts"], 8_081_061)
        self.assertLess(tiger_50dc["relative_delta"], -0.14)
        self.assertEqual(
            tiger_50dc["classification"],
            "not_exact__same_feature_count_as_arcgis_but_too_few_points",
        )

    def test_related_rayjoin_cdb_is_not_xhd_wkt_provenance(self) -> None:
        cdb = {
            row["candidate_id"]: row for row in self.payload["county_candidates"]
        }["prior_rayjoin_dtl_cnty_point_cdb"]
        self.assertEqual(cdb["points"], 17_325_792)
        self.assertEqual(
            cdb["classification"],
            "related_rayjoin_topology_not_xhd_wkt_provenance",
        )
        self.assertNotEqual(cdb["points"], 9_438_045)

    def test_zcta_is_near_count_but_not_exact_and_not_primary_blocker(self) -> None:
        zcta = self.payload["zcta_context"][
            "arcgis_usa_zip_code_areas_current_service"
        ]
        self.assertEqual(zcta["paper_point_count"], 43_952_878)
        self.assertEqual(zcta["author_loader_point_count"], 43_984_131)
        self.assertLess(zcta["relative_delta"], 0.001)
        self.assertEqual(
            zcta["classification"],
            "near_paper_count_but_no_hash__not_primary_blocker",
        )

    def test_exit_label_and_forbidden_claims(self) -> None:
        self.assertEqual(
            self.payload["exit_label"],
            "county_zcta_exact_provenance_not_found__source_conversion_blocked",
        )
        forbidden = "\n".join(self.payload["not_allowed"])
        self.assertIn("claim County-ZCTA exact paper input recovery", forbidden)
        self.assertIn("claim current ArcGIS County service is an exact author input", forbidden)
        self.assertIn("claim direct TIGER2023 County is an exact author input", forbidden)
        self.assertIn("claim old RayJoin CDB is X-HD WKT provenance", forbidden)
        self.assertIn("performance ratio", forbidden)

    def test_no_pod_expected_for_source_investigation(self) -> None:
        pod = self.payload["pod_usage"]
        self.assertFalse(pod["used"])
        self.assertFalse(pod["expected_next"])


if __name__ == "__main__":
    unittest.main()
