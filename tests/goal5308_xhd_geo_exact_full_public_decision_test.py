import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5308_geo_exact_full_public_decision_2026-07-09.json"
)


class Goal5308XhdGeoExactFullPublicDecisionTest(unittest.TestCase):
    def _summary(self) -> dict:
        return json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_exact_geo_files_are_still_missing(self) -> None:
        payload = self._summary()

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5308.geo_exact_full_public_decision.v1",
        )
        self.assertEqual(
            payload["status"],
            "exact_geo_wkt_files_missing__bounded_level_b_complete__full_public_probe_required",
        )
        probe = payload["exact_file_probe"]
        self.assertFalse(probe["local_generated_exact_files"])
        self.assertFalse(probe["pod_exact_paths_found"])
        self.assertFalse(probe["known_author_paths_available_on_current_pod"])
        self.assertEqual(probe["known_author_paths_root"], "/local/storage/shared/HDDatasets/geo")

    def test_paper_log_geo_point_counts_are_much_larger_than_bounded_fixtures(self) -> None:
        payload = self._summary()
        pairs = {item["file_name"]: item for item in payload["paper_log_geo_pairs"]}

        county = pairs["dtl_cnty.wkt_uszipcode.wkt.json"]
        self.assertEqual([f["num_points"] for f in county["input_files"]], [9438045, 43952878])
        self.assertAlmostEqual(county["paper_log_hd_result"], 0.4093780517578125, places=12)

        water = pairs["USADetailedWaterBodies.wkt_USACensusBlockGroupBoundaries.wkt.json"]
        self.assertEqual([f["num_points"] for f in water["input_files"]], [22818694, 52271340])
        self.assertAlmostEqual(water["paper_log_hd_result"], 0.8964367508888245, places=12)

        bounded = {item["pair"]: item for item in payload["bounded_level_b_current_evidence"]}
        self.assertEqual(bounded["dtl_cnty.wkt -> uszipcode.wkt"]["bounded_point_counts"], [38034, 50272])
        self.assertEqual(
            bounded["USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt"][
                "bounded_point_counts"
            ],
            [124, 894],
        )

    def test_decision_keeps_bounded_evidence_bounded_and_names_next_gate(self) -> None:
        payload = self._summary()
        decision = payload["decision"]

        self.assertTrue(decision["level_b_bounded_geo_packet_ready_for_review"])
        self.assertTrue(decision["level_c_exact_paper_geo_reproduction_blocked"])
        self.assertIn("Exact paper WKT files", decision["blocker"])
        self.assertEqual(
            decision["next_allowed_goal"],
            "full_public_arcgis_point_count_mbr_probe_before_any_figure5_claim",
        )

        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["bounded_level_b_complete_for_two_geo_pair_names"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["geo_figure5_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()
