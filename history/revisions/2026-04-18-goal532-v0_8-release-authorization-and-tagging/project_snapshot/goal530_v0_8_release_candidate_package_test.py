from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
V08_DIR = REPO_ROOT / "docs" / "release_reports" / "v0_8"


class Goal530V08ReleasePackageTest(unittest.TestCase):
    def test_release_files_exist(self) -> None:
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

        self.assertIn("Status: released as `v0.8.0`", text)
        self.assertIn("current released version is `v0.8.0`", text)
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

    def test_audit_and_tag_docs_record_release_authorization(self) -> None:
        audit = (V08_DIR / "audit_report.md").read_text(encoding="utf-8")
        tag = (V08_DIR / "tag_preparation.md").read_text(encoding="utf-8")

        self.assertIn("Status: **ACCEPT**", audit)
        self.assertIn("authorized for release tag", tag)
        self.assertIn("Tag `v0.8.0` is authorized", tag)
        self.assertIn("Goal532 release commit", tag)


if __name__ == "__main__":
    unittest.main()
