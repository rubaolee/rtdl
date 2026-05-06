import unittest

import rtdsl as rt


class Goal1406V15BenchmarkEvidenceMatrixTest(unittest.TestCase):
    def test_benchmark_evidence_matrix_covers_public_apps(self):
        matrix = rt.validate_v1_5_benchmark_evidence_matrix()

        self.assertEqual(set(matrix), set(rt.public_apps()))
        self.assertEqual(len(matrix), 18)
        self.assertEqual(set(rt.V1_5_BENCHMARK_EVIDENCE_STATUSES), {
            "covered_by_existing_same_contract_benchmark_evidence",
            "excluded_from_standalone_v1_5",
        })

    def test_included_apps_have_same_contract_benchmark_evidence_refs(self):
        matrix = rt.validate_v1_5_benchmark_evidence_matrix()

        included = {
            app for app, row in matrix.items()
            if row["standalone_included"]
        }
        self.assertEqual(len(included), 14)
        for app in included:
            with self.subTest(app=app):
                row = matrix[app]
                self.assertEqual(
                    row["benchmark_status"],
                    "covered_by_existing_same_contract_benchmark_evidence",
                )
                self.assertEqual(row["benchmark_readiness_status"], "ready_for_rtx_claim_review")
                self.assertTrue(row["evidence_refs"])
                self.assertTrue(row["benchmark_contract"])
                self.assertTrue(row["release_gate_counts_as_passed"])
                self.assertFalse(row["public_wording_authorized_by_this_gate"])

    def test_excluded_apps_are_not_benchmark_release_scope(self):
        matrix = rt.validate_v1_5_benchmark_evidence_matrix()

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
                self.assertEqual(matrix[app]["benchmark_status"], "excluded_from_standalone_v1_5")
                self.assertTrue(matrix[app]["release_gate_counts_as_passed"])

    def test_summary_closes_benchmark_gate_without_public_wording(self):
        summary = rt.validate_v1_5_benchmark_evidence_summary()

        self.assertTrue(summary["release_gate_complete"])
        self.assertEqual(summary["included_app_count"], 14)
        self.assertEqual(summary["excluded_app_count"], 4)
        self.assertEqual(summary["failed_apps"], ())
        self.assertFalse(summary["public_wording_authorized_by_this_gate"])

    def test_release_gate_embeds_completed_benchmark_summary(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertTrue(gate["gate_results"]["same_contract_per_app_benchmarks"])
        self.assertIn("same_contract_per_app_benchmarks", gate["passed_gates"])
        self.assertNotIn("same_contract_per_app_benchmarks", gate["failed_gates"])
        self.assertEqual(gate["benchmark_evidence_included_app_count"], 14)
        self.assertEqual(gate["benchmark_evidence_excluded_app_count"], 4)
        self.assertEqual(gate["benchmark_evidence_failed_apps"], ())
        self.assertFalse(gate["benchmark_evidence_public_wording_authorized"])
        self.assertFalse(gate["public_release_authorized"])


if __name__ == "__main__":
    unittest.main()
