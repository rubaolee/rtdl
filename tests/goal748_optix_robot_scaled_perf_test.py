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


class Goal748OptixRobotScaledPerfTest(unittest.TestCase):
    def test_lists_backends(self) -> None:
        payload = run_json("scripts/goal748_optix_robot_scaled_perf.py", "--list-backends")
        self.assertIn("optix_prepared_count", payload["backends"])
        self.assertIn("optix_prepared_pose_flags", payload["backends"])
        self.assertIn("embree_rows", payload["backends"])

    def test_portable_cpu_rows_small_case_matches_oracle(self) -> None:
        payload = run_json(
            "scripts/goal748_optix_robot_scaled_perf.py",
            "--backend",
            "cpu_rows",
            "--pose-count",
            "4",
            "--obstacle-count",
            "2",
            "--repeats",
            "1",
            "--warmups",
            "0",
        )
        self.assertEqual(payload["suite"], "goal748_optix_robot_scaled_perf")
        self.assertEqual(payload["edge_ray_count"], 16)
        result = payload["results"][0]
        self.assertEqual(result["backend"], "cpu_rows")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["output_shape"], "per_ray_dict_rows")

    def test_missing_optional_backends_are_recorded_without_strict(self) -> None:
        payload = run_json(
            "scripts/goal748_optix_robot_scaled_perf.py",
            "--backend",
            "optix_prepared_count",
            "--pose-count",
            "2",
            "--obstacle-count",
            "1",
            "--repeats",
            "1",
            "--warmups",
            "0",
        )
        result = payload["results"][0]
        self.assertIn(result["status"], {"ok", "skipped_or_failed"})
        self.assertIn("RTX RT-core speedup", payload["boundary"])

    def test_missing_optional_pose_flags_backend_is_recorded_without_strict(self) -> None:
        payload = run_json(
            "scripts/goal748_optix_robot_scaled_perf.py",
            "--backend",
            "optix_prepared_pose_flags",
            "--pose-count",
            "2",
            "--obstacle-count",
            "1",
            "--repeats",
            "1",
            "--warmups",
            "0",
        )
        result = payload["results"][0]
        self.assertEqual(result["backend"], "optix_prepared_pose_flags")
        self.assertIn(result["status"], {"ok", "skipped_or_failed"})
        if result["status"] == "ok":
            self.assertIn("matches_oracle_pose_flags", result)
            self.assertIn("colliding_pose_ids", result)
            self.assertIn("oracle_colliding_pose_ids", result)
            self.assertIn("pose_index_construction_sec", result)


if __name__ == "__main__":
    unittest.main()
