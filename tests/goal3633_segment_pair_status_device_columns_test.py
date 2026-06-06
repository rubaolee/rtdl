import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3633_segment_pair_status_device_columns_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3633_segment_pair_status_device_columns_a5000" / "summary.json"


class Goal3633SegmentPairStatusDeviceColumnsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_a5000_artifact_is_clean_and_matches_same_contract_references(self):
        self.assertEqual(self.summary["git_commit"][:8], "4a537484")
        self.assertEqual(self.summary["git_tracked_status_short"], "")
        self.assertIn("NVIDIA RTX A5000", self.summary["gpu"])
        self.assertTrue(self.summary["pod_validation_succeeded"])
        self.assertTrue(self.summary["all_same_contract_counts_match"])

    def test_status_device_columns_are_present_and_valid_for_every_case(self):
        for case in self.summary["cases"]:
            dense = case["optix"]["dense_device_count_route"]
            metadata = dense["metadata"]
            self.assertTrue(metadata["counts_device_ptr_nonzero"], case["name"])
            self.assertTrue(metadata["source_row_count_device_ptr_nonzero"], case["name"])
            self.assertTrue(metadata["overflow_device_ptr_nonzero"], case["name"])
            self.assertTrue(dense["status_device_columns_valid"], case["name"])
            self.assertEqual(dense["source_row_count_from_device_status"], dense["hit_pair_count"])
            self.assertEqual(dense["overflow_from_device_status"], 0)

    def test_residency_contract_moves_to_two_columns_but_blocks_full_residency(self):
        for case in self.summary["cases"]:
            contract = case["optix"]["dense_device_count_route"]["residency_contract"]
            self.assertEqual(contract["device_resident_column_count"], 2)
            self.assertFalse(contract["all_columns_device_resident"])
            self.assertTrue(contract["fallback_required"])
            self.assertFalse(contract["true_zero_copy_authorized"])
            self.assertFalse(contract["public_speedup_claim_authorized"])
            self.assertFalse(contract["release_authorized"])
            columns = {column["name"]: column for column in contract["columns"]}
            self.assertIn("segment_pair_left_id_counts", columns)
            self.assertIn("segment_pair_overflow_status", columns)
            self.assertIn("segment_pair_ambiguous_count", columns)
            self.assertTrue(columns["segment_pair_ambiguous_count"]["fallback_required"])

    def test_report_states_the_boundary(self):
        self.assertIn("Verdict: `accept-with-boundary`", self.report)
        self.assertIn("No app-specific rule or RayJoin-specific continuation was added", self.report)
        self.assertIn("not complete multi-column residency", self.report)
        self.assertIn("ambiguity classification", self.report)


if __name__ == "__main__":
    unittest.main()
