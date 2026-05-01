from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1216_v0_9_8_release_candidate_audit as goal1216


ROOT = Path(__file__).resolve().parents[1]


class Goal1216V098ReleaseCandidateAuditTest(unittest.TestCase):
    def test_release_candidate_audit_is_valid(self) -> None:
        payload = goal1216.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["recommendation"], "local_release_candidate_ready_for_final_external_release_decision")
        self.assertFalse(payload["pod_needed_now"])
        self.assertEqual(payload["closure_goal_count"], 12)
        self.assertEqual(payload["closure_failure_count"], 0)
        self.assertEqual(payload["evidence_failure_count"], 0)

    def test_all_recent_goals_have_external_review_and_consensus(self) -> None:
        payload = goal1216.build_audit()
        rows = {row["goal"]: row for row in payload["closure_rows"]}
        self.assertEqual(set(rows), {f"Goal{number}" for number in range(1204, 1216)})
        for goal, row in rows.items():
            with self.subTest(goal=goal):
                self.assertEqual(row["status"], "ok")
                self.assertTrue(row["has_external_review"])
                self.assertTrue(row["has_two_ai_consensus"])
                self.assertFalse(row["missing_files"])

    def test_public_state_stays_bounded(self) -> None:
        payload = goal1216.build_audit()
        public_state = payload["current_public_state"]
        self.assertEqual(public_state["reviewed_public_rtx_wording_rows"], 11)
        self.assertEqual(
            public_state["new_reviewed_row_after_goal1208"],
            "road_hazard_screening / prepared_native_compact_summary_40k",
        )
        self.assertEqual(public_state["database_analytics_public_speedup"], "blocked")
        self.assertEqual(public_state["polygon_set_jaccard_public_speedup"], "blocked")
        self.assertIn("not default app behavior", public_state["road_hazard_boundary"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1216.json"
            output_md = Path(tmpdir) / "goal1216.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1216_v0_9_8_release_candidate_audit.py",
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
            self.assertIn("Goal1216 v0.9.8 Release-Candidate Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("pod needed now: `False`", markdown)
            self.assertIn("Goal1214 full unittest discovery", markdown)
            self.assertIn("Goal1215 release-surface docs", markdown)


if __name__ == "__main__":
    unittest.main()
