from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


class Goal1056PostGoal1048ArtifactIntakeTest(unittest.TestCase):
    def test_default_intake_waits_for_cloud_artifacts_without_authorizing_claims(self) -> None:
        module = __import__(
            "scripts.goal1056_post_goal1048_artifact_intake",
            fromlist=["build_intake"],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = module.build_intake(Path(tmpdir))
        self.assertEqual(payload["overall_status"], "needs_cloud_artifacts")
        self.assertEqual(payload["expected_artifact_count"], 11)
        self.assertEqual(payload["missing_artifact_count"], 11)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not run cloud", payload["boundary"])

    def test_diagnostic_artifacts_need_validation_and_oracle_parity(self) -> None:
        module = __import__(
            "scripts.goal1056_post_goal1048_artifact_intake",
            fromlist=["build_intake"],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "coverage_threshold_prepared.json",
                {
                    "parameters": {"skip_validation": False},
                    "scenario": {
                        "mode": "optix",
                        "result": {"matches_oracle": True},
                    },
                },
            )
            _write_json(
                root / "prepared_pose_flags.json",
                {
                    "validated": True,
                    "matches_oracle": True,
                    "mode": "optix",
                    "input_mode": "python_objects",
                    "result_mode": "pose_flags",
                },
            )
            payload = module.build_intake(root)
        rows = {(row["app"], row["path_name"]): row for row in payload["rows"]}
        self.assertEqual(
            rows[("facility_knn_assignment", "coverage_threshold_prepared")]["review_status"],
            "diagnostic_validated",
        )
        self.assertEqual(
            rows[("robot_collision_screening", "prepared_pose_flags")]["review_status"],
            "diagnostic_validated",
        )
        self.assertEqual(payload["diagnostic_validated_count"], 2)
        self.assertEqual(payload["overall_status"], "needs_cloud_artifacts")

    def test_bad_diagnostic_artifact_blocks_intake(self) -> None:
        module = __import__(
            "scripts.goal1056_post_goal1048_artifact_intake",
            fromlist=["build_intake"],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "prepared_pose_flags.json",
                {
                    "validated": False,
                    "matches_oracle": True,
                    "mode": "optix",
                    "input_mode": "python_objects",
                    "result_mode": "pose_flags",
                },
            )
            payload = module.build_intake(root)
        robot = next(row for row in payload["rows"] if row["app"] == "robot_collision_screening")
        self.assertEqual(robot["review_status"], "blocked")
        self.assertEqual(payload["overall_status"], "blocked")
        self.assertFalse(payload["valid"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / "artifacts"
            artifact_dir.mkdir()
            output_json = Path(tmpdir) / "goal1056.json"
            output_md = Path(tmpdir) / "goal1056.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1056_post_goal1048_artifact_intake.py",
                    "--artifact-dir",
                    str(artifact_dir),
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
            self.assertEqual(payload["overall_status"], "needs_cloud_artifacts")
            self.assertIn("Goal1056 Post-Goal1048 Artifact Intake", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
