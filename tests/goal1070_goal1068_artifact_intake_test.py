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


class Goal1070Goal1068ArtifactIntakeTest(unittest.TestCase):
    def test_default_intake_waits_for_goal1068_cloud_artifacts(self) -> None:
        module = __import__("scripts.goal1070_goal1068_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = module.build_intake(Path(tmpdir))
        self.assertEqual(payload["overall_status"], "needs_cloud_artifacts")
        self.assertEqual(payload["expected_artifact_count"], 6)
        self.assertEqual(payload["missing_artifact_count"], 6)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not run cloud", payload["boundary"])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_manifest_timing_rows_all_have_floor(self) -> None:
        manifest_module = __import__("scripts.goal1068_next_rtx_pod_efficiency_batch", fromlist=["build_manifest"])
        timing_rows = [
            row
            for row in manifest_module.build_manifest()["rows"]
            if row["phase"] == "large_timing_repeat"
        ]
        self.assertEqual(len(timing_rows), 3)
        for row in timing_rows:
            self.assertEqual(row["timing_floor_sec"], 0.100)

    def test_complete_good_artifacts_are_ready_for_review_not_authorized(self) -> None:
        module = __import__("scripts.goal1070_goal1068_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for name in (
                "facility_coverage_threshold_validation.json",
                "barnes_hut_node_coverage_validation.json",
            ):
                _write_json(
                    root / name,
                    {
                        "parameters": {"skip_validation": False},
                        "scenario": {"mode": "optix", "result": {"matches_oracle": True}},
                    },
                )
            for name in (
                "facility_coverage_threshold_large_timing.json",
                "barnes_hut_node_coverage_1m_timing.json",
            ):
                _write_json(
                    root / name,
                    {
                        "scenario": {
                            "timings_sec": {
                                "optix_query_sec": {
                                    "min_sec": 0.11,
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
                {"phases": {"prepared_pose_flags_warm_query_sec": {"median_sec": 0.13}}},
            )
            payload = module.build_intake(root)
        self.assertEqual(payload["overall_status"], "ready_for_public_wording_review")
        self.assertEqual(payload["validation_passed_count"], 3)
        self.assertEqual(payload["timing_floor_passed_count"], 3)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_barnes_below_floor_keeps_review_blocked(self) -> None:
        module = __import__("scripts.goal1070_goal1068_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for name in (
                "facility_coverage_threshold_validation.json",
                "barnes_hut_node_coverage_validation.json",
            ):
                _write_json(
                    root / name,
                    {
                        "parameters": {"skip_validation": False},
                        "scenario": {"mode": "optix", "result": {"matches_oracle": True}},
                    },
                )
            _write_json(
                root / "facility_coverage_threshold_large_timing.json",
                {"scenario": {"timings_sec": {"optix_query_sec": {"median_sec": 0.15}}}},
            )
            _write_json(
                root / "barnes_hut_node_coverage_1m_timing.json",
                {"scenario": {"timings_sec": {"optix_query_sec": {"median_sec": 0.02, "max_sec": 0.20}}}},
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
        barnes = next(row for row in payload["rows"] if row["app"] == "barnes_hut_force_app" and row["phase"] == "large_timing_repeat")
        self.assertEqual(barnes["rtx_phase_sec"], 0.02)
        self.assertEqual(barnes["review_status"], "timing_below_floor")
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_bad_barnes_validation_blocks_intake(self) -> None:
        module = __import__("scripts.goal1070_goal1068_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "barnes_hut_node_coverage_validation.json",
                {
                    "parameters": {"skip_validation": False},
                    "scenario": {"mode": "optix", "result": {"matches_oracle": False}},
                },
            )
            payload = module.build_intake(root)
        barnes = next(row for row in payload["rows"] if row["app"] == "barnes_hut_force_app")
        self.assertEqual(barnes["review_status"], "blocked")
        self.assertEqual(payload["overall_status"], "blocked")
        self.assertFalse(payload["valid"])

    def test_bad_facility_and_robot_validation_block_intake(self) -> None:
        module = __import__("scripts.goal1070_goal1068_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "facility_coverage_threshold_validation.json",
                {
                    "parameters": {"skip_validation": True},
                    "scenario": {"mode": "optix", "result": {"matches_oracle": True}},
                },
            )
            _write_json(
                root / "robot_prepared_pose_flags_validation.json",
                {
                    "validated": True,
                    "matches_oracle": True,
                    "mode": "optix",
                    "input_mode": "packed_arrays",
                    "result_mode": "pose_flags",
                },
            )
            payload = module.build_intake(root)
        facility = next(row for row in payload["rows"] if row["app"] == "facility_knn_assignment")
        robot = next(row for row in payload["rows"] if row["app"] == "robot_collision_screening")
        self.assertEqual(facility["review_status"], "blocked")
        self.assertEqual(robot["review_status"], "blocked")
        self.assertEqual(payload["overall_status"], "blocked")
        self.assertFalse(payload["valid"])

    def test_missing_prepared_decision_median_blocks_timing_artifact(self) -> None:
        module = __import__("scripts.goal1070_goal1068_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "barnes_hut_node_coverage_1m_timing.json",
                {"scenario": {"timings_sec": {"optix_query_sec": {"max_sec": 0.20, "min_sec": 0.11}}}},
            )
            payload = module.build_intake(root)
        barnes = next(
            row
            for row in payload["rows"]
            if row["app"] == "barnes_hut_force_app" and row["phase"] == "large_timing_repeat"
        )
        self.assertEqual(barnes["review_status"], "blocked")
        self.assertIn("does not expose the expected RTX phase", barnes["reason"])
        self.assertEqual(payload["overall_status"], "blocked")

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / "artifacts"
            artifact_dir.mkdir()
            output_json = Path(tmpdir) / "goal1070.json"
            output_md = Path(tmpdir) / "goal1070.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1070_goal1068_artifact_intake.py",
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
            self.assertIn("Goal1070 Goal1068 Artifact Intake", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
