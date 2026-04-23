from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal762RtxCloudArtifactReportTest(unittest.TestCase):
    def test_dry_run_summary_is_ok_without_benchmark_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "dry_run_summary.json"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal761_rtx_cloud_run_all.py",
                    "--dry-run",
                    "--only",
                    "robot_collision_screening",
                    "--output-json",
                    str(summary),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze", "to_markdown"])
            payload = module.analyze(summary)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["entry_count"], 1)
            self.assertEqual(payload["rows"][0]["artifact_status"], "dry_run_not_expected")
            markdown = module.to_markdown(payload)
            self.assertIn("does not authorize RTX speedup claims", markdown)

    def test_missing_artifact_after_ok_runner_needs_attention(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "dry_run": False,
                        "results": [
                            {
                                "app": "robot_collision_screening",
                                "path_name": "prepared_pose_flags",
                                "claim_scope": "prepared OptiX ray/triangle any-hit pose-flag summary",
                                "non_claim": "not continuous collision detection",
                                "result": {
                                    "status": "ok",
                                    "returncode": 0,
                                    "command": [
                                        "python3",
                                        "script.py",
                                        "--output-json",
                                        "docs/reports/does_not_exist_goal762.json",
                                    ],
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            payload = module.analyze(summary)
            self.assertEqual(payload["status"], "needs_attention")
            self.assertEqual(payload["rows"][0]["artifact_status"], "missing")


if __name__ == "__main__":
    unittest.main()
