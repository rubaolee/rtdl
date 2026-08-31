import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))

import build_xhd_goal5355_radius_trace_mapping as goal5355


ARTIFACT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5355_radius_trace_mapping.json"


class Goal5355RadiusTraceMappingTest(unittest.TestCase):
    def test_full_public_author_trace_replays_next_radius(self):
        payload = goal5355.build_artifact(tolerance=1.0e-6)
        cases = {case["case_id"]: case for case in payload["cases"]}
        full_public = cases["full_public_dragon_happy_buddha_goal5186"]
        self.assertGreater(full_public["transition_count"], 0)
        self.assertTrue(full_public["all_transitions_matched"])
        transition = full_public["transitions"][0]
        self.assertEqual("adaptive", transition["mode"])
        self.assertLessEqual(transition["abs_diff"], payload["tolerance"])
        self.assertAlmostEqual(
            transition["observed_next_radius"],
            transition["predicted_next_radius"],
            places=6,
        )
        self.assertEqual("none", transition["step"]["app_semantics"])
        self.assertEqual("rtdl.radius_growth_schedule.v1", transition["step"]["contract"])

    def test_cell_diagonal_is_derived_from_target_mbr_and_grid(self):
        payload = goal5355.build_artifact(tolerance=1.0e-6)
        case = next(item for item in payload["cases"] if item["case_id"] == "res4full_dragon_happy_buddha_perf")
        transition = case["transitions"][0]
        # In the res4 author JSON, the next radius increment is exactly the
        # target grid-cell diagonal for adaptive mode after a large reduction.
        increment = transition["observed_next_radius"] - transition["previous_radius"]
        self.assertAlmostEqual(case["derived_target_cell_diagonal"], increment, places=6)
        self.assertEqual(
            "Input.Files[1].MBR / Running.Repeats[0].GridResolution",
            case["cell_diagonal_source"],
        )

    def test_terminal_zero_output_stops_without_next_iteration(self):
        payload = goal5355.build_artifact(tolerance=1.0e-6)
        for case in payload["cases"]:
            terminal = case["terminal"]
            self.assertIsNotNone(terminal)
            if terminal["num_output_points"] == 0:
                self.assertFalse(terminal["step_update_applied"])

    def test_artifact_claim_boundary_and_route_status(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            "radius_trace_mapping_matches_available_author_json__route_still_fail_closed",
            payload["status"],
        )
        self.assertTrue(payload["all_transition_cases_matched"])
        self.assertGreater(payload["total_transition_count"], 0)
        mapping = payload["current_xhd_mapping_status"]
        self.assertTrue(mapping["author_json_trace_mapping_available"])
        self.assertFalse(mapping["route_uses_tune_radius_helper"])
        self.assertTrue(mapping["run_xhd_rtdl_hd_exec_explicit_tune_radius_still_fail_closed"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)

    def test_core_api_reference_is_app_neutral(self):
        payload = goal5355.build_artifact(tolerance=1.0e-6)
        api = payload["rtdl_api"]
        self.assertEqual("radius_growth_step", api["helper"])
        self.assertEqual("none", api["app_semantics"])
        self.assertNotIn("xhd", api["helper"].lower())
        self.assertNotIn("author", api["helper"].lower())


if __name__ == "__main__":
    unittest.main()
