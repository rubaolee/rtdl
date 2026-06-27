from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_ann_candidate_app
from examples import rtdl_dbscan_clustering_app
from examples import rtdl_outlier_detection_app


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class Goal520DbscanClusteringAppTest(unittest.TestCase):
    def test_ann_candidate_app_reports_bounded_approximation_quality(self) -> None:
        payload = rtdl_ann_candidate_app.run_app("cpu_python_reference")

        self.assertEqual(payload["app"], "ann_candidate_search")
        self.assertEqual(payload["query_count"], 3)
        self.assertEqual(payload["candidate_count"], 3)
        self.assertEqual(payload["exact_match_count"], 2)
        self.assertAlmostEqual(float(payload["recall_at_1"]), 2.0 / 3.0)
        self.assertIn("does not yet provide an ANN index", payload["boundary"])

    def test_outlier_app_matches_brute_force_oracle(self) -> None:
        payload = rtdl_outlier_detection_app.run_app("cpu_python_reference")

        self.assertEqual(payload["app"], "outlier_detection")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["outlier_point_ids"], [7, 8])
        self.assertIn("density-threshold outlier demo", payload["boundary"])

    def test_dbscan_app_matches_brute_force_oracle(self) -> None:
        payload = rtdl_dbscan_clustering_app.run_app("cpu_python_reference")

        self.assertEqual(payload["app"], "dbscan_clustering")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["cluster_sizes"], {1: 4, 2: 3})
        self.assertEqual(payload["noise_point_ids"], [8])

    def test_dbscan_app_scales_fixture_without_cross_copy_merges(self) -> None:
        payload = rtdl_dbscan_clustering_app.run_app("cpu_python_reference", copies=2)

        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["point_count"], 16)
        self.assertEqual(payload["cluster_sizes"], {1: 4, 2: 3, 3: 4, 4: 3})
        self.assertEqual(payload["noise_point_ids"], [8, 108])

    def test_dbscan_app_boundary_message_preserves_language_scope(self) -> None:
        payload = rtdl_dbscan_clustering_app.run_app("cpu_python_reference")

        self.assertIn("RTDL emits fixed-radius neighbor rows", payload["rtdl_role"])
        self.assertIn("does not yet expose clustering expansion", payload["boundary"])

    def test_stage1_proximity_clis_emit_json(self) -> None:
        cases = (
            ("examples/rtdl_ann_candidate_app.py", "ann_candidate_search"),
            ("examples/rtdl_outlier_detection_app.py", "outlier_detection"),
            ("examples/rtdl_dbscan_clustering_app.py", "dbscan_clustering"),
        )
        for script, app_name in cases:
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

    def test_public_docs_include_dbscan_app(self) -> None:
        examples_readme = (REPO_ROOT / "examples" / "README.md").read_text(encoding="utf-8")
        tutorial = (REPO_ROOT / "docs" / "tutorials" / "v0_8_app_building.md").read_text(encoding="utf-8")
        release_examples = (REPO_ROOT / "docs" / "release_facing_examples.md").read_text(encoding="utf-8")
        itre = (REPO_ROOT / "docs" / "rtdl" / "itre_app_model.md").read_text(encoding="utf-8")

        for text in (examples_readme, tutorial, release_examples, itre):
            self.assertIn("rtdl_ann_candidate_app.py", text)
            self.assertIn("rtdl_dbscan_clustering_app.py", text)
            self.assertIn("rtdl_outlier_detection_app.py", text)
            self.assertIn("ANN", text)
            self.assertIn("DBSCAN", text)
            self.assertIn("outlier", text)


if __name__ == "__main__":
    unittest.main()
