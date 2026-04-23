import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal760_optix_robot_pose_flags_phase_profiler.py"


class Goal760OptixRobotPoseFlagsPhaseProfilerTest(unittest.TestCase):
    def test_dry_run_schema_and_boundary(self):
        payload = __import__(
            "scripts.goal760_optix_robot_pose_flags_phase_profiler",
            fromlist=["run_suite"],
        ).run_suite(
            mode="dry-run",
            pose_count=8,
            obstacle_count=4,
            iterations=2,
            validate=True,
        )
        self.assertEqual(payload["suite"], "Goal760 OptiX robot pose-flags phase profiler")
        self.assertEqual(payload["mode"], "dry-run")
        self.assertTrue(payload["validated"])
        self.assertTrue(payload["matches_oracle"])
        self.assertIn("phase profiler, not a speedup claim", payload["boundary"])
        self.assertIn("dry-run mode is schema/logic validation only", payload["boundary"])

        phases = payload["phases"]
        for key in (
            "python_input_construction_sec",
            "optix_prepare_scene_sec",
            "optix_prepare_rays_sec",
            "prepared_pose_flags_warm_query_sec",
            "oracle_validate_sec",
            "close_sec",
            "total_sec",
        ):
            with self.subTest(key=key):
                self.assertIn(key, phases)

        self.assertEqual(phases["optix_prepare_scene_sec"], 0.0)
        self.assertEqual(phases["optix_prepare_rays_sec"], 0.0)
        self.assertGreaterEqual(phases["prepared_pose_flags_warm_query_sec"]["median_sec"], 0.0)
        self.assertIn("colliding_pose_count", payload["result"])

    def test_skip_validation_records_no_oracle_claim(self):
        payload = __import__(
            "scripts.goal760_optix_robot_pose_flags_phase_profiler",
            fromlist=["run_suite"],
        ).run_suite(
            mode="dry-run",
            pose_count=4,
            obstacle_count=2,
            iterations=1,
            validate=False,
        )
        self.assertFalse(payload["validated"])
        self.assertIsNone(payload["matches_oracle"])
        self.assertIsNone(payload["result"]["oracle_colliding_pose_count"])

    def test_packed_arrays_requires_optix_and_skip_validation(self):
        module = __import__(
            "scripts.goal760_optix_robot_pose_flags_phase_profiler",
            fromlist=["run_suite"],
        )
        with self.assertRaisesRegex(ValueError, "only supported with mode='optix'"):
            module.run_suite(
                mode="dry-run",
                pose_count=4,
                obstacle_count=2,
                iterations=1,
                validate=False,
                input_mode="packed_arrays",
            )
        with self.assertRaisesRegex(ValueError, "requires --skip-validation"):
            module.run_suite(
                mode="optix",
                pose_count=4,
                obstacle_count=2,
                iterations=1,
                validate=True,
                input_mode="packed_arrays",
            )

    def test_cli_emits_valid_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "dry-run",
                "--pose-count",
                "8",
                "--obstacle-count",
                "4",
                "--iterations",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "dry-run")
        self.assertIn("prepared_pose_flags_warm_query_sec", payload["phases"])


if __name__ == "__main__":
    unittest.main()
