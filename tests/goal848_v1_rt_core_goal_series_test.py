from __future__ import annotations

import unittest

from scripts import goal848_v1_rt_core_goal_series as goal848


class Goal848V1RtCoreGoalSeriesTest(unittest.TestCase):
    def test_summary_counts_match_current_matrix(self) -> None:
        payload = goal848.build_goal_series()
        summary = payload["summary"]
        self.assertEqual(summary["public_app_count"], 18)
        self.assertEqual(summary["rt_core_ready_now"], 16)
        self.assertEqual(summary["rt_core_partial_ready_now"], 0)
        self.assertEqual(summary["needs_redesign_or_new_surface"], 0)
        self.assertEqual(summary["out_of_scope_for_nvidia_rt"], 2)

    def test_priority_buckets_match_expected_apps(self) -> None:
        payload = goal848.build_goal_series()
        buckets = payload["priority_buckets"]
        self.assertEqual(
            buckets["already_ready_keep_and_optimize"],
            [
                "graph_analytics",
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
                "barnes_hut_force_app",
            ],
        )
        self.assertEqual(
            buckets["must_finish_first"],
            [
                "database_analytics",
                "service_coverage_gaps",
                "event_hotspot_screening",
                "robot_collision_screening",
            ],
        )
        self.assertEqual(
            buckets["second_wave"],
            [],
        )
        self.assertEqual(
            buckets["out_of_scope_for_nvidia_rt"],
            ["apple_rt_demo", "hiprt_ray_triangle_hitcount"],
        )

    def test_goal_series_has_expected_consensus_points(self) -> None:
        payload = goal848.build_goal_series()
        items = {item["goal_id"]: item for item in payload["goal_series"]}
        self.assertEqual(items["Goal848"]["consensus_requirement"], "3-AI for planning significance")
        self.assertEqual(items["Goal849"]["consensus_requirement"], "2-AI before completion")
        self.assertEqual(items["Goal852"]["consensus_requirement"], "3-AI because it changes strategic scope")
        self.assertEqual(items["Goal853"]["consensus_requirement"], "3-AI because it changes flagship app scope")

    def test_fixed_radius_required_actions_use_scalar_count_terms(self) -> None:
        rows = {row["app"]: row for row in goal848.build_goal_series()["apps"]}
        self.assertIn("--output-mode density_count", rows["outlier_detection"]["required_action"])
        self.assertIn("scalar threshold-count", rows["outlier_detection"]["required_action"])
        self.assertIn("--output-mode core_count", rows["dbscan_clustering"]["required_action"])
        self.assertIn("scalar core-count", rows["dbscan_clustering"]["required_action"])
        self.assertNotIn("core-threshold", rows["dbscan_clustering"]["required_action"])


if __name__ == "__main__":
    unittest.main()
