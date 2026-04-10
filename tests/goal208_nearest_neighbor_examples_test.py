import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_fixed_radius_neighbors
from examples import rtdl_knn_rows


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class Goal208NearestNeighborExamplesTest(unittest.TestCase):
    def test_fixed_radius_example_runs_in_process(self) -> None:
        payload = rtdl_fixed_radius_neighbors.run_case("cpu_python_reference")
        self.assertEqual(payload["app"], "fixed_radius_neighbors")
        self.assertEqual(payload["radius"], 0.5)
        self.assertIn(100, payload["neighbors_by_query"])

    def test_knn_example_runs_in_process(self) -> None:
        payload = rtdl_knn_rows.run_case("cpu_python_reference")
        self.assertEqual(payload["app"], "knn_rows")
        self.assertEqual(payload["k"], 3)
        self.assertEqual(tuple(item["neighbor_rank"] for item in payload["neighbors_by_query"][100]), (1, 2, 3))

    def test_fixed_radius_example_cli(self) -> None:
        completed = subprocess.run(
            [
                PYTHON,
                "examples/rtdl_fixed_radius_neighbors.py",
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
        self.assertEqual(payload["app"], "fixed_radius_neighbors")

    def test_knn_example_cli(self) -> None:
        completed = subprocess.run(
            [
                PYTHON,
                "examples/rtdl_knn_rows.py",
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
        self.assertEqual(payload["app"], "knn_rows")


if __name__ == "__main__":
    unittest.main()
