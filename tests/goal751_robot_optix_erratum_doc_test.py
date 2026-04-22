from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal751RobotOptixErratumDocTest(unittest.TestCase):
    def test_public_docs_record_goal748_robot_optix_erratum(self) -> None:
        paths = (
            "README.md",
            "docs/README.md",
            "docs/app_engine_support_matrix.md",
            "docs/release_facing_examples.md",
            "docs/tutorials/feature_quickstart_cookbook.md",
            "docs/capability_boundaries.md",
            "docs/reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md",
        )
        for rel_path in paths:
            with self.subTest(path=rel_path):
                text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
                self.assertIn("Goal748", text)
                self.assertIn("OptiX", text)
                self.assertRegex(text, r"short-ray|short ray")

    def test_old_goal509_report_no_longer_accepts_robot_optix_unqualified(self) -> None:
        text = (REPO_ROOT / "docs/reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Post-Goal748 Erratum", text)
        self.assertRegex(text, r"pre-fix OptiX\s+robot evidence in this Goal509 report is now treated as suspect")
        self.assertIn("superseded by the Goal748 post-fix rerun", text)


if __name__ == "__main__":
    unittest.main()
