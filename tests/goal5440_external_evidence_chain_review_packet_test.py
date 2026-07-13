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
    / "build_xhd_goal5440_external_evidence_chain_review_packet.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5440_external_evidence_chain_review_packet.json"
)
REVIEW_MD = (
    ROOT
    / "history"
    / "internal_docs"
    / "call_for_review_goals5433_5439_xhd_external_evidence_chain_2026-07-10.md"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5440_external_chain", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5440ExternalEvidenceChainReviewPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.review = REVIEW_MD.read_text(encoding="utf-8")

    def test_current_chain_is_prepared_not_sent_and_no_response(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5440.external_evidence_chain_review_packet.v1",
        )
        self.assertEqual(
            payload["status"],
            "external_evidence_chain_prepared_not_sent__await_owner_or_external_action",
        )
        summary = payload["summary"]
        self.assertEqual(summary["ready_external_request_count"], 4)
        self.assertEqual(summary["sent_receipt_count"], 0)
        self.assertEqual(summary["external_response_count"], 0)
        self.assertEqual(summary["positive_classifier_outcome_count"], 0)
        self.assertEqual(summary["planned_gate_count"], 0)
        self.assertFalse(summary["full_xhd_paper_reproduction_ready"])
        self.assertFalse(summary["pod_expected_next"])
        self.assertFalse(summary["pod_used_anywhere_in_chain"])
        self.assertTrue(summary["claim_boundaries_preserved"])

    def test_covers_goals_5433_to_5439_and_preserves_claim_boundary(self) -> None:
        self.assertEqual(
            self.payload["goals_covered"],
            ["Goal5433", "Goal5434", "Goal5435", "Goal5436", "Goal5437", "Goal5438", "Goal5439"],
        )
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["external_evidence_chain_review_packet_claimed"])
        self.assertTrue(boundary["request_send_manifest_claimed"])
        for key in [
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

    def test_chain_state_matches_underlying_gates(self) -> None:
        state = self.payload["chain_state"]
        self.assertEqual(state["classifier_ready"], "water_bg_external_response_classifier_ready__await_response")
        self.assertEqual(state["action_packet_ready"], "water_bg_external_action_packet_ready__prepared_not_sent")
        self.assertEqual(state["inbox_status"], "external_response_inbox_empty__await_response")
        self.assertEqual(state["readiness_status"], "full_xhd_reproduction_not_ready__await_external_response_or_artifact")
        self.assertEqual(state["next_gate_plan_status"], "external_response_next_gate_plan_empty__await_response")
        self.assertEqual(state["send_manifest_status"], "external_request_send_manifest_ready__prepared_not_sent")
        self.assertEqual(state["sent_receipt_status"], "external_request_sent_receipt_gate_empty__no_request_sent")

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "external evidence-chain review packet / provenance governance workflow",
        )
        self.assertFalse(stop_loss["gate_requires_app_specific_logic"])
        self.assertTrue(stop_loss["gate_downstream_consumer_reachable"])
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)
        self.assertNotIn("hd_exec", source)

    def test_call_for_review_has_questions_and_forbidden_claims(self) -> None:
        text = self.review
        self.assertIn("Goals5433-5439 X-HD External Evidence Chain", text)
        self.assertIn("prepared requests, sent receipts, incoming responses", text)
        self.assertIn("request_sent_claimed = false", text)
        self.assertIn("full_xhd_paper_reproduction_claimed = false", text)
        self.assertIn("approve_goals5433_5439_external_evidence_chain_fail_closed", text)


if __name__ == "__main__":
    unittest.main()
