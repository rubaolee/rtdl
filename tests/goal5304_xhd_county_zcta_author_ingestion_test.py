import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SUMMARY = APP / "results" / "xhd_goal5304_county_zcta_author_ingestion_summary_pod.json"
AUTHOR_JSON = APP / "results" / "goal5304_raw" / "author_county_zcta_arcgis_bounded.json"


class Goal5304CountyZctaAuthorIngestionTest(unittest.TestCase):
    def _summary(self) -> dict:
        return json.loads(SUMMARY.read_text(encoding="utf-8"))

    def _author(self) -> dict:
        return json.loads(AUTHOR_JSON.read_text(encoding="utf-8"))

    def test_author_ingestion_summary_reports_success_without_rtdl_claim(self) -> None:
        payload = self._summary()
        self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.goal5304.county_zcta_author_ingestion.v1")
        self.assertEqual(
            payload["status"],
            "author_hd_exec_ingested_goal5303_county_zcta_wkt__rtdl_not_run__level_b_only",
        )
        self.assertEqual(payload["author"]["returncode"], 0)
        self.assertIs(payload["readiness"]["author_hd_exec_ingestion_passed"], True)
        self.assertIs(payload["readiness"]["author_json_produced"], True)
        self.assertIs(payload["readiness"]["rtdl_route_run"], False)

        claims = payload["claim_boundary"]
        self.assertIs(claims["level_b_author_ingestion_claimed"], True)
        for key in (
            "rtdl_route_claimed",
            "author_rtdl_correctness_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "geo_correctness_claimed",
            "figure5_reproduction_claimed",
            "performance_ratio_claimed",
            "full_paper_reproduction_claimed",
        ):
            self.assertIs(claims[key], False, key)

    def test_author_json_matches_manifest_point_counts_and_hd_result(self) -> None:
        summary = self._summary()
        author = self._author()
        self.assertAlmostEqual(float(author["HDResult"]), 65.44752502441406)
        self.assertAlmostEqual(float(summary["author_result"]["HDResult"]), float(author["HDResult"]))
        self.assertEqual(author["Input"]["NumDims"], 2)
        self.assertIs(author["Input"]["Normalize"], False)
        self.assertEqual([row["NumPoints"] for row in author["Input"]["Files"]], [38034, 50272])
        self.assertEqual(summary["author_result"]["input_point_counts"], [38034, 50272])
        self.assertEqual(summary["input_fixture"]["county"]["goal5303_author_loader_point_estimate"], 38034)
        self.assertEqual(summary["input_fixture"]["zipcode"]["goal5303_author_loader_point_estimate"], 50272)
        self.assertAlmostEqual(float(author["Running"]["AvgTime"]), 6.169)

    def test_command_and_fixture_caveat_are_preserved(self) -> None:
        payload = self._summary()
        command = payload["author"]["command"]
        self.assertIn("-input_type", command)
        self.assertIn("wkt", command)
        self.assertIn("-n_dims", command)
        self.assertIn("2", command)
        self.assertIn("-normalize=false", command)
        self.assertIn("-check=false", command)
        self.assertIn("-overwrite=true", command)
        self.assertIn("Alabama", payload["input_fixture"]["fixture_caveat"])
        self.assertIn("Alaska", payload["input_fixture"]["fixture_caveat"])
        self.assertIn("not geographic representativeness", payload["input_fixture"]["fixture_caveat"])


if __name__ == "__main__":
    unittest.main()
