from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal682V096ReleaseCandidatePackageTest(unittest.TestCase):
    def test_release_files_exist_and_are_released_state(self) -> None:
        for rel_path in (
            "docs/release_reports/v0_9_6/README.md",
            "docs/release_reports/v0_9_6/release_statement.md",
            "docs/release_reports/v0_9_6/support_matrix.md",
            "docs/release_reports/v0_9_6/audit_report.md",
            "docs/release_reports/v0_9_6/tag_preparation.md",
        ):
            with self.subTest(path=rel_path):
                text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
                self.assertIn("released as `v0.9.6`", text)
                self.assertNotIn("release candidate / hold", text.lower())
                self.assertNotIn("not tagged", text.lower())

    def test_release_marks_v096_as_current_release_boundary(self) -> None:
        readme = (REPO_ROOT / "docs/release_reports/v0_9_6/README.md").read_text(
            encoding="utf-8"
        )
        statement = (
            REPO_ROOT / "docs/release_reports/v0_9_6/release_statement.md"
        ).read_text(encoding="utf-8")
        tag_record = (
            REPO_ROOT / "docs/release_reports/v0_9_6/tag_preparation.md"
        ).read_text(encoding="utf-8")

        self.assertIn("This package is the released `v0.9.6` public boundary", readme)
        self.assertIn("RTDL `v0.9.6` is the prepared/prepacked", statement)
        self.assertIn("maintainer explicitly authorized release", tag_record)
        self.assertIn("git tag -a v0.9.6", tag_record)

    def test_release_records_gate_counts_and_non_claims(self) -> None:
        audit = (REPO_ROOT / "docs/release_reports/v0_9_6/audit_report.md").read_text(
            encoding="utf-8"
        )
        matrix = (
            REPO_ROOT / "docs/release_reports/v0_9_6/support_matrix.md"
        ).read_text(encoding="utf-8")

        self.assertIn("`1274` tests OK", audit)
        self.assertIn("`250` commands across `14` docs", audit)
        self.assertIn("DB or graph workloads", audit)
        self.assertIn("GTX 1070", matrix)
        self.assertIn("AMD GPU", matrix)
        self.assertIn("full emitted-row", matrix)


if __name__ == "__main__":
    unittest.main()
