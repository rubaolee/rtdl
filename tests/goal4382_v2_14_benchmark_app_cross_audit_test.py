from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4382_v2_14_benchmark_app_cross_audit_2026-06-14.md"


class Goal4382V214BenchmarkAppCrossAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.report = REPORT.read_text(encoding="utf-8")

    def test_report_covers_all_release_rows(self) -> None:
        for row_id in (
            "hausdorff_xhd_threshold",
            "spatial_rayjoin_lsi",
            "spatial_rayjoin_pip",
            "spatial_rayjoin_overlay",
            "rt_dbscan_core_flags_numba_signature",
            "robot_collision_grouped_segment_flags",
            "contact_manifold_aabb_collect_k",
            "raydb_style_grouped_i64_count",
            "barnes_hut_node_coverage",
            "librts_spatial_index_aabb",
            "rtnn_ranked_summary",
            "triangle_counting_any_hit",
        ):
            self.assertIn(f"`{row_id}`", self.report)

    def test_report_preserves_rtnn_lesson_and_blockers(self) -> None:
        self.assertIn("human-scale timing is not the same thing as large or paper-faithful data", self.report)
        self.assertIn("RTNN was fixed by adding native Embree aggregate", self.report)
        self.assertIn("Goal4383 fixed the biggest RTDBSCAN unfairness", self.report)
        self.assertIn("up to 524,288 synthetic points", self.report)
        self.assertIn("available exact CDB subset is 2/8", self.report)
        self.assertIn("Public-review-ready for the available 2/8 exact subset", self.report)
        self.assertIn("LibRTS AABB is now large on paper-like uniform fixtures", self.report)
        self.assertIn("fp32 envelope predicate aligned", self.report)
        self.assertIn("triangle counting is now large on synthetic RT-Graph-shaped fixtures", self.report)
        self.assertIn("Barnes-Hut node coverage is now large on synthetic fixed-depth quadtree cells", self.report)
        self.assertIn("1,000,000 bodies x 65,536 nodes", self.report)
        self.assertIn("Hausdorff threshold is now large at 1,048,576 points per side", self.report)
        self.assertIn("not exact X-HD paper data", self.report)
        self.assertIn("robot collision is now large at 9,437,184 query segments", self.report)
        self.assertIn("native device-buffer OptiX route can be reported separately", self.report)
        self.assertIn("contact is now large at 4,294,967,296 possible pairs", self.report)
        self.assertIn("jittered_grid_65536", self.report)
        self.assertIn("not a full contact-manifold solver", self.report)

    def test_report_keeps_public_wording_narrow(self) -> None:
        self.assertIn("2/8 available exact subset is allowed as public-review evidence", self.report)
        self.assertIn("full 8/8 Section 5.7 matrix remains blocked", self.report)
        self.assertIn("prepared primitive comparisons", self.report)
        self.assertIn("paper-dataset claims require the listed v2.14 cleanup reruns", self.report)


if __name__ == "__main__":
    unittest.main()
