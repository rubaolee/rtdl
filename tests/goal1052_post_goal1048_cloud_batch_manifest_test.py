from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1052PostGoal1048CloudBatchManifestTest(unittest.TestCase):
    def test_manifest_is_valid_and_batched(self) -> None:
        module = __import__(
            "scripts.goal1052_post_goal1048_cloud_batch_manifest",
            fromlist=["build_manifest"],
        )
        payload = module.build_manifest()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["summary"]["diagnostic_rerun_count"], 2)
        self.assertEqual(payload["summary"]["same_semantics_review_candidate_count"], 6)
        self.assertEqual(payload["summary"]["total_command_count"], 8)
        self.assertIn("Do not start or stop a cloud pod per app", payload["policy"])
        self.assertIn("does not run cloud", payload["boundary"])

    def test_diagnostic_rows_are_validation_enabled(self) -> None:
        module = __import__(
            "scripts.goal1052_post_goal1048_cloud_batch_manifest",
            fromlist=["build_manifest"],
        )
        payload = module.build_manifest()
        self.assertEqual(payload["summary"]["diagnostic_without_validation"], [])
        rows = payload["diagnostic_validation_reruns"]
        self.assertEqual(
            [row["app"] for row in rows],
            ["facility_knn_assignment", "robot_collision_screening"],
        )
        for row in rows:
            self.assertNotIn("--skip-validation", row["command"])
            self.assertTrue(row["force_validation_enabled"])
            self.assertFalse(row["contains_skip_validation"])

    def test_robot_diagnostic_uses_profiler_validation_capable_mode(self) -> None:
        module = __import__(
            "scripts.goal1052_post_goal1048_cloud_batch_manifest",
            fromlist=["build_manifest"],
        )
        payload = module.build_manifest()
        robot = next(
            row
            for row in payload["diagnostic_validation_reruns"]
            if row["app"] == "robot_collision_screening"
        )
        command = robot["command"]
        self.assertIn("scripts/goal760_optix_robot_pose_flags_phase_profiler.py", command)
        self.assertIn("--input-mode", command)
        self.assertEqual(command[command.index("--input-mode") + 1], "python_objects")
        self.assertIn("--result-mode", command)
        self.assertEqual(command[command.index("--result-mode") + 1], "pose_flags")
        self.assertEqual(command[command.index("--pose-count") + 1], "4096")
        self.assertEqual(command[command.index("--obstacle-count") + 1], "256")
        self.assertEqual(command[command.index("--iterations") + 1], "3")

    def test_outputs_are_goal1052_scoped_and_unique(self) -> None:
        module = __import__(
            "scripts.goal1052_post_goal1048_cloud_batch_manifest",
            fromlist=["build_manifest"],
        )
        payload = module.build_manifest()
        self.assertEqual(payload["summary"]["duplicate_output_json"], [])
        all_rows = payload["diagnostic_validation_reruns"] + payload["same_semantics_review_candidates"]
        for row in all_rows:
            self.assertIsNotNone(row["output_json"])
            self.assertIn("goal1052_post_goal1048_cloud_batch", row["output_json"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1052.json"
            output_md = Path(tmpdir) / "goal1052.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1052_post_goal1048_cloud_batch_manifest.py",
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
            self.assertIn("Goal1052 Post-Goal1048 Cloud Batch Manifest", markdown)
            self.assertIn("Diagnostic Validation Reruns", markdown)
            self.assertIn("Same-Semantics Review Candidates", markdown)


if __name__ == "__main__":
    unittest.main()
