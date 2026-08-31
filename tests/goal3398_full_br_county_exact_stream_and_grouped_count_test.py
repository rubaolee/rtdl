from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXACT = ROOT / "docs" / "reports" / "goal3398_full_br_county_exact_device_columns_2026-06-04.json"
GROUPED = ROOT / "docs" / "reports" / "goal3398_full_br_county_exact_grouped_count_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3398_full_br_county_exact_stream_and_grouped_count_2026-06-04.md"


class Goal3398FullBrCountyExactStreamAndGroupedCountTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exact = json.loads(EXACT.read_text(encoding="utf-8"))
        cls.grouped = json.loads(GROUPED.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_full_br_county_exact_device_columns_match_exact_rows(self):
        payload = self.exact
        self.assertEqual(payload["schema"], "rtdl.goal3394.optix_exact_membership_device_columns_live_probe.v1")
        self.assertEqual(payload["start"], 0)
        self.assertEqual(payload["count"], 16545)
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)
        self.assertEqual(payload["exact_row_count"], 47262)
        self.assertEqual(payload["device_column_row_count"], 47262)
        self.assertEqual(payload["exact_relation_row_count"], 47262)
        self.assertTrue(payload["pairs_match_exact_rows"])
        self.assertEqual(payload["missing_exact_pair_count"], 0)
        self.assertEqual(payload["extra_pair_count"], 0)
        self.assertTrue(payload["device_resident"])
        self.assertFalse(payload["overflow"])
        producer = payload["metadata"]["v2_8_typed_producer_metadata"]
        self.assertEqual(producer["schema_id"], "point_closed_shape_membership_2d_exact_device_columns")
        self.assertEqual(producer["exact_relation_row_count"], 47262)
        self.assertEqual(producer["legacy_pair_column_count_field"], "candidate_event_count")

    def test_full_br_county_grouped_count_matches_host_counts(self):
        payload = self.grouped
        self.assertEqual(payload["schema"], "rtdl.goal3396.exact_device_columns_grouped_count_live_probe.v1")
        self.assertEqual(payload["start"], 0)
        self.assertEqual(payload["count"], 16545)
        self.assertEqual(payload["exact_row_count"], 47262)
        self.assertEqual(payload["exact_device_row_count"], 47262)
        self.assertEqual(payload["exact_relation_row_count"], 47262)
        self.assertEqual(payload["group_count"], 16476)
        self.assertEqual(payload["device_group_count"], 16476)
        self.assertTrue(payload["group_counts_match_host"])
        self.assertEqual(payload["missing_group_key_count"], 0)
        self.assertEqual(payload["extra_group_key_count"], 0)
        self.assertEqual(payload["mismatched_group_value_count"], 0)
        self.assertFalse(payload["grouped_overflow"])
        for key, value in payload["claim_boundary"].items():
            self.assertFalse(value, key)

    def test_report_keeps_bridge_boundary(self):
        self.assertIn("full available `br_county.cdb`", self.report)
        self.assertIn("This is still a bridge", self.report)
        self.assertIn("does not authorize release", self.report)
        self.assertIn("device-only exact predicate", self.report)


if __name__ == "__main__":
    unittest.main()
