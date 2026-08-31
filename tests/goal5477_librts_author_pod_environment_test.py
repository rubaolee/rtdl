from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "librts-paper"
    / "results"
    / "librts_goal5477_author_pod_environment.json"
)


class Goal5477LibrtsAuthorPodEnvironmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_all_author_commits_match_and_binaries_are_nonempty(self):
        self.assertTrue(all(self.payload["provenance"]["commit_matches"].values()))
        self.assertGreater(self.payload["binaries"]["query"]["size_bytes"], 1_000_000)
        self.assertGreater(self.payload["binaries"]["pip"]["size_bytes"], 1_000_000)

    def test_gpu_smoke_counts_match_existing_bounded_gates(self):
        self.assertEqual(self.payload["status"], "pinned_author_gpu_query_and_pip_smoke_passed")
        self.assertTrue(self.payload["matched"])
        self.assertEqual(self.payload["smoke"]["query_point_contains_result_count"], 5)
        self.assertEqual(self.payload["smoke"]["pip_result_count"], 4)

    def test_claims_remain_bounded_while_archive_downloads(self):
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["author_gpu_environment_ready_for_exact_input_gates"])
        self.assertFalse(boundary["exact_archive_download_completed"])
        self.assertFalse(boundary["paper_figure_reproduced"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["embree_in_scope"])


if __name__ == "__main__":
    unittest.main()
