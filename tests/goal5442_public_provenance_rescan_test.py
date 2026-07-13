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
    / "run_xhd_goal5442_public_provenance_rescan.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5442_public_provenance_rescan.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5442_public_provenance_rescan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5442PublicProvenanceRescanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_schema_and_status_are_public_provenance_only(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5442.public_provenance_rescan.v1",
        )
        self.assertEqual(payload["goal"], "Goal5442")
        self.assertIn("public_provenance_rescan", payload["status"])
        self.assertFalse(payload["classification"]["exact_input_blocker_removed"])
        self.assertFalse(payload["interpretation"]["pod_expected_next"])

    def test_public_observations_do_not_become_exact_input_evidence(self) -> None:
        observations = self.payload["public_web_observations"]
        self.assertGreaterEqual(len(observations), 4)
        surfaces = "\n".join(row["surface"] for row in observations)
        self.assertIn("ACM proceedings", surfaces)
        self.assertIn("GitHub repository", surfaces)
        self.assertIn("ArcGIS USA Detailed Water Bodies", surfaces)
        for row in observations:
            self.assertFalse(row["exact_input_evidence"], row)
            self.assertIn("reason_not_exact", row)

    def test_live_refresh_classification_is_carried_forward(self) -> None:
        embedded = self.payload["live_refresh_embedded"]
        self.assertEqual(
            embedded["schema"],
            "rtdl.paper_reproduction.xhd.goal5432.public_artifact_live_refresh.v1",
        )
        classification = self.payload["classification"]
        self.assertTrue(classification["acm_zip_listing_observed"])
        self.assertTrue(classification["github_public_source_repo_present"])
        self.assertTrue(classification["arcgis_source_candidates_present"])
        self.assertFalse(classification["arcgis_source_candidates_are_exact_author_inputs"])
        self.assertEqual(
            classification["new_public_exact_input_artifact_found"],
            embedded["classification"]["new_public_exact_input_artifact_found"],
        )

    def test_claim_boundary_preserves_no_exact_or_runtime_claims(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["public_provenance_rescan_claimed"])
        for key in [
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

    def test_stop_loss_gate_fields_pass_and_script_does_not_run_routes(self) -> None:
        gate = self.payload["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertIn("public provenance", gate["gate_non_app_consumer"])
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)
        self.assertNotIn("hd_exec", source)


if __name__ == "__main__":
    unittest.main()
