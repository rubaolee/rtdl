from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_barnes_hut_force_app


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class Goal504BarnesHutForceAppTest(unittest.TestCase):
    def test_barnes_hut_app_runs_with_bounded_error(self) -> None:
        payload = rtdl_barnes_hut_force_app.run_app("cpu_python_reference")
        self.assertEqual(payload["app"], "barnes_hut_force_app")
        self.assertEqual(payload["body_count"], 6)
        self.assertEqual(payload["node_count"], 4)
        self.assertEqual(payload["candidate_row_count"], 24)
        self.assertLess(payload["max_relative_error"], 0.01)

    def test_barnes_hut_app_uses_both_accepted_nodes_and_exact_fallback(self) -> None:
        payload = rtdl_barnes_hut_force_app.run_app("cpu_python_reference")
        force_rows = payload["force_rows"]
        self.assertTrue(any(row["accepted_node_ids"] for row in force_rows))
        self.assertTrue(any(row["exact_body_ids"] for row in force_rows))
        by_body = {int(row["body_id"]): row for row in force_rows}
        self.assertEqual(by_body[1]["accepted_node_ids"], [13])
        self.assertEqual(by_body[6]["accepted_node_ids"], [10, 12])

    def test_barnes_hut_app_cli(self) -> None:
        completed = subprocess.run(
            [
                PYTHON,
                "examples/rtdl_barnes_hut_force_app.py",
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
        self.assertEqual(payload["app"], "barnes_hut_force_app")
        self.assertLess(payload["max_relative_error"], 0.01)
        self.assertIn("RTDL does not yet expose hierarchical tree-node primitives", payload["boundary"])


if __name__ == "__main__":
    unittest.main()
