import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5449_deep_public_mirror_probe.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5449_deep_public_mirror_probe.json"
)


class Goal5449DeepPublicMirrorProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_schema_and_conservative_status(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5449.deep_public_mirror_probe.v1",
        )
        self.assertEqual(payload["goal"], "Goal5449")
        self.assertEqual(
            payload["status"],
            "deep_public_mirror_probe_no_new_exact_input_path__external_event_still_required",
        )
        classification = payload["classification"]
        self.assertFalse(classification["new_public_exact_input_artifact_found"])
        self.assertFalse(classification["exact_input_blocker_removed"])
        self.assertFalse(classification["pod_expected_next"])

    def test_deeper_surfaces_are_present(self) -> None:
        surfaces = self.payload["deep_surfaces"]
        self.assertIn("github_metadata", surfaces)
        self.assertIn("github_data_paths", surfaces)
        self.assertIn("github_branch_trees", surfaces)
        self.assertIn("registries", surfaces)
        self.assertIn("acm_url_variants", surfaces)

        self.assertEqual(surfaces["github_data_paths"]["checked_count"], 42)
        self.assertEqual(surfaces["github_data_paths"]["found_count"], 0)
        self.assertEqual(
            surfaces["github_branch_trees"]["non_log_artifact_like_blob_count"],
            0,
        )
        self.assertEqual(surfaces["acm_url_variants"]["zip_success_count"], 0)

    def test_registry_false_positives_do_not_become_candidates(self) -> None:
        registries = self.payload["deep_surfaces"]["registries"]
        self.assertFalse(registries["registry_dataset_candidate_found"])
        self.assertEqual(registries["artifact_like_registries"], [])
        for row in registries["registries"].values():
            self.assertEqual(row["xhd_relevant_artifact_candidate_count"], 0)
            self.assertEqual(row["xhd_relevant_artifact_candidates"], [])

    def test_claim_boundary_forbids_runtime_and_reproduction_claims(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["deep_public_mirror_probe_claimed"])
        for key in [
            "external_artifacts_acquired",
            "exact_equivalence_accepted",
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
            "performance_ratio_claimed",
            "pod_execution_claimed",
            "new_rtdl_route_code_added",
            "explicit_lb_reopened",
            "route_micro_optimization_goal_authorized",
        ]:
            self.assertFalse(boundary[key], key)

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        gate = self.payload["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertIn("deep public mirror", gate["gate_non_app_consumer"])
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)
        self.assertNotIn("hd_exec", source)


if __name__ == "__main__":
    unittest.main()
