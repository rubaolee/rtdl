import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5346_external_artifact_surface_refresh.json"
)


class Goal5346XhdExternalArtifactSurfaceRefreshTest(unittest.TestCase):
    def test_refresh_keeps_exact_input_blocker_closed(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(
            summary["schema"],
            "rtdl.paper_reproduction.xhd.goal5346.external_artifact_surface_refresh.v1",
        )
        self.assertEqual(
            summary["exit_label"],
            "external_artifact_surface_refresh_no_new_exact_input__acm_still_forbidden",
        )
        self.assertFalse(summary["interpretation"]["new_exact_input_artifact_found"])
        self.assertFalse(summary["interpretation"]["exact_input_blocker_removed"])

    def test_acm_probe_still_forbidden_and_uninspected(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        acm = summary["acm_live_probe"]
        self.assertEqual(acm["classification"], "acm_supplement_visible_but_forbidden_from_current_environment")
        self.assertEqual(acm["head_statuses"], [403, 403, 403])
        self.assertEqual(acm["range_get_statuses"], [403, 403, 403])
        self.assertFalse(acm["zip_magic_observed"])
        self.assertFalse(summary["claim_boundary"]["acm_supplement_inspected"])

    def test_github_probe_has_no_release_or_data_directory(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        github = summary["github_live_probe"]
        self.assertEqual(github["full_name"], "pwrliang/X-HD")
        self.assertEqual(github["public_release_count"], 0)
        self.assertFalse(github["data_directory_found"])
        self.assertIn("expr/", github["top_level_contents"])
        self.assertIn("src/", github["top_level_contents"])
        self.assertIn("main", github["branches"])
        self.assertIn("paper", github["branches"])
        self.assertIn("hybrid", github["branches"])

    def test_claim_boundaries_forbid_reproduction_claims(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        boundary = summary["claim_boundary"]
        self.assertFalse(boundary["same_input_gate_passed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["pod_execution_claimed"])


if __name__ == "__main__":
    unittest.main()
