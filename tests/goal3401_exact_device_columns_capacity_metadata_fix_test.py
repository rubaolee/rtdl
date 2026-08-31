from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
SLICE_ARTIFACT = ROOT / "docs" / "reports" / "goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json"
FULL_ARTIFACT = ROOT / "docs" / "reports" / "goal3398_full_br_county_exact_device_columns_2026-06-04.json"
OVERFLOW_ARTIFACT = ROOT / "docs" / "reports" / "goal3400_exact_device_columns_overflow_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3401_exact_device_columns_capacity_metadata_fix_2026-06-04.md"
NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3401ExactDeviceColumnsCapacityMetadataFixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slice_payload = json.loads(SLICE_ARTIFACT.read_text(encoding="utf-8"))
        cls.full_payload = json.loads(FULL_ARTIFACT.read_text(encoding="utf-8"))
        cls.overflow_payload = json.loads(OVERFLOW_ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.native = NATIVE.read_text(encoding="utf-8")

    def _producer_metadata(self, payload):
        return payload["metadata"]["v2_8_typed_producer_metadata"]

    def _typed_stream(self, payload):
        return payload["metadata"]["typed_result_stream"]

    def test_successful_slice_capacity_matches_allocated_exact_rows(self):
        payload = self.slice_payload
        producer = self._producer_metadata(payload)
        stream = self._typed_stream(payload)

        self.assertEqual(payload["rtdl_commit"][:8], "8bdc8a64")
        self.assertEqual(payload["exact_relation_row_count"], 11316)
        self.assertEqual(payload["device_column_row_count"], 11316)
        self.assertEqual(producer["capacity"], 11316)
        self.assertEqual(producer["capacity"], producer["row_count"])
        self.assertEqual(producer["capacity"], producer["exact_relation_row_count"])
        self.assertEqual(stream["page_capacity"], 11316)
        self.assertNotEqual(producer["capacity"], payload["point_count"] * payload["shape_count"])
        self.assertFalse(payload["overflow"])
        self.assertTrue(payload["device_resident"])

    def test_successful_full_capacity_matches_allocated_exact_rows(self):
        payload = self.full_payload
        producer = self._producer_metadata(payload)
        stream = self._typed_stream(payload)

        self.assertEqual(payload["rtdl_commit"][:8], "8bdc8a64")
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)
        self.assertEqual(payload["exact_relation_row_count"], 47262)
        self.assertEqual(payload["device_column_row_count"], 47262)
        self.assertEqual(producer["capacity"], 47262)
        self.assertEqual(producer["capacity"], producer["row_count"])
        self.assertEqual(producer["capacity"], producer["exact_relation_row_count"])
        self.assertEqual(stream["page_capacity"], 47262)
        self.assertNotEqual(producer["capacity"], 259756500)
        self.assertNotEqual(producer["capacity"], payload["point_count"] * payload["shape_count"])
        self.assertFalse(payload["overflow"])
        self.assertTrue(payload["device_resident"])

    def test_overflow_capacity_remains_the_caller_bound(self):
        payload = self.overflow_payload

        self.assertEqual(payload["rtdl_commit"][:8], "8bdc8a64")
        self.assertEqual(payload["relation_row_count"], 11316)
        self.assertEqual(payload["max_rows"], 100)
        self.assertEqual(payload["capacity"], 100)
        self.assertEqual(payload["row_count"], 0)
        self.assertTrue(payload["overflow"])
        self.assertFalse(payload["device_resident"])
        self.assertTrue(payload["as_cupy_columns_raised"])

    def test_native_fix_and_report_preserve_boundaries(self):
        self.assertIn("columns_out->capacity = 0u;", self.native)
        self.assertIn("columns_out->capacity = static_cast<uint64_t>(exact_count);", self.native)
        self.assertIn("no longer reports `15409152` capacity", self.report)
        self.assertIn("no longer reports `259756500` capacity", self.report)
        self.assertIn("does not implement chunked overflow recovery", self.report)
        self.assertIn("true zero-copy", self.report)

        for payload in (self.slice_payload, self.full_payload, self.overflow_payload):
            for key, value in payload["claim_boundary"].items():
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
