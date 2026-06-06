from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal3561_near_parity_rows_probe_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3561_near_parity_rows_probe_2026-06-06.md"


class Goal3561NearParityRowsProbeTest(unittest.TestCase):
    def test_near_parity_rows_are_target_compliant(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        rows = {row["case_id"]: row for row in payload["rows"]}

        self.assertEqual(len(rows), 4)
        self.assertGreater(payload["min_speedup"], 0.99)
        self.assertGreater(payload["median_speedup"], 1.0)
        for row in rows.values():
            self.assertTrue(row["v23_target_met_by_observed_sum"], row["case_id"])
            self.assertTrue(row["v28_target_met_by_observed_sum"], row["case_id"])
            self.assertTrue(row["claim_boundary"]["internal_results_only"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["release_authorized"])

    def test_row_interpretation(self) -> None:
        rows = {
            row["case_id"]: row
            for row in json.loads(SUMMARY.read_text(encoding="utf-8"))["rows"]
        }
        self.assertAlmostEqual(
            rows["librts_optix_aabb_index"]["v28_speedup_vs_v23"],
            0.993580830750488,
        )
        self.assertGreater(
            rows["spatial_rayjoin_optix_prepared_full_route"]["v28_speedup_vs_v23"],
            1.04,
        )
        self.assertGreater(
            rows["robot_collision_optix_prepared_device_buffers"]["v28_speedup_vs_v23"],
            1.0,
        )

    def test_report_blocks_code_change_mandate(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("near-parity variance", text)
        self.assertIn("No immediate code change", text)
        self.assertIn("internal benchmark evidence only", text)


if __name__ == "__main__":
    unittest.main()
