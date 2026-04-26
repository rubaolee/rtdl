import unittest
from pathlib import Path

import rtdsl as rt


class Goal705OptixAppBenchmarkReadinessTest(unittest.TestCase):
    def test_every_public_app_has_benchmark_readiness_row(self):
        apps = set(rt.public_apps())
        readiness = rt.optix_app_benchmark_readiness_matrix()
        self.assertEqual(set(readiness), apps)
        for app, support in readiness.items():
            with self.subTest(app=app):
                self.assertEqual(support.app, app)
                self.assertIn(support.status, rt.OPTIX_APP_BENCHMARK_READINESS_STATUSES)
                self.assertTrue(support.next_goal.strip())
                self.assertTrue(support.benchmark_contract.strip())
                self.assertTrue(support.blocker.strip())
                self.assertTrue(support.allowed_claim.strip())

    def test_only_reviewed_prepared_summary_paths_enter_rtx_claim_review(self):
        readiness = rt.optix_app_benchmark_readiness_matrix()
        ready = [
            app
            for app, support in readiness.items()
            if support.status == "ready_for_rtx_claim_review"
        ]
        self.assertEqual(
            ready,
            [
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
            ],
        )

    def test_goal795_prepared_scalar_candidates_are_bounded_ready(self):
        expected = {
            "service_coverage_gaps": (
                "bounded prepared gap-summary path",
                "Goal917",
            ),
            "event_hotspot_screening": (
                "bounded prepared count-summary path",
                "Goal917/Goal919",
            ),
            "facility_knn_assignment": (
                "bounded prepared facility service-coverage decision sub-path",
                "Goal887/Goal920",
            ),
            "graph_analytics": (
                "bounded graph visibility any-hit plus native BFS/triangle graph-ray candidate-generation sub-paths",
                "Goal889/Goal905/Goal929",
            ),
            "polygon_pair_overlap_area_rows": (
                "native-assisted candidate-discovery path",
                "Goal877/Goal929",
            ),
            "polygon_set_jaccard": (
                "native-assisted candidate-discovery path",
                "Goal877/Goal929",
            ),
            "robot_collision_screening": "prepared ray/triangle any-hit scalar pose-count sub-path",
            "outlier_detection": ("prepared fixed-radius scalar threshold-count sub-path", "Goal795/Goal992"),
            "dbscan_clustering": ("prepared fixed-radius scalar core-count sub-path", "Goal795/Goal992"),
            "database_analytics": ("prepared DB compact-summary traversal/filter/grouping sub-path", "Goal921/Goal941"),
            "road_hazard_screening": ("prepared native road-hazard summary traversal sub-path", "Goal933/Goal941"),
            "segment_polygon_hitcount": ("prepared native segment/polygon hit-count traversal sub-path", "Goal933/Goal941"),
            "segment_polygon_anyhit_rows": ("prepared bounded native pair-row traversal sub-path", "Goal934/Goal941"),
            "hausdorff_distance": ("prepared Hausdorff <= radius decision sub-path", "Goal887/Goal941"),
            "ann_candidate_search": ("prepared ANN candidate-coverage decision sub-path", "Goal887/Goal941"),
            "barnes_hut_force_app": ("prepared Barnes-Hut node-coverage decision sub-path", "Goal887/Goal941"),
        }
        for app, expected_value in expected.items():
            with self.subTest(app=app):
                support = rt.optix_app_benchmark_readiness(app)
                self.assertEqual(support.status, "ready_for_rtx_claim_review")
                if isinstance(expected_value, tuple):
                    claim_phrase, goal = expected_value
                else:
                    claim_phrase, goal = expected_value, "Goal795"
                self.assertIn(claim_phrase, support.allowed_claim)
                self.assertIn(goal, support.next_goal)

    def test_non_nvidia_apps_are_not_benchmark_candidates(self):
        expected = {
            "apple_rt_demo": "exclude_from_rtx_app_benchmark",
            "hiprt_ray_triangle_hitcount": "exclude_from_rtx_app_benchmark",
        }
        for app, status in expected.items():
            with self.subTest(app=app):
                self.assertEqual(rt.optix_app_benchmark_readiness(app).status, status)

    def test_readiness_api_is_in_public_all(self):
        for symbol in (
            "OPTIX_APP_BENCHMARK_READINESS_STATUSES",
            "optix_app_benchmark_readiness",
            "optix_app_benchmark_readiness_matrix",
        ):
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, rt.__all__)

    def test_goal705_pins_optix_performance_class_for_every_app(self):
        expected = {
            "database_analytics": "python_interface_dominated",
            "graph_analytics": "optix_traversal",
            "apple_rt_demo": "not_optix_applicable",
            "service_coverage_gaps": "optix_traversal_prepared_summary",
            "event_hotspot_screening": "optix_traversal_prepared_summary",
            "facility_knn_assignment": "optix_traversal_prepared_summary",
            "road_hazard_screening": "optix_traversal_prepared_summary",
            "segment_polygon_hitcount": "optix_traversal_prepared_summary",
            "segment_polygon_anyhit_rows": "optix_traversal",
            "polygon_pair_overlap_area_rows": "python_interface_dominated",
            "polygon_set_jaccard": "python_interface_dominated",
            "hausdorff_distance": "optix_traversal_prepared_summary",
            "ann_candidate_search": "optix_traversal_prepared_summary",
            "outlier_detection": "optix_traversal_prepared_summary",
            "dbscan_clustering": "optix_traversal_prepared_summary",
            "robot_collision_screening": "optix_traversal",
            "barnes_hut_force_app": "optix_traversal_prepared_summary",
            "hiprt_ray_triangle_hitcount": "not_optix_exposed",
        }
        self.assertEqual(set(expected), set(rt.public_apps()))
        perf = rt.optix_app_performance_matrix()
        for app, performance_class in expected.items():
            with self.subTest(app=app):
                self.assertEqual(perf[app].performance_class, performance_class)

    def test_prepared_summary_non_exclude_readiness_is_explicitly_allowlisted(self):
        allowed = {
            "outlier_detection": "rt_count_threshold_prepared summary sub-path uses OptiX traversal",
            "dbscan_clustering": "rt_core_flags_prepared summary sub-path uses OptiX traversal",
            "service_coverage_gaps": "gap_summary_prepared mode uses OptiX traversal",
            "event_hotspot_screening": "count_summary_prepared mode uses OptiX traversal",
            "facility_knn_assignment": "coverage_threshold_prepared mode uses OptiX traversal",
            "road_hazard_screening": "prepared road-hazard summary profiler uses native OptiX traversal",
            "segment_polygon_hitcount": "prepared hit-count profiler uses native OptiX traversal",
            "hausdorff_distance": "directed_threshold_prepared mode uses OptiX traversal",
            "ann_candidate_search": "candidate_threshold_prepared mode uses OptiX traversal",
            "barnes_hut_force_app": "node_coverage_prepared mode uses OptiX traversal",
        }
        non_excluded_prepared_summary_apps = {
            app
            for app, perf in rt.optix_app_performance_matrix().items()
            if perf.performance_class == "optix_traversal_prepared_summary"
            and rt.optix_app_benchmark_readiness(app).status != "exclude_from_rtx_app_benchmark"
        }
        self.assertEqual(non_excluded_prepared_summary_apps, set(allowed))

    def test_public_doc_records_readiness_gate_and_cloud_policy(self):
        doc = Path(__file__).resolve().parents[1] / "docs" / "app_engine_support_matrix.md"
        text = doc.read_text(encoding="utf-8")
        for phrase in (
            "OptiX RTX Benchmark Readiness",
            "rtdsl.optix_app_benchmark_readiness_matrix()",
            "do not rent or keep a paid RTX instance",
            "needs_phase_contract",
            "needs_real_rtx_artifact",
            "needs_interface_tuning",
            "needs_native_kernel_tuning",
            "needs_postprocess_split",
            "exclude_from_rtx_app_benchmark",
            "ready_for_rtx_claim_review",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_goal_report_records_follow_up_goal_sequence(self):
        report = (
            Path(__file__).resolve().parents[1]
            / "docs"
            / "reports"
            / "goal705_optix_app_benchmark_readiness_goals_2026-04-21.md"
        )
        text = report.read_text(encoding="utf-8")
        for phrase in (
            "Goal706: DB analytics interface tuning.",
            "Goal707: graph analytics native-kernel decision.",
            "Goal708: segment/polygon native/compact-path tuning.",
            "Goal709: CUDA-through-OptiX app classification closure.",
            "Goal710: outlier fixed-radius summary timing cleanup.",
            "Goal711: DBSCAN core-flag timing cleanup.",
            "Goal712: robot collision flagship timing cleanup.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
