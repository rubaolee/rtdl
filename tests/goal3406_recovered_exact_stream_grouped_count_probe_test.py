from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3406_recovered_exact_stream_grouped_count_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3406_recovered_exact_stream_grouped_count_probe_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3406_recovered_exact_stream_grouped_count_probe.py"


class Goal3406RecoveredExactStreamGroupedCountProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_recovered_exact_stream_is_explicit_and_device_resident(self):
        payload = self.payload

        self.assertEqual(payload["schema"], "rtdl.goal3406.recovered_exact_stream_grouped_count_probe.v1")
        self.assertEqual(payload["goal"], 3406)
        self.assertEqual(payload["rtdl_commit"][:8], "86d3aa1e")
        self.assertEqual(payload["initial_max_rows"], 100)
        self.assertEqual(payload["overflow_retry_capacity_hint"], 11316)
        self.assertEqual(payload["exact_row_count"], 11316)
        self.assertEqual(payload["recovered_exact_row_count"], 11316)
        self.assertEqual(payload["exact_relation_row_count"], 11316)
        self.assertTrue(payload["recovered_device_resident"])

        overflow = payload["overflow_capacity_status"]
        self.assertEqual(overflow["capacity"], 100)
        self.assertEqual(overflow["row_count"], 0)
        self.assertEqual(overflow["required_capacity"], 11316)
        self.assertTrue(overflow["overflowed"])
        self.assertEqual(overflow["retry_capacity_hint"], 11316)

        recovered = payload["recovered_capacity_status"]
        self.assertEqual(recovered["capacity"], 11316)
        self.assertEqual(recovered["row_count"], 11316)
        self.assertEqual(recovered["required_capacity"], 11316)
        self.assertFalse(recovered["overflowed"])
        self.assertIsNone(recovered["retry_capacity_hint"])

    def test_grouped_count_from_recovered_stream_matches_host(self):
        payload = self.payload

        self.assertEqual(payload["group_count"], 4094)
        self.assertEqual(payload["device_group_count"], 4094)
        self.assertTrue(payload["group_counts_match_host"])
        self.assertEqual(payload["grouped_source_row_count"], 11316)
        self.assertEqual(payload["grouped_row_count"], 4094)
        self.assertFalse(payload["grouped_overflow"])
        self.assertEqual(payload["missing_group_key_count"], 0)
        self.assertEqual(payload["extra_group_key_count"], 0)
        self.assertEqual(payload["mismatched_group_value_count"], 0)

    def test_script_and_report_preserve_no_hidden_retry_boundary(self):
        self.assertIn("retry_hint = overflow_columns.retry_capacity_hint", self.script)
        self.assertIn("prepared.exact_device_columns(points, max_rows=retry_hint)", self.script)
        self.assertIn("grouped_count_by_left_id_compact_device_columns", self.script)
        self.assertIn("The recovery remains caller-controlled", self.report)
        self.assertIn("does not implement automatic retry", self.report)
        self.assertIn("hidden dispatch", self.report)

        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.payload["claim_boundary"]["automatic_retry_authorized"])
        self.assertFalse(self.payload["claim_boundary"]["hidden_dispatch_authorized"])


if __name__ == "__main__":
    unittest.main()
