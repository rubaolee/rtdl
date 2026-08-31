from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5323_external_author_artifact_availability_sweep.json"
)


class Goal5323ExternalAuthorArtifactAvailabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_claim_boundary_remains_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["external_author_availability_search_claimed"])
        self.assertFalse(boundary["external_author_dataset_artifacts_found"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertFalse(boundary["pod_execution_claimed"])

    def test_github_repository_metadata_records_no_release_or_lfs_manifest(self) -> None:
        repo = self.payload["github_repository_checked"]
        self.assertEqual(repo["full_name"], "pwrliang/X-HD")
        self.assertEqual(repo["default_branch"], "main")
        self.assertEqual(
            repo["branches"]["main"],
            "7bf41c8442d059c94f4178355c6d5a10571d9658",
        )
        self.assertEqual(
            repo["branches"]["paper"],
            "8c3846866052e1e8755210021f23fac2cbe8c3d6",
        )
        self.assertEqual(repo["release_count"], 0)
        self.assertEqual(
            repo["gitattributes_status"],
            "absent_404_no_lfs_pointer_manifest_found",
        )
        self.assertIn("*.zip", repo["gitignore_ignores"])
        self.assertIn("*.pkl", repo["gitignore_ignores"])

    def test_repository_tree_is_source_and_logs_without_dataset_blobs(self) -> None:
        tree = self.payload["github_tree_recursive_sweep"]
        self.assertEqual(tree["ref"], "main")
        self.assertGreaterEqual(tree["total_paths"], 400)
        self.assertEqual(tree["data_like_paths"], [])
        self.assertEqual(tree["input_dataset_blob_extensions_found"], [])
        self.assertGreater(tree["expr_log_json_count"], 0)
        self.assertIn("expr/run_fig5.sh", tree["expr_directory_contents"])
        self.assertIn("expr/logs/", tree["expr_directory_contents"])
        self.assertEqual(
            tree["classification"],
            "source_scripts_and_checked_in_logs_present__exact_input_dataset_blobs_absent",
        )

    def test_readme_has_cli_contract_but_no_dataset_download_contract(self) -> None:
        readme = self.payload["github_repository_checked"]["readme_contract"]
        self.assertTrue(readme["contains_hd_exec_cli_example"])
        self.assertTrue(readme["states_variant_rt_is_xhd_algorithm"])
        self.assertFalse(readme["contains_dataset_download_links"])
        self.assertFalse(readme["contains_hddatasets_download_instructions"])

    def test_local_assets_remain_level_b_not_author_hddatasets(self) -> None:
        local = self.payload["local_workspace_artifacts_checked"]
        self.assertTrue(local["external_stanford_assets_present"])
        self.assertTrue(local["generated_wkt_assets_present"])
        self.assertFalse(local["external_stanford_assets_are_author_hddatasets"])
        self.assertFalse(local["generated_wkt_assets_are_author_hddatasets"])
        self.assertFalse(local["current_pod_hddatasets_root_present"])
        self.assertIn("level_b", local["external_stanford_assets_classification"])

    def test_exit_label_and_forbidden_claims(self) -> None:
        self.assertEqual(
            self.payload["exit_label"],
            "external_author_dataset_artifacts_not_found__repo_source_logs_only",
        )
        classification = self.payload["classification"]
        self.assertEqual(
            classification["current_level"],
            "public_author_repo_source_logs_only__exact_input_artifacts_absent",
        )
        self.assertFalse(
            classification[
                "statistics_logs_paths_or_public_repo_presence_sufficient_for_exact"
            ]
        )
        forbidden = "\n".join(self.payload["not_allowed"])
        self.assertIn("public GitHub repository contains exact paper input datasets", forbidden)
        self.assertIn("full X-HD paper reproduction", forbidden)
        self.assertIn("author-vs-RTDL performance ratio", forbidden)

    def test_no_pod_required_for_this_sweep(self) -> None:
        pod = self.payload["pod_usage"]
        self.assertFalse(pod["used"])
        self.assertFalse(pod["expected_next"])
        self.assertIn("provenance", pod["reason"])
        actions = self.payload["recommended_next_actions"]
        self.assertFalse(actions[0]["requires_pod"])
        self.assertFalse(actions[1]["requires_pod"])
        self.assertTrue(actions[3]["requires_pod"])


if __name__ == "__main__":
    unittest.main()
