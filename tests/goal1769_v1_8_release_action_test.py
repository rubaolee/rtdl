import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1769_v1_8_release_action_2026-05-12.md"
RELEASE_README = ROOT / "docs" / "release_reports" / "v1_8" / "README.md"


class Goal1769V18ReleaseActionTest(unittest.TestCase):
    def test_v1_8_release_package_keeps_marker(self) -> None:
        text = RELEASE_README.read_text(encoding="utf-8")
        self.assertIn("Version marker: `v1.8`", text)

    def test_release_action_records_authorized_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1_8_source_tree_python_rtdl_release_action_authorized", text)
        self.assertIn("first source-tree Python+RTDL language release", text)
        self.assertIn("tag the committed tree as `v1.8`", text)
        self.assertIn("does not claim package-install support", text)
        self.assertIn("Python+partner+RTDL readiness", text)

    def test_front_door_docs_no_longer_name_v1_8_as_current_release(self) -> None:
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        public_map = (ROOT / "docs" / "public_documentation_map.md").read_text(
            encoding="utf-8"
        )
        for text in (root_readme, docs_readme, public_map):
            self.assertIn("v2.0", text)
            self.assertIn("source-tree Python+partner+RTDL", text)
            self.assertNotIn("current released version is `v1.8`", text)
        self.assertNotIn("v1.8 is not tagged or released yet", root_readme)
        self.assertNotIn("v1.8 is not a released tag yet", docs_readme)
        self.assertNotIn("v1.8 still requires explicit user authorization", public_map)

    def test_release_package_is_source_tree_only_and_evidence_linked(self) -> None:
        text = RELEASE_README.read_text(encoding="utf-8")
        self.assertIn("Version marker: `v1.8`", text)
        self.assertIn("PYTHONPATH=src:.", text)
        self.assertIn("not a package-install release", text)
        self.assertIn("not the Python+partner+RTDL milestone", text)
        for goal in ("Goal1758", "Goal1762", "Goal1763", "Goal1764", "Goal1765", "Goal1768", "Goal1769"):
            self.assertIn(goal, text)

    def test_protected_local_files_are_named_for_exclusion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for protected in (
            "docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz",
            "id_ed25519_rtdl_codex",
            "rtdl_v0_4.tar.gz",
            "scratch/",
        ):
            self.assertIn(protected, text)


if __name__ == "__main__":
    unittest.main()
