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

    def test_only_goal795_prepared_scalar_paths_enter_rtx_claim_review(self):
        readiness = rt.optix_app_benchmark_readiness_matrix()
        ready = [
            app
            for app, support in readiness.items()
            if support.status == "ready_for_rtx_claim_review"
        ]
        self.assertEqual(
            ready,
            [
                "outlier_detection",
                "dbscan_clustering",
                "robot_collision_screening",
            ],
        )

    def test_goal795_prepared_scalar_candidates_are_bounded_ready(self):
        expected = {
            "robot_collision_screening": "prepared ray/triangle any-hit scalar pose-count sub-path",
            "outlier_detection": "prepared fixed-radius scalar threshold-count sub-path",
            "dbscan_clustering": "prepared fixed-radius core-threshold summary",
        }
        for app, claim_phrase in expected.items():
            with self.subTest(app=app):
                support = rt.optix_app_benchmark_readiness(app)
                self.assertEqual(support.status, "ready_for_rtx_claim_review")
                self.assertIn(claim_phrase, support.allowed_claim)
                self.assertIn("Goal795", support.next_goal)

    def test_high_risk_or_non_optix_apps_are_not_benchmark_candidates(self):
        expected = {
            "database_analytics": "needs_interface_tuning",
            "graph_analytics": "needs_native_kernel_tuning",
            "road_hazard_screening": "needs_native_kernel_tuning",
            "segment_polygon_hitcount": "needs_native_kernel_tuning",
            "segment_polygon_anyhit_rows": "needs_native_kernel_tuning",
            "hausdorff_distance": "exclude_from_rtx_app_benchmark",
            "ann_candidate_search": "exclude_from_rtx_app_benchmark",
            "barnes_hut_force_app": "exclude_from_rtx_app_benchmark",
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
            "graph_analytics": "host_indexed_fallback",
            "apple_rt_demo": "not_optix_applicable",
            "service_coverage_gaps": "not_optix_exposed",
            "event_hotspot_screening": "not_optix_exposed",
            "facility_knn_assignment": "not_optix_exposed",
            "road_hazard_screening": "host_indexed_fallback",
            "segment_polygon_hitcount": "host_indexed_fallback",
            "segment_polygon_anyhit_rows": "host_indexed_fallback",
            "polygon_pair_overlap_area_rows": "not_optix_exposed",
            "polygon_set_jaccard": "not_optix_exposed",
            "hausdorff_distance": "cuda_through_optix",
            "ann_candidate_search": "cuda_through_optix",
            "outlier_detection": "optix_traversal_prepared_summary",
            "dbscan_clustering": "optix_traversal_prepared_summary",
            "robot_collision_screening": "optix_traversal",
            "barnes_hut_force_app": "cuda_through_optix",
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
