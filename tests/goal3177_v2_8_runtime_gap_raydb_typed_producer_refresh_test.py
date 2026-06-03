from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3177_v2_8_runtime_gap_raydb_typed_producer_refresh_2026-06-03.md"


class Goal3177V28RuntimeGapRaydbTypedProducerRefreshTest(unittest.TestCase):
    def test_raydb_row_records_typed_producer_metadata_and_remaining_residency_gap(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        raydb = rows["raydb_style"]

        self.assertIn("generic ray/triangle grouped-i64 typed producer metadata", raydb["current_best_path"])
        self.assertIn("native typed producer metadata now exists", raydb["current_bottleneck"])
        self.assertIn("device-resident output stream evidence", raydb["current_bottleneck"])
        self.assertIn("broader partner conformance", raydb["current_bottleneck"])
        self.assertIn("Goal3176", raydb["evidence_refs"])
        self.assertFalse(raydb["release_authorized"])
        self.assertFalse(raydb["public_speedup_claim_authorized"])
        self.assertFalse(raydb["rt_core_speedup_claim_authorized"])
        self.assertFalse(raydb["true_zero_copy_claim_authorized"])

    def test_gap_map_and_older_raydb_refresh_test_still_validate(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])

    def test_report_records_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3176",
            "RayDB-style grouped aggregates",
            "typed producer metadata",
            "device-resident output stream evidence",
            "`true_zero_copy_claim_authorized: False`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
