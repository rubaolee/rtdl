import unittest
from pathlib import Path

import rtdsl as rt


class Goal690OptixPerformanceClassificationTest(unittest.TestCase):
    def test_every_public_app_has_optix_performance_classification(self):
        app_matrix = rt.app_engine_support_matrix()
        perf_matrix = rt.optix_app_performance_matrix()
        self.assertEqual(set(perf_matrix), set(app_matrix))
        for app, support in perf_matrix.items():
            with self.subTest(app=app):
                self.assertEqual(support.app, app)
                self.assertIn(support.performance_class, rt.OPTIX_APP_PERFORMANCE_CLASSES)
                self.assertTrue(support.note.strip())

    def test_high_risk_optix_paths_are_not_classified_as_rt_traversal(self):
        perf = rt.optix_app_performance_matrix()
        expected = {
            "graph_analytics": "optix_traversal",
            "road_hazard_screening": "optix_traversal_prepared_summary",
            "segment_polygon_hitcount": "optix_traversal_prepared_summary",
            "segment_polygon_anyhit_rows": "optix_traversal",
            "facility_knn_assignment": "optix_traversal_prepared_summary",
            "hausdorff_distance": "optix_traversal_prepared_summary",
            "ann_candidate_search": "optix_traversal_prepared_summary",
            "barnes_hut_force_app": "optix_traversal_prepared_summary",
            "outlier_detection": "optix_traversal_prepared_summary",
            "dbscan_clustering": "optix_traversal_prepared_summary",
            "robot_collision_screening": "optix_traversal",
            "database_analytics": "python_interface_dominated",
        }
        for app, performance_class in expected.items():
            with self.subTest(app=app):
                self.assertEqual(perf[app].performance_class, performance_class)

    def test_doc_records_optix_performance_classification(self):
        text = (Path(__file__).resolve().parents[1] / "docs" / "app_engine_support_matrix.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "OptiX Performance Classification",
            "rtdsl.optix_app_performance_matrix()",
            "host_indexed_fallback",
            "cuda_through_optix",
            "optix_traversal",
            "optix_traversal_prepared_summary",
            "python_interface_dominated",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
