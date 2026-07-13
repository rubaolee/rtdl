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
    / "build_xhd_goal5434_external_action_packet.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5434_water_bg_external_action_packet.json"
)
PACKET = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "requests"
    / "water_bg_external_action_packet.md"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5434_action_packet", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5434WaterBgExternalActionPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.packet = PACKET.read_text(encoding="utf-8")

    def test_summary_schema_status_and_workflow(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5434.water_bg_external_action_packet.v1",
        )
        self.assertEqual(payload["goal"], "Goal5434")
        self.assertEqual(payload["status"], "water_bg_external_action_packet_ready__prepared_not_sent")
        self.assertEqual(
            payload["action_packet"],
            "Paper-reproduction-apps/x-hd-paper/requests/water_bg_external_action_packet.md",
        )
        self.assertIn("goal5430", payload["inputs"])
        self.assertIn("goal5433", payload["inputs"])
        workflow = payload["included_workflow"]
        self.assertTrue(workflow["send_or_review_author_request"].endswith("author_water_bg_input_hash_request.md"))
        self.assertTrue(workflow["send_or_review_exact_equivalence_request"].endswith("water_bg_exact_equivalence_review_request.md"))
        self.assertTrue(workflow["classify_response_script"].endswith("classify_xhd_goal5433_water_bg_external_response.py"))

    def test_packet_contains_current_evidence_and_fail_closed_instructions(self) -> None:
        text = self.packet
        self.assertIn("Status: `prepared_not_sent`", text)
        self.assertIn("input_identity_level = level_b_full_public_same_source_geo_not_exact_file_hash", text)
        self.assertIn("This is strong Level-B public-reconstruction evidence", text)
        self.assertIn("It is **not** exact", text)
        self.assertIn("0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39", text)
        self.assertIn("8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e", text)
        self.assertIn("public_artifact_refresh_no_new_exact_input_path__acm_supplement_still_uninspected", text)
        self.assertIn("new_public_exact_input_artifact_found = false", text)
        self.assertIn("author_water_bg_input_hash_request.md", text)
        self.assertIn("water_bg_exact_equivalence_review_request.md", text)
        self.assertIn("classify_xhd_goal5433_water_bg_external_response.py --input <response.json>", text)
        self.assertIn("Keep Level-B if:", text)
        self.assertIn("hashes do not match current public reconstruction", text)

    def test_claim_boundary_keeps_all_external_and_pod_claims_false(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["external_action_packet_prepared"])
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
            self.assertIn(f"{key} = false", self.packet)

    def test_stop_loss_fields_pass_and_name_non_app_consumer(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "external action packet / response classification workflow",
        )
        self.assertFalse(stop_loss["gate_requires_app_specific_logic"])
        self.assertTrue(stop_loss["gate_downstream_consumer_reachable"])
        self.assertIn("gate_generic_capability_produced: true", self.packet)
        self.assertIn("gate_requires_app_specific_logic: false", self.packet)
        self.assertIn("gate_downstream_consumer_reachable: true", self.packet)

    def test_builder_does_not_run_pod_author_or_routes(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)
        self.assertNotIn("hd_exec", source)


if __name__ == "__main__":
    unittest.main()
