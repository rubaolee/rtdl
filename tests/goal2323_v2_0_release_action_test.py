from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2323_v2_0_release_action_2026-05-18.md"
RELEASE_README = ROOT / "docs" / "release_reports" / "v2_0" / "README.md"


class Goal2323V20ReleaseActionTest(unittest.TestCase):
    def test_version_marker_has_moved_beyond_v2_0(self) -> None:
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "v2.3")

    def test_release_action_records_authorized_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v2_0_source_tree_python_partner_rtdl_release_action_authorized", text)
        self.assertIn("source-tree Python+partner+RTDL language release", text)
        self.assertIn("tag the committed tree as `v2.0`", text)
        self.assertIn("does not claim package-install support", text)
        self.assertIn("Goal2322", text)

    def test_front_door_docs_now_name_current_release(self) -> None:
        for rel in ("README.md", "docs/README.md", "docs/current_architecture.md"):
            with self.subTest(rel=rel):
                text = (ROOT / rel).read_text(encoding="utf-8")
                self.assertIn("v2.3", text)
                self.assertIn("release", text)
                self.assertIn("source-tree", text)
                self.assertNotIn("fresh Claude-family review is still missing", text)
                self.assertNotIn("pre-release candidate", text.lower())

    def test_release_package_is_source_tree_only_and_evidence_linked(self) -> None:
        text = RELEASE_README.read_text(encoding="utf-8")
        self.assertIn("Version marker: `v2.0`", text)
        self.assertIn("PYTHONPATH=src:.", text)
        self.assertIn("not a package-install release", text)
        self.assertIn("not a broad RT-core", text)
        for goal in ("Goal2068", "Goal2085", "Goal2319", "Goal2320", "Goal2321", "Goal2322", "Goal2323"):
            self.assertIn(goal, text)

    def test_protected_local_files_are_named_for_exclusion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for protected in (
            "docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz",
            "id_ed25519_rtdl_codex",
            "rtdl_v0_4.tar.gz",
            "scratch/",
            "Lib/",
        ):
            self.assertIn(protected, text)


if __name__ == "__main__":
    unittest.main()
