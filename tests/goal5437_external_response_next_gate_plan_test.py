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
    / "build_xhd_goal5437_external_response_next_gate_plan.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5437_external_response_next_gate_plan.json"
)
READINESS = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5436_full_reproduction_readiness_matrix.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5437_next_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


class Goal5437ExternalResponseNextGatePlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_current_empty_inbox_produces_no_planned_gate(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5437.external_response_next_gate_plan.v1",
        )
        self.assertEqual(payload["status"], "external_response_next_gate_plan_empty__await_response")
        self.assertEqual(payload["response_count"], 0)
        self.assertEqual(payload["planned_gate_count"], 0)
        self.assertFalse(payload["pod_usage"]["used"])
        self.assertFalse(payload["pod_usage"]["expected_next"])
        self.assertEqual(payload["planned_gates"], [])

    def test_matching_hash_classification_maps_to_same_input_gate_without_execution(self) -> None:
        inbox = {
            "status": "external_response_inbox_has_positive_classifier_outcome__manual_review_before_gate",
            "response_count": 1,
            "classified_responses": [
                {
                    "path": "Paper-reproduction-apps/x-hd-paper/requests/incoming/hash.json",
                    "classification": "author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim",
                    "recommended_next_action": "run_same_input_author_rtdl_gate_on_current_public_wkt_then_external_review_exact_wording",
                    "validation_status": {
                        "sufficient_to_run_pod_gate": True,
                        "sufficient_to_claim_exact_input": False,
                    },
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            inbox_path = _write_json(Path(tmp) / "inbox.json", inbox)
            payload = self.module.build_plan(inbox_path, READINESS)
        self.assertEqual(
            payload["status"],
            "external_response_next_gate_plan_ready__strict_review_required_before_execution",
        )
        self.assertEqual(payload["planned_gate_count"], 1)
        gate = payload["planned_gates"][0]
        self.assertEqual(gate["gate_label"], "same_input_author_rtdl_gate_on_current_public_wkt_hash_matched")
        self.assertTrue(gate["requires_pod"])
        self.assertTrue(gate["requires_strict_review_before_execution"])
        self.assertEqual(gate["execution_status"], "not_executed__requires_strict_review")
        self.assertTrue(payload["pod_usage"]["expected_next"])
        self.assertFalse(payload["claim_boundary"]["planned_gate_executed"])
        self.assertFalse(payload["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])

    def test_acm_possible_provenance_maps_to_local_mapping_gate_not_pod(self) -> None:
        inbox = {
            "status": "external_response_inbox_has_positive_classifier_outcome__manual_review_before_gate",
            "response_count": 1,
            "classified_responses": [
                {
                    "path": "Paper-reproduction-apps/x-hd-paper/requests/incoming/acm.json",
                    "classification": "acm_supplement_contains_possible_provenance__map_before_route",
                    "recommended_next_action": "ingest_supplement_listing_map_to_workloads_before_any_pod_route",
                    "validation_status": {},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            inbox_path = _write_json(Path(tmp) / "inbox.json", inbox)
            payload = self.module.build_plan(inbox_path, READINESS)
        self.assertEqual(payload["planned_gate_count"], 1)
        gate = payload["planned_gates"][0]
        self.assertEqual(gate["gate_label"], "map_acm_supplement_artifacts_to_workloads_before_any_route")
        self.assertFalse(gate["requires_pod"])
        self.assertFalse(payload["pod_usage"]["expected_next"])
        self.assertIn("same-input correctness", gate["forbidden_direct_claims"])

    def test_fail_closed_classification_does_not_make_gate(self) -> None:
        inbox = {
            "status": "external_response_inbox_all_fail_closed__keep_level_b",
            "response_count": 1,
            "classified_responses": [
                {
                    "path": "Paper-reproduction-apps/x-hd-paper/requests/incoming/no.json",
                    "classification": "external_non_availability_statement__keep_level_b_and_record_blocker",
                    "recommended_next_action": "record_non_availability_keep_level_b",
                    "validation_status": {},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            inbox_path = _write_json(Path(tmp) / "inbox.json", inbox)
            payload = self.module.build_plan(inbox_path, READINESS)
        self.assertEqual(payload["status"], "external_response_next_gate_plan_all_fail_closed__keep_level_b")
        self.assertEqual(payload["planned_gate_count"], 0)
        self.assertEqual(payload["fail_closed_response_count"], 1)
        self.assertFalse(payload["pod_usage"]["expected_next"])

    def test_all_positive_classifications_have_gate_mappings(self) -> None:
        self.assertEqual(
            set(self.module.NEXT_GATE_BY_CLASSIFICATION),
            {
                "author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim",
                "author_input_archive_contains_required_paths__extract_hash_then_run_pod_gate",
                "byte_identical_regeneration_available__run_regeneration_then_hash_gate",
                "acm_supplement_contains_possible_provenance__map_before_route",
                "exact_equivalence_accepted_for_bounded_public_reconstruction__run_accepted_matrix",
            },
        )

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "external response next-gate planner / provenance workflow",
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
