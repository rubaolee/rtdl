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
    / "build_xhd_goal5445_external_action_dispatch_bundle.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5445_external_action_dispatch_bundle.json"
)
SOURCE_MANIFEST = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5438_external_request_send_manifest.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5445_dispatch_bundle", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5445ExternalActionDispatchBundleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.source_manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        cls.bundle_index = json.loads((ROOT / cls.payload["bundle_index"]).read_text(encoding="utf-8"))
        cls.bundle_readme = (ROOT / cls.payload["bundle_readme"]).read_text(encoding="utf-8")

    def test_bundle_ready_but_not_sent(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5445.external_action_dispatch_bundle.v1",
        )
        self.assertEqual(payload["status"], "external_action_dispatch_bundle_ready__not_sent")
        self.assertEqual(payload["ready_external_request_count"], 4)
        self.assertEqual(payload["receipt_stub_count"], 4)
        self.assertFalse(payload["request_sent_claimed"])
        self.assertFalse(payload["external_response_received"])
        self.assertFalse(payload["exact_input_blocker_removed"])
        self.assertFalse(payload["pod_expected_next"])
        self.assertFalse(payload["claim_boundary"]["request_sent_claimed"])
        self.assertFalse(payload["claim_boundary"]["pod_execution_claimed"])

    def test_bundle_index_matches_result(self) -> None:
        self.assertEqual(self.bundle_index["schema"], self.payload["schema"])
        self.assertEqual(
            [item["id"] for item in self.bundle_index["sendable_requests"]],
            [item["id"] for item in self.payload["sendable_requests"]],
        )

    def test_sendable_requests_have_receipt_stubs_with_prepare_hashes(self) -> None:
        manifest_items = {item["id"]: item for item in self.source_manifest["items"]}
        self.assertEqual(
            [item["id"] for item in self.payload["sendable_requests"]],
            [
                "general_author_input_provenance_request",
                "general_acm_supplement_inspection_request",
                "water_bg_author_hash_request",
                "water_bg_exact_equivalence_review_request",
            ],
        )
        for item in self.payload["sendable_requests"]:
            source = manifest_items[item["id"]]
            self.assertTrue(source["sendable_external"])
            self.assertEqual(item["sha256"], source["sha256"])
            self.assertFalse(item["sent_claimed"])
            stub = json.loads((ROOT / item["receipt_stub_path"]).read_text(encoding="utf-8"))
            self.assertEqual(stub["schema"], "rtdl.paper_reproduction.xhd.external_request_send_receipt.v1")
            self.assertEqual(stub["status"], "stub_not_a_receipt")
            self.assertEqual(stub["request_id"], item["id"])
            self.assertEqual(stub["request_path"], item["path"])
            self.assertEqual(stub["request_sha256_at_prepare_time"], source["sha256"])
            self.assertIsNone(stub["request_sha256_at_send_time"])
            self.assertFalse(stub["sent"])
            self.assertFalse(stub["claim_boundary"]["request_sent_claimed"])
            self.assertFalse(stub["claim_boundary"]["external_response_received"])
            self.assertFalse(stub["claim_boundary"]["pod_execution_claimed"])

    def test_readme_preserves_prepared_not_sent_boundary(self) -> None:
        text = self.bundle_readme
        self.assertIn("Status: `prepared_not_sent`", text)
        self.assertIn("does not claim that any request was sent", text)
        self.assertIn("request_sent_claimed = false", text)
        self.assertIn("external_response_received = false", text)
        self.assertIn("pod_execution_claimed = false", text)
        self.assertIn("gate_non_app_consumer: external action dispatch bundle / receipt workflow", text)

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "external action dispatch bundle / receipt workflow",
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
