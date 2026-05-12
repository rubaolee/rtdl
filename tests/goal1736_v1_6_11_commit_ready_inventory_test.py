import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1736_v1_6_11_commit_ready_inventory_2026-05-12.md"


class Goal1736V1611CommitReadyInventoryTest(unittest.TestCase):
    def test_inventory_names_final_decision_core(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for goal in ("goal1729", "goal1730", "goal1731", "goal1732", "goal1733", "goal1734", "goal1735", "goal1736"):
            self.assertIn(goal, text)

    def test_inventory_excludes_local_protected_files(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Do Not Stage", text)
        self.assertIn("docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz", text)
        self.assertIn("id_ed25519_rtdl_codex", text)
        self.assertIn("rtdl_v0_4.tar.gz", text)
        self.assertIn("scratch/", text)

    def test_inventory_requires_explicit_user_authorization_before_tag(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Pre-Tag Checklist", text)
        self.assertIn("Only tag/push if the user explicitly authorizes", text)
        self.assertIn("not a release command", text)


if __name__ == "__main__":
    unittest.main()
