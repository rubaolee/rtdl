from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1051PostGoal1048FollowupPlanTest(unittest.TestCase):
    def test_plan_separates_diagnostic_reruns_from_review_work(self) -> None:
        module = __import__(
            "scripts.goal1051_post_goal1048_followup_plan",
            fromlist=["build_plan"],
        )
        payload = module.build_plan()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(
            [row["app"] for row in payload["diagnostic_reruns"]],
            ["facility_knn_assignment", "robot_collision_screening"],
        )
        self.assertEqual(len(payload["reviewed_keep_as_is"]), 11)
        self.assertEqual(len(payload["blocked_public_wording"]), 0)
        self.assertEqual(len(payload["same_semantics_review_needed"]), 5)
        self.assertIn("Do not start paid cloud per app", payload["policy"])
        self.assertIn("does not run cloud", payload["boundary"])

    def test_gemini_architecture_reports_are_registered_inputs(self) -> None:
        module = __import__(
            "scripts.goal1051_post_goal1048_followup_plan",
            fromlist=["build_plan"],
        )
        payload = module.build_plan()
        self.assertIn(
            "docs/reports/gemini_v1_0_project_foundational_review_2026-04-27.md",
            payload["inputs"],
        )
        self.assertIn(
            "docs/reports/gemini_v2_0_architectural_direction_compute_partnership_2026-04-27.md",
            payload["inputs"],
        )

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1051.json"
            output_md = Path(tmpdir) / "goal1051.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1051_post_goal1048_followup_plan.py",
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
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1051 Post-Goal1048 Follow-Up Plan", markdown)
            self.assertIn("facility_knn_assignment", markdown)
            self.assertIn("robot_collision_screening", markdown)
            self.assertIn("Same-Semantics Review Needed", markdown)


if __name__ == "__main__":
    unittest.main()
