import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5334_public_artifact_refresh.json"
)


class Goal5334PublicArtifactRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_refresh_keeps_exact_input_blocked(self):
        s = self.summary
        self.assertEqual(
            s["exit_label"],
            "public_artifact_refresh_no_new_exact_input_path__external_response_chain_still_needed",
        )
        self.assertEqual(s["interpretation"]["exact_input_provenance_status"], "still_blocked")
        self.assertTrue(s["interpretation"]["external_request_outbox_still_needed"])
        self.assertTrue(s["interpretation"]["response_intake_chain_still_needed"])
        self.assertFalse(s["public_search_refresh"]["new_exact_input_dataset_found"])

    def test_acm_supplement_still_unresolved_not_inspected(self):
        checks = self.summary["direct_url_refresh"]
        self.assertEqual(len(checks), 2)
        for check in checks:
            self.assertIn("ics26-106.zip", check["url"])
            self.assertEqual(check["observed_status"], 403)
            self.assertFalse(check["downloaded"])
        self.assertEqual(
            self.summary["interpretation"]["acm_supplement_status"],
            "visible_but_not_publicly_downloadable_from_current_environment",
        )
        self.assertFalse(self.summary["claim_boundary"]["acm_supplement_inspected"])

    def test_crossref_and_github_do_not_expose_dataset_artifact(self):
        crossref = self.summary["crossref_refresh"]
        self.assertEqual(crossref["doi"], "10.1145/3797905.3800509")
        self.assertEqual(crossref["link_count"], 1)
        self.assertFalse(crossref["dataset_or_artifact_link_found"])
        self.assertEqual(crossref["relation_keys"], [])
        github = self.summary["github_refresh"]
        self.assertEqual(github["release_count"], 0)
        self.assertFalse(github["root_data_directory_found"])
        self.assertFalse(github["dataset_archive_release_found"])
        self.assertIn("expr", github["root_entries"])
        self.assertIn("src", github["root_entries"])

    def test_claim_and_pod_boundaries(self):
        boundary = self.summary["claim_boundary"]
        for key, value in boundary.items():
            self.assertFalse(value, key)
        self.assertFalse(self.summary["pod_usage"]["used"])
        self.assertFalse(self.summary["pod_usage"]["expected_next"])
        forbidden = "\n".join(self.summary["not_allowed"])
        self.assertIn("contains datasets", forbidden)
        self.assertIn("contains no useful artifacts", forbidden)
        self.assertIn("all public publication-adjacent artifacts are exhausted", forbidden)


if __name__ == "__main__":
    unittest.main()
