from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_example(*args: str) -> str:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": "src:."},
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def run_json_example(*args: str) -> dict[str, object]:
    return json.loads(run_example(*args))


class Goal513PublicExampleSmokeTest(unittest.TestCase):
    def test_front_page_portable_examples_run(self) -> None:
        self.assertEqual(run_example("examples/rtdl_hello_world.py").strip(), "hello, world")

        cases = (
            ("examples/rtdl_segment_polygon_hitcount.py", "--backend", "cpu_python_reference", "--copies", "16"),
            ("examples/rtdl_graph_bfs.py", "--backend", "cpu_python_reference"),
            ("examples/rtdl_graph_triangle_count.py", "--backend", "cpu_python_reference"),
            ("examples/rtdl_db_conjunctive_scan.py", "--backend", "cpu_python_reference"),
            ("examples/rtdl_db_grouped_count.py", "--backend", "cpu_python_reference"),
            ("examples/rtdl_db_grouped_sum.py", "--backend", "cpu_python_reference"),
            ("examples/rtdl_v0_7_db_app_demo.py", "--backend", "auto"),
            ("examples/rtdl_v0_7_db_kernel_app_demo.py", "--backend", "auto"),
            ("examples/rtdl_hausdorff_distance_app.py", "--backend", "cpu_python_reference"),
            ("examples/rtdl_robot_collision_screening_app.py", "--backend", "cpu_python_reference"),
            ("examples/rtdl_barnes_hut_force_app.py", "--backend", "cpu_python_reference"),
        )

        for args in cases:
            with self.subTest(example=args[0]):
                payload = run_json_example(*args)
                self.assertTrue("app" in payload or "rows" in payload)

    def test_front_page_v08_examples_report_oracle_or_boundary(self) -> None:
        hausdorff = run_json_example("examples/rtdl_hausdorff_distance_app.py", "--backend", "cpu_python_reference")
        robot = run_json_example("examples/rtdl_robot_collision_screening_app.py", "--backend", "cpu_python_reference")
        barnes = run_json_example("examples/rtdl_barnes_hut_force_app.py", "--backend", "cpu_python_reference")

        self.assertTrue(hausdorff["matches_oracle"])
        self.assertTrue(robot["matches_oracle"])
        self.assertIn("Bounded one-level 2D approximation", barnes["boundary"])
        self.assertIn("candidate_row_count", barnes)

    def test_front_page_feature_cookbook_runs_all_public_recipes(self) -> None:
        payload = run_json_example("examples/rtdl_feature_quickstart_cookbook.py")

        self.assertEqual(payload["app"], "feature_quickstart_cookbook")
        self.assertGreaterEqual(payload["feature_count"], 19)
        recipe_names = {recipe["feature"] for recipe in payload["recipes"]}  # type: ignore[index]
        self.assertIn("hausdorff_distance_app", recipe_names)
        self.assertIn("robot_collision_screening_app", recipe_names)
        self.assertIn("barnes_hut_force_app", recipe_names)


if __name__ == "__main__":
    unittest.main()
