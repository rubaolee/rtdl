from __future__ import annotations

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_coverage_audit import V4_COVERAGE_CANDIDATE
from rtdsl.v4_coverage_audit import V4_COVERAGE_DEFERRED
from rtdsl.v4_coverage_audit import V4_COVERAGE_PARTIAL_MEASURED
from rtdsl.v4_coverage_audit import V4_COVERAGE_STRONG_MEASURED
from rtdsl.v4_coverage_audit import validate_v4_goal4627_coverage_audit
from rtdsl.v4_coverage_audit import v4_goal4627_coverage_rows
from rtdsl.v4_coverage_audit import v4_goal4627_coverage_summary


class V4Goal4627CoverageAuditTest(unittest.TestCase):
    def test_audit_covers_all_promoted_benchmark_apps(self) -> None:
        rows = v4_goal4627_coverage_rows()

        self.assertEqual(
            tuple(row.app for row in rows),
            (
                "hausdorff_xhd",
                "spatial_rayjoin",
                "rt_dbscan",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "barnes_hut",
                "librts_spatial_index",
                "rtnn",
                "triangle_counting",
            ),
        )
        self.assertEqual(len(rows), 10)

    def test_summary_keeps_deferred_and_candidate_rows_visible(self) -> None:
        summary = v4_goal4627_coverage_summary()

        self.assertEqual(summary["row_count"], 10)
        self.assertEqual(summary["by_status"][V4_COVERAGE_STRONG_MEASURED], 4)
        self.assertEqual(summary["by_status"][V4_COVERAGE_PARTIAL_MEASURED], 4)
        self.assertEqual(summary["by_status"][V4_COVERAGE_CANDIDATE], 0)
        self.assertEqual(summary["by_status"][V4_COVERAGE_DEFERRED], 2)
        self.assertEqual(summary["latest_refresh_goal"], "Goal4637_after_aabb_index_frontdoor_catalog")
        self.assertFalse(summary["release_claim_authorized"])
        self.assertFalse(summary["broad_speedup_claim_authorized"])
        self.assertFalse(summary["whole_app_speedup_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])

    def test_recommends_grouped_i64_for_goal4628(self) -> None:
        summary = validate_v4_goal4627_coverage_audit()
        rows_by_app = {row.app: row for row in v4_goal4627_coverage_rows()}

        self.assertEqual(summary["recommended_goal4628_apps"], ("raydb_style",))
        self.assertEqual(
            summary["recommended_goal4628_operator"],
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        )
        self.assertTrue(rows_by_app["raydb_style"].recommended_for_goal4628)
        self.assertIn(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            rows_by_app["raydb_style"].mapped_v4_operators,
        )
        self.assertIn(
            "external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive",
            summary["fixed_radius_wrapper_prerequisite"],
        )

    def test_rejects_app_identity_and_candidate_shortcuts(self) -> None:
        rows_by_app = {row.app: row for row in v4_goal4627_coverage_rows()}

        self.assertEqual(rows_by_app["barnes_hut"].coverage_status, V4_COVERAGE_DEFERRED)
        self.assertEqual(rows_by_app["spatial_rayjoin"].coverage_status, V4_COVERAGE_DEFERRED)
        self.assertEqual(rows_by_app["librts_spatial_index"].coverage_status, V4_COVERAGE_STRONG_MEASURED)
        self.assertIn(
            "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
            rows_by_app["librts_spatial_index"].mapped_v4_operators,
        )
        self.assertIn("not a LibRTS paper reproduction", rows_by_app["librts_spatial_index"].release_gap)
        self.assertEqual(rows_by_app["rt_dbscan"].coverage_status, V4_COVERAGE_STRONG_MEASURED)
        self.assertIn(
            "v4_fixed_radius_graph_component_union_3d_device_arrays",
            rows_by_app["rt_dbscan"].mapped_v4_operators,
        )
        self.assertIn("operator coverage, not whole-app RTDBSCAN", rows_by_app["rt_dbscan"].release_gap)
        self.assertEqual(rows_by_app["triangle_counting"].coverage_status, V4_COVERAGE_STRONG_MEASURED)
        self.assertIn("goal4633", rows_by_app["triangle_counting"].evidence_refs[-1])
        self.assertIn("operator coverage, not whole-app", rows_by_app["triangle_counting"].release_gap)
        self.assertIn("whole-app triangle-counting speedup unauthorized", rows_by_app["triangle_counting"].next_action)


if __name__ == "__main__":
    unittest.main()
