from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1210_v0_9_8_release_readiness_audit as goal1210


ROOT = Path(__file__).resolve().parents[1]


class Goal1210V098ReleaseReadinessAuditTest(unittest.TestCase):
    def test_current_release_readiness_audit_is_valid(self) -> None:
        payload = goal1210.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["failing_goal_count"], 0)
        self.assertEqual(payload["failing_surface_doc_count"], 0)
        self.assertEqual(payload["public_wording_row_count_expected"], 13)
        self.assertEqual(
            payload["new_public_wording_rows"],
            ["road_hazard_screening / prepared_native_compact_summary_40k"],
        )
        self.assertEqual(payload["blocked_public_speedup_wording"], ["graph_analytics"])

    def test_goal1204_to_goal1209_have_consensus_rows(self) -> None:
        payload = goal1210.build_audit()
        rows = {row["goal"]: row for row in payload["goal_rows"]}
        self.assertEqual(set(rows), {f"Goal{number}" for number in range(1204, 1210)})
        for goal, row in rows.items():
            with self.subTest(goal=goal):
                self.assertEqual(row["status"], "ok")
                self.assertFalse(row["missing_files"])
                self.assertTrue(any("two_ai_consensus" in item["path"] for item in row["files"]))

    def test_public_surface_forbids_old_or_broad_claims(self) -> None:
        payload = goal1210.build_audit()
        checked_text = "\n".join(
            (ROOT / row["path"]).read_text(encoding="utf-8")
            for row in payload["surface_rows"]
            if (ROOT / row["path"]).exists()
        )
        self.assertIn("reviewed public RTX sub-path wording rows: `13`", checked_text)
        self.assertIn("Goal1208 adds exactly one reviewed public wording row", checked_text)
        self.assertIn("road_hazard_screening / prepared_native_compact_summary_40k", checked_text)
        self.assertNotIn("reviewed public RTX sub-path wording rows: `10`", checked_text)
        self.assertNotIn("Goal1208 authorizes whole-app", checked_text)
        self.assertNotIn("database_analytics / public speedup", checked_text)
        self.assertNotIn("polygon_set_jaccard / public speedup", checked_text)

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "audit.json"
            output_md = Path(tmpdir) / "audit.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1210_v0_9_8_release_readiness_audit.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("Goal1210 v0.9.8 Release-Readiness Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("expected reviewed public wording rows: `13`", markdown)
            self.assertIn("graph public speedup wording: `blocked`", markdown)


if __name__ == "__main__":
    unittest.main()
