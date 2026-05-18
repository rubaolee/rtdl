from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.json"


class Goal2085V2PerfTableAfterStreamingWitnessUpdateTest(unittest.TestCase):
    def test_tables_remain_filled_and_segment_anyhit_uses_streaming_contract(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_cells_filled"])
        self.assertEqual(16, len(payload["embree_rows"]))
        self.assertEqual(16, len(payload["optix_rt_rows"]))
        rows = {row["app"]: row for row in payload["optix_rt_rows"]}
        segment = rows["segment_polygon_anyhit_rows"]
        self.assertIn("streaming_exact_witness_page", segment["scale"])
        self.assertIn("streaming exact witness-column contract", segment["evidence_note"])
        self.assertLess(segment["v2_over_v1_8_ratio"], 1.0)

    def test_claim_boundary_preserves_release_gate(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["v2_0_release_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized_without_final_consensus"])
        self.assertTrue(boundary["segment_polygon_anyhit_rows_contract_changed_to_streaming_witness_columns"])


if __name__ == "__main__":
    unittest.main()
