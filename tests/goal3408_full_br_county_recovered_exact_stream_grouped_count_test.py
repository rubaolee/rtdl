from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3408_full_br_county_recovered_exact_stream_grouped_count_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3408_full_br_county_recovered_exact_stream_grouped_count_2026-06-04.md"


class Goal3408FullBrCountyRecoveredExactStreamGroupedCountTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_full_br_county_recovered_stream_capacity_status(self):
        payload = self.payload

        self.assertEqual(payload["schema"], "rtdl.goal3406.recovered_exact_stream_grouped_count_probe.v1")
        self.assertEqual(payload["goal"], 3406)
        self.assertEqual(payload["rtdl_commit"][:8], "67da8826")
        self.assertEqual(payload["start"], 0)
        self.assertEqual(payload["count"], 16545)
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)
        self.assertEqual(payload["initial_max_rows"], 100)

        overflow = payload["overflow_capacity_status"]
        self.assertEqual(overflow["capacity"], 100)
        self.assertEqual(overflow["row_count"], 0)
        self.assertEqual(overflow["required_capacity"], 47262)
        self.assertTrue(overflow["overflowed"])
        self.assertEqual(overflow["retry_capacity_hint"], 47262)
        self.assertFalse(overflow["partial_result_returned"])

        recovered = payload["recovered_capacity_status"]
        self.assertEqual(recovered["capacity"], 47262)
        self.assertEqual(recovered["row_count"], 47262)
        self.assertEqual(recovered["required_capacity"], 47262)
        self.assertFalse(recovered["overflowed"])
        self.assertIsNone(recovered["retry_capacity_hint"])
        self.assertTrue(payload["recovered_device_resident"])

    def test_full_br_county_grouped_count_matches_host(self):
        payload = self.payload

        self.assertEqual(payload["exact_row_count"], 47262)
        self.assertEqual(payload["recovered_exact_row_count"], 47262)
        self.assertEqual(payload["exact_relation_row_count"], 47262)
        self.assertEqual(payload["group_count"], 16476)
        self.assertEqual(payload["device_group_count"], 16476)
        self.assertEqual(payload["grouped_source_row_count"], 47262)
        self.assertEqual(payload["grouped_row_count"], 16476)
        self.assertTrue(payload["group_counts_match_host"])
        self.assertFalse(payload["grouped_overflow"])
        self.assertEqual(payload["missing_group_key_count"], 0)
        self.assertEqual(payload["extra_group_key_count"], 0)
        self.assertEqual(payload["mismatched_group_value_count"], 0)

    def test_report_explains_schema_reuse_and_keeps_boundaries(self):
        self.assertIn("same probe run at full dataset scale", self.report)
        self.assertIn("does not implement automatic retry", self.report)
        self.assertIn("hidden dispatch", self.report)
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.payload["claim_boundary"]["automatic_retry_authorized"])
        self.assertFalse(self.payload["claim_boundary"]["hidden_dispatch_authorized"])


if __name__ == "__main__":
    unittest.main()
