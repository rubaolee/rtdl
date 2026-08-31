import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5450_public_external_blocker_review_packet.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5450_public_external_blocker_review_packet.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5450_packet", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5450PublicExternalBlockerReviewPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_packet_status_and_blocker_state(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5450.public_external_blocker_review_packet.v1",
        )
        self.assertEqual(
            payload["status"],
            "public_external_blocker_packet_ready__external_event_required",
        )
        blocker = payload["current_blocker"]
        self.assertFalse(blocker["exact_input_blocker_removed"])
        self.assertFalse(blocker["full_objective_complete"])
        self.assertFalse(blocker["new_public_exact_input_artifact_found"])
        self.assertTrue(blocker["external_paths_ready"])
        self.assertFalse(blocker["pod_expected_next"])

    def test_public_and_external_summaries_are_consistent(self) -> None:
        public = self.payload["public_provenance_summary"]
        self.assertFalse(public["goal5442_new_public_exact_input_artifact_found"])
        self.assertFalse(public["goal5449_new_public_exact_input_artifact_found"])
        self.assertFalse(public["exact_input_blocker_removed"])
        self.assertIn("github_metadata", public["deep_surface_classes_checked"])
        self.assertIn("registries", public["deep_surface_classes_checked"])

        paths = self.payload["external_path_summary"]
        self.assertEqual(paths["path_count"], 6)
        self.assertEqual(paths["ready_path_count"], 6)
        self.assertEqual(paths["missing_required_file_count"], 0)
        self.assertTrue(paths["all_paths_ready"])
        self.assertTrue(paths["all_paths_disallow_direct_pod"])
        self.assertTrue(paths["all_paths_disallow_direct_exact_claim"])

    def test_next_external_events_are_actionable_but_not_claims(self) -> None:
        events = self.payload["next_external_events"]
        self.assertGreaterEqual(len(events), 5)
        joined = "\n".join(row["event"] + " " + row["first_local_gate"] for row in events)
        self.assertIn("sent receipt", joined)
        self.assertIn("authorized ACM supplement zip", joined)
        self.assertIn("exact-equivalence verdict", joined)
        self.assertIn("run_xhd_goal5439_external_request_sent_receipt_gate.py", joined)
        self.assertIn("validate_xhd_external_response_intake.py", joined)

    def test_claim_boundary_and_stop_loss(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["consolidated_blocker_packet_claimed"])
        for key in [
            "external_artifacts_acquired",
            "external_response_received",
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

        gate = self.payload["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertIn("public/external blocker", gate["gate_non_app_consumer"])
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

    def test_script_does_not_run_pod_or_routes(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)
        self.assertNotIn("hd_exec", source)


if __name__ == "__main__":
    unittest.main()
