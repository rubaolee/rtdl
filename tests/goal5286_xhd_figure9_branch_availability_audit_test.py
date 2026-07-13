import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json"
)


class Goal5286XhdFigure9BranchAvailabilityAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ARTIFACT.exists():
            raise unittest.SkipTest(f"missing artifact: {ARTIFACT}")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_no_pinned_branch_has_all_expected_figure9_variants(self):
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.figure9_branch_availability_audit.v1",
        )
        self.assertEqual(payload["goal"], "Goal5286")
        self.assertFalse(payload["decision"]["any_branch_has_all_expected_figure9_variants"])
        self.assertFalse(payload["decision"]["figure9_reproduced"])
        self.assertEqual(
            payload["decision"]["status"],
            "missing_figure9_variants_not_found_on_pinned_branches__figure9_not_reproduced",
        )
        for branch_payload in payload["branches"].values():
            self.assertFalse(
                branch_payload["run_all_auto_tune"]["all_expected_figure9_variants_present"]
            )

    def test_paper_branch_has_only_two_run_all_variants_and_checked_in_pdf(self):
        paper = self.payload["branches"]["paper"]
        run_all = paper["run_all_auto_tune"]
        files = paper["figure9_files"]

        self.assertEqual(paper["head"], "8c3846866052e1e8755210021f23fac2cbe8c3d6")
        self.assertEqual(run_all["record_count"], 1814)
        self.assertEqual(run_all["unique_pair_count"], 907)
        self.assertEqual(run_all["configs"], {
            "n_points_cell_false_max_hit_false": 907,
            "n_points_cell_true_max_hit_true": 907,
        })
        self.assertEqual(
            run_all["missing_expected_figure9_variants"],
            [
                "n_points_cell_true_max_hit_false",
                "n_points_cell_false_max_hit_true",
            ],
        )
        self.assertEqual(run_all["config_set_size_histogram"], {"2": 907})
        self.assertIsNotNone(files["plot_script"])
        self.assertIsNotNone(files["runner_script"])
        self.assertIsNotNone(files["train_script"])
        self.assertIsNotNone(files["checked_in_pdf"])
        self.assertEqual(files["checked_in_pdf"]["path"], "expr/for_the_paper/auto-tune.pdf")
        self.assertGreater(files["checked_in_pdf"]["size_bytes"], 0)

    def test_main_and_hybrid_do_not_hide_missing_variants(self):
        for branch in ("main", "hybrid"):
            branch_payload = self.payload["branches"][branch]
            run_all = branch_payload["run_all_auto_tune"]
            files = branch_payload["figure9_files"]

            self.assertEqual(run_all["record_count"], 0)
            self.assertEqual(run_all["unique_pair_count"], 0)
            self.assertEqual(run_all["configs"], {})
            self.assertEqual(run_all["observed_configs"], [])
            self.assertEqual(
                run_all["missing_expected_figure9_variants"],
                self.payload["expected_figure9_variants"],
            )
            self.assertIsNone(files["plot_script"])
            self.assertIsNone(files["runner_script"])
            self.assertIsNone(files["train_script"])
            self.assertIsNone(files["checked_in_pdf"])

    def test_checked_in_pdf_is_not_promoted_to_reproducible_denominator(self):
        payload = self.payload
        self.assertTrue(payload["decision"]["checked_in_pdf_is_reproduction_evidence_only"])
        self.assertIn("checked-in PDF equals reproducible Figure 9", payload["decision"]["forbidden_summaries"])
        self.assertFalse(payload["claim_boundary"]["figure9_reproduced"])
        self.assertFalse(payload["claim_boundary"]["rtdl_route_result_claimed"])
        self.assertFalse(payload["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
