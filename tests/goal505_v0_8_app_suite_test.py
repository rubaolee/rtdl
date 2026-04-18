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
from examples import rtdl_ann_candidate_app
from examples import rtdl_dbscan_clustering_app
from examples import rtdl_hausdorff_distance_app
from examples import rtdl_outlier_detection_app
from examples import rtdl_robot_collision_screening_app


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class Goal505V08AppSuiteTest(unittest.TestCase):
    def test_all_v0_8_apps_run_in_process(self) -> None:
        hausdorff = rtdl_hausdorff_distance_app.run_app("cpu_python_reference")
        ann = rtdl_ann_candidate_app.run_app("cpu_python_reference")
        outlier = rtdl_outlier_detection_app.run_app("cpu_python_reference")
        dbscan = rtdl_dbscan_clustering_app.run_app("cpu_python_reference")
        collision = rtdl_robot_collision_screening_app.run_app("cpu_python_reference")
        barnes_hut = rtdl_barnes_hut_force_app.run_app("cpu_python_reference")

        self.assertEqual(hausdorff["app"], "hausdorff_distance")
        self.assertTrue(hausdorff["matches_oracle"])
        self.assertEqual(ann["app"], "ann_candidate_search")
        self.assertAlmostEqual(float(ann["recall_at_1"]), 2.0 / 3.0)
        self.assertEqual(outlier["app"], "outlier_detection")
        self.assertTrue(outlier["matches_oracle"])
        self.assertEqual(dbscan["app"], "dbscan_clustering")
        self.assertTrue(dbscan["matches_oracle"])
        self.assertEqual(collision["app"], "robot_collision_screening")
        self.assertTrue(collision["matches_oracle"])
        self.assertEqual(barnes_hut["app"], "barnes_hut_force_app")
        self.assertLess(barnes_hut["max_relative_error"], 0.01)

    def test_v0_8_apps_preserve_boundary_messages(self) -> None:
        hausdorff = rtdl_hausdorff_distance_app.run_app("cpu_python_reference")
        ann = rtdl_ann_candidate_app.run_app("cpu_python_reference")
        outlier = rtdl_outlier_detection_app.run_app("cpu_python_reference")
        dbscan = rtdl_dbscan_clustering_app.run_app("cpu_python_reference")
        collision = rtdl_robot_collision_screening_app.run_app("cpu_python_reference")
        barnes_hut = rtdl_barnes_hut_force_app.run_app("cpu_python_reference")

        self.assertIn("RTDL emits k=1 nearest-neighbor rows", hausdorff["rtdl_role"])
        self.assertIn("Python-selected candidate subset", ann["rtdl_role"])
        self.assertIn("density counts into outlier labels", outlier["rtdl_role"])
        self.assertIn("RTDL emits fixed-radius neighbor rows", dbscan["rtdl_role"])
        self.assertIn("not continuous CCD", collision["boundary"])
        self.assertIn("RTDL does not yet expose hierarchical tree-node primitives", barnes_hut["boundary"])

    def test_v0_8_app_building_tutorial_links_examples(self) -> None:
        tutorial = (REPO_ROOT / "docs" / "tutorials" / "v0_8_app_building.md").read_text(encoding="utf-8")
        self.assertIn("examples/rtdl_hausdorff_distance_app.py", tutorial)
        self.assertIn("examples/rtdl_ann_candidate_app.py", tutorial)
        self.assertIn("examples/rtdl_outlier_detection_app.py", tutorial)
        self.assertIn("examples/rtdl_dbscan_clustering_app.py", tutorial)
        self.assertIn("examples/rtdl_robot_collision_screening_app.py", tutorial)
        self.assertIn("examples/rtdl_barnes_hut_force_app.py", tutorial)
        self.assertIn("tree-node inputs", tutorial)
        self.assertIn("opening predicate", tutorial)
        self.assertIn("vector reductions", tutorial)

    def test_v0_8_app_clis_emit_json(self) -> None:
        scripts = (
            ("examples/rtdl_hausdorff_distance_app.py", "hausdorff_distance"),
            ("examples/rtdl_ann_candidate_app.py", "ann_candidate_search"),
            ("examples/rtdl_outlier_detection_app.py", "outlier_detection"),
            ("examples/rtdl_dbscan_clustering_app.py", "dbscan_clustering"),
            ("examples/rtdl_robot_collision_screening_app.py", "robot_collision_screening"),
            ("examples/rtdl_barnes_hut_force_app.py", "barnes_hut_force_app"),
        )
        for script, app_name in scripts:
            with self.subTest(script=script):
                completed = subprocess.run(
                    [PYTHON, script, "--backend", "cpu_python_reference"],
                    check=True,
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    env={**os.environ, "PYTHONPATH": "src:."},
                )
                payload = json.loads(completed.stdout)
                self.assertEqual(payload["app"], app_name)


if __name__ == "__main__":
    unittest.main()
