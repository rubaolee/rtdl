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
    / "build_xhd_goal5447_current_external_blocker_state.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5447_current_external_blocker_state.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5447_current_state", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5447CurrentExternalBlockerStateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_current_state_waits_on_external_action(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5447.current_external_blocker_state.v1",
        )
        self.assertEqual(payload["status"], "current_external_blocker_waiting_on_owner_or_external_action")
        summary = payload["summary"]
        self.assertFalse(summary["full_objective_complete"])
        self.assertFalse(summary["exact_input_blocker_removed"])
        self.assertEqual(summary["ready_external_request_count"], 4)
        self.assertEqual(summary["receipt_stub_count"], 4)
        self.assertFalse(summary["request_sent_claimed"])
        self.assertFalse(summary["external_response_received"])
        self.assertEqual(summary["external_artifact_candidate_count"], 0)
        self.assertFalse(summary["external_artifacts_acquired"])
        self.assertFalse(summary["pod_expected_next"])

    def test_current_interfaces_include_dispatch_bundle_and_dropbox(self) -> None:
        interfaces = {row["interface"]: row for row in self.payload["current_interfaces"]}
        self.assertIn("sendable external request bundle", interfaces)
        self.assertIn("external artifact dropbox", interfaces)
        self.assertEqual(interfaces["sendable external request bundle"]["ready_count"], 4)
        self.assertEqual(interfaces["external artifact dropbox"]["artifact_candidate_count"], 0)
        self.assertIn("prepared_not_sent", interfaces["sendable external request bundle"]["claim_boundary"])
        self.assertIn("hash-and-route only", interfaces["external artifact dropbox"]["claim_boundary"])

    def test_claim_boundary_forbids_runtime_and_reproduction_claims(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["current_external_blocker_state_claimed"])
        for key in [
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
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "current external blocker state packet / reproduction-governance workflow",
        )
        self.assertFalse(stop_loss["gate_requires_app_specific_logic"])
        self.assertTrue(stop_loss["gate_downstream_consumer_reachable"])
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)
        self.assertNotIn("hd_exec", source)


if __name__ == "__main__":
    unittest.main()
