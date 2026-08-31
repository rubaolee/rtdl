from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3172_v2_8_runtime_gap_compact_mask_refresh_2026-06-03.md"


class Goal3172V28RuntimeGapCompactMaskRefreshTest(unittest.TestCase):
    def test_rayjoin_and_triangle_rows_record_direct_compact_mask_front_door(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}

        rayjoin = rows["spatial_rayjoin"]
        self.assertIn("direct v2.8 compact-mask typed-stream front door", rayjoin["current_best_path"])
        self.assertIn("relation-row typed producer metadata", rayjoin["current_bottleneck"])
        self.assertIn("boundary-witness ownership", rayjoin["current_bottleneck"])
        self.assertIn("Goal3147", rayjoin["evidence_refs"])
        self.assertIn("Goal3171", rayjoin["evidence_refs"])

        triangle = rows["triangle_counting"]
        self.assertIn("direct v2.8 compact-mask typed-stream front door", triangle["current_best_path"])
        self.assertIn("native typed candidate-row producer", triangle["current_bottleneck"])
        self.assertIn("resident continuation", triangle["current_bottleneck"])
        self.assertIn("Goal3147", triangle["evidence_refs"])
        self.assertIn("Goal3171", triangle["evidence_refs"])

        for row in (rayjoin, triangle):
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["true_zero_copy_claim_authorized"])

    def test_gap_map_still_validates_after_compact_mask_refresh(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["public_speedup_claim_authorized"])
        self.assertFalse(validation["rt_core_speedup_claim_authorized"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])

    def test_report_records_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3171",
            "Spatial RayJoin",
            "Triangle counting",
            "direct compact-mask typed-stream front door",
            "native typed hit-stream producer",
            "native typed candidate-row producer",
            "`release_authorized: False`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
