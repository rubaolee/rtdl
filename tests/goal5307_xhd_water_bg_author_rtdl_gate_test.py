import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5307_water_bg_author_rtdl_partner_gate_summary_pod.json"
)
AUTHOR_JSON = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "goal5307_raw"
    / "author_water_bg_arcgis_bounded.json"
)
RAW_RTDL = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "goal5307_raw"
    / "rtdl_water_bg_arcgis_bounded_triton_summary_raw_goal5305_runner.json"
)


class Goal5307XhdWaterBgAuthorRtdlGateTest(unittest.TestCase):
    def _summary(self) -> dict:
        return json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_author_and_rtdl_match_on_same_bounded_water_bg_fixture(self) -> None:
        payload = self._summary()

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5307.water_bg_author_rtdl_partner_gate.v1",
        )
        self.assertEqual(
            payload["input"]["paper_pair"],
            "USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt",
        )
        self.assertEqual(payload["input"]["point_count_a"], 124)
        self.assertEqual(payload["input"]["point_count_b"], 894)
        self.assertEqual(payload["author"]["point_counts"], [124, 894])
        self.assertAlmostEqual(payload["author"]["HDResult"], 72.38665008544922, places=12)
        self.assertAlmostEqual(payload["rtdl"]["HDResult"], 72.38664516014835, places=12)
        self.assertLessEqual(payload["comparison"]["abs_diff"], payload["comparison"]["tolerance"])
        self.assertTrue(payload["comparison"]["matched"])

    def test_raw_author_and_rtdl_provenance_files_exist(self) -> None:
        payload = self._summary()

        self.assertTrue(AUTHOR_JSON.exists())
        self.assertTrue(RAW_RTDL.exists())
        self.assertEqual(
            payload["author"]["json"],
            "Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/author_water_bg_arcgis_bounded.json",
        )
        self.assertEqual(
            payload["rtdl"]["raw_runner_summary"],
            "Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/rtdl_water_bg_arcgis_bounded_triton_summary_raw_goal5305_runner.json",
        )

    def test_route_and_claim_boundary_are_bounded_only(self) -> None:
        payload = self._summary()
        rtdl = payload["rtdl"]

        self.assertEqual(rtdl["route"], "directed_max_of_nearest_distance_2d_partner_columns")
        self.assertEqual(rtdl["partner"], "triton")
        self.assertEqual(rtdl["triton_strategy"], "dense_point_nearest_tiled")
        self.assertEqual(rtdl["partner_reference_contract"], "generic_directed_max_of_nearest_distance_2d")
        self.assertEqual(rtdl["native_engine_row_contract"], "not_called_partner_reference_only")
        self.assertTrue(rtdl["per_source_witness_exact"])

        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["level_b_bounded_geo_correctness_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["geo_figure5_reproduction_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["author_performance_parity_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertIn("not Figure 5 reproduction", payload["boundary"])
        self.assertIn("not author RT-core equivalence", payload["boundary"])


if __name__ == "__main__":
    unittest.main()
