from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
V08_DIR = REPO_ROOT / "docs" / "release_reports" / "v0_8"


class Goal530V08ReleaseCandidatePackageTest(unittest.TestCase):
    def test_release_candidate_files_exist(self) -> None:
        for name in (
            "README.md",
            "release_statement.md",
            "support_matrix.md",
            "audit_report.md",
            "tag_preparation.md",
        ):
            with self.subTest(name=name):
                self.assertTrue((V08_DIR / name).is_file())

    def test_release_statement_preserves_v08_boundaries(self) -> None:
        text = (V08_DIR / "release_statement.md").read_text(encoding="utf-8")

        self.assertIn("release candidate / not yet tagged", text)
        self.assertIn("current released version remains `v0.7.0`", text)
        self.assertIn("RTDL emits rows; Python turns those rows into an application answer", text)
        self.assertIn("Goal528: macOS post-doc-refresh local audit", text)
        self.assertIn("Goal529: Linux post-doc-refresh validation", text)
        self.assertIn("does not claim", text)
        self.assertIn("Stage-1 proximity apps beat SciPy, scikit-learn, FAISS", text)

    def test_support_matrix_lists_all_six_apps_and_backend_boundaries(self) -> None:
        text = (V08_DIR / "support_matrix.md").read_text(encoding="utf-8")

        for app_name in (
            "Hausdorff distance",
            "ANN candidate search",
            "Outlier detection",
            "DBSCAN clustering",
            "Robot collision screening",
            "Barnes-Hut force approximation",
        ):
            with self.subTest(app_name=app_name):
                self.assertIn(app_name, text)

        self.assertIn("Robot collision screening | yes | yes | yes | yes | no", text)
        self.assertIn("Goal529 public command harnesses pass `88/88`", text)
        self.assertIn("not a full ANN index", text)

    def test_audit_and_tag_docs_do_not_authorize_release(self) -> None:
        audit = (V08_DIR / "audit_report.md").read_text(encoding="utf-8")
        tag = (V08_DIR / "tag_preparation.md").read_text(encoding="utf-8")

        self.assertIn("ACCEPT PENDING EXTERNAL REVIEW", audit)
        self.assertIn("not authorized for tag yet", tag)
        self.assertIn("Do not tag `v0.8.0` yet", tag)
        self.assertIn("No tag has been created by this document.", tag)


if __name__ == "__main__":
    unittest.main()
