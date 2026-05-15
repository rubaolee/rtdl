from __future__ import annotations

import pathlib
import json
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2077_embree_v18_v2_complete_table_runner.py"
REPORT_JSON = ROOT / "docs" / "reports" / "goal2077_complete_v18_v2_perf_tables_2026-05-15.json"
REPORT_MD = ROOT / "docs" / "reports" / "goal2077_complete_v18_v2_perf_tables_2026-05-15.md"


class Goal2077CompleteV18V2PerfTablesTest(unittest.TestCase):
    def test_runner_declares_complete_embree_surface_and_no_na_intent(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for app in (
            "database_analytics",
            "graph_analytics",
            "service_coverage_gaps",
            "event_hotspot_screening",
            "facility_knn_assignment",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
            "hausdorff_distance",
            "ann_candidate_search",
            "outlier_detection",
            "dbscan_clustering",
            "robot_collision_screening",
            "barnes_hut_force_app",
        ):
            self.assertIn(app, text)
        self.assertIn("all_cells_filled", text)
        self.assertIn("v1_8_way_embree_sec", text)
        self.assertIn("v2_embree_cpu_partner_sec", text)
        self.assertIn("RTDL_EMBREE_THREADS", text)

    def test_database_and_graph_are_measured_not_marked_ne(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('"database_analytics"', text)
        self.assertIn('"graph_analytics"', text)
        self.assertIn("--backend\", \"embree\"", text)
        self.assertIn("--scenario\", \"all\"", text)
        self.assertNotIn("n/e cells", text.lower())
        self.assertNotIn("not evaluable", text.lower())

    def test_help_works(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertIn("complete Embree", completed.stdout)
        self.assertIn("--scale", completed.stdout)
        self.assertIn("--apps", completed.stdout)

    def test_report_tables_are_complete_when_generated(self) -> None:
        if not REPORT_JSON.exists() or not REPORT_MD.exists():
            self.skipTest("Goal2077 evidence report has not been generated")

        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        text = REPORT_MD.read_text(encoding="utf-8")

        self.assertTrue(payload["all_cells_filled"])
        self.assertTrue(payload["all_optix_cells_filled"])
        self.assertEqual(16, len(payload["rows"]))
        self.assertEqual(16, len(payload["optix_rt_rows"]))
        self.assertIn("## Embree Table", text)
        self.assertIn("## OptiX/RT Table", text)
        self.assertNotIn("| n/a |", text.lower())
        self.assertNotIn("| failed |", text.lower())


if __name__ == "__main__":
    unittest.main()
