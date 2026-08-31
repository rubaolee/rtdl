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
    / "build_xhd_goal5443_acm_supplement_access_gate.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5443_acm_supplement_access_gate.json"
)
RAW_PROBE = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5443_acm_supplement_live_access_retry.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5443_acm_access_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5443AcmSupplementAccessGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.raw = json.loads(RAW_PROBE.read_text(encoding="utf-8"))

    def test_status_matches_current_forbidden_probe(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5443.acm_supplement_access_gate.v1",
        )
        self.assertEqual(
            payload["status"],
            "acm_supplement_access_gate_forbidden__external_access_still_needed",
        )
        self.assertFalse(payload["classification"]["current_environment_can_download_zip"])
        self.assertFalse(payload["classification"]["exact_input_blocker_removed"])
        self.assertFalse(payload["classification"]["pod_expected_next"])

    def test_raw_probe_was_forbidden_html_without_zip_magic(self) -> None:
        summary = self.payload["raw_probe_summary"]
        self.assertEqual(summary["classification"], self.raw["classification"])
        self.assertEqual(summary["classification"], "acm_supplement_visible_but_forbidden_from_current_environment")
        self.assertEqual(summary["url_count"], 3)
        self.assertEqual(summary["head_statuses"], [403, 403, 403])
        self.assertEqual(summary["range_get_statuses"], [403, 403, 403])
        self.assertFalse(summary["zip_magic_observed"])
        self.assertTrue(summary["all_current_attempts_forbidden"])

    def test_claim_boundary_preserves_no_inspection_or_runtime_claims(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["acm_access_gate_claimed"])
        for key in [
            "acm_supplement_inspected",
            "zip_contents_inspected",
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

    def test_existing_zip_inspector_chain_is_named_as_next_step_only(self) -> None:
        sources = self.payload["source_artifacts"]
        self.assertIn("inspect_xhd_acm_supplement_zip.py", sources["local_zip_inspector"])
        self.assertIn("run_xhd_acm_artifact_to_packet_pipeline.py", sources["artifact_ingestion_pipeline"])
        self.assertIn("authorized ACM access", self.payload["interpretation"]["next_action"])
        self.assertIn("POD cannot inspect", self.payload["interpretation"]["reason_pod_not_expected"])

    def test_stop_loss_fields_pass_and_builder_does_not_run_routes(self) -> None:
        gate = self.payload["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertIn("ACM supplement access gate", gate["gate_non_app_consumer"])
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("hd_exec", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)


if __name__ == "__main__":
    unittest.main()
