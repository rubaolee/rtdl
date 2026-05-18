from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1217VersionMarkerCurrentReleaseSyncTest(unittest.TestCase):
    def test_version_marker_matches_current_public_release(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "v2.0")

    def test_front_page_and_release_package_match_version_marker(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        release_readme = (
            ROOT / "docs" / "release_reports" / "v2_0" / "README.md"
        ).read_text(encoding="utf-8")
        self.assertIn(f"current released version is `{version}`", readme)
        self.assertIn(f"Version marker: `{version}`", release_readme)
        self.assertIn("released source-tree Python+partner+RTDL language boundary", release_readme)


if __name__ == "__main__":
    unittest.main()
