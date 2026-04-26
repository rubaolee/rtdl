from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1017RecentGoalConsensusAuditTest(unittest.TestCase):
    def test_recent_goals_have_required_review_trails(self) -> None:
        module = __import__(
            "scripts.goal1017_recent_goal_consensus_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["audited_goal_count"], 12)
        self.assertEqual(payload["complete_goal_count"], 12)
        self.assertEqual(payload["incomplete_goal_count"], 0)
        for row in payload["rows"]:
            self.assertEqual(row["status"], "complete")
            self.assertEqual(row["missing_requirements"], [])
            self.assertGreaterEqual(len(row["files"]["claude_review"]), 1)
            self.assertGreaterEqual(len(row["files"]["gemini_review"]), 1)
            self.assertGreaterEqual(len(row["files"]["two_ai_consensus"]), 1)

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1017.json"
            output_md = Path(tmpdir) / "goal1017.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1017_recent_goal_consensus_audit.py",
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
            self.assertIn("Goal1017 Recent Goal Consensus Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("complete goals", markdown)
            self.assertIn("does not authorize public speedup claims", markdown)


if __name__ == "__main__":
    unittest.main()
