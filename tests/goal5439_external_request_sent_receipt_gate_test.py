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
    / "run_xhd_goal5439_external_request_sent_receipt_gate.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5439_external_request_sent_receipt_gate.json"
)
MANIFEST = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5438_external_request_send_manifest.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5439_sent_receipt_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _manifest_item() -> dict:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in payload["items"]:
        if item["id"] == "water_bg_author_hash_request":
            return item
    raise AssertionError("water_bg_author_hash_request missing from Goal5438 manifest")


def _valid_receipt() -> dict:
    item = _manifest_item()
    return {
        "schema": "rtdl.paper_reproduction.xhd.external_request_send_receipt.v1",
        "status": "sent_receipt_recorded_for_test",
        "request_id": item["id"],
        "request_path": item["path"],
        "request_sha256_at_send_time": item["sha256"],
        "sent": True,
        "sent_at_utc": "2026-07-10T12:00:00Z",
        "sent_by": "unit-test",
        "channel": "manual-test",
        "recipient_or_reviewer": "test-recipient",
        "subject_or_thread": "test-thread",
        "raw_message_committed": False,
        "privacy_notes": "synthetic receipt",
        "expected_response_intake": "Normalize responses into requests/incoming.",
        "claim_boundary": {
            "request_sent_claimed": True,
            "external_response_received": False,
            "external_artifacts_acquired": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
    }


class Goal5439ExternalRequestSentReceiptGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main([])
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_current_sent_dir_is_empty_and_claims_no_send(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5439.external_request_sent_receipt_gate.v1",
        )
        self.assertEqual(payload["status"], "external_request_sent_receipt_gate_empty__no_request_sent")
        self.assertEqual(payload["receipt_count"], 0)
        self.assertEqual(payload["valid_receipt_count"], 0)
        self.assertEqual(payload["invalid_receipt_count"], 0)
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["sent_receipt_gate_scanned"])
        self.assertFalse(boundary["request_sent_claimed"])
        for key in [
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

    def test_valid_receipt_claims_sent_but_not_response_or_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sent_water_bg_author_hash_request.json"
            path.write_text(json.dumps(_valid_receipt()), encoding="utf-8")
            payload = self.module.build_sent_receipt_gate(Path(tmp), MANIFEST)
        self.assertEqual(payload["status"], "external_request_sent_receipts_valid__await_response_intake")
        self.assertEqual(payload["receipt_count"], 1)
        self.assertEqual(payload["valid_receipt_count"], 1)
        self.assertEqual(payload["invalid_receipt_count"], 0)
        self.assertEqual(payload["valid_request_ids"], ["water_bg_author_hash_request"])
        self.assertTrue(payload["claim_boundary"]["request_sent_claimed"])
        self.assertFalse(payload["claim_boundary"]["external_response_received"])
        self.assertFalse(payload["claim_boundary"]["external_artifacts_acquired"])
        self.assertFalse(payload["pod_usage"]["used"])
        self.assertFalse(payload["pod_usage"]["expected_next"])

    def test_hash_mismatch_invalidates_receipt_and_send_claim(self) -> None:
        receipt = _valid_receipt()
        receipt["request_sha256_at_send_time"] = "0" * 64
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_hash.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            payload = self.module.build_sent_receipt_gate(Path(tmp), MANIFEST)
        self.assertEqual(payload["status"], "external_request_sent_receipts_invalid__fix_before_response_claim")
        self.assertEqual(payload["invalid_receipt_count"], 1)
        self.assertFalse(payload["claim_boundary"]["request_sent_claimed"])
        self.assertIn(
            "request_sha256_at_send_time_does_not_match_manifest",
            payload["receipts"][0]["errors"],
        )

    def test_missing_required_sent_fields_invalidates_receipt(self) -> None:
        receipt = _valid_receipt()
        del receipt["sent_at_utc"]
        receipt["channel"] = ""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing_fields.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            payload = self.module.build_sent_receipt_gate(Path(tmp), MANIFEST)
        self.assertEqual(payload["status"], "external_request_sent_receipts_invalid__fix_before_response_claim")
        errors = payload["receipts"][0]["errors"]
        self.assertIn("missing_or_empty_sent_at_utc", errors)
        self.assertIn("missing_or_empty_channel", errors)
        self.assertFalse(payload["claim_boundary"]["request_sent_claimed"])

    def test_template_receipt_is_invalid(self) -> None:
        template = {
            "schema": "rtdl.paper_reproduction.xhd.external_request_send_receipt.v1",
            "status": "template_not_a_receipt",
            "sent": False,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "template.json"
            path.write_text(json.dumps(template), encoding="utf-8")
            payload = self.module.build_sent_receipt_gate(Path(tmp), MANIFEST)
        self.assertEqual(payload["status"], "external_request_sent_receipts_invalid__fix_before_response_claim")
        errors = payload["receipts"][0]["errors"]
        self.assertIn("template_not_a_receipt", errors)
        self.assertIn("sent_is_not_true", errors)

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "external request sent-receipt gate / response intake workflow",
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
