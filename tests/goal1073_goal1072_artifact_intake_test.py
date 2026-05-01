from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class Goal1073Goal1072ArtifactIntakeTest(unittest.TestCase):
    def test_missing_artifacts_require_cloud(self) -> None:
        module = __import__("scripts.goal1073_goal1072_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = module.build_intake(Path(tmpdir))
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["overall_status"], "needs_cloud_artifacts")
        self.assertEqual(payload["expected_artifact_count"], 4)
        self.assertEqual(payload["missing_artifact_count"], 4)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertEqual(payload["excluded_rows"][0]["app"], "barnes_hut_force_app")

    def test_goal1071_artifacts_pass_when_named_as_goal1072_outputs(self) -> None:
        module = __import__("scripts.goal1073_goal1072_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            shutil.copyfile(
                ROOT / "docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_validation.json",
                artifact_dir / "facility_coverage_threshold_validation.json",
            )
            shutil.copyfile(
                ROOT / "docs/reports/goal1071_scale_up_probes/facility_coverage_threshold_2_5m_timing.json",
                artifact_dir / "facility_coverage_threshold_2_5m_timing.json",
            )
            shutil.copyfile(
                ROOT / "docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_validation.json",
                artifact_dir / "robot_prepared_pose_flags_validation.json",
            )
            shutil.copyfile(
                ROOT / "docs/reports/goal1071_scale_up_probes/robot_prepared_pose_flags_36m_timing.json",
                artifact_dir / "robot_prepared_pose_flags_36m_timing.json",
            )
            payload = module.build_intake(artifact_dir)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["overall_status"], "ready_for_public_wording_review")
        self.assertEqual(payload["validation_passed_count"], 2)
        self.assertEqual(payload["timing_floor_passed_count"], 2)
        self.assertEqual(payload["timing_below_floor_count"], 0)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_bad_validation_artifact_blocks(self) -> None:
        module = __import__("scripts.goal1073_goal1072_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            _write_json(
                artifact_dir / "facility_coverage_threshold_validation.json",
                {
                    "parameters": {"skip_validation": False},
                    "scenario": {"mode": "optix", "result": {"matches_oracle": False}},
                },
            )
            payload = module.build_intake(artifact_dir)
        self.assertFalse(payload["valid"])
        self.assertEqual(payload["overall_status"], "blocked")
        self.assertEqual(payload["blocked_count"], 1)

    def test_bad_robot_validation_artifact_blocks(self) -> None:
        module = __import__("scripts.goal1073_goal1072_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            _write_json(
                artifact_dir / "robot_prepared_pose_flags_validation.json",
                {
                    "validated": True,
                    "matches_oracle": False,
                    "mode": "optix",
                    "input_mode": "python_objects",
                    "result_mode": "pose_flags",
                },
            )
            payload = module.build_intake(artifact_dir)
        self.assertFalse(payload["valid"])
        self.assertEqual(payload["overall_status"], "blocked")
        self.assertEqual(payload["blocked_count"], 1)

    def test_missing_median_blocks_timing_artifact(self) -> None:
        module = __import__("scripts.goal1073_goal1072_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            _write_json(
                artifact_dir / "facility_coverage_threshold_2_5m_timing.json",
                {
                    "parameters": {"skip_validation": True},
                    "scenario": {"timings_sec": {"optix_query_sec": {"min_sec": 0.2, "max_sec": 0.3}}},
                },
            )
            payload = module.build_intake(artifact_dir)
        self.assertFalse(payload["valid"])
        self.assertEqual(payload["overall_status"], "blocked")
        self.assertEqual(payload["blocked_count"], 1)

    def test_below_floor_is_not_claim_ready(self) -> None:
        module = __import__("scripts.goal1073_goal1072_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            shutil.copyfile(
                ROOT / "docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_validation.json",
                artifact_dir / "facility_coverage_threshold_validation.json",
            )
            _write_json(
                artifact_dir / "facility_coverage_threshold_2_5m_timing.json",
                {
                    "parameters": {"skip_validation": True},
                    "scenario": {"timings_sec": {"optix_query_sec": {"median_sec": 0.01}}},
                },
            )
            shutil.copyfile(
                ROOT / "docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_validation.json",
                artifact_dir / "robot_prepared_pose_flags_validation.json",
            )
            shutil.copyfile(
                ROOT / "docs/reports/goal1071_scale_up_probes/robot_prepared_pose_flags_36m_timing.json",
                artifact_dir / "robot_prepared_pose_flags_36m_timing.json",
            )
            payload = module.build_intake(artifact_dir)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["overall_status"], "timing_floor_not_met")
        self.assertEqual(payload["timing_below_floor_count"], 1)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_cli_writes_intake_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "intake.json"
            output_md = Path(tmpdir) / "intake.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1073_goal1072_artifact_intake.py",
                    "--artifact-dir",
                    tmpdir,
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
            self.assertIn("needs_cloud_artifacts", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["expected_artifact_count"], 4)
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1073 Goal1072 Artifact Intake", markdown)
            self.assertIn("barnes_hut_force_app", markdown)


if __name__ == "__main__":
    unittest.main()
