from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3404_exact_device_columns_explicit_retry_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3404_exact_device_columns_explicit_retry_probe_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3404_exact_device_columns_explicit_retry_probe.py"


class Goal3404ExactDeviceColumnsExplicitRetryProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_overflow_status_produces_explicit_retry_hint(self):
        payload = self.payload

        self.assertEqual(payload["schema"], "rtdl.goal3404.exact_device_columns_explicit_retry_probe.v1")
        self.assertEqual(payload["goal"], 3404)
        self.assertEqual(payload["rtdl_commit"][:8], "02bd4510")
        self.assertEqual(payload["point_count"], 4096)
        self.assertEqual(payload["shape_count"], 3762)
        self.assertEqual(payload["initial_max_rows"], 100)
        self.assertEqual(payload["overflow_capacity"], 100)
        self.assertEqual(payload["overflow_row_count"], 0)
        self.assertEqual(payload["overflow_required_capacity"], 11316)
        self.assertEqual(payload["overflow_retry_capacity_hint"], 11316)
        self.assertTrue(payload["overflow_wrap_raised"])
        self.assertIn("retry explicitly with max_rows>=required_capacity", payload["overflow_wrap_error"])

        status = payload["overflow_capacity_status"]
        self.assertEqual(status["capacity"], 100)
        self.assertEqual(status["row_count"], 0)
        self.assertEqual(status["required_capacity"], 11316)
        self.assertTrue(status["overflowed"])
        self.assertEqual(status["retry_capacity_hint"], 11316)
        self.assertFalse(status["partial_result_returned"])

    def test_explicit_retry_matches_exact_rows(self):
        payload = self.payload

        retry_status = payload["retry_capacity_status"]
        self.assertEqual(payload["retry_capacity"], 11316)
        self.assertEqual(payload["retry_row_count"], 11316)
        self.assertEqual(payload["exact_row_count"], 11316)
        self.assertFalse(payload["retry_overflow"])
        self.assertTrue(payload["retry_device_resident"])
        self.assertTrue(payload["pairs_match_exact_rows"])
        self.assertEqual(payload["missing_exact_pair_count"], 0)
        self.assertEqual(payload["extra_pair_count"], 0)

        self.assertEqual(retry_status["capacity"], 11316)
        self.assertEqual(retry_status["row_count"], 11316)
        self.assertEqual(retry_status["required_capacity"], 11316)
        self.assertFalse(retry_status["overflowed"])
        self.assertIsNone(retry_status["retry_capacity_hint"])
        self.assertFalse(retry_status["partial_result_returned"])

    def test_retry_is_explicit_and_boundaries_are_closed(self):
        self.assertIn("retry_hint = overflow_columns.retry_capacity_hint", self.script)
        self.assertIn("prepared.exact_device_columns(points, max_rows=retry_hint)", self.script)
        self.assertIn("This is not hidden dispatch or automatic retry", self.report)
        self.assertIn("does not implement automatic retry", self.report)
        self.assertIn("hidden dispatch", self.report)

        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.payload["claim_boundary"]["automatic_retry_authorized"])
        self.assertFalse(self.payload["claim_boundary"]["hidden_dispatch_authorized"])


if __name__ == "__main__":
    unittest.main()
