from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
ROUND = "2026-04-20-goal650-656-current-main-anyhit-doc-test-catchup"


class Goal657HistoryCurrentMainCatchupTest(unittest.TestCase):
    def test_history_indexes_include_current_main_catchup_round(self) -> None:
        for path in (
            REPO_ROOT / "history" / "COMPLETE_HISTORY.md",
            REPO_ROOT / "history" / "revision_dashboard.md",
            REPO_ROOT / "history" / "revision_dashboard.html",
            REPO_ROOT / "history" / "README.md",
        ):
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertIn("Goals650-656", path.read_text(encoding="utf-8"))

        dashboard = (REPO_ROOT / "history" / "revision_dashboard.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(ROUND, dashboard)
        self.assertIn("v0.9.5-current-main", dashboard)

    def test_revision_round_metadata_and_summary_exist(self) -> None:
        base = REPO_ROOT / "history" / "revisions" / ROUND
        metadata = (base / "metadata.txt").read_text(encoding="utf-8")
        summary = (
            base
            / "project_snapshot"
            / "goal650_656_current_main_anyhit_doc_test_catchup.md"
        ).read_text(encoding="utf-8")

        self.assertIn("source_commit: 8d96924", metadata)
        self.assertIn("Goal650", summary)
        self.assertIn("Goal656", summary)
        self.assertIn("not retroactive `v0.9.5` tag claims", summary)
        self.assertIn("Ran 1232 tests", summary)


if __name__ == "__main__":
    unittest.main()
