from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs/reports/goal3601_librts_same_contract_resident_repeat_a5000"
REPORT = ROOT / "docs/reports/goal3601_librts_same_contract_resident_repeat_2026-06-06.md"
SCRIPT = ROOT / "scripts/goal3601_librts_same_contract_resident_repeat.py"


class Goal3601LibRTSSameContractResidentRepeatTest(unittest.TestCase):
    def _payload(self, name: str) -> dict:
        return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))

    def test_artifacts_are_clean_same_contract_pair(self) -> None:
        v23 = self._payload("v23_summary.json")
        current = self._payload("current_summary.json")

        self.assertEqual(v23["schema"], "rtdl.goal3601.librts_same_contract_resident_repeat.v1")
        self.assertEqual(current["schema"], "rtdl.goal3601.librts_same_contract_resident_repeat.v1")
        self.assertEqual(v23["contract"], "generic_prepared_aabb_index_query_2d")
        self.assertEqual(current["contract"], "generic_prepared_aabb_index_query_2d")
        self.assertEqual(v23["primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(current["primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(v23["git_status_short"], "")
        self.assertEqual(current["git_status_short"], "")
        self.assertEqual(v23["source_commit"], "2a28365d0246d51f3e3322b546f8a68c58632db4")
        self.assertEqual(current["source_commit"], "42fb464c88502f5c32bcee2c7be255ed17c3aa20")

    def test_results_are_correct_and_long_enough(self) -> None:
        v23 = self._payload("v23_summary.json")
        current = self._payload("current_summary.json")

        self.assertTrue(v23["all_match_cpu_reference"])
        self.assertTrue(current["all_match_cpu_reference"])
        self.assertGreaterEqual(v23["repeat_protocol"]["query_total_sec"], 10.0)
        self.assertGreaterEqual(current["repeat_protocol"]["query_total_sec"], 10.0)
        self.assertEqual(
            {row["operation"]: row["count"] for row in v23["rows"]},
            {row["operation"]: row["count"] for row in current["rows"]},
        )
        self.assertEqual(
            {row["operation"]: row["count"] for row in current["rows"]},
            {
                "point_contains": 21475,
                "range_contains": 14675,
                "range_intersects": 32531,
            },
        )

    def test_current_is_near_parity_or_better_and_not_claim_authorized(self) -> None:
        v23 = self._payload("v23_summary.json")
        current = self._payload("current_summary.json")

        speedup = (
            v23["repeat_protocol"]["query_summed_median_sec"]
            / current["repeat_protocol"]["query_summed_median_sec"]
        )
        self.assertGreater(speedup, 1.0)
        self.assertLess(speedup, 1.1)
        for payload in (v23, current):
            boundary = payload["claim_boundary"]
            self.assertFalse(boundary["release_authorized"])
            self.assertFalse(boundary["public_speedup_claim_authorized"])
            self.assertFalse(boundary["paper_reproduction_claim_authorized"])
            self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
            self.assertFalse(boundary["true_zero_copy_claim_authorized"])

    def test_report_and_harness_capture_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("LibRTS is now a clean parity row", report)
        self.assertIn("No app-specific native symbol or engine customization was added", report)
        self.assertIn("public v2.9 speedup claims", report)
        self.assertIn("APP_MODULE", script)
        self.assertIn("generic_prepared_aabb_index_query_2d", script)
        self.assertIn("release_authorized", script)


if __name__ == "__main__":
    unittest.main()
