import unittest

import rtdsl as rt


class Goal1400StandaloneAppClassificationTest(unittest.TestCase):
    def test_classification_covers_public_apps(self):
        matrix = rt.validate_v1_5_standalone_app_classification_matrix()

        self.assertEqual(set(matrix), set(rt.public_apps()))
        self.assertEqual(len(matrix), 18)
        self.assertEqual(set(rt.V1_5_STANDALONE_APP_CLASSIFICATIONS), {
            "fully_generic",
            "wrapper_backed",
            "scalar_only",
            "collection_dependent",
            "frozen",
            "demo_only",
        })

    def test_representative_classifications(self):
        matrix = rt.validate_v1_5_standalone_app_classification_matrix()

        self.assertEqual(matrix["service_coverage_gaps"]["classification"], "fully_generic")
        self.assertTrue(matrix["service_coverage_gaps"]["standalone_included"])
        self.assertEqual(matrix["database_analytics"]["classification"], "wrapper_backed")
        self.assertEqual(matrix["hausdorff_distance"]["classification"], "scalar_only")
        self.assertEqual(matrix["polygon_set_jaccard"]["classification"], "collection_dependent")
        self.assertFalse(matrix["polygon_set_jaccard"]["standalone_included"])
        self.assertEqual(matrix["hiprt_ray_triangle_hitcount"]["classification"], "frozen")
        self.assertFalse(matrix["hiprt_ray_triangle_hitcount"]["standalone_included"])
        self.assertEqual(matrix["apple_rt_demo"]["classification"], "demo_only")
        self.assertFalse(matrix["apple_rt_demo"]["standalone_included"])

    def test_collection_dependent_apps_are_excluded_until_collect_k_resolution(self):
        matrix = rt.validate_v1_5_standalone_app_classification_matrix()

        collection_apps = {
            app for app, row in matrix.items()
            if row["classification"] == "collection_dependent"
        }
        self.assertEqual(collection_apps, {"segment_polygon_anyhit_rows", "polygon_set_jaccard"})
        for app in collection_apps:
            with self.subTest(app=app):
                self.assertFalse(matrix[app]["standalone_included"])
                self.assertIn("COLLECT_K_BOUNDED", matrix[app]["generic_surface"])
                self.assertIn("excluded", matrix[app]["release_boundary"])

    def test_gate_counts_classification_as_complete_but_not_release_complete(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertTrue(gate["gate_results"]["app_migration_classification"])
        self.assertIn("app_migration_classification", gate["passed_gates"])
        self.assertEqual(gate["standalone_included_app_count"], 14)
        self.assertEqual(gate["standalone_excluded_app_count"], 4)
        self.assertFalse(gate["public_release_authorized"])
        self.assertFalse(gate["release_tag_action_authorized"])


if __name__ == "__main__":
    unittest.main()
