import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5432_public_artifact_live_refresh.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5432_public_artifact_live_refresh.py"
)


class Goal5432PublicArtifactLiveRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_summary_schema_and_status(self) -> None:
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5432.public_artifact_live_refresh.v1",
        )
        self.assertEqual(payload["goal"], "Goal5432")
        self.assertIn("public_artifact_refresh", payload["status"])
        self.assertEqual(
            payload["input_context"]["current_strongest_candidate"],
            "WaterBodies->BlockGroups Level-B public reconstruction, not exact paper input",
        )

    def test_claim_boundary_preserves_no_exact_or_pod_claims(self) -> None:
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["public_artifact_refresh_claimed"])
        self.assertFalse(boundary["external_artifacts_acquired"])
        self.assertFalse(boundary["exact_equivalence_accepted"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["pod_execution_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])

    def test_acm_supplement_not_inspected_without_zip_bytes(self) -> None:
        acm = self.summary["live_surfaces"]["acm_supplement"]
        self.assertEqual(acm["artifact_name"], "ics26-106.zip")
        self.assertFalse(acm["downloaded_or_zip_magic_observed"])
        self.assertFalse(self.summary["classification"]["acm_supplement_inspected"])
        self.assertFalse(self.summary["claim_boundary"]["acm_supplement_inspected"])
        self.assertGreaterEqual(len(acm["checks"]), 2)
        for check in acm["checks"]:
            self.assertFalse(check["range_get"]["zip_magic_observed"])

    def test_crossref_and_github_do_not_expose_exact_input_artifact(self) -> None:
        classification = self.summary["classification"]
        self.assertFalse(classification["crossref_has_dataset_or_artifact_link"])
        self.assertFalse(classification["github_has_release_assets"])
        self.assertFalse(classification["github_has_dataset_archive_release"])
        self.assertFalse(classification["github_has_root_data_directory"])
        self.assertFalse(classification["github_has_likely_input_dataset_blob"])
        self.assertFalse(classification["new_public_exact_input_artifact_found"])
        self.assertFalse(classification["exact_input_blocker_removed"])

        github = self.summary["live_surfaces"]["github"]
        self.assertEqual(github["full_name"], "pwrliang/X-HD")
        self.assertEqual(github["release_count"], 0)
        self.assertIn("main", github["branches"])
        self.assertIn("paper", github["branches"])
        self.assertIn("hybrid", github["branches"])
        self.assertIn("source_scripts_logs_only", github["interpretation"])

    def test_stop_loss_gate_fields_present_and_passing(self) -> None:
        gate = self.summary["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertIn("public artifact", gate["gate_non_app_consumer"].lower())
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

    def test_script_is_public_refresh_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)
        self.assertIn("api.github.com/repos/pwrliang/X-HD", source)
        self.assertIn("api.crossref.org/works", source)


if __name__ == "__main__":
    unittest.main()
