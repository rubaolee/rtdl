import json
import subprocess
import sys
import unittest
from pathlib import Path

from examples import rtdl_robot_collision_screening_app as robot


ROOT = Path(__file__).resolve().parents[1]


class Goal701RobotCollisionCompactOutputTest(unittest.TestCase):
    def test_pose_flags_output_omits_full_witness_rows_but_matches_oracle(self):
        payload = robot.run_app("cpu_python_reference", output_mode="pose_flags")

        self.assertEqual(payload["output_mode"], "pose_flags")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["colliding_pose_ids"], [2, 3])
        self.assertEqual(payload["colliding_pose_count"], 2)
        self.assertIn("pose_collision_flags", payload)
        self.assertNotIn("rows", payload)
        self.assertNotIn("edge_any_hit_rows", payload)
        self.assertNotIn("pose_summaries", payload)
        self.assertIn("Compact output modes reduce app-interface row volume", payload["boundary"])

    def test_hit_count_output_omits_full_witness_rows_but_matches_oracle(self):
        payload = robot.run_app("cpu_python_reference", output_mode="hit_count")

        self.assertEqual(payload["output_mode"], "hit_count")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["hit_edge_count"], payload["oracle_hit_edge_count"])
        self.assertGreater(payload["hit_edge_count"], 0)
        self.assertNotIn("rows", payload)
        self.assertNotIn("pose_collision_flags", payload)

    def test_default_full_output_is_backwards_compatible(self):
        payload = robot.run_app("cpu_python_reference")

        self.assertEqual(payload["output_mode"], "full")
        self.assertTrue(payload["matches_oracle"])
        self.assertIn("rows", payload)
        self.assertIn("edge_any_hit_rows", payload)
        self.assertIn("pose_summaries", payload)

    def test_cli_exposes_output_mode(self):
        completed = subprocess.run(
            [
                sys.executable,
                "examples/rtdl_robot_collision_screening_app.py",
                "--backend",
                "cpu_python_reference",
                "--output-mode",
                "pose_flags",
            ],
            cwd=ROOT,
            env={"PYTHONPATH": "src:."},
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["output_mode"], "pose_flags")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["colliding_pose_ids"], [2, 3])

    def test_cli_exposes_prepared_pose_flags_optix_summary_mode(self):
        completed = subprocess.run(
            [
                sys.executable,
                "examples/rtdl_robot_collision_screening_app.py",
                "--help",
            ],
            cwd=ROOT,
            env={"PYTHONPATH": "src:."},
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("prepared_pose_flags", completed.stdout)

    def test_prepared_pose_flags_requires_optix_backend(self):
        with self.assertRaisesRegex(ValueError, "require backend='optix'"):
            robot.run_app("cpu_python_reference", optix_summary_mode="prepared_pose_flags")


if __name__ == "__main__":
    unittest.main()
