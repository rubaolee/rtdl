import unittest

import rtdsl as rt


class Goal1401StandaloneCorrectnessMatrixTest(unittest.TestCase):
    def test_correctness_matrix_covers_public_apps_and_statuses(self):
        matrix = rt.validate_v1_5_standalone_correctness_matrix()

        self.assertEqual(set(matrix), set(rt.public_apps()))
        self.assertEqual(len(matrix), 18)
        self.assertEqual(set(rt.V1_5_STANDALONE_CORRECTNESS_STATUSES), {
            "covered_by_existing_local_tests",
            "defined_pending_execution",
            "excluded_from_standalone_v1_5",
        })

    def test_correctness_summary_closes_local_correctness_gate(self):
        summary = rt.validate_v1_5_standalone_correctness_summary()

        self.assertEqual(summary["covered_app_count"], 14)
        self.assertEqual(summary["pending_app_count"], 0)
        self.assertEqual(summary["excluded_app_count"], 4)
        self.assertTrue(summary["release_gate_complete"])
        self.assertEqual(summary["pending_apps"], ())

    def test_covered_apps_reference_existing_local_tests(self):
        matrix = rt.validate_v1_5_standalone_correctness_matrix()

        covered_apps = {
            app for app, row in matrix.items()
            if row["correctness_status"] == "covered_by_existing_local_tests"
        }
        self.assertEqual(covered_apps, {
            "ann_candidate_search",
            "barnes_hut_force_app",
            "database_analytics",
            "dbscan_clustering",
            "event_hotspot_screening",
            "facility_knn_assignment",
            "graph_analytics",
            "hausdorff_distance",
            "outlier_detection",
            "polygon_pair_overlap_area_rows",
            "road_hazard_screening",
            "robot_collision_screening",
            "segment_polygon_hitcount",
            "service_coverage_gaps",
        })
        for app in covered_apps:
            with self.subTest(app=app):
                self.assertTrue(matrix[app]["standalone_included"])
                self.assertEqual(matrix[app]["required_backends"], ("embree", "optix"))
                self.assertTrue(matrix[app]["test_modules"])
                self.assertTrue(matrix[app]["release_gate_counts_as_passed"])

    def test_pending_apps_define_missing_same_contract_evidence(self):
        matrix = rt.validate_v1_5_standalone_correctness_matrix()

        self.assertEqual(rt.V1_5_STANDALONE_CORRECTNESS_PENDING_APPS, ())
        for app in rt.V1_5_STANDALONE_CORRECTNESS_PENDING_APPS:
            with self.subTest(app=app):
                row = matrix[app]
                self.assertTrue(row["standalone_included"])
                self.assertEqual(row["correctness_status"], "defined_pending_execution")
                self.assertFalse(row["release_gate_counts_as_passed"])
                self.assertEqual(row["required_backends"], ("embree", "optix"))
                self.assertIn("required_evidence", row)

    def test_excluded_apps_align_with_standalone_classification(self):
        matrix = rt.validate_v1_5_standalone_correctness_matrix()

        excluded_apps = {
            app for app, row in matrix.items()
            if row["correctness_status"] == "excluded_from_standalone_v1_5"
        }
        self.assertEqual(excluded_apps, {
            "apple_rt_demo",
            "hiprt_ray_triangle_hitcount",
            "polygon_set_jaccard",
            "segment_polygon_anyhit_rows",
        })
        for app in excluded_apps:
            with self.subTest(app=app):
                self.assertFalse(matrix[app]["standalone_included"])
                self.assertFalse(matrix[app]["required_backends"])

    def test_release_gate_embeds_completed_correctness_summary(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertTrue(gate["gate_results"]["same_contract_per_app_correctness"])
        self.assertEqual(gate["same_contract_correctness_covered_app_count"], 14)
        self.assertEqual(gate["same_contract_correctness_pending_app_count"], 0)
        self.assertEqual(gate["same_contract_correctness_excluded_app_count"], 4)
        self.assertEqual(gate["same_contract_correctness_pending_apps"], ())
        self.assertIn("same_contract_per_app_correctness", gate["passed_gates"])
        self.assertFalse(gate["public_release_authorized"])


if __name__ == "__main__":
    unittest.main()
