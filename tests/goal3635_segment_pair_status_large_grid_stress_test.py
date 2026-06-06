import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3635_segment_pair_status_large_grid_stress_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3635_segment_pair_status_large_grid_a5000" / "summary.json"


class Goal3635SegmentPairStatusLargeGridStressTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_large_grid_artifact_records_clean_a5000_source_state(self):
        self.assertEqual(self.summary["git_commit"][:8], "11b9721c")
        self.assertEqual(self.summary["git_tracked_status_short"], "")
        self.assertIn("NVIDIA RTX A5000", self.summary["gpu"])
        self.assertTrue(self.summary["pod_validation_succeeded"])
        self.assertTrue(self.summary["all_same_contract_counts_match"])

    def test_large_grid_cases_match_and_keep_status_columns_valid(self):
        cases = {case["name"]: case for case in self.summary["cases"]}
        self.assertEqual(set(cases), {"adversarial", "crossing_grid_2048", "crossing_grid_4096"})
        self.assertEqual(cases["crossing_grid_2048"]["candidate_pair_count"], 4194304)
        self.assertEqual(cases["crossing_grid_4096"]["candidate_pair_count"], 16777216)

        for case in cases.values():
            dense = case["optix"]["dense_device_count_route"]
            self.assertTrue(case["all_same_contract_counts_match"], case["name"])
            self.assertTrue(dense["status_device_columns_valid"], case["name"])
            self.assertEqual(dense["source_row_count_from_device_status"], dense["hit_pair_count"])
            self.assertEqual(dense["overflow_from_device_status"], 0)
            self.assertTrue(dense["validation_download_only"])
            self.assertEqual(dense["residency_contract"]["device_resident_column_count"], 2)
            self.assertFalse(dense["residency_contract"]["all_columns_device_resident"])
            self.assertTrue(dense["residency_contract"]["fallback_required"])

    def test_claim_boundary_and_diagnostic_timing_wording_are_conservative(self):
        for flag, value in self.summary["claim_boundary"].items():
            self.assertFalse(value, flag)
        self.assertIn("diagnostic only", self.report)
        self.assertIn("not a public performance claim", self.report)
        self.assertIn("CuPy's dense kernel is faster", self.report)
        self.assertIn("does not authorize public RT-core speedup wording", self.report)
        self.assertIn("ambiguous_count", self.report)


if __name__ == "__main__":
    unittest.main()
