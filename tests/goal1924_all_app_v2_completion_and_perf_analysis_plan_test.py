from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1924_all_app_v2_completion_and_perf_analysis_plan_2026-05-13.md"


class Goal1924AllAppV2CompletionAndPerfAnalysisPlanTest(unittest.TestCase):
    def test_report_lists_all_active_app_rows_and_completion_state(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: execution-plan-not-complete", text)
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
            with self.subTest(app=app):
                self.assertIn(f"`{app}`", text)

    def test_report_decomposes_missing_work_by_reusable_family(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Family A: Fixed-Radius Decision and Scalar Summary", text)
        self.assertIn("Family B: Ray/Triangle Any-Hit Flags", text)
        self.assertIn("Family C: Segment/Polygon Count and Derived Flags", text)
        self.assertIn("Family D: Polygon Exact-Metric Continuations", text)
        self.assertIn("Family E: Columnar Database Analytics", text)
        self.assertIn("Family F: Graph Analytics", text)
        self.assertIn("complete Family A first", text)

    def test_report_defines_analysis_rules_not_just_speedup_table(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("The final report should not be a simple speedup table", text)
        self.assertIn("positive", text)
        self.assertIn("mixed", text)
        self.assertIn("negative", text)
        self.assertIn("not-comparable", text)
        self.assertIn("No, all apps are not finished in v2.0 yet", text)


if __name__ == "__main__":
    unittest.main()
