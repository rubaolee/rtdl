import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5420_figure5_level_b_matrix_consolidation_decision.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5420_figure5_level_b_matrix_consolidation_decision.py"
)


class Goal5420Figure5MatrixDecisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_decision_consolidates_matched_graphics_matrix(self):
        payload = self.summary
        self.assertTrue(payload["matched"])
        matrix = payload["graphics_matrix"]
        self.assertTrue(matrix["same_pod_execution_claimed"])
        self.assertEqual(matrix["graphics_case_count"], 3)
        self.assertEqual(matrix["route_result_count"], 6)
        self.assertTrue(matrix["matched"])
        self.assertEqual(
            [row["case_id"] for row in matrix["rows"]],
            ["dragon_happy", "thai_happy_scaled", "thai_asian_scaled"],
        )
        for row in matrix["rows"]:
            self.assertEqual(row["required_rtdl_preprocessing"], ["translate_each_input_to_min_bound"])
            self.assertTrue(row["author_rerun_matches_paper_log"])
            self.assertFalse(row["ratio_authorized"])
            for route in row["rtdl_routes"]:
                self.assertTrue(route["matched_author_rerun"])
                self.assertFalse(route["ratio_authorized"])

    def test_decision_authorizes_geo_packet_plan_not_execution(self):
        decision = self.summary["decision"]
        self.assertTrue(decision["graphics_matrix_ready_for_strict_review"])
        self.assertTrue(decision["bounded_geo_matrix_packet_authorized_next"])
        self.assertFalse(decision["bounded_geo_matrix_execution_authorized_now"])
        self.assertEqual(decision["recommended_next_goal"], "Goal5421_bounded_geo_same_pod_packet_plan")
        geo = self.summary["secondary_bounded_geo_candidates"]
        self.assertEqual([row["case_id"] for row in geo], ["county_zcta_bounded", "water_bg_bounded"])
        for row in geo:
            self.assertEqual(row["input_identity_level"], "level_b_bounded_geo_fixture")
            self.assertEqual(row["packet_status"], "authorize_separate_packet_plan_not_execution")

    def test_no_ratio_no_exact_no_lb_reopen(self):
        boundary = self.summary["claim_boundary"]
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["bounded_geo_execution_claimed"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(self.summary["decision"]["continue_route_micro_optimization_by_default"])

    def test_builder_does_not_run_pod_or_commands(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn(".run(", source)
        self.assertNotIn(".Popen(", source)


if __name__ == "__main__":
    unittest.main()
