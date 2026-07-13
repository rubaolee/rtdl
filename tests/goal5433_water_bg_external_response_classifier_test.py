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
    / "classify_xhd_goal5433_water_bg_external_response.py"
)
CONTRACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5433_water_bg_external_response_classifier_contract.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5433_classifier", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5433WaterBgExternalResponseClassifierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.current_hashes = cls.contract["current_public_hashes"]

    def _base(self, response_type: str) -> dict:
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

    def test_contract_is_fail_closed_and_no_claims(self) -> None:
        payload = self.contract
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5433.water_bg_external_response_classifier_contract.v1",
        )
        self.assertEqual(payload["status"], "water_bg_external_response_classifier_ready__await_response")
        self.assertEqual(payload["default_classification"], "fail_closed_keep_level_b")
        self.assertEqual(
            set(payload["current_required_paths"]),
            {"USADetailedWaterBodies.wkt", "USACensusBlockGroupBoundaries.wkt"},
        )
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["classifier_contract_claimed"])
        for key in [
            "external_response_received",
            "external_artifacts_acquired",
            "exact_equivalence_accepted",
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "full_paper_reproduction_claimed",
            "performance_ratio_claimed",
            "pod_execution_claimed",
            "new_rtdl_route_code_added",
            "explicit_lb_reopened",
            "route_micro_optimization_goal_authorized",
        ]:
            self.assertFalse(boundary[key])

    def test_author_hash_manifest_matching_current_public_hashes_runs_gate_but_does_not_claim_exact(self) -> None:
        response = self._base("author_hash_manifest")
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
        result = self.module.classify_response(response)
        self.assertEqual(
            result["classification"],
            "author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim",
        )
        self.assertTrue(result["validation_status"]["sufficient_to_run_pod_gate"])
        self.assertFalse(result["validation_status"]["sufficient_to_claim_exact_input"])
        self.assertFalse(result["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])

    def test_author_hash_manifest_mismatch_does_not_run_pod_gate(self) -> None:
        response = self._base("author_hash_manifest")
        response["artifacts"]["hash_manifest_entries"] = [
            {
                "paper_input_path": "USADetailedWaterBodies.wkt",
                "hash_algorithm": "sha256",
                "hash_value": "0" * 64,
            },
            {
                "paper_input_path": "USACensusBlockGroupBoundaries.wkt",
                "hash_algorithm": "sha256",
                "hash_value": self.current_hashes["USACensusBlockGroupBoundaries.wkt"],
            },
        ]
        result = self.module.classify_response(response)
        self.assertEqual(
            result["classification"],
            "author_hashes_do_not_match_current_public_reconstruction__need_author_bytes_or_regeneration",
        )
        self.assertFalse(result["validation_status"]["sufficient_to_run_pod_gate"])
        self.assertFalse(result["validation_status"]["sufficient_to_claim_exact_input"])
        self.assertFalse(result["evidence"]["hashes_match_current_public_reconstruction"]["USADetailedWaterBodies.wkt"])

    def test_missing_hash_entry_fail_closes(self) -> None:
        response = self._base("author_hash_manifest")
        response["artifacts"]["hash_manifest_entries"] = [
            {
                "paper_input_path": "USADetailedWaterBodies.wkt",
                "hash_algorithm": "sha256",
                "hash_value": self.current_hashes["USADetailedWaterBodies.wkt"],
            }
        ]
        result = self.module.classify_response(response)
        self.assertEqual(result["classification"], "author_hash_manifest_incomplete__keep_level_b")
        self.assertFalse(result["validation_status"]["sufficient_to_run_pod_gate"])
        self.assertIn("USACensusBlockGroupBoundaries.wkt", "\n".join(result["failure_or_missing_items"]))

    def test_exact_equivalence_verdict_accepted_is_bounded_not_exact_input(self) -> None:
        response = self._base("exact_equivalence_verdict")
        response["artifacts"]["exact_equivalence_verdict"] = {
            "outcome": "exact_equivalent_accepted_with_renamed_bounded_public_reconstruction_claim",
            "reviewed_reconstruction": "WaterBodies to BlockGroups public ArcGIS reconstruction",
            "accepted_claim_name": "bounded_public_reconstruction_exact_equivalent_for_water_bg",
            "limitations": ["not byte-identical paper input"],
        }
        result = self.module.classify_response(response)
        self.assertEqual(
            result["classification"],
            "exact_equivalence_accepted_for_bounded_public_reconstruction__run_accepted_matrix",
        )
        self.assertTrue(result["validation_status"]["exact_equivalence_accepted"])
        self.assertTrue(result["validation_status"]["sufficient_to_run_pod_gate"])
        self.assertFalse(result["validation_status"]["sufficient_to_claim_exact_input"])

    def test_non_availability_keeps_level_b(self) -> None:
        response = self._base("explicit_non_availability_statement")
        response["artifacts"]["freeform_notes"] = "No input hashes or data are available."
        result = self.module.classify_response(response)
        self.assertEqual(result["classification"], "external_non_availability_statement__keep_level_b_and_record_blocker")
        self.assertFalse(result["validation_status"]["sufficient_to_run_pod_gate"])

    def test_cli_classifies_response_file(self) -> None:
        response = self._base("explicit_non_availability_statement")
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "response.json"
            out = Path(tmp) / "classified.json"
            src.write_text(json.dumps(response), encoding="utf-8")
            exit_code = self.module.main(["--input", str(src), "--output", str(out)])
            self.assertEqual(exit_code, 0)
            result = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(result["classification"], "external_non_availability_statement__keep_level_b_and_record_blocker")

    def test_script_does_not_run_pod_or_routes(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)
        self.assertNotIn("hd_exec", source)


if __name__ == "__main__":
    unittest.main()
