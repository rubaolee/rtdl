from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3400_exact_device_columns_overflow_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3400_exact_device_columns_overflow_probe_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3400_exact_device_columns_overflow_probe.py"


class Goal3400ExactDeviceColumnsOverflowProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_exact_device_columns_fail_closed_on_capacity_overflow(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3400.exact_device_columns_overflow_probe.v1")
        self.assertEqual(payload["goal"], 3400)
        self.assertEqual(payload["point_count"], 4096)
        self.assertEqual(payload["shape_count"], 3762)
        self.assertEqual(payload["max_rows"], 100)
        self.assertEqual(payload["relation_row_count"], 11316)
        self.assertEqual(payload["candidate_event_count"], 11316)
        self.assertEqual(payload["capacity"], 100)
        self.assertEqual(payload["row_count"], 0)
        self.assertTrue(payload["overflow"])
        self.assertFalse(payload["device_resident"])
        self.assertTrue(payload["as_cupy_columns_raised"])
        self.assertIn("cannot wrap an overflowed device pair-column stream", payload["as_cupy_columns_error"])
        self.assertIn("exact_device_columns(points, max_rows=args.max_rows)", self.script)

    def test_claim_boundaries_and_report_are_bounded(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertIn("fail-closed overflow behavior", self.report)
        self.assertIn("does not provide a streaming overflow recovery path yet", self.report)
        self.assertIn("does not authorize release", self.report)


if __name__ == "__main__":
    unittest.main()
