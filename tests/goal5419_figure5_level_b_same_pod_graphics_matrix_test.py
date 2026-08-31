import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json"
)
RUNNER = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.py"
)


class Goal5419Figure5LevelBMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_matrix_executed_and_keeps_claim_boundary(self):
        payload = self.summary
        self.assertTrue(payload["matched"])
        self.assertTrue(payload["same_pod_execution_claimed"])
        self.assertEqual(payload["matrix_rows_executed"], 3)
        self.assertEqual(payload["route_result_count"], 6)
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])

    def test_graphics_cases_and_scalar_matches(self):
        rows = self.summary["rows"]
        self.assertEqual(
            [row["case_id"] for row in rows],
            ["dragon_happy", "thai_happy_scaled", "thai_asian_scaled"],
        )
        for row in rows:
            self.assertEqual(row["input_identity_level"], "level_b_same_source_public_graphics")
            self.assertEqual(row["required_rtdl_preprocessing"], ["translate_each_input_to_min_bound"])
            self.assertTrue(row["author_rerun_matches_paper_log"])
            self.assertLessEqual(row["abs_diff_author_rerun_vs_paper_log"], self.summary["tolerance"])
            self.assertFalse(row["ratio_authorized"])
            for route in row["rtdl_routes"]:
                self.assertTrue(route["matched_author_rerun"], (row["case_id"], route["route_label"]))
                self.assertLessEqual(route["abs_diff_vs_author_rerun"], self.summary["tolerance"])
                self.assertFalse(route["ratio_authorized"])

    def test_exact_witness_and_fast_scalar_witness_flags_are_explicit(self):
        expected = {
            "cell-mbr-exact-witness": True,
            "cell-mbr-fast-scalar": False,
        }
        for row in self.summary["rows"]:
            observed = {route["route_label"]: route["rtdl"]["per_source_witness_exact"] for route in row["rtdl_routes"]}
            self.assertEqual(observed, expected)

    def test_denominator_columns_are_separate_not_ratios(self):
        for row in self.summary["rows"]:
            self.assertIsNotNone(row["author"]["running_avg_time_ms"])
            self.assertIsNotNone(row["author_process_wall_sec"])
            for route in row["rtdl_routes"]:
                rtdl = route["rtdl"]
                self.assertIsNotNone(rtdl["rtdl_route_wall_sec"])
                self.assertIsNotNone(route["process_wall_sec"])
                self.assertIsNotNone(rtdl["rtdl_input_load_sec"])
                self.assertNotIn("speedup", route)
                self.assertIn("ratio_authorized", route)
                self.assertFalse(route["ratio_authorized"])

    def test_runner_is_app_owned_and_no_ratio_calculation(self):
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("performance_ratio_claimed", source)
        self.assertIn('"performance_ratio_claimed": False', source)
        self.assertNotIn("speedup", source.lower())
        self.assertIn("ratio_authorized", source)


if __name__ == "__main__":
    unittest.main()
