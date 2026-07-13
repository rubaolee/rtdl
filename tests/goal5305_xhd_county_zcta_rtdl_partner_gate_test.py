import json
import math
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5305_county_zcta_rtdl_triton_summary_pod.json"
)


class Goal5305XhdCountyZctaRtdlPartnerGateTest(unittest.TestCase):
    def test_pod_summary_matches_author_on_same_bounded_wkt_fixture(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5305.county_zcta_rtdl_partner_gate.v2",
        )
        self.assertEqual(payload["input"]["input_type"], "wkt")
        self.assertEqual(payload["input"]["n_dims"], 2)
        self.assertEqual(payload["input"]["point_count_a"], 38034)
        self.assertEqual(payload["input"]["point_count_b"], 50272)

        self.assertEqual(payload["author"]["comparison_reference"], "directed_input1_to_input2")
        self.assertAlmostEqual(payload["author"]["HDResult"], 65.44752502441406, places=12)
        self.assertAlmostEqual(payload["rtdl"]["HDResult"], 65.44751976280666, places=12)
        self.assertLessEqual(payload["author"]["abs_diff"], payload["author"]["tolerance"])
        self.assertTrue(payload["author"]["matched"])
        self.assertTrue(payload["claim_boundary"]["level_b_bounded_geo_correctness_claimed"])

    def test_route_is_generic_partner_reference_not_author_rt_core_or_performance_claim(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        rtdl = payload["rtdl"]

        self.assertEqual(rtdl["route"], "directed_max_of_nearest_distance_2d_partner_columns")
        self.assertEqual(rtdl["partner"], "triton")
        self.assertEqual(rtdl["triton_strategy"], "dense_point_nearest_tiled")
        self.assertEqual(rtdl["native_engine_row_contract"], "not_called_partner_reference_only")
        self.assertEqual(
            rtdl["partner_reference_contract"],
            "generic_directed_max_of_nearest_distance_2d",
        )
        self.assertTrue(rtdl["per_source_witness_exact"])
        self.assertFalse(rtdl["rt_core_speedup_claim_authorized"])
        self.assertFalse(rtdl["whole_app_speedup_claim_authorized"])

        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["geo_figure5_reproduction_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["author_performance_parity_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertIn("not the author X-HD RT-core algorithm", payload["boundary"])
        self.assertIn("not a performance-ratio denominator", payload["boundary"])

    def test_phase_numbers_are_present_but_not_used_as_author_ratio(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        phases = payload["run_phases"]

        self.assertGreater(phases["load_input_sec"], 0.0)
        self.assertGreater(phases["partner_column_upload_sec"], 0.0)
        self.assertGreater(phases["rtdl_route_sec"], 0.0)
        self.assertGreater(phases["total_sec"], 0.0)
        self.assertTrue(math.isfinite(phases["rtdl_route_sec"]))
        self.assertFalse(payload["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
