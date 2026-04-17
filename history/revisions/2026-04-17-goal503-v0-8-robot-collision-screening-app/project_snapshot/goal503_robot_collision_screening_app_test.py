from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_robot_collision_screening_app


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class Goal503RobotCollisionScreeningAppTest(unittest.TestCase):
    def test_robot_collision_app_matches_oracle(self) -> None:
        payload = rtdl_robot_collision_screening_app.run_app("cpu_python_reference")
        self.assertEqual(payload["app"], "robot_collision_screening")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["colliding_pose_ids"], [2, 3])

    def test_robot_collision_app_reports_clear_and_colliding_poses(self) -> None:
        payload = rtdl_robot_collision_screening_app.run_app("cpu_python_reference")
        by_pose = {int(row["pose_id"]): row for row in payload["pose_summaries"]}
        self.assertFalse(by_pose[1]["collides"])
        self.assertTrue(by_pose[2]["collides"])
        self.assertTrue(by_pose[3]["collides"])
        self.assertFalse(by_pose[4]["collides"])

    def test_robot_collision_app_cli(self) -> None:
        completed = subprocess.run(
            [
                PYTHON,
                "examples/rtdl_robot_collision_screening_app.py",
                "--backend",
                "cpu_python_reference",
            ],
            check=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["app"], "robot_collision_screening")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["colliding_pose_ids"], [2, 3])


if __name__ == "__main__":
    unittest.main()
