from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2342_v2_1_all_app_rethink_and_comparison_2026-05-18.md"
CATALOG = ROOT / "docs" / "application_catalog.md"
BENCHMARK_README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2343_gemini_review_goal2342_v2_1_all_app_rethink_2026-05-18.md"


APP_SCRIPTS = (
    "examples/v2_0/apps/analytics/rtdl_database_analytics_app.py",
    "examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py",
    "examples/v2_0/apps/geospatial/rtdl_event_hotspot_screening.py",
    "examples/v2_0/apps/geospatial/rtdl_facility_knn_assignment.py",
    "examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py",
    "examples/v2_0/apps/geospatial/rtdl_sales_risk_screening.py",
    "examples/v2_0/apps/geospatial/rtdl_service_coverage_gaps.py",
    "examples/v2_0/apps/ml/rtdl_ann_candidate_app.py",
    "examples/v2_0/apps/ml/rtdl_dbscan_clustering_app.py",
    "examples/v2_0/apps/ml/rtdl_outlier_detection_app.py",
    "examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py",
    "examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py",
    "examples/v2_0/apps/trajectory/rtdl_continuous_frechet_distance_app.py",
)


class Goal2342V21AllAppRethinkTest(unittest.TestCase):
    def test_report_covers_every_ordinary_app_script(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for script in APP_SCRIPTS:
            with self.subTest(script=script):
                self.assertIn(script, report)
        self.assertIn("no_app_specific_native", report)
        self.assertIn("no_rewrite_same_contract", report)

    def test_report_includes_both_research_benchmarks_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for required in (
            "RayJoin-Style Spatial Join",
            "Hausdorff/X-HD-Style Distance",
            "734.597 ms",
            "10.073 ms",
            "72.93x faster",
            "1.78x slower",
            "13.93x faster",
            "needs-pod-evidence",
            "needs-external-review",
            "Goal2343 Gemini review was received",
        ):
            with self.subTest(required=required):
                self.assertIn(required, report)

    def test_public_catalog_points_to_v2_1_rethink_without_stale_v2_0_only_framing(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")
        self.assertIn("v2.x-facing catalog", catalog)
        self.assertIn("v2.1 App Rethink Rule", catalog)
        self.assertIn("goal2342_v2_1_all_app_rethink_and_comparison_2026-05-18.md", catalog)
        self.assertNotIn("This is the v2.0-facing catalog", catalog)

    def test_research_benchmark_readme_is_v2_x_facing(self) -> None:
        readme = BENCHMARK_README.read_text(encoding="utf-8")
        self.assertIn("RTDL v2.x Research Benchmarks", readme)
        self.assertIn("v2.1 scale-aware grouped traversal defaults", readme)
        self.assertIn("v2.1 first-hit/nearest-boundary evidence", readme)
        self.assertIn("../../../docs/reports/goal2342_v2_1_all_app_rethink_and_comparison_2026-05-18.md", readme)
        self.assertNotIn("RTDL v2.0 Research Benchmarks", readme)

    def test_gemini_review_is_concrete(self) -> None:
        review = GEMINI_REVIEW.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", review)
        self.assertIn("26.394 ms", review)
        self.assertIn("13.93x", review)
        self.assertNotIn("[Insert Verdict Here]", review)
        self.assertNotIn("...", review)


if __name__ == "__main__":
    unittest.main()
