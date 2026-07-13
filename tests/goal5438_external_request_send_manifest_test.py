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
    / "build_xhd_goal5438_external_request_send_manifest.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5438_external_request_send_manifest.json"
)
MANIFEST_MD = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "requests" / "external_request_send_manifest.md"
RECEIPT_TEMPLATE = (
    ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "requests" / "external_request_send_receipt_template.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5438_send_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5438ExternalRequestSendManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.manifest_md = MANIFEST_MD.read_text(encoding="utf-8")
        cls.receipt = json.loads(RECEIPT_TEMPLATE.read_text(encoding="utf-8"))

    def test_manifest_ready_but_not_sent(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5438.external_request_send_manifest.v1",
        )
        self.assertEqual(payload["status"], "external_request_send_manifest_ready__prepared_not_sent")
        self.assertEqual(payload["missing_item_ids"], [])
        self.assertEqual(payload["non_prepared_item_ids"], [])
        self.assertGreaterEqual(len(payload["ready_external_request_ids"]), 4)
        self.assertFalse(payload["claim_boundary"]["request_sent_claimed"])
        self.assertFalse(payload["claim_boundary"]["external_response_received"])
        self.assertFalse(payload["pod_usage"]["used"])

    def test_items_have_hashes_and_prepared_status(self) -> None:
        items = {item["id"]: item for item in self.payload["items"]}
        for required in [
            "general_author_input_provenance_request",
            "general_acm_supplement_inspection_request",
            "water_bg_author_hash_request",
            "water_bg_exact_equivalence_review_request",
            "water_bg_external_action_packet",
        ]:
            self.assertIn(required, items)
            self.assertTrue(items[required]["exists"])
            self.assertEqual(items[required]["status"], "prepared_not_sent")
            self.assertRegex(items[required]["sha256"], r"^[0-9a-f]{64}$")
            self.assertFalse(items[required]["sent_claimed"])
        self.assertFalse(items["water_bg_external_action_packet"]["sendable_external"])
        self.assertIn("water_bg_external_action_packet", self.payload["internal_packet_ids"])

    def test_receipt_template_is_not_a_receipt_and_preserves_boundary(self) -> None:
        receipt = self.receipt
        self.assertEqual(receipt["schema"], "rtdl.paper_reproduction.xhd.external_request_send_receipt.v1")
        self.assertEqual(receipt["status"], "template_not_a_receipt")
        self.assertFalse(receipt["sent"])
        self.assertFalse(receipt["claim_boundary"]["request_sent_claimed"])
        self.assertFalse(receipt["claim_boundary"]["external_response_received"])
        self.assertFalse(receipt["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])

    def test_markdown_manifest_lists_items_and_claim_boundary(self) -> None:
        text = self.manifest_md
        self.assertIn("Status: `prepared_not_sent`", text)
        self.assertIn("author_water_bg_input_hash_request.md", text)
        self.assertIn("water_bg_exact_equivalence_review_request.md", text)
        self.assertIn("request_sent_claimed = false", text)
        self.assertIn("external_response_received = false", text)
        self.assertIn("gate_non_app_consumer: external request send manifest / receipt workflow", text)

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "external request send manifest / receipt workflow",
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
