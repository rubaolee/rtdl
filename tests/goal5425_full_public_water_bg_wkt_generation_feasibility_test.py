import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.py"
)


class Goal5425FullPublicWaterBgWktGenerationFeasibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_selects_water_bg_and_does_not_execute(self):
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5425.full_public_water_bg_wkt_generation_feasibility.v1",
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["selected_candidate"], "full_public_waterbodies_blockgroups")
        self.assertFalse(payload["feasibility"]["author_or_rtdl_execution_claimed"])
        self.assertFalse(payload["feasibility"]["wkt_generation_executed"])
        self.assertEqual(
            payload["feasibility"]["full_public_candidate_level"],
            "Level-B full-public candidate, not exact paper input",
        )

    def test_size_estimates_are_bounded_and_resource_gate_exists(self):
        feasibility = self.summary["feasibility"]
        self.assertGreater(feasibility["estimated_total_wkt_gib"], 2.0)
        self.assertLess(feasibility["estimated_total_wkt_gib"], 3.0)
        self.assertAlmostEqual(
            feasibility["recommended_free_disk_gib"],
            feasibility["estimated_total_wkt_gib"] * feasibility["safety_factor"],
            places=9,
        )
        self.assertGreater(feasibility["recommended_free_disk_gib"], 6.0)
        self.assertGreater(feasibility["estimated_generation_time_sec_from_probe_floor"], 1500.0)

    def test_service_evidence_comes_from_goal5309_and_bounded_manifest(self):
        water = self.summary["services"]["waterbodies"]
        block = self.summary["services"]["blockgroups"]
        self.assertEqual(water["author_loader_point_count"], 22824823)
        self.assertEqual(water["point_count_delta"], 6129)
        self.assertLess(water["point_count_relative_delta"], 0.001)
        self.assertEqual(water["bounded_author_loader_points"], 124)
        self.assertEqual(water["bounded_bytes"], 3742)

        self.assertEqual(block["author_loader_point_count"], 52271467)
        self.assertEqual(block["point_count_delta"], 127)
        self.assertLess(block["point_count_relative_delta"], 1e-5)
        self.assertEqual(block["bounded_author_loader_points"], 894)
        self.assertEqual(block["bounded_bytes"], 26682)

    def test_generation_plan_requires_checkpoint_and_resource_preflight(self):
        plan = self.summary["generation_plan"]
        self.assertEqual(
            plan["next_goal"],
            "Goal5426_full_public_water_bg_wkt_generation_dry_run_or_execute_if_resources_pass",
        )
        self.assertFalse(plan["local_generation_allowed"])
        self.assertIn("/tmp/xhd_goal5426/full_public_water_bg", plan["preferred_generation_location"])
        self.assertIn("df -BG /tmp", plan["resource_preflight_required"])
        self.assertIn("USADetailedWaterBodies_full_public.checkpoint.json", plan["checkpoint_files"])
        self.assertIn("USACensusBlockGroupBoundaries_full_public.checkpoint.json", plan["checkpoint_files"])
        semantics = plan["author_loader_semantics"]
        self.assertTrue(semantics["one_geometry_per_line"])
        self.assertTrue(semantics["polygon_outer_ring_only_for_author_point_count"])
        self.assertTrue(semantics["ignore_holes"])

    def test_claim_boundary_and_stop_loss_gate(self):
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["feasibility_plan_claimed"])
        self.assertFalse(boundary["full_public_wkt_generated"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])
        self.assertFalse(boundary["explicit_lb_reopened"])

        gate = self.summary["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertIn("no app-artifact parity work", gate["gate_non_app_consumer"])
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

    def test_builder_is_feasibility_only(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("urlopen", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn(".run(", source)
        self.assertNotIn(".Popen(", source)


if __name__ == "__main__":
    unittest.main()
