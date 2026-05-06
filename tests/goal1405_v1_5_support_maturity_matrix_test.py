import unittest

import rtdsl as rt


class Goal1405V15SupportMaturityMatrixTest(unittest.TestCase):
    def test_support_maturity_matrix_covers_public_apps(self):
        matrix = rt.validate_v1_5_support_maturity_matrix()

        self.assertEqual(set(matrix), set(rt.public_apps()))
        self.assertEqual(len(matrix), 18)
        self.assertEqual(set(rt.V1_5_SUPPORT_MATURITY_STATUSES), {
            "standalone_v1_5_supported",
            "excluded_from_standalone_v1_5",
        })

    def test_included_apps_have_embree_optix_support_and_correctness(self):
        matrix = rt.validate_v1_5_support_maturity_matrix()

        included = {
            app for app, row in matrix.items()
            if row["standalone_included"]
        }
        self.assertEqual(len(included), 14)
        for app in included:
            with self.subTest(app=app):
                row = matrix[app]
                self.assertEqual(row["support_status"], "standalone_v1_5_supported")
                self.assertEqual(row["required_backends"], ("embree", "optix"))
                self.assertNotEqual(row["embree_support_status"], "not_exposed_by_app_cli")
                self.assertNotEqual(row["optix_support_status"], "not_exposed_by_app_cli")
                self.assertEqual(row["correctness_status"], "covered_by_existing_local_tests")
                self.assertTrue(row["release_gate_counts_as_passed"])

    def test_excluded_apps_are_not_part_of_standalone_v1_5_surface(self):
        matrix = rt.validate_v1_5_support_maturity_matrix()

        excluded = {
            app for app, row in matrix.items()
            if not row["standalone_included"]
        }
        self.assertEqual(excluded, {
            "apple_rt_demo",
            "hiprt_ray_triangle_hitcount",
            "polygon_set_jaccard",
            "segment_polygon_anyhit_rows",
        })
        for app in excluded:
            with self.subTest(app=app):
                row = matrix[app]
                self.assertEqual(row["support_status"], "excluded_from_standalone_v1_5")
                self.assertEqual(row["required_backends"], ())
                self.assertTrue(row["release_gate_counts_as_passed"])

    def test_summary_closes_support_maturity_gate(self):
        summary = rt.validate_v1_5_support_maturity_summary()

        self.assertTrue(summary["release_gate_complete"])
        self.assertTrue(summary["test_backed"])
        self.assertEqual(summary["included_app_count"], 14)
        self.assertEqual(summary["excluded_app_count"], 4)
        self.assertEqual(summary["failed_apps"], ())

    def test_release_gate_embeds_completed_support_maturity_summary(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertTrue(gate["gate_results"]["test_backed_support_maturity_matrix"])
        self.assertIn("test_backed_support_maturity_matrix", gate["passed_gates"])
        self.assertNotIn("test_backed_support_maturity_matrix", gate["failed_gates"])
        self.assertEqual(gate["support_maturity_included_app_count"], 14)
        self.assertEqual(gate["support_maturity_excluded_app_count"], 4)
        self.assertEqual(gate["support_maturity_failed_apps"], ())
        self.assertTrue(gate["support_maturity_test_backed"])
        self.assertFalse(gate["public_release_authorized"])


if __name__ == "__main__":
    unittest.main()
