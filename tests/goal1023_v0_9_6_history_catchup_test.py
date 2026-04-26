from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUND = "2026-04-26-goal1023-v0_9_6-history-catchup"


class Goal1023V096HistoryCatchupTest(unittest.TestCase):
    def test_public_history_indexes_include_v096_goal684_catchup(self) -> None:
        for rel_path in (
            "history/COMPLETE_HISTORY.md",
            "history/revision_dashboard.md",
            "history/revision_dashboard.html",
            "history/README.md",
            "history/revisions/README.md",
        ):
            with self.subTest(path=rel_path):
                text = (ROOT / rel_path).read_text(encoding="utf-8")
                self.assertIn("v0.9.6", text)
                self.assertIn("Goal684", text)
                self.assertIn(ROUND, text)

    def test_revision_round_metadata_and_summary_exist(self) -> None:
        base = ROOT / "history" / "revisions" / ROUND
        metadata = (base / "metadata.txt").read_text(encoding="utf-8")
        summary = (
            base
            / "project_snapshot"
            / "goal1023_v0_9_6_history_catchup.md"
        ).read_text(encoding="utf-8")

        self.assertIn("version: v0.9.6", metadata)
        self.assertIn("Goal1022 detected", summary)
        self.assertIn("Goal684", summary)
        self.assertIn("not a new release", summary)

    def test_history_db_registers_v096_catchup_round(self) -> None:
        con = sqlite3.connect(ROOT / "history" / "history.db")
        try:
            row = con.execute(
                """
                select s.version, s.status, r.title
                from revision_rounds r
                join revision_round_status s on s.round_id = r.id
                where r.slug = ?
                """,
                (ROUND,),
            ).fetchone()
        finally:
            con.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "v0.9.6")
        self.assertEqual(row[1], "accepted")
        self.assertIn("history catch-up", row[2])


if __name__ == "__main__":
    unittest.main()
