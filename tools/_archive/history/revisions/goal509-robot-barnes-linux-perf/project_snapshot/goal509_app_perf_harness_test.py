from __future__ import annotations

import subprocess
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from scripts import goal509_app_perf_linux


class Goal509AppPerfHarnessTest(unittest.TestCase):
    def test_robot_cli_exposes_only_correctness_validated_gpu_backend(self) -> None:
        completed = subprocess.run(
            [sys.executable, "examples/rtdl_robot_collision_screening_app.py", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("optix", completed.stdout)
        self.assertNotIn("vulkan", completed.stdout)

    def test_barnes_cli_exposes_validated_gpu_backends(self) -> None:
        completed = subprocess.run(
            [sys.executable, "examples/rtdl_barnes_hut_force_app.py", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("optix", completed.stdout)
        self.assertIn("vulkan", completed.stdout)

    def test_robot_perf_tiny_cpu_case_matches_oracle(self) -> None:
        cases = goal509_app_perf_linux.run_robot_perf(
            sizes=(4,),
            obstacle_count=3,
            iterations=1,
            backends=("cpu",),
        )

        self.assertEqual(len(cases), 1)
        case = cases[0]
        self.assertEqual(case["pose_count"], 4)
        self.assertEqual(case["edge_ray_count"], 16)
        measurement = case["measurements"][0]
        self.assertEqual(measurement["status"], "ok")
        self.assertTrue(measurement["matches_oracle"])

    def test_barnes_perf_tiny_cpu_case_splits_candidate_and_full_app(self) -> None:
        cases = goal509_app_perf_linux.run_barnes_perf(
            sizes=(16,),
            iterations=1,
            backends=("cpu",),
        )

        self.assertEqual(len(cases), 1)
        case = cases[0]
        self.assertEqual(case["body_count"], 16)
        candidate = case["candidate_measurements"][0]
        full = case["full_measurements"][0]
        self.assertEqual(candidate["status"], "ok")
        self.assertTrue(candidate["matches_oracle"])
        self.assertEqual(full["status"], "ok")
        self.assertTrue(full["matches_reference_reduction"])
        self.assertIn("full_reference_summary", case)


if __name__ == "__main__":
    unittest.main()
