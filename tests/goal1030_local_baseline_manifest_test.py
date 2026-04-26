from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1030LocalBaselineManifestTest(unittest.TestCase):
    def test_manifest_covers_goal1029_apps(self) -> None:
        module = __import__("scripts.goal1030_local_baseline_manifest", fromlist=["build_manifest"])
        payload = module.build_manifest()
        apps = {entry["app"] for entry in payload["entries"]}
        expected = {
            "robot_collision_screening",
            "outlier_detection",
            "dbscan_clustering",
            "database_analytics:sales_risk",
            "database_analytics:regional_dashboard",
            "service_coverage_gaps",
            "event_hotspot_screening",
            "facility_knn_assignment",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "graph_analytics",
            "hausdorff_distance",
            "ann_candidate_search",
            "barnes_hut_force_app",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        }
        self.assertEqual(apps, expected)
        self.assertEqual(payload["entry_count"], len(expected))
        self.assertEqual(payload["status_counts"]["baseline_ready"], 4)
        self.assertEqual(payload["status_counts"]["baseline_partial"], 13)
        for entry in payload["entries"]:
            self.assertTrue(entry["commands"])
            for command in entry["commands"]:
                self.assertEqual(command[0], "python3")
                self.assertTrue(command[1].startswith(("examples/", "scripts/")))

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "manifest.json"
            output_md = Path(tmpdir) / "manifest.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1030_local_baseline_manifest.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["goal"], "Goal1030 local RTX baseline manifest")
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1030 Local RTX Baseline Manifest", markdown)
            self.assertIn("does not authorize speedup claims", markdown)


if __name__ == "__main__":
    unittest.main()
