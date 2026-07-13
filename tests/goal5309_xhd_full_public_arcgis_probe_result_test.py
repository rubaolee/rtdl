import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json"
)


class Goal5309XhdFullPublicArcgisProbeResultTest(unittest.TestCase):
    def _summary(self) -> dict:
        return json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_all_four_full_public_services_completed(self) -> None:
        payload = self._summary()
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5309.full_public_arcgis_point_count_mbr_probe.summary.v1",
        )
        services = payload["services"]
        self.assertEqual(set(services), {"county", "zcta", "waterbodies", "blockgroups"})
        for service in services.values():
            self.assertTrue(service["complete"])
            self.assertEqual(service["features_seen"], service["service_feature_count"])
            self.assertLess(service["max_abs_mbr_delta"], 1.0e-5)

    def test_county_zcta_pair_is_not_exact_because_county_point_count_mismatches(self) -> None:
        services = self._summary()["services"]

        county = services["county"]
        self.assertEqual(county["author_loader_point_count"], 12_477_179)
        self.assertEqual(county["paper_point_count"], 9_438_045)
        self.assertEqual(county["point_count_delta"], 3_039_134)
        self.assertGreater(county["point_count_relative_delta"], 0.32)
        self.assertEqual(county["classification"], "extent_match_point_count_mismatch_not_exact")

        zcta = services["zcta"]
        self.assertEqual(zcta["author_loader_point_count"], 43_984_131)
        self.assertEqual(zcta["paper_point_count"], 43_952_878)
        self.assertEqual(zcta["point_count_delta"], 31_253)
        self.assertLess(zcta["point_count_relative_delta"], 0.001)

        decision = self._summary()["pair_decisions"]["county_zcta"]
        self.assertEqual(
            decision["classification"],
            "full_public_candidate_but_not_exact_due_county_point_count_mismatch",
        )

    def test_waterbodies_blockgroups_pair_is_strong_full_public_candidate_but_not_exact(self) -> None:
        services = self._summary()["services"]

        water = services["waterbodies"]
        self.assertEqual(water["author_loader_point_count"], 22_824_823)
        self.assertEqual(water["paper_point_count"], 22_818_694)
        self.assertEqual(water["point_count_delta"], 6_129)
        self.assertLess(water["point_count_relative_delta"], 0.001)

        blockgroups = services["blockgroups"]
        self.assertEqual(blockgroups["author_loader_point_count"], 52_271_467)
        self.assertEqual(blockgroups["paper_point_count"], 52_271_340)
        self.assertEqual(blockgroups["point_count_delta"], 127)
        self.assertLess(blockgroups["point_count_relative_delta"], 1.0e-5)

        decision = self._summary()["pair_decisions"]["waterbodies_blockgroups"]
        self.assertEqual(
            decision["classification"],
            "strong_full_public_candidate_not_exact_without_file_hash",
        )

    def test_claim_boundary_blocks_exact_figure5_and_performance_claims(self) -> None:
        boundary = self._summary()["claim_boundary"]
        self.assertTrue(boundary["full_public_input_candidate_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["geo_figure5_reproduction_claimed"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()
