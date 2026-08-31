from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3396_exact_device_columns_grouped_count_live_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3396_exact_device_columns_grouped_count_continuation_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3396_exact_device_columns_grouped_count_live_probe.py"


class Goal3396ExactDeviceColumnsGroupedCountContinuationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_exact_device_columns_feed_grouped_count_continuation(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3396.exact_device_columns_grouped_count_live_probe.v1")
        self.assertEqual(payload["goal"], 3396)
        self.assertEqual(payload["count"], 4096)
        self.assertEqual(payload["point_count"], 4096)
        self.assertEqual(payload["shape_count"], 3762)
        self.assertEqual(payload["exact_row_count"], 11316)
        self.assertEqual(payload["exact_device_row_count"], 11316)
        self.assertEqual(payload["exact_relation_row_count"], 11316)
        self.assertEqual(payload["group_count"], 4094)
        self.assertEqual(payload["device_group_count"], 4094)
        self.assertTrue(payload["group_counts_match_host"])
        self.assertEqual(payload["missing_group_key_count"], 0)
        self.assertEqual(payload["extra_group_key_count"], 0)
        self.assertEqual(payload["mismatched_group_value_count"], 0)
        self.assertEqual(payload["grouped_source_row_count"], 11316)
        self.assertEqual(payload["grouped_row_count"], 4094)
        self.assertFalse(payload["grouped_overflow"])
        self.assertIn("exact_device_columns(points)", self.script)
        self.assertIn("grouped_count_by_left_id_compact_device_columns", self.script)

    def test_claim_boundaries_and_report_are_bounded(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertIn("generic exact relation columns", self.report)
        self.assertIn("generic grouped", self.report)
        self.assertIn("does not authorize release", self.report)
        self.assertIn("device-only exact predicate", self.report)


if __name__ == "__main__":
    unittest.main()
