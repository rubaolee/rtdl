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
    / "xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json"
)


class Goal5321OsmLakesParksAllNodesProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_claim_boundary_remains_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["figure7_reproduction_claimed"])
        self.assertFalse(boundary["figure10_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertTrue(boundary["provenance_search_claimed"])

    def test_author_lakes_parks_log_values_are_recorded(self) -> None:
        target = self.payload["paper_targets"]["lakes_parks"]
        self.assertEqual(target["paper_pair"], "lakes.bz2.wkt -> parks.bz2.wkt")
        self.assertEqual(target["author_log_records"], 5)
        self.assertEqual(target["author_log_hdresult"], 55.734275817871094)
        self.assertEqual(target["author_log_point_counts"], [301_704_289, 403_688_408])
        self.assertIn("rt_gpu", target["sections_present"])

    def test_spatialhadoop_public_catalog_is_not_exact_provenance(self) -> None:
        page = self.payload["public_catalog"]["spatialhadoop_datasets_page"]
        self.assertTrue(page["available"])
        self.assertEqual(
            page["classification"],
            "public_source_available_but_snapshot_hash_filter_and_author_conversion_identity_absent",
        )
        new_osm = page["openstreetmap_new_datasets"]
        self.assertEqual(new_osm["all_nodes"]["records"], "2.7 Billion records")
        self.assertEqual(new_osm["lakes"]["records"], "8.4M records")
        self.assertEqual(new_osm["parks"]["records"], "10M records")
        old_osm = page["openstreetmap_old_datasets"]
        self.assertEqual(old_osm["all_nodes"]["records"], "1.7 Billion points")
        self.assertEqual(old_osm["lakes"]["records"], "4.3M Polygons")
        self.assertEqual(old_osm["parks"]["records"], "234K Polygons")

    def test_prior_overpass_work_is_only_bounded_analogue(self) -> None:
        analogue = self.payload["prior_bounded_analogue"]["goal54_lkau_pkau"]
        self.assertEqual(analogue["status"], "bounded_live_overpass_australia_analogue_only")
        self.assertEqual(analogue["lakes_source_elements"], 280)
        self.assertEqual(analogue["parks_source_elements"], 264)
        rejected = "\n".join(analogue["not_accepted_as"])
        self.assertIn("continent-scale", rejected)
        self.assertIn("exact SpatialHadoop", rejected)

    def test_exit_label_and_blockers(self) -> None:
        self.assertEqual(
            self.payload["exit_label"],
            "osm_lakes_parks_allnodes_exact_provenance_not_found__snapshot_filter_blocked",
        )
        blockers = "\n".join(self.payload["blocking_gaps"])
        self.assertIn("No author lakes.bz2.wkt", blockers)
        self.assertIn("No author hashes", blockers)
        self.assertIn("No OSM planet snapshot date", blockers)

    def test_forbidden_claims_and_pod_expectation(self) -> None:
        forbidden = "\n".join(self.payload["not_allowed"])
        self.assertIn("claiming OSM Lakes/Parks/AllNodes exact", forbidden)
        self.assertIn("SpatialHadoop public catalog entries", forbidden)
        self.assertIn("bounded Overpass analogues", forbidden)
        self.assertIn("performance ratio", forbidden)
        pod = self.payload["pod_usage"]
        self.assertFalse(pod["used"])
        self.assertFalse(pod["expected_next"])


if __name__ == "__main__":
    unittest.main()
