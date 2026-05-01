from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal841LocalBaselineCollectTest(unittest.TestCase):
    def test_build_run_plan_can_select_robot_only(self) -> None:
        module = __import__("scripts.goal841_local_baseline_collect", fromlist=["build_run_plan"])
        payload = module.build_run_plan(app="robot_collision_screening")
        self.assertEqual(payload["selected_count"], 0)
        self.assertEqual(payload["actions"], [])

    def test_build_run_plan_can_select_single_baseline(self) -> None:
        module = __import__("scripts.goal841_local_baseline_collect", fromlist=["build_run_plan"])
        payload = module.build_run_plan(
            app="database_analytics",
            path_name="prepared_db_session_sales_risk",
            baseline="cpu_oracle_compact_summary",
        )
        self.assertEqual(payload["selected_count"], 1)
        self.assertEqual(payload["actions"][0]["baseline"], "cpu_oracle_compact_summary")

    def test_cli_dry_run_does_not_execute_collectors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "run.json"
            output_md = Path(tmpdir) / "run.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal841_local_baseline_collect.py",
                    "--app",
                    "database_analytics",
                    "--path-name",
                    "prepared_db_session_sales_risk",
                    "--baseline",
                    "cpu_oracle_compact_summary",
                    "--dry-run",
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
            self.assertIn("Goal841 Local Baseline Collector Runner", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["selected_count"], 1)
            self.assertEqual(payload["result_count"], 0)
            self.assertEqual(payload["status"], "plan_only")
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
