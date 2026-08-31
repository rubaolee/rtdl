import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5446_external_artifact_dropbox_gate.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5446_external_artifact_dropbox_gate.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5446_dropbox_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5446ExternalArtifactDropboxGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main([])
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_default_dropbox_is_empty_and_fail_closed(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5446.external_artifact_dropbox_gate.v1",
        )
        self.assertEqual(payload["status"], "external_artifact_dropbox_empty__await_authorized_artifact")
        self.assertEqual(payload["artifact_candidate_count"], 0)
        self.assertFalse(payload["exact_input_blocker_removed"])
        self.assertFalse(payload["pod_expected_next"])
        self.assertFalse(payload["claim_boundary"]["pod_execution_claimed"])
        self.assertFalse(payload["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])

    def test_acm_zip_candidate_gets_inspector_next_gate_but_no_pod(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            dropbox = Path(td) / "artifacts"
            dropbox.mkdir()
            zip_path = dropbox / "ics26-106.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("artifact/README.md", "synthetic")
            payload = self.module.build_gate(dropbox)
        self.assertEqual(payload["status"], "external_artifact_dropbox_candidates_present__requires_intake_gate")
        self.assertEqual(payload["artifact_candidate_count"], 1)
        record = payload["records"][0]
        self.assertEqual(record["kind"], "acm_or_supplement_zip_candidate")
        self.assertTrue(record["is_zipfile"])
        self.assertEqual(
            record["recommended_next_gate"],
            "inspect_xhd_acm_supplement_zip_then_acm_artifact_instruction_ingestion_if_actionable",
        )
        self.assertFalse(record["pod_allowed_from_this_record"])
        self.assertFalse(record["claim_exact_input_from_this_record"])
        self.assertFalse(payload["pod_usage"]["expected_next"])

    def test_json_candidate_routes_to_response_intake_but_no_claim(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            dropbox = Path(td) / "artifacts"
            dropbox.mkdir()
            (dropbox / "response.json").write_text("{}", encoding="utf-8")
            payload = self.module.build_gate(dropbox)
        self.assertEqual(payload["artifact_candidate_count"], 1)
        record = payload["records"][0]
        self.assertEqual(record["kind"], "normalized_or_raw_json_candidate")
        self.assertEqual(record["recommended_next_gate"], "validate_or_ingest_external_response_json_before_any_pod_gate")
        self.assertFalse(payload["exact_input_blocker_removed"])
        self.assertFalse(payload["claim_boundary"]["exact_equivalence_accepted"])

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "external artifact dropbox gate / intake workflow",
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
