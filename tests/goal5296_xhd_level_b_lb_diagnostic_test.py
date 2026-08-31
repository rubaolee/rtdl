import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5296_level_b_dragon_asian_lb_diagnostic_2026-07-09.json"
)


class Goal5296XhdLevelBLbDiagnosticTest(unittest.TestCase):
    def test_artifact_is_level_b_author_only_not_figure7_reproduction(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["goal"], "Goal5296")
        self.assertEqual(
            payload["status"],
            "level_b_dragon_asian_author_lb_diagnostic_ready__not_figure7_reproduction",
        )
        self.assertEqual(payload["level"], "level_b_temporary_input_author_only_diagnostic")
        self.assertFalse(payload["decision"]["figure7_reproduced"])
        self.assertFalse(payload["decision"]["author_lb_comparison_matrix_regenerated"])
        self.assertFalse(payload["decision"]["rtdl_comparison_started"])
        self.assertFalse(payload["decision"]["same_denominator_performance_ratio_allowed"])

        boundary = payload["claim_boundary"]
        for key, value in boundary.items():
            self.assertFalse(value, key)

    def test_lb0_and_lb256_author_runs_are_recorded_and_value_equal(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        lb0 = payload["author_runs"]["lb_0"]
        lb256 = payload["author_runs"]["lb_256"]

        self.assertEqual(lb0["lb"], 0)
        self.assertEqual(lb256["lb"], 256)
        self.assertEqual(lb0["hd_result"], lb256["hd_result"])
        self.assertTrue(payload["comparison"]["hd_result_equal"])
        self.assertEqual(payload["comparison"]["hd_result_abs_diff"], 0.0)

        self.assertEqual(lb0["iterations_record_count"], 3)
        self.assertEqual(lb256["iterations_record_count"], 3)
        self.assertEqual(lb0["large_cells"], 0)
        self.assertGreater(lb256["large_cells"], 0)
        self.assertEqual(lb0["memory"]["WL Heavy Peak"], 0)
        self.assertGreater(lb256["memory"]["WL Heavy Peak"], 0)

    def test_lb256_is_not_reported_as_a_performance_win(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        comparison = payload["comparison"]

        self.assertGreater(comparison["lb256_running_avg_time_div_lb0"], 1.0)
        self.assertGreater(comparison["lb256_process_wall_div_lb0"], 1.0)
        self.assertLess(comparison["lb256_iteration3_compared_points_div_lb0"], 1.0)
        self.assertIn("single-run author Running.AvgTime is slower", comparison["interpretation"])
        self.assertIn("diagnostic only", comparison["interpretation"])

    def test_partial_tmp_input_paths_are_not_promoted(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        scope = payload["input_scope"]

        self.assertEqual(scope["input1"], "/tmp/xhd_goal5234/data/dragon.ply")
        self.assertEqual(scope["input2"], "/tmp/xhd_goal5234/data/asian_dragon.ply")
        self.assertFalse(scope["exact_paper_dataset_identity_proven"])
        self.assertIn("not /local/storage/shared/HDDatasets", scope["source"])
        self.assertIn("not_full_figure7_matrix_reason", scope)
        self.assertIn("full author lb_comparison matrix", scope["not_full_figure7_matrix_reason"])


if __name__ == "__main__":
    unittest.main()
