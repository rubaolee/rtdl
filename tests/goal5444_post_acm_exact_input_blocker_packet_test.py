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
    / "build_xhd_goal5444_post_acm_exact_input_blocker_packet.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5444_post_acm_exact_input_blocker_packet.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5444_post_acm_packet", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5444PostAcmExactInputBlockerPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_packet_marks_blocker_unchanged_and_no_pod(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5444.post_acm_exact_input_blocker_packet.v1",
        )
        self.assertEqual(
            payload["status"],
            "post_acm_exact_input_blocker_unchanged__owner_external_action_needed",
        )
        summary = payload["summary"]
        self.assertFalse(summary["exact_input_blocker_removed"])
        self.assertFalse(summary["pod_expected_next"])
        self.assertFalse(summary["full_objective_complete"])
        self.assertEqual(summary["achieved_requirement_count"], 1)
        self.assertEqual(summary["requirement_count"], 14)

    def test_public_acm_and_external_chain_status_are_carried_forward(self) -> None:
        summary = self.payload["summary"]
        self.assertFalse(summary["new_public_exact_input_artifact_found"])
        self.assertFalse(summary["acm_current_environment_can_download_zip"])
        self.assertFalse(summary["acm_supplement_inspected"])
        self.assertEqual(summary["ready_external_request_count"], 4)
        self.assertEqual(summary["sent_receipt_count"], 0)
        self.assertEqual(summary["external_response_count"], 0)
        self.assertEqual(summary["planned_gate_count"], 0)

    def test_blocker_rows_cover_required_reasons(self) -> None:
        rows = {row["blocker"]: row for row in self.payload["blocker_rows"]}
        self.assertIn("exact input artifacts or accepted exact-equivalence evidence", rows)
        self.assertIn("ACM supplement contents", rows)
        self.assertIn("external request/response chain", rows)
        self.assertIn("full user objective", rows)
        self.assertIn("visible but forbidden", rows["ACM supplement contents"]["current_state"])
        self.assertIn("prepared but not sent", rows["external request/response chain"]["current_state"])

    def test_claim_boundary_does_not_upgrade_any_paper_claim(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["post_acm_blocker_packet_claimed"])
        for key in [
            "exact_input_blocker_removed",
            "request_sent_claimed",
            "external_response_received",
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

    def test_next_actions_are_external_or_intake_not_runtime(self) -> None:
        next_actions = "\n".join(row["action"] for row in self.payload["recommended_next_actions"])
        self.assertIn("send_or_review_selected_external_requests", next_actions)
        self.assertIn("obtain_authorized_acm_access", next_actions)
        self.assertIn("normalize_external_response", next_actions)
        not_next = "\n".join(self.payload["not_recommended_next_actions"])
        self.assertIn("POD execution", not_next)
        self.assertIn("route micro-optimization", not_next)
        self.assertIn("explicit -lb", not_next)

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        gate = self.payload["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertIn("post-ACM exact-input blocker", gate["gate_non_app_consumer"])
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("hd_exec", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)


if __name__ == "__main__":
    unittest.main()
