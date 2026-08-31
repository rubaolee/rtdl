import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5435_external_response_inbox_gate.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5435_external_response_inbox_gate.json"
)
CONTRACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5433_water_bg_external_response_classifier_contract.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5435_inbox_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _base_response(response_type: str) -> dict:
    return {
        "schema": "rtdl.paper_reproduction.xhd.external_response_intake.v1",
        "status": "normalized_for_test",
        "received_from": {
            "actor_type": "paper_author",
            "name_or_role": "test",
            "contact_or_source": "test",
            "received_date": "2026-07-10",
        },
        "response_type": response_type,
        "scope": {
            "paper": "X-HD",
            "families": ["geo"],
            "paper_paths_or_figures": [
                "USADetailedWaterBodies.wkt",
                "USACensusBlockGroupBoundaries.wkt",
            ],
            "claim_boundary_requested": "exact_input",
        },
        "artifacts": {
            "hash_manifest_entries": [],
            "archive": None,
            "regeneration_script": None,
            "acm_supplement_listing": None,
            "exact_equivalence_verdict": None,
            "freeform_notes": "",
        },
    }


class Goal5435ExternalResponseInboxGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main([])
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.current_hashes = json.loads(CONTRACT.read_text(encoding="utf-8"))["current_public_hashes"]

    def test_current_inbox_is_empty_and_claims_nothing(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5435.external_response_inbox_gate.v1",
        )
        self.assertEqual(payload["status"], "external_response_inbox_empty__await_response")
        self.assertEqual(payload["response_count"], 0)
        self.assertEqual(payload["positive_classifier_outcome_count"], 0)
        self.assertFalse(payload["pod_usage"]["used"])
        self.assertFalse(payload["pod_usage"]["expected_next"])
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["inbox_scanned"])
        self.assertFalse(boundary["external_response_received"])
        for key in [
            "request_sent_claimed",
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

    def test_matching_hash_response_is_positive_but_only_authorizes_next_gate(self) -> None:
        response = _base_response("author_hash_manifest")
        response["artifacts"]["hash_manifest_entries"] = [
            {
                "paper_input_path": "USADetailedWaterBodies.wkt",
                "hash_algorithm": "sha256",
                "hash_value": self.current_hashes["USADetailedWaterBodies.wkt"],
            },
            {
                "paper_input_path": "USACensusBlockGroupBoundaries.wkt",
                "hash_algorithm": "sha256",
                "hash_value": self.current_hashes["USACensusBlockGroupBoundaries.wkt"],
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "matching_hashes.json"
            path.write_text(json.dumps(response), encoding="utf-8")
            payload = self.module.build_inbox_gate(Path(tmp))
        self.assertEqual(
            payload["status"],
            "external_response_inbox_has_positive_classifier_outcome__manual_review_before_gate",
        )
        self.assertEqual(payload["response_count"], 1)
        self.assertEqual(payload["positive_classifier_outcome_count"], 1)
        row = payload["classified_responses"][0]
        self.assertEqual(
            row["classification"],
            "author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim",
        )
        self.assertTrue(row["validation_status"]["sufficient_to_run_pod_gate"])
        self.assertFalse(row["validation_status"]["sufficient_to_claim_exact_input"])
        self.assertTrue(payload["pod_usage"]["expected_next"])
        self.assertFalse(payload["pod_usage"]["used"])
        self.assertFalse(payload["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])

    def test_non_availability_response_keeps_level_b(self) -> None:
        response = _base_response("explicit_non_availability_statement")
        response["artifacts"]["freeform_notes"] = "No input hashes or data are available."
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "non_available.json"
            path.write_text(json.dumps(response), encoding="utf-8")
            payload = self.module.build_inbox_gate(Path(tmp))
        self.assertEqual(payload["status"], "external_response_inbox_all_fail_closed__keep_level_b")
        self.assertEqual(payload["positive_classifier_outcome_count"], 0)
        self.assertEqual(
            payload["classified_responses"][0]["classification"],
            "external_non_availability_statement__keep_level_b_and_record_blocker",
        )
        self.assertFalse(payload["pod_usage"]["expected_next"])

    def test_invalid_json_fail_closes_before_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text("{not json", encoding="utf-8")
            payload = self.module.build_inbox_gate(Path(tmp))
        self.assertEqual(payload["status"], "external_response_inbox_has_invalid_items__fix_before_gate")
        self.assertEqual(payload["invalid_response_count"], 1)
        self.assertEqual(payload["positive_classifier_outcome_count"], 0)
        self.assertFalse(payload["pod_usage"]["expected_next"])

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "external response inbox gate / classifier-driven provenance workflow",
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
