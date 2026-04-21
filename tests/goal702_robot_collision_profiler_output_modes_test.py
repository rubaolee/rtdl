from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_json(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": "src:."},
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal702RobotCollisionProfilerOutputModesTest(unittest.TestCase):
    def test_profiler_rows_mode_profiles_pose_flags_without_full_rows(self) -> None:
        payload = run_json(
            "scripts/goal691_optix_app_phase_profiler.py",
            "--backend",
            "cpu_python_reference",
            "--iterations",
            "1",
            "--output-mode",
            "pose_flags",
        )

        self.assertEqual(payload["summary_mode"], "rows")
        self.assertEqual(payload["output_mode"], "pose_flags")
        self.assertTrue(payload["last_output"]["matches_oracle"])
        self.assertEqual(payload["last_output"]["pose_flag_count"], 4)
        self.assertEqual(payload["last_output"]["colliding_pose_count"], 2)
        self.assertNotIn("row_count", payload["last_output"])

    def test_profiler_rows_mode_profiles_hit_count_without_full_rows(self) -> None:
        payload = run_json(
            "scripts/goal691_optix_app_phase_profiler.py",
            "--backend",
            "cpu_python_reference",
            "--iterations",
            "1",
            "--output-mode",
            "hit_count",
        )

        self.assertEqual(payload["summary_mode"], "rows")
        self.assertEqual(payload["output_mode"], "hit_count")
        self.assertTrue(payload["last_output"]["matches_oracle"])
        self.assertEqual(payload["last_output"]["hit_edge_count"], 7)
        self.assertNotIn("row_count", payload["last_output"])

    def test_profiler_default_full_mode_remains_backward_compatible(self) -> None:
        payload = run_json(
            "scripts/goal691_optix_app_phase_profiler.py",
            "--backend",
            "cpu_python_reference",
            "--iterations",
            "1",
        )

        self.assertEqual(payload["summary_mode"], "rows")
        self.assertEqual(payload["output_mode"], "full")
        self.assertTrue(payload["last_output"]["matches_oracle"])
        self.assertEqual(payload["last_output"]["row_count"], 16)
        self.assertEqual(payload["last_output"]["colliding_pose_count"], 2)


if __name__ == "__main__":
    unittest.main()
