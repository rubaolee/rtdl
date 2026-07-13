import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5421_bounded_geo_same_pod_packet_plan.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5421_bounded_geo_same_pod_packet_plan.py"
)


class Goal5421BoundedGeoSamePodPacketPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_packet_contains_two_bounded_geo_rows_only(self):
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5421.bounded_geo_same_pod_packet_plan.v1",
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["status"], "bounded_geo_same_pod_packet_planned__no_execution")
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(payload["case_ids"], ["county_zcta_bounded", "water_bg_bounded"])
        for row in payload["rows"]:
            self.assertEqual(row["category"], "geo_bounded")
            self.assertEqual(row["input_identity_level"], "level_b_bounded_geo_fixture")
            self.assertEqual(row["input_type"], "wkt")
            self.assertEqual(row["n_dims"], 2)
            self.assertEqual(row["packet_status"], "planned_not_executed")
            self.assertTrue(row["comparison"]["prior_matched"])
            self.assertLessEqual(row["comparison"]["prior_abs_diff"], row["comparison"]["tolerance"])

    def test_execution_is_planning_only_and_wrapper_required(self):
        payload = self.summary
        self.assertFalse(payload["execution"]["goal5421_executes_pod"])
        self.assertFalse(payload["execution"]["bounded_geo_matrix_execution_claimed"])
        self.assertEqual(
            payload["execution"]["next_execution_goal"],
            "Goal5422_bounded_geo_same_pod_packet_execution",
        )
        self.assertTrue(payload["pod"]["wrapper_required"])
        self.assertFalse(payload["pod"]["naked_ssh_allowed"])
        self.assertIn("current_pod_ssh.py", payload["pod"]["wrapper_command_prefix"])

    def test_author_and_rtdl_commands_are_denominator_disciplined(self):
        payload = self.summary
        for row in payload["rows"]:
            author_command = row["author"]["command"]
            rtdl_command = row["rtdl"]["command"]

            self.assertIn("/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec", author_command)
            self.assertIn("-input_type", author_command)
            self.assertIn("wkt", author_command)
            self.assertIn("-n_dims", author_command)
            self.assertIn("2", author_command)
            self.assertIn("-variant", author_command)
            self.assertIn("rt", author_command)
            self.assertIn("-normalize=false", author_command)

            self.assertIn("run_xhd_goal5305_county_zcta_rtdl_numba_gate.py", " ".join(rtdl_command))
            self.assertIn("--partner", rtdl_command)
            self.assertIn("triton", rtdl_command)
            self.assertIn("--triton-strategy", rtdl_command)
            self.assertIn("dense_point_nearest_tiled", rtdl_command)
            self.assertIn("--tolerance", rtdl_command)
            self.assertIn("1e-5", rtdl_command)

            self.assertEqual(row["rtdl"]["route"], "directed_max_of_nearest_distance_2d_partner_columns")
            self.assertEqual(row["rtdl"]["partner"], "triton")
            self.assertEqual(row["rtdl"]["triton_strategy"], "dense_point_nearest_tiled")
            self.assertEqual(
                row["rtdl"]["partner_reference_contract"],
                "generic_directed_max_of_nearest_distance_2d",
            )
            self.assertEqual(row["rtdl"]["native_engine_row_contract"], "not_called_partner_reference_only")
            self.assertTrue(row["rtdl"]["per_source_witness_exact"])

    def test_claim_boundary_blocks_figure_ratio_exact_and_lb_claims(self):
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["bounded_geo_packet_plan_claimed"])
        self.assertTrue(boundary["level_b_bounded_geo_correctness_claimed_from_prior_evidence"])
        self.assertFalse(boundary["bounded_geo_execution_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["geo_figure5_reproduction_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])
        self.assertFalse(self.summary["denominator_policy"]["ratio_authorized"])

    def test_builder_does_not_execute_commands(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn(".run(", source)
        self.assertNotIn(".Popen(", source)
        self.assertNotIn("os.system", source)


if __name__ == "__main__":
    unittest.main()
