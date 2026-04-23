from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal843LinuxActiveBaselineBatchTest(unittest.TestCase):
    def test_plan_selects_four_active_linux_actions(self) -> None:
        module = __import__("scripts.goal843_linux_active_baseline_batch", fromlist=["build_linux_active_batch_plan"])
        payload = module.build_linux_active_batch_plan()
        self.assertEqual(payload["selected_count"], 4)
        self.assertEqual(
            {action["status"] for action in payload["actions"]},
            {"linux_postgresql_required", "linux_preferred_for_large_exact_oracle"},
        )

    def test_plan_contains_db_and_robot_collectors(self) -> None:
        module = __import__("scripts.goal843_linux_active_baseline_batch", fromlist=["build_linux_active_batch_plan"])
        payload = module.build_linux_active_batch_plan()
        commands = {action["command"][1] for action in payload["actions"]}
        self.assertIn("scripts/goal842_postgresql_db_prepared_baseline.py", commands)
        self.assertIn("scripts/goal839_robot_pose_count_baseline.py", commands)

    def test_cli_dry_run_writes_plan_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "plan.json"
            output_md = Path(tmpdir) / "plan.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal843_linux_active_baseline_batch.py",
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
            self.assertIn("Goal843 Linux Active Baseline Batch", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["selected_count"], 4)
            self.assertEqual(payload["status"], "plan_only")
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
