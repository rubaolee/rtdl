from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TUTORIAL_DIR = ROOT / "docs" / "tutorials"


class Goal2096V2TutorialDirectoryCleanupTest(unittest.TestCase):
    def test_active_tutorial_directory_has_no_old_version_file_names(self) -> None:
        result = subprocess.run(
            ["git", "ls-files", "docs/tutorials/*.md"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        tracked = result.stdout.splitlines()
        self.assertIn("docs/tutorials/v2_app_building.md", tracked)
        self.assertNotIn("docs/tutorials/v0_8_app_building.md", tracked)
        self.assertTrue((ROOT / "docs/history/legacy_tutorials/v0_8_app_building.md").exists())

    def test_active_tutorials_do_not_expose_old_version_markers(self) -> None:
        pattern = re.compile(
            r"\bv0\.|\bv1\.|\bv0_|\bv1_|Goal\s*\d+|release line|released `v|current released",
            re.IGNORECASE,
        )
        offenders: list[str] = []
        for path in sorted(TUTORIAL_DIR.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{line_no}: {line}")
        self.assertEqual([], offenders)

    def test_tutorial_index_is_v2_facing(self) -> None:
        text = (TUTORIAL_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn("# RTDL v2.0 Tutorials", text)
        self.assertIn("[v2.0 App Building](v2_app_building.md)", text)
        self.assertIn("Python+partner+RTDL", text)
        self.assertIn("3-AI consensus gate", text)

    def test_report_records_file_by_file_operations(self) -> None:
        report = (
            ROOT
            / "docs/reports/goal2096_v2_tutorial_directory_cleanup_2026-05-15.md"
        ).read_text(encoding="utf-8")
        for rel in (
            "docs/tutorials/README.md",
            "docs/tutorials/v2_app_building.md",
            "docs/history/legacy_tutorials/v0_8_app_building.md",
            "docs/tutorials/db_workloads.md",
            "docs/tutorials/partner_optix_zero_copy_anyhit.md",
        ):
            self.assertIn(rel, report)


if __name__ == "__main__":
    unittest.main()
