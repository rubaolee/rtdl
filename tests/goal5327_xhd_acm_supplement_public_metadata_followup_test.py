import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5327_acm_supplement_public_metadata_followup.json"
)


class Goal5327AcmSupplementPublicMetadataFollowupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SUMMARY.open("r", encoding="utf-8") as f:
            cls.summary = json.load(f)

    def test_records_acm_supplement_as_unresolved_not_inspected(self):
        s = self.summary
        self.assertEqual(
            s["exit_label"],
            "acm_supplement_still_unresolved__no_public_metadata_or_mirror_path_found",
        )
        self.assertEqual(
            s["interpretation"]["acm_supplement_status"],
            "visible_but_not_publicly_downloadable_from_current_environment",
        )
        self.assertFalse(s["claim_boundary"]["acm_supplement_inspected"])
        self.assertTrue(s["interpretation"]["goal5326_request_package_still_needed"])

    def test_acm_urls_remain_forbidden_from_current_environment(self):
        checks = self.summary["acm_supplement_url_checks"]
        self.assertEqual(len(checks), 2)
        for check in checks:
            self.assertIn("ics26-106.zip", check["url"])
            self.assertEqual(check["observed_status"], 403)
            self.assertFalse(check["downloaded"])

    def test_crossref_metadata_has_no_dataset_or_artifact_link(self):
        meta = self.summary["crossref_doi_metadata_check"]
        self.assertEqual(meta["status"], "readable")
        self.assertEqual(meta["doi"], "10.1145/3797905.3800509")
        self.assertEqual(meta["title"], "X-HD: Fast Hausdorff Distance Computation with Ray Tracing")
        self.assertFalse(meta["dataset_or_artifact_link_found"])
        self.assertEqual(meta["relation_keys"], [])
        self.assertEqual(meta["archive"], [])
        self.assertEqual(meta["link_count"], 1)
        self.assertIn("dl.acm.org/doi/abs/10.1145/3797905.3800509", meta["links"][0]["URL"])

    def test_public_search_does_not_find_mirror_or_author_dataset_link(self):
        followup = self.summary["public_search_followup"]
        self.assertIn('"ics26-106.zip"', followup["queries"])
        self.assertFalse(followup["public_mirror_found"])
        self.assertFalse(followup["author_dataset_link_found"])
        self.assertIn("no public dataset mirror", followup["result_summary"])

    def test_claim_boundary_and_pod_boundary(self):
        boundary = self.summary["claim_boundary"]
        for key in [
            "external_artifacts_acquired",
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "full_paper_reproduction_claimed",
            "performance_ratio_claimed",
            "pod_execution_claimed",
        ]:
            self.assertFalse(boundary[key])
        self.assertFalse(self.summary["pod_usage"]["used"])
        self.assertFalse(self.summary["pod_usage"]["expected_next"])

    def test_forbidden_summaries_include_both_positive_and_negative_acm_overclaims(self):
        forbidden = "\n".join(self.summary["not_allowed"])
        self.assertIn("contains datasets", forbidden)
        self.assertIn("contains no useful artifacts", forbidden)
        self.assertIn("all publication-adjacent artifacts are exhausted", forbidden)


if __name__ == "__main__":
    unittest.main()
