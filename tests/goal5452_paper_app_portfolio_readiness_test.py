import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_APPS = ROOT / "Paper-reproduction-apps"


class Goal5452PaperAppPortfolioReadinessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(
            (PAPER_APPS / "paper_app_status_snapshot.json").read_text(
                encoding="utf-8"
            )
        )

    @staticmethod
    def _review_paths(app):
        paths = [app["review_evidence"]]
        additional = app.get("additional_review_evidence", [])
        if isinstance(additional, str):
            additional = [additional]
        return paths + additional

    def test_snapshot_covers_all_current_paper_apps_without_full_claim(self):
        apps = self.snapshot["apps"]
        self.assertEqual(
            set(apps),
            {
                "rayjoin-paper",
                "rt-barneshut-paper",
                "rt-dbscan-paper",
                "x-hd-paper",
                "librts-paper",
            },
        )
        self.assertFalse(
            self.snapshot["full_all_dataset_all_figure_reproduction_claimed"]
        )
        for app in apps.values():
            self.assertFalse(app["full_paper_reproduction_claimed"])
            self.assertTrue((ROOT / app["primary_doc"]).is_file())
            if not app["externally_reviewed_closeout"]:
                self.assertTrue(app["review_status"].endswith("review_pending"))
                continue
            self.assertTrue(app["reviewer"])
            evidence_text = []
            for review_path in self._review_paths(app):
                path = ROOT / review_path
                self.assertTrue(path.is_file(), review_path)
                evidence_text.append(path.read_text(encoding="utf-8").lower())
            combined = "\n".join(evidence_text)
            for term in app["review_identity_terms"]:
                self.assertIn(term.lower(), combined)

    def test_top_level_readme_matches_current_scoped_status(self):
        readme = (PAPER_APPS / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("Scaffold only", readme)
        self.assertIn("0.328842s", readme)
        self.assertIn("bounded authorofficial same-input gates", readme.lower())
        self.assertIn("Same-input directed input1-to-input2", readme)
        self.assertIn("LibRTS paper", readme)
        self.assertIn("No current app claims complete reproduction", readme)

    def test_xhd_manifest_uses_externally_approved_scoped_closeout(self):
        manifest = json.loads(
            (PAPER_APPS / "x-hd-paper" / "data" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            manifest["reproduction_scope"]["status"],
            "xhd_same_input_directed_hdresult_reproduction_complete__externally_reviewed_and_approved",
        )

    def test_rt_barneshut_manifest_matches_final_phase_boundary_packet(self):
        manifest = json.loads(
            (
                PAPER_APPS
                / "rt-barneshut-paper"
                / "data"
                / "manifest.json"
            ).read_text(encoding="utf-8")
        )
        status = manifest["current_rtdl_status"]
        self.assertTrue(status["bounded_same_input_reproduction_complete"])
        self.assertFalse(status["paper_reproduction_complete"])
        self.assertEqual(status["same_input_author_rtdl_match"]["mismatch_count"], 0)
        self.assertAlmostEqual(
            status["performance_phase_context"][
                "prep_plus_kernel_ratio_rtdl_over_author_reported_envelope"
            ],
            2.530902373428573,
        )


if __name__ == "__main__":
    unittest.main()
