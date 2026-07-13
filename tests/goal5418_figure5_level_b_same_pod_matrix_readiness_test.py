import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.py"
)


class Goal5418Figure5LevelBReadinessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_packet_is_readiness_only(self):
        payload = self.summary
        self.assertTrue(payload["matched"])
        self.assertTrue(payload["dry_run_only"])
        self.assertEqual(payload["matrix_rows_executed"], 0)
        self.assertFalse(payload["same_pod_execution_claimed"])
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["execution_packet_claimed"])
        self.assertFalse(boundary["same_pod_execution_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])

    def test_primary_graphics_rows_are_value_matched_candidates_only(self):
        rows = self.summary["graphics_execution_rows"]
        case_ids = [row["case_id"] for row in rows]
        self.assertEqual(
            case_ids,
            ["dragon_happy", "thai_happy_scaled", "thai_asian_scaled"],
        )
        self.assertNotIn("dragon_asian_scaled", case_ids)
        self.assertEqual(self.summary["graphics_case_count"], 3)
        self.assertEqual(self.summary["graphics_command_count"], 9)
        for row in rows:
            self.assertEqual(row["input_identity_level"], "level_b_same_source_public_graphics")
            self.assertFalse(row["ratio_authorized"])
            self.assertIn("author_running_avg_time_ms", row["planned_denominator_columns"])
            self.assertIn("rtdl_route_wall_sec", row["planned_denominator_columns"])
            self.assertIn("per_source_witness_exact", row["planned_denominator_columns"])
            self.assertEqual(
                row["required_rtdl_preprocessing"],
                ["translate_each_input_to_min_bound"],
            )

    def test_commands_use_author_hd_exec_and_rtdl_hd_exec_wrapper_shape(self):
        for row in self.summary["graphics_execution_rows"]:
            author = row["author_command"]
            self.assertTrue(author[0].endswith("hd_exec"), author)
            self.assertIn("-variant", author)
            self.assertIn("rt", author)
            self.assertIn("-execution", author)
            self.assertIn("gpu", author)
            self.assertIn("-json", author)
            self.assertIn("-lb=256", author)
            for route in row["rtdl_route_commands"]:
                command = route["command"]
                self.assertEqual(command[0], "py")
                self.assertIn(
                    "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py",
                    command,
                )
                self.assertIn("--rtdl-route", command)
                self.assertIn(route["route_label"], command)
                self.assertIn("--grid-shape", command)
                self.assertIn("32,32,32", command)
                self.assertIn("--max-inline-points", command)
                self.assertIn("512", command)
                self.assertIn("--translate-each-input-to-min-bound", command)
                self.assertIn(route["condition"], {"execute", "execute_if_operational"})

    def test_secondary_geo_rows_are_deferred_not_executed(self):
        rows = self.summary["secondary_geo_rows"]
        self.assertEqual(self.summary["secondary_geo_case_count"], 2)
        self.assertEqual(
            [row["case_id"] for row in rows],
            ["county_zcta_bounded", "water_bg_bounded"],
        )
        for row in rows:
            self.assertEqual(row["execution_status"], "deferred_secondary_bounded_geo")
            self.assertEqual(row["input_identity_level"], "level_b_bounded_geo_fixture")
            self.assertFalse(row["ratio_authorized"])
            self.assertIn("partner/Triton", row["reason"])

    def test_pod_wrapper_policy_is_carried_forward(self):
        pod = self.summary["pod_wrapper"]
        self.assertTrue(pod["required"])
        self.assertFalse(pod["naked_ssh_allowed"])
        self.assertIn("scripts/current_pod_ssh.py", pod["preflight"])
        self.assertIn("scripts/current_pod_ssh.py", pod["exec"])
        self.assertTrue(self.summary["recommended_next"]["requires_pod_endpoint"])
        self.assertTrue(self.summary["recommended_next"]["requires_preflight"])

    def test_readiness_builder_does_not_execute_pod_commands(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("paramiko", source)
        self.assertNotIn(".run(", source)
        self.assertNotIn(".Popen(", source)


if __name__ == "__main__":
    unittest.main()
