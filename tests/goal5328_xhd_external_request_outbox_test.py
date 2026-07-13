import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5328_external_request_outbox.json"
)
REQUESTS_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "requests"


class Goal5328ExternalRequestOutboxTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SUMMARY.open("r", encoding="utf-8") as f:
            cls.summary = json.load(f)

    def _read_request(self, name):
        return (REQUESTS_DIR / name).read_text(encoding="utf-8")

    def test_outbox_status_and_claim_boundary(self):
        s = self.summary
        self.assertEqual(s["status"], "external_request_outbox_ready__not_sent_by_codex")
        self.assertEqual(s["exit_label"], "external_request_outbox_ready__await_owner_send")
        self.assertTrue(s["claim_boundary"]["outbox_prepared"])
        for key in [
            "request_sent_claimed",
            "external_artifacts_acquired",
            "acm_supplement_inspected",
            "exact_equivalence_accepted",
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "full_paper_reproduction_claimed",
            "performance_ratio_claimed",
            "pod_execution_claimed",
        ]:
            self.assertFalse(s["claim_boundary"][key])

    def test_public_author_contacts_are_recorded_from_paper(self):
        emails = {entry["email"] for entry in self.summary["author_recipients"]}
        self.assertEqual(
            emails,
            {
                "liang.geng@case.edu",
                "yuan.1203@osu.edu",
                "liru@cse.ohio-state.edu",
                "fusheng.wang@stonybrook.edu",
                "zhang.574@osu.edu",
            },
        )
        self.assertTrue(all(entry["source"] == "paper_pdf_first_page" for entry in self.summary["author_recipients"]))

    def test_all_declared_outbox_files_exist_and_are_not_sent(self):
        paths = []
        for entry in self.summary["outbox_files"]:
            self.assertEqual(entry["send_status"], "prepared_not_sent")
            path = ROOT / entry["path"]
            self.assertTrue(path.exists(), entry["path"])
            paths.append(path.name)
        self.assertEqual(
            set(paths),
            {
                "author_input_provenance_request.md",
                "acm_supplement_inspection_request.md",
                "water_bg_exact_equivalence_review_request.md",
            },
        )

    def test_author_request_contains_all_required_dataset_families(self):
        text = self._read_request("author_input_provenance_request.md")
        for needle in [
            "/local/storage/shared/HDDatasets",
            "Dragon",
            "HappyBuddha",
            "AsianDragon",
            "ThaiStatuette",
            "dtl_cnty",
            "uszipcode",
            "USADetailedWaterBodies",
            "USACensusBlockGroupBoundaries",
            "lakes",
            "parks",
            "all_nodes",
            "BraTS",
            "NIfTI-to-point",
        ]:
            self.assertIn(needle, text)

    def test_acm_request_preserves_unresolved_boundary(self):
        text = self._read_request("acm_supplement_inspection_request.md")
        self.assertIn("ics26-106.zip", text)
        self.assertIn("HTTP 403", text)
        self.assertIn("We will not claim this supplement contains or lacks useful artifacts until it", text)

    def test_water_bg_review_request_is_fail_closed(self):
        text = self._read_request("water_bg_exact_equivalence_review_request.md")
        self.assertIn("accepted_as_exact_equivalent_with_named_boundary", text)
        self.assertIn("accepted_only_as_level_b_public_reconstruction", text)
        self.assertIn("rejected_keep_level_b", text)
        self.assertIn("Default without an explicit answer", text)
        self.assertIn("No author WKT hashes", text)

    def test_next_actions_require_external_response_before_pod(self):
        actions = "\n".join(item["action"] for item in self.summary["next_action_after_send"])
        self.assertIn("run one author/RTDL same-input gate", actions)
        self.assertIn("Keep full-paper claims blocked", actions)
        self.assertFalse(self.summary["pod_usage"]["used"])
        self.assertFalse(self.summary["pod_usage"]["expected_next"])


if __name__ == "__main__":
    unittest.main()
