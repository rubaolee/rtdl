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
    / "build_xhd_goal5448_external_path_readiness_audit.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5448_external_path_readiness_audit.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5448_readiness", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5448ExternalPathReadinessAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_all_external_paths_have_ready_fail_closed_gates(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5448.external_path_readiness_audit.v1",
        )
        self.assertEqual(payload["status"], "external_path_readiness_complete__all_paths_have_fail_closed_gates")
        self.assertEqual(payload["path_count"], 6)
        self.assertEqual(payload["ready_path_count"], 6)
        self.assertEqual(payload["missing_required_file_count"], 0)
        self.assertEqual(payload["missing_required_files"], [])
        self.assertFalse(payload["exact_input_blocker_removed"])
        self.assertFalse(payload["pod_expected_next"])

    def test_expected_paths_are_present_and_no_direct_pod(self) -> None:
        rows = {row["path_id"]: row for row in self.payload["paths"]}
        for path_id in [
            "sent_receipt_path",
            "incoming_response_json_path",
            "artifact_dropbox_path",
            "acm_supplement_zip_path",
            "acm_artifact_pipeline_path",
            "exact_equivalence_verdict_path",
        ]:
            self.assertIn(path_id, rows)
            self.assertTrue(rows[path_id]["ready"])
            self.assertFalse(rows[path_id]["pod_direct_allowed"])
            self.assertFalse(rows[path_id]["exact_claim_direct_allowed"])
            self.assertGreater(len(rows[path_id]["command_templates"]), 0)

    def test_acm_artifact_pipeline_requires_mapping_before_pod(self) -> None:
        rows = {row["path_id"]: row for row in self.payload["paths"]}
        row = rows["acm_artifact_pipeline_path"]
        self.assertIn("requires_prior_zip_inspection_and_mapping_review", row["status_now"])
        self.assertIn("POD remains separate and reviewed", row["expected_output"])

    def test_claim_boundary_forbids_runtime_and_reproduction_claims(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["external_path_readiness_audit_claimed"])
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

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "external path readiness audit / reproduction-governance workflow",
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
