from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1221V098ReleaseActionTest(unittest.TestCase):
    def test_v098_release_package_remains_historical_release(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("The current released version is `v1.0`", readme)
        self.assertIn("- current released version: `v1.0`", readme)
        self.assertNotIn("- current released version: `v0.9.6`\n- current released version: `v0.9.8`", readme)

    def test_release_package_is_released_not_prepared(self) -> None:
        package_dir = ROOT / "docs" / "release_reports" / "v0_9_8"
        for path in package_dir.glob("*.md"):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("Status: released as `v0.9.8`", text)
                self.assertNotIn("release-prepared as `v0.9.8`; not tagged or published", text)

    def test_release_action_report_records_boundary(self) -> None:
        text = (
            ROOT / "docs" / "reports" / "goal1221_v0_9_8_release_action_2026-05-01.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Bumped `VERSION` from `v0.9.6` to `v0.9.8`", text)
        self.assertIn("Commit, tag, and push are\nseparate git operations", text)


if __name__ == "__main__":
    unittest.main()
