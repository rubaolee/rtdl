from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1139CurrentWindowConsensusAuditTest(unittest.TestCase):
    def test_current_window_is_closed(self) -> None:
        from scripts import goal1139_current_window_consensus_audit as goal1139

        payload = goal1139.build_audit()
        self.assertTrue(payload["valid"], payload["summary"]["blockers"])
        self.assertEqual(payload["summary"]["goal_count"], 19)
        self.assertEqual(payload["summary"]["blocker_count"], 0)
        self.assertIn("goal1138", payload["audited_goals"])
        rows = {row["goal"]: row for row in payload["rows"]}
        self.assertIn("goal1138_gemini_review_2026-04-29.md", rows["goal1138"]["external_review"])
        self.assertIn("goal1138_two_ai_consensus_2026-04-29.md", rows["goal1138"]["consensus"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "audit.json"
            output_md = Path(tmp) / "audit.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1139_current_window_consensus_audit.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("Goal1139 Current-Window Consensus Audit", markdown)
            self.assertIn("goal1138", markdown)
            self.assertIn("Blockers", markdown)


if __name__ == "__main__":
    unittest.main()
