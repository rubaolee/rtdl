import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3631_segment_pair_backend_conformance_a5000_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3631_segment_pair_backend_conformance_a5000" / "summary.json"
RUNNER = ROOT / "scripts" / "goal3631_segment_pair_backend_conformance_runner.py"


class Goal3631SegmentPairBackendConformanceA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.runner = RUNNER.read_text(encoding="utf-8")

    def test_a5000_artifact_records_clean_tracked_source_and_all_matches(self):
        self.assertEqual(self.summary["schema"], "rtdl.goal3631.segment_pair_backend_conformance_a5000.v1")
        self.assertEqual(self.summary["goal"], 3631)
        self.assertIn("NVIDIA RTX A5000", self.summary["gpu"])
        self.assertEqual(self.summary["git_commit"][:8], "4a537484")
        self.assertEqual(self.summary["git_tracked_status_short"], "")
        self.assertTrue(self.summary["all_same_contract_counts_match"])
        self.assertTrue(self.summary["pod_validation_succeeded"])

    def test_all_cases_match_python_or_analytic_reference_cupy_and_optix(self):
        cases = {case["name"]: case for case in self.summary["cases"]}
        self.assertEqual(set(cases), {"adversarial", "crossing_grid_64", "crossing_grid_256", "crossing_grid_1024"})

        self.assertEqual(cases["adversarial"]["reference"]["hit_pair_count"], 23)
        self.assertEqual(cases["crossing_grid_1024"]["candidate_pair_count"], 1048576)
        self.assertEqual(cases["crossing_grid_1024"]["reference"]["hit_pair_count"], 1048576)

        for case in cases.values():
            self.assertTrue(case["all_same_contract_counts_match"], case["name"])
            for comparison in case["comparisons"].values():
                self.assertTrue(comparison["match"], (case["name"], comparison))
                self.assertEqual(comparison["diff_count"], 0)
            self.assertEqual(
                case["cupy_dense_same_contract"]["hit_pair_count"],
                case["optix"]["dense_device_count_route"]["hit_pair_count"],
            )

    def test_optix_dense_count_route_is_device_resident_but_bounded(self):
        for case in self.summary["cases"]:
            dense = case["optix"]["dense_device_count_route"]
            metadata = dense["metadata"]
            self.assertEqual(
                metadata["native_symbol"],
                "rtdl_optix_prepared_segment_pair_left_id_count_device_columns",
            )
            self.assertTrue(metadata["device_resident"])
            self.assertTrue(metadata["counts_device_ptr_nonzero"])
            self.assertTrue(metadata["source_row_count_device_ptr_nonzero"])
            self.assertTrue(metadata["overflow_device_ptr_nonzero"])
            self.assertFalse(metadata["overflow"])
            self.assertFalse(metadata["release_authorized"])
            self.assertFalse(metadata["true_zero_copy_authorized"])
            self.assertFalse(metadata["public_speedup_claim_authorized"])
            self.assertTrue(dense["status_device_columns_valid"])
            self.assertEqual(dense["source_row_count_from_device_status"], dense["hit_pair_count"])
            self.assertEqual(dense["overflow_from_device_status"], 0)

            contract = dense["residency_contract"]
            self.assertEqual(contract["device_resident_column_count"], 2)
            self.assertFalse(contract["all_columns_device_resident"])
            self.assertTrue(contract["fallback_required"])
            self.assertFalse(contract["true_zero_copy_authorized"])
            self.assertFalse(contract["release_authorized"])
            self.assertTrue(dense["validation_download_only"])

    def test_report_and_runner_keep_claim_boundaries_clear(self):
        for flag, value in self.summary["claim_boundary"].items():
            self.assertFalse(value, flag)
        self.assertIn("does not authorize", self.report)
        self.assertIn("validation download only", self.report)
        self.assertIn("not complete multi-column residency", self.report)
        self.assertIn("Goal3633", self.report)
        self.assertNotIn("RayJoin data loaders", self.runner)
        self.assertIn("segment_pair_left_id_dense_count_output_residency_contract", self.runner)
        self.assertIn("host_synchronized_before_consumer", self.runner)


if __name__ == "__main__":
    unittest.main()
