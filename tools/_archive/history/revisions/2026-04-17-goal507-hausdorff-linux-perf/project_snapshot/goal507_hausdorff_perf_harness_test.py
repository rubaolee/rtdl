from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from scripts import goal507_hausdorff_linux_perf


class Goal507HausdorffPerfHarnessTest(unittest.TestCase):
    def test_hausdorff_cli_exposes_gpu_backends(self) -> None:
        completed = subprocess.run(
            [sys.executable, "examples/rtdl_hausdorff_distance_app.py", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("optix", completed.stdout)
        self.assertIn("vulkan", completed.stdout)

    @unittest.skipUnless(importlib.util.find_spec("numpy") is not None, "numpy is required for the perf harness")
    def test_perf_harness_runs_tiny_cpu_case(self) -> None:
        payload = goal507_hausdorff_linux_perf.run_benchmark(sizes=(8,), iterations=1, backends=("cpu",))

        self.assertEqual(payload["goal"], "goal507_hausdorff_linux_perf")
        self.assertEqual(payload["sizes"], [8])
        case = payload["cases"][0]
        self.assertEqual(case["point_count_a"], 8)
        names = {measurement["name"] for measurement in case["measurements"]}
        self.assertIn("rtdl_cpu", names)
        for measurement in case["measurements"]:
            if measurement["name"] == "rtdl_cpu":
                self.assertEqual(measurement["status"], "ok")
                self.assertTrue(measurement["matches_reference_distance"])
                self.assertEqual(measurement["last_result"]["row_count"], 16)


if __name__ == "__main__":
    unittest.main()
