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


class Goal1065Goal1062ArtifactIntakeTest(unittest.TestCase):
    def test_default_intake_waits_for_goal1062_cloud_artifacts(self) -> None:
        module = __import__("scripts.goal1065_goal1062_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = module.build_intake(Path(tmpdir))
        self.assertEqual(payload["overall_status"], "needs_cloud_artifacts")
        self.assertEqual(payload["expected_artifact_count"], 4)
        self.assertEqual(payload["missing_artifact_count"], 4)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not run cloud", payload["boundary"])

    def test_complete_good_artifacts_are_ready_for_public_wording_review_not_authorized(self) -> None:
        module = __import__("scripts.goal1065_goal1062_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "facility_coverage_threshold_validation.json",
                {
                    "parameters": {"skip_validation": False},
                    "scenario": {"mode": "optix", "result": {"matches_oracle": True}},
                },
            )
            _write_json(
                root / "facility_coverage_threshold_large_timing.json",
                {
                    "scenario": {
                        "timings_sec": {
                            "optix_query_sec": {
                                "min_sec": 0.12,
                                "median_sec": 0.15,
                                "max_sec": 0.16,
                            }
                        }
                    }
                },
            )
            _write_json(
                root / "robot_prepared_pose_flags_validation.json",
                {
                    "validated": True,
                    "matches_oracle": True,
                    "mode": "optix",
                    "input_mode": "python_objects",
                    "result_mode": "pose_flags",
                },
            )
            _write_json(
                root / "robot_prepared_pose_flags_large_timing.json",
                {
                    "phases": {
                        "prepared_pose_flags_warm_query_sec": {
                            "min_sec": 0.11,
                            "median_sec": 0.13,
                            "max_sec": 0.14,
                        }
                    }
                },
            )
            payload = module.build_intake(root)
        self.assertEqual(payload["overall_status"], "ready_for_public_wording_review")
        self.assertEqual(payload["validation_passed_count"], 2)
        self.assertEqual(payload["timing_floor_passed_count"], 2)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_below_floor_timing_keeps_public_wording_blocked(self) -> None:
        module = __import__("scripts.goal1065_goal1062_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "facility_coverage_threshold_validation.json",
                {
                    "parameters": {"skip_validation": False},
                    "scenario": {"mode": "optix", "result": {"matches_oracle": True}},
                },
            )
            _write_json(
                root / "facility_coverage_threshold_large_timing.json",
                {"scenario": {"timings_sec": {"optix_query_sec": {"median_sec": 0.02}}}},
            )
            _write_json(
                root / "robot_prepared_pose_flags_validation.json",
                {
                    "validated": True,
                    "matches_oracle": True,
                    "mode": "optix",
                    "input_mode": "python_objects",
                    "result_mode": "pose_flags",
                },
            )
            _write_json(
                root / "robot_prepared_pose_flags_large_timing.json",
                {"phases": {"prepared_pose_flags_warm_query_sec": {"median_sec": 0.13}}},
            )
            payload = module.build_intake(root)
        self.assertEqual(payload["overall_status"], "timing_floor_not_met")
        self.assertEqual(payload["timing_below_floor_count"], 1)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_zero_median_timing_is_not_hidden_by_fallback_fields(self) -> None:
        module = __import__("scripts.goal1065_goal1062_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "facility_coverage_threshold_validation.json",
                {
                    "parameters": {"skip_validation": False},
                    "scenario": {"mode": "optix", "result": {"matches_oracle": True}},
                },
            )
            _write_json(
                root / "facility_coverage_threshold_large_timing.json",
                {
                    "scenario": {
                        "timings_sec": {
                            "optix_query_sec": {
                                "min_sec": 0.0,
                                "median_sec": 0.0,
                                "max_sec": 0.20,
                            }
                        }
                    }
                },
            )
            _write_json(
                root / "robot_prepared_pose_flags_validation.json",
                {
                    "validated": True,
                    "matches_oracle": True,
                    "mode": "optix",
                    "input_mode": "python_objects",
                    "result_mode": "pose_flags",
                },
            )
            _write_json(
                root / "robot_prepared_pose_flags_large_timing.json",
                {"phases": {"prepared_pose_flags_warm_query_sec": {"median_sec": 0.13}}},
            )
            payload = module.build_intake(root)
        facility_timing = next(
            row for row in payload["rows"]
            if row["app"] == "facility_knn_assignment" and row["phase"] == "large_timing_repeat"
        )
        self.assertEqual(facility_timing["rtx_phase_sec"], 0.0)
        self.assertEqual(facility_timing["review_status"], "timing_below_floor")

    def test_bad_validation_blocks_intake(self) -> None:
        module = __import__("scripts.goal1065_goal1062_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "robot_prepared_pose_flags_validation.json",
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
            output_json = Path(tmpdir) / "goal1065.json"
            output_md = Path(tmpdir) / "goal1065.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1065_goal1062_artifact_intake.py",
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
            self.assertIn("Goal1065 Goal1062 Artifact Intake", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
