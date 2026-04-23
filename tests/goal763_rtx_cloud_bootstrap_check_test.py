from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal763RtxCloudBootstrapCheckTest(unittest.TestCase):
    def test_dry_run_records_build_and_test_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "bootstrap.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal763_rtx_cloud_bootstrap_check.py",
                    "--dry-run",
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
            self.assertEqual(payload["suite"], "goal763_rtx_cloud_bootstrap_check")
            self.assertEqual(payload["status"], "ok")
            self.assertTrue(payload["dry_run"])
            self.assertEqual([step["name"] for step in payload["steps"]], ["build_optix", "native_optix_focused_tests"])
            self.assertIn("OPTIX_PREFIX", " ".join(payload["steps"][0]["result"]["command"]))
            self.assertTrue(output.exists())

    def test_skip_flags_omit_steps(self) -> None:
        module = __import__("scripts.goal763_rtx_cloud_bootstrap_check", fromlist=["run_check"])
        payload = module.run_check(dry_run=True, skip_build=True, skip_tests=True)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["steps"], [])


if __name__ == "__main__":
    unittest.main()
