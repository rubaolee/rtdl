from __future__ import annotations

import json
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2086_streaming_witness_page_extended_scale_pod_2026-05-15.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2086_streaming_witness_page_extended_pod"


class Goal2086StreamingWitnessPageExtendedScalePodTest(unittest.TestCase):
    def _artifact(self, count: int) -> dict:
        matches = sorted(ARTIFACT_DIR.glob(f"*_{count}_cupy_*.json"))
        self.assertEqual(1, len(matches), f"expected one artifact for count={count}")
        return json.loads(matches[0].read_text(encoding="utf-8"))

    def test_report_records_extended_scale_without_release_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("32768", text)
        self.assertIn("65536", text)
        self.assertIn("No v2.0 release authorization", text)
        self.assertIn("No broad whole-app speedup authorization", text)
        self.assertNotIn("v2.0 is released", text.lower())

    def test_artifacts_preserve_exact_witnesses_and_avoid_overflow(self) -> None:
        for count in (32768, 65536):
            payload = self._artifact(count)
            metadata = payload["v2_0_streaming_exact_witness_page_columns"]["metadata"]
            self.assertEqual(count, payload["count"])
            self.assertEqual(count, metadata["exact_witness_count"])
            self.assertEqual(count, metadata["page_row_count"])
            self.assertFalse(metadata["overflowed"])
            self.assertTrue(metadata["full_python_row_table_materialization_avoided"])
            self.assertFalse(metadata["v2_0_release_authorized"])
            self.assertFalse(metadata["whole_app_speedup_claim_authorized"])

    def test_streaming_contract_beats_old_full_row_contract_at_large_scale(self) -> None:
        for count in (32768, 65536):
            payload = self._artifact(count)
            old = payload["v2_0_partner_columns_full_python_rows"]["query_summary"]["median_s"]
            new = payload["v2_0_streaming_exact_witness_page_columns"]["query_summary"]["median_s"]
            v18 = payload["v1_8_native_optix_rows"]["query_summary"]["median_s"]
            self.assertGreater(old / v18, 1.0)
            self.assertLess(new / v18, 0.02)
            self.assertLess(new / old, 0.002)

    def test_report_table_matches_artifact_ratios_after_rounding(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for count in (32768, 65536):
            payload = self._artifact(count)
            old = payload["v2_0_partner_columns_full_python_rows"]["query_summary"]["median_s"]
            new = payload["v2_0_streaming_exact_witness_page_columns"]["query_summary"]["median_s"]
            v18 = payload["v1_8_native_optix_rows"]["query_summary"]["median_s"]
            old_ratio = old / v18
            new_ratio = new / v18
            pattern = rf"\| {count} \| .* \| {old_ratio:.3f}x \| {new_ratio:.3f}x \|"
            self.assertRegex(text, re.compile(pattern))


if __name__ == "__main__":
    unittest.main()
