import unittest

from scripts import goal1408_v1_5_vs_v1_0_perf_runner as runner


class Goal1408V15VsV10PerfRunnerTest(unittest.TestCase):
    def test_profiles_cover_all_v1_5_included_apps(self):
        apps = {profile.app for profile in runner.PROFILES}

        self.assertEqual(apps, {
            "database_analytics",
            "graph_analytics",
            "service_coverage_gaps",
            "event_hotspot_screening",
            "facility_knn_assignment",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "polygon_pair_overlap_area_rows",
            "hausdorff_distance",
            "ann_candidate_search",
            "outlier_detection",
            "dbscan_clustering",
            "robot_collision_screening",
            "barnes_hut_force_app",
        })
        self.assertEqual(set(runner.EXCLUDED_APPS), {
            "apple_rt_demo",
            "hiprt_ray_triangle_hitcount",
            "polygon_set_jaccard",
            "segment_polygon_anyhit_rows",
        })

    def test_profile_commands_have_output_placeholder_and_boundary(self):
        for profile in runner.PROFILES:
            with self.subTest(app=profile.app, backend=profile.backend):
                self.assertIn("{output_json}", profile.command_template)
                self.assertTrue(profile.metric_hints)
                boundary = profile.boundary.lower()
                self.assertTrue("outside" in boundary or "no " in boundary)

    def test_select_metric_prefers_hinted_median(self):
        payload = {
            "timings_sec": {
                "input_build_sec": 9.0,
                "optix_query_sec": {"min_sec": 0.9, "median_sec": 1.25, "max_sec": 1.7},
            },
            "other": {"median_sec": 5.0},
        }

        metric = runner._select_metric(payload, ("optix_query_sec.median_sec",))

        self.assertEqual(metric["metric_path"], "timings_sec.optix_query_sec.median_sec")
        self.assertEqual(metric["seconds"], 1.25)

    def test_compare_classifies_v1_5_direction(self):
        v1_0 = {"metric": {"seconds": 10.0}}
        v1_5 = {"metric": {"seconds": 5.0}}

        comparison = runner._compare(v1_0, v1_5)

        self.assertEqual(comparison["status"], "compared")
        self.assertEqual(comparison["classification"], "v1_5_faster")
        self.assertEqual(comparison["v1_0_over_v1_5_ratio"], 2.0)

    def test_markdown_lists_excluded_apps(self):
        payload = {
            "current_commit": "current",
            "v1_0_commit": "old",
            "copies": 1,
            "iterations": 1,
            "boundary": "boundary",
            "rows": [],
            "excluded_apps": runner.EXCLUDED_APPS,
        }

        markdown = runner.to_markdown(payload)

        self.assertIn("polygon_set_jaccard", markdown)
        self.assertIn("COLLECT_K_BOUNDED", markdown)


if __name__ == "__main__":
    unittest.main()
