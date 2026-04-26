from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1026PreCloudRunnerDryRunAuditTest(unittest.TestCase):
    def test_runner_dry_run_covers_full_active_and_deferred_batch(self) -> None:
        module = __import__(
            "scripts.goal1026_pre_cloud_runner_dry_run_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["entry_count"], 17)
        self.assertEqual(payload["unique_command_count"], 16)
        self.assertEqual(payload["section_counts"]["entries"], 8)
        self.assertEqual(payload["section_counts"]["deferred_entries"], 9)
        self.assertEqual(payload["result_status_counts"]["dry_run"], 17)
        self.assertEqual(payload["failed_count"], 0)
        self.assertEqual(payload["command_result_reuse_paths"], ["prepared_fixed_radius_core_flags"])
        self.assertIn("does not authorize RTX speedup claims", payload["manifest_boundary"])
        self.assertIn("RTX-class NVIDIA hardware with RT cores", " ".join(payload["global_preconditions"]))

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1026.json"
            output_md = Path(tmpdir) / "goal1026.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1026_pre_cloud_runner_dry_run_audit.py",
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
            self.assertIn("Goal1026 Pre-Cloud RTX Runner Dry-Run Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("does not start cloud", markdown)
            self.assertIn("single-session runbook", markdown)


if __name__ == "__main__":
    unittest.main()
