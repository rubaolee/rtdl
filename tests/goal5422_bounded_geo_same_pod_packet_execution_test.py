import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5422_bounded_geo_same_pod_packet_execution.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5422_bounded_geo_same_pod_packet_execution.py"
)


class Goal5422BoundedGeoSamePodPacketExecutionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_packet_executed_two_bounded_geo_rows_and_matched(self):
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5422.bounded_geo_same_pod_packet_execution.v1",
        )
        self.assertEqual(payload["status"], "bounded_geo_same_pod_packet_executed__level_b_only_no_ratio")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual([row["case_id"] for row in payload["rows"]], ["county_zcta_bounded", "water_bg_bounded"])
        for row in payload["rows"]:
            self.assertEqual(row["input_identity_level"], "level_b_bounded_geo_fixture")
            self.assertTrue(row["comparison"]["matched"])
            self.assertLessEqual(row["comparison"]["abs_diff"], row["comparison"]["tolerance"])
            self.assertEqual(row["comparison"]["comparison_reference"], "directed_input1_to_input2")

    def test_expected_values_and_point_counts_are_preserved(self):
        rows = {row["case_id"]: row for row in self.summary["rows"]}
        county = rows["county_zcta_bounded"]
        self.assertEqual(county["point_counts"], [38034, 50272])
        self.assertAlmostEqual(county["author"]["HDResult"], 65.44752502441406, places=12)
        self.assertAlmostEqual(county["rtdl"]["HDResult"], 65.44751976280666, places=12)

        water = rows["water_bg_bounded"]
        self.assertEqual(water["point_counts"], [124, 894])
        self.assertAlmostEqual(water["author"]["HDResult"], 72.38665008544922, places=12)
        self.assertAlmostEqual(water["rtdl"]["HDResult"], 72.38664516014835, places=12)

    def test_route_family_and_denominators_are_explicit(self):
        for row in self.summary["rows"]:
            rtdl = row["rtdl"]
            self.assertEqual(rtdl["route"], "directed_max_of_nearest_distance_2d_partner_columns")
            self.assertEqual(rtdl["partner"], "triton")
            self.assertEqual(rtdl["triton_strategy"], "dense_point_nearest_tiled")
            self.assertEqual(rtdl["partner_reference_contract"], "generic_directed_max_of_nearest_distance_2d")
            self.assertEqual(rtdl["native_engine_row_contract"], "not_called_partner_reference_only")
            self.assertTrue(rtdl["per_source_witness_exact"])
            self.assertGreater(row["author"]["remote_process_wall_sec"], 0.0)
            self.assertGreater(row["rtdl"]["remote_process_wall_sec"], 0.0)
            self.assertGreater(rtdl["run_phases"]["rtdl_route_sec"], 0.0)
            self.assertGreater(rtdl["run_phases"]["total_sec"], 0.0)

        self.assertFalse(self.summary["denominator_policy"]["ratio_authorized"])

    def test_claim_boundary_blocks_overclaims(self):
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["bounded_geo_execution_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["geo_figure5_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])

    def test_raw_jsons_were_downloaded_and_runner_uses_wrapper(self):
        for row in self.summary["rows"]:
            self.assertTrue(Path(row["author"]["local_json"]).exists())
            self.assertTrue(Path(row["rtdl"]["local_json"]).exists())

        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("current_pod_ssh.py", source)
        self.assertNotIn("\"ssh\"", source)
        self.assertNotIn("'ssh'", source)


if __name__ == "__main__":
    unittest.main()
