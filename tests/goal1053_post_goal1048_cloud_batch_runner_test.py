from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1053PostGoal1048CloudBatchRunnerTest(unittest.TestCase):
    def test_runner_payload_matches_manifest_shape(self) -> None:
        module = __import__(
            "scripts.goal1053_post_goal1048_cloud_batch_runner",
            fromlist=["build_runner"],
        )
        payload = module.build_runner()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(len(payload["commands"]), 11)
        self.assertEqual(payload["commands"][0]["app"], "facility_knn_assignment")
        self.assertEqual(payload["commands"][1]["app"], "robot_collision_screening")
        self.assertFalse(payload["commands"][0]["contains_skip_validation"])
        self.assertFalse(payload["commands"][1]["contains_skip_validation"])

    def test_shell_contains_required_safety_controls(self) -> None:
        module = __import__(
            "scripts.goal1053_post_goal1048_cloud_batch_runner",
            fromlist=["build_runner", "to_shell"],
        )
        shell = module.to_shell(module.build_runner())
        self.assertIn("RTDL_SOURCE_COMMIT is empty", shell)
        self.assertIn("nvidia-smi", shell)
        self.assertIn("goal763_rtx_cloud_bootstrap_check.py", shell)
        self.assertIn("Copy back ${REPORT_DIR}", shell)
        self.assertIn("does not authorize speedup claims", shell)
        self.assertNotIn("runpod", shell.lower())
        self.assertNotIn("terminatepod", shell.lower())

    def test_diagnostic_commands_do_not_skip_validation(self) -> None:
        module = __import__(
            "scripts.goal1053_post_goal1048_cloud_batch_runner",
            fromlist=["build_runner"],
        )
        payload = module.build_runner()
        diagnostic = payload["commands"][:2]
        for command in diagnostic:
            self.assertNotIn("--skip-validation", command["command"])

    def test_cli_writes_json_and_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1053.json"
            output_sh = Path(tmpdir) / "goal1053.sh"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1053_post_goal1048_cloud_batch_runner.py",
                    "--output-json",
                    str(output_json),
                    "--output-sh",
                    str(output_sh),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            shell = output_sh.read_text(encoding="utf-8")
            self.assertIn("Goal1053 post-Goal1048 RTX cloud batch runner", shell)
            self.assertIn("facility_service_coverage", shell)
            self.assertIn("prepared_pose_flags", shell)


if __name__ == "__main__":
    unittest.main()
