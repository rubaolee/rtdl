import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3637_segment_pair_optional_ambiguity_status_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3637_segment_pair_ambiguity_status_a5000" / "summary.json"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3637SegmentPairOptionalAmbiguityStatusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.native = NATIVE.read_text(encoding="utf-8")

    def test_artifact_records_optional_route_and_clean_source_state(self):
        self.assertEqual(self.summary["git_commit"][:8], "1eeff46c")
        self.assertEqual(self.summary["git_tracked_status_short"], "")
        self.assertTrue(self.summary["include_ambiguity_status"])
        self.assertTrue(self.summary["pod_validation_succeeded"])
        self.assertTrue(self.summary["all_same_contract_counts_match"])

    def test_optional_ambiguity_status_matches_reference(self):
        cases = {case["name"]: case for case in self.summary["cases"]}
        self.assertEqual(set(cases), {"adversarial", "crossing_grid_1024", "crossing_grid_2048", "crossing_grid_4096"})
        self.assertEqual(cases["adversarial"]["reference"]["ambiguous_pair_count"], 19)

        for case in cases.values():
            dense = case["optix"]["dense_device_count_route"]
            metadata = dense["metadata"]
            self.assertTrue(metadata["ambiguous_count_device_ptr_nonzero"], case["name"])
            self.assertTrue(dense["ambiguity_device_status_valid"], case["name"])
            self.assertEqual(
                dense["ambiguous_count_from_device_status"],
                case["reference"]["ambiguous_pair_count"],
            )

    def test_full_residency_is_true_only_for_optional_status_route(self):
        for case in self.summary["cases"]:
            contract = case["optix"]["dense_device_count_route"]["residency_contract"]
            self.assertEqual(contract["device_resident_column_count"], 3)
            self.assertTrue(contract["all_columns_device_resident"])
            self.assertFalse(contract["fallback_required"])
            self.assertFalse(contract["true_zero_copy_authorized"])
            self.assertFalse(contract["public_speedup_claim_authorized"])
            self.assertFalse(contract["release_authorized"])

    def test_code_and_report_preserve_default_hot_route_boundary(self):
        self.assertIn("include_ambiguity_status: bool = False", self.runtime)
        self.assertIn("with_ambiguity_status", self.runtime)
        self.assertIn("segment_pair_ambiguity_count_kernel", self.native)
        self.assertIn("The default hot path from Goal3633 stays unchanged", self.report)
        self.assertIn("not enabled on the default hot route", self.report)
        self.assertIn("does not authorize", self.report)


if __name__ == "__main__":
    unittest.main()
