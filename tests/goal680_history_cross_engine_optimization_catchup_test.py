from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
ROUND = "2026-04-20-goal658-679-cross-engine-prepared-visibility-optimization"


class Goal680HistoryCrossEngineOptimizationCatchupTest(unittest.TestCase):
    def test_history_indexes_include_goal658_679_round(self) -> None:
        for rel_path in (
            "history/COMPLETE_HISTORY.md",
            "history/revision_dashboard.md",
            "history/revision_dashboard.html",
            "history/README.md",
            "history/revisions/README.md",
        ):
            with self.subTest(path=rel_path):
                text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
                self.assertIn("Goals658-679", text)
                self.assertIn(ROUND, text)

    def test_revision_round_metadata_and_summary_exist(self) -> None:
        base = REPO_ROOT / "history" / "revisions" / ROUND
        metadata = (base / "metadata.txt").read_text(encoding="utf-8")
        summary = (
            base
            / "project_snapshot"
            / "goal658_679_cross_engine_prepared_visibility_optimization.md"
        ).read_text(encoding="utf-8")

        self.assertIn("source_commit: f5f2338-plus-uncommitted-goal658-679-worktree", metadata)
        self.assertIn("Goal679", summary)
        self.assertIn("Ran 1266 tests", summary)
        self.assertIn("focused native suite: Ran 30 tests", summary)
        self.assertIn("not a retroactive `v0.9.5` tag", summary)


if __name__ == "__main__":
    unittest.main()
