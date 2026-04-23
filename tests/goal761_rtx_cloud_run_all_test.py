from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal761RtxCloudRunAllTest(unittest.TestCase):
    def test_dry_run_emits_manifest_commands_without_running_benchmarks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal761_rtx_cloud_run_all.py",
                    "--dry-run",
                    "--only",
                    "robot_collision_screening",
                    "--output-json",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["suite"], "goal761_rtx_cloud_run_all")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["entry_count"], 1)
            self.assertEqual(payload["unique_command_count"], 1)
            self.assertEqual(payload["results"][0]["app"], "robot_collision_screening")
            self.assertEqual(payload["results"][0]["result"]["status"], "dry_run")
            self.assertEqual(payload["results"][0]["result"]["execution_mode"], "executed")
            self.assertTrue(output.exists())

    def test_duplicate_manifest_commands_are_reused(self) -> None:
        module = __import__("scripts.goal761_rtx_cloud_run_all", fromlist=["run_all"])
        payload = module.run_all(dry_run=True, only={"outlier_detection", "dbscan_clustering"})
        self.assertEqual(payload["entry_count"], 2)
        self.assertEqual(payload["unique_command_count"], 1)
        modes = [row["result"]["execution_mode"] for row in payload["results"]]
        self.assertEqual(modes, ["executed", "reused_command_result"])


if __name__ == "__main__":
    unittest.main()
