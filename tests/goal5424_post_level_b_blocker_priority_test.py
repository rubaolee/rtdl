import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5424_post_level_b_blocker_priority.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5424_post_level_b_blocker_priority.py"
)


class Goal5424PostLevelBBlockerPriorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_selects_waterbodies_blockgroups_as_next_full_public_candidate(self):
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5424.post_level_b_blocker_priority.v1",
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(
            payload["status"],
            "post_level_b_next_branch_selected__full_public_water_bg_feasibility_first__no_route_tuning",
        )
        decision = payload["decision"]
        self.assertEqual(
            decision["recommended_next_goal"],
            "Goal5425_full_public_waterbodies_blockgroups_wkt_generation_feasibility",
        )
        self.assertEqual(
            decision["technical_branch"],
            "full_public_waterbodies_blockgroups_before_more_route_work",
        )
        self.assertFalse(decision["route_micro_optimization"])
        self.assertFalse(decision["explicit_lb"])

    def test_ranking_uses_goal5309_point_count_and_mbr_evidence(self):
        ranking = self.summary["candidate_ranking"]
        self.assertEqual(ranking[0]["candidate"], "full_public_waterbodies_blockgroups")
        water = ranking[0]["services"]["waterbodies"]
        block = ranking[0]["services"]["blockgroups"]
        self.assertEqual(water["point_count_delta"], 6129)
        self.assertLess(water["point_count_relative_delta"], 0.001)
        self.assertLess(water["max_abs_mbr_delta"], 1e-5)
        self.assertEqual(block["point_count_delta"], 127)
        self.assertLess(block["point_count_relative_delta"], 1e-5)
        self.assertLess(block["max_abs_mbr_delta"], 1e-5)

        county_branch = ranking[1]
        self.assertEqual(county_branch["candidate"], "alternate_county_source_or_simplification_search")
        county = county_branch["services"]["county"]
        self.assertGreater(county["point_count_relative_delta"], 0.3)

    def test_goal5425_is_feasibility_before_execution(self):
        requirements = self.summary["goal5425_requirements"]
        self.assertTrue(requirements["must_not_run_author_or_rtdl_yet"])
        self.assertTrue(requirements["must_estimate_or_bound_wkt_size_and_disk"])
        self.assertTrue(requirements["must_define_resume_checkpoint_plan"])
        self.assertTrue(requirements["must_define_author_loader_semantics"])
        self.assertTrue(requirements["must_define_pod_upload_or_generation_location"])
        self.assertEqual(
            requirements["must_keep_claim_level"],
            "Level-B full-public candidate, not exact paper input",
        )
        self.assertIn(
            "generated point counts diverge materially from Goal5309 probe",
            requirements["must_define_kill_conditions"],
        )

    def test_claim_boundary_and_stop_loss_gate(self):
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["level_b_same_pod_matrix_claimed"])
        self.assertTrue(boundary["next_branch_decision_claimed"])
        self.assertFalse(boundary["full_public_water_bg_execution_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])

        gate = self.summary["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])
        self.assertIn("no app-artifact parity work", gate["gate_non_app_consumer"])

    def test_builder_is_decision_only(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn(".run(", source)
        self.assertNotIn(".Popen(", source)


if __name__ == "__main__":
    unittest.main()
