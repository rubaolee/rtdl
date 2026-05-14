from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1946_all_app_v2_perf_deep_dive_2026-05-13.md"


class Goal1946AllAppV2PerfDeepDiveTest(unittest.TestCase):
    def test_report_covers_all_app_rows_and_classes(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

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

        self.assertIn("`positive` | 7", text)
        self.assertIn("`positive-subsecond` | 1", text)
        self.assertIn("`positive-bounded` | 3", text)
        self.assertIn("`positive-bounded-exact` | 5", text)

    def test_report_explains_speedups_without_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Aggregate speedup summaries", text)
        self.assertIn("must not be turned into a", text)
        self.assertIn("public \"RTDL is N times", text)
        self.assertIn("fixed-radius", text)
        self.assertIn("segment any-hit", text)
        self.assertIn("true device-handoff", text)
        self.assertIn("bounded evidence", text)
        self.assertIn("does not authorize v2.0 release", text)

    def test_report_keeps_bounded_rows_out_of_broad_speedup_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("### Bounded Families", text)
        self.assertIn("Goals1993-1994", text)
        self.assertIn("generic columnar partner path", text)
        self.assertIn("generic metric-table payload", text)
        self.assertIn("using bounded rows as broad speedup evidence", text)


if __name__ == "__main__":
    unittest.main()
