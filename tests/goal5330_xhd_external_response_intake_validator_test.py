import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "validate_xhd_external_response_intake.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5330_external_response_intake_validator.json"
)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_xhd_external_response_intake", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def base_payload(response_type, artifacts):
    return {
        "schema": "rtdl.paper_reproduction.xhd.external_response_intake.v1",
        "status": "filled_for_test",
        "received_from": {
            "actor_type": "paper_author",
            "name_or_role": "test sender",
            "contact_or_source": "test@example.invalid",
            "received_date": "2026-07-09",
        },
        "response_type": response_type,
        "scope": {
            "paper": "X-HD",
            "families": ["graphics_stanford"],
            "paper_paths_or_figures": ["Figure 5"],
            "claim_boundary_requested": "exact_input",
        },
        "artifacts": artifacts,
        "validation_status": {
            "validated_by_codex": False,
            "sufficient_to_run_pod_gate": False,
            "sufficient_to_claim_exact_input": False,
            "requires_external_review_before_use": True,
            "failure_or_missing_items": [],
        },
        "next_action": "classify_response_before_action",
        "claim_boundary": {
            "request_sent_claimed": False,
            "external_response_received": False,
            "external_artifacts_acquired": False,
            "acm_supplement_inspected": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
    }


class Goal5330ExternalResponseIntakeValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def test_template_fails_closed(self):
        template = json.loads(
            (
                ROOT
                / "Paper-reproduction-apps"
                / "x-hd-paper"
                / "requests"
                / "external_response_intake_template.json"
            ).read_text(encoding="utf-8")
        )
        result = self.validator.classify_intake(template)
        self.assertFalse(result["valid"])
        self.assertFalse(result["pod_expected"])
        self.assertIn("template_not_filled is not a usable response", result["errors"])
        self.assertFalse(result["sufficient_to_claim_exact_input"])

    def test_hash_manifest_with_bytes_can_trigger_pod_but_not_exact_claim(self):
        payload = base_payload(
            "author_hash_manifest",
            {
                "hash_manifest_entries": [
                    {
                        "paper_input_path": "/local/storage/shared/HDDatasets/graphics/dragon.ply",
                        "hash_algorithm": "sha256",
                        "hash_value": "a" * 64,
                        "input_bytes_available": True,
                    }
                ],
                "archive": None,
                "regeneration_script": None,
                "acm_supplement_listing": None,
                "exact_equivalence_verdict": None,
                "freeform_notes": "",
            },
        )
        result = self.validator.classify_intake(payload)
        self.assertTrue(result["valid"])
        self.assertTrue(result["pod_expected"])
        self.assertEqual(result["next_action"], "hashes_with_candidate_bytes__verify_hashes_then_pod_gate")
        self.assertFalse(result["sufficient_to_claim_exact_input"])
        self.assertFalse(result["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])

    def test_hash_manifest_without_bytes_does_not_trigger_pod(self):
        payload = base_payload(
            "author_hash_manifest",
            {
                "hash_manifest_entries": [
                    {
                        "logical_workload_row": "graphics_dragon_happy",
                        "hash_algorithm": "sha256",
                        "hash_value": "b" * 64,
                    }
                ],
                "archive": None,
                "regeneration_script": None,
                "acm_supplement_listing": None,
                "exact_equivalence_verdict": None,
                "freeform_notes": "",
            },
        )
        result = self.validator.classify_intake(payload)
        self.assertTrue(result["valid"])
        self.assertFalse(result["pod_expected"])
        self.assertEqual(result["next_action"], "hashes_only__compare_or_request_bytes_before_pod")

    def test_archive_response_triggers_pod_after_hash_recording(self):
        payload = base_payload(
            "author_input_archive",
            {
                "hash_manifest_entries": [],
                "archive": {
                    "filename": "HDDatasets.tar.zst",
                    "sha256": "c" * 64,
                    "redistribution_boundary": "private",
                    "extraction_policy": "extract outside public repo",
                    "file_listing": ["graphics/dragon.ply"],
                },
                "regeneration_script": None,
                "acm_supplement_listing": None,
                "exact_equivalence_verdict": None,
                "freeform_notes": "",
            },
        )
        result = self.validator.classify_intake(payload)
        self.assertTrue(result["valid"])
        self.assertTrue(result["pod_expected"])
        self.assertTrue(result["claim_boundary"]["external_artifacts_acquired"])
        self.assertFalse(result["sufficient_to_claim_exact_input"])

    def test_acm_listing_no_artifact_is_valid_but_no_pod(self):
        payload = base_payload(
            "acm_supplement_artifact_instructions",
            {
                "hash_manifest_entries": [],
                "archive": None,
                "regeneration_script": None,
                "acm_supplement_listing": {
                    "top_level_files": ["camera-ready.pdf"],
                    "contains_artifact_material": False,
                },
                "exact_equivalence_verdict": None,
                "freeform_notes": "",
            },
        )
        result = self.validator.classify_intake(payload)
        self.assertTrue(result["valid"])
        self.assertFalse(result["pod_expected"])
        self.assertTrue(result["claim_boundary"]["acm_supplement_inspected"])
        self.assertEqual(result["next_action"], "acm_listing_inspected_no_actionable_artifact__keep_blocked")

    def test_exact_equivalence_acceptance_triggers_bounded_pod_but_not_exact_claim_by_itself(self):
        payload = base_payload(
            "exact_equivalence_verdict",
            {
                "hash_manifest_entries": [],
                "archive": None,
                "regeneration_script": None,
                "acm_supplement_listing": None,
                "exact_equivalence_verdict": {
                    "decision": "accepted_as_exact_equivalent_with_named_boundary",
                    "reviewed_reconstruction": "WaterBodies/BG public reconstruction",
                    "accepted_claim_name": "bounded_public_reconstruction_exact_equivalent",
                    "accepted_denominator": "full-public WaterBodies/BG n_points_cell=8",
                },
                "freeform_notes": "",
            },
        )
        result = self.validator.classify_intake(payload)
        self.assertTrue(result["valid"])
        self.assertTrue(result["pod_expected"])
        self.assertTrue(result["claim_boundary"]["exact_equivalence_accepted"])
        self.assertFalse(result["sufficient_to_claim_exact_input"])
        self.assertFalse(result["claim_boundary"]["full_paper_reproduction_claimed"])

    def test_cli_exit_code_and_output_file(self):
        payload = base_payload(
            "explicit_non_availability_statement",
            {
                "hash_manifest_entries": [],
                "archive": None,
                "regeneration_script": None,
                "acm_supplement_listing": None,
                "exact_equivalence_verdict": None,
                "freeform_notes": "Authors cannot share data or hashes.",
            },
        )
        with tempfile.TemporaryDirectory() as td:
            inp = pathlib.Path(td) / "response.json"
            out = pathlib.Path(td) / "validated.json"
            inp.write_text(json.dumps(payload), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(inp), "--output", str(out)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(result["valid"])
            self.assertFalse(result["pod_expected"])
            self.assertEqual(result["next_action"], "non_availability_statement__keep_blocked")

    def test_goal5330_summary_records_fail_closed_contract(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "external_response_intake_validator_ready__await_response")
        self.assertEqual(summary["validator_contract"]["invalid_exit_code"], 2)
        self.assertEqual(summary["validator_contract"]["default_behavior"], "fail_closed")
        self.assertIn("sufficient_to_claim_exact_input", summary["classification_outputs"])
        self.assertFalse(summary["claim_boundary"]["external_response_received"])
        self.assertFalse(summary["claim_boundary"]["pod_execution_claimed"])


if __name__ == "__main__":
    unittest.main()
