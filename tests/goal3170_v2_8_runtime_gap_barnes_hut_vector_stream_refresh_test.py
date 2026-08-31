from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3170_v2_8_runtime_gap_barnes_hut_vector_stream_refresh_2026-06-03.md"


class Goal3170V28RuntimeGapBarnesHutVectorStreamRefreshTest(unittest.TestCase):
    def test_barnes_hut_gap_row_records_goal3169_front_door_and_remaining_native_gap(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        row = rows["barnes_hut"]

        self.assertIn("v2.8 grouped-vector typed-stream front door", row["current_best_path"])
        self.assertIn("app-owned force/vector continuation", row["current_best_path"])
        self.assertIn("CuPy remains", row["partner_position"])
        self.assertIn("torch/triton", row["partner_position"])
        self.assertIn("grouped vector continuation now has a generic front door", row["current_bottleneck"])
        self.assertIn("native typed aggregate-frontier producer", row["current_bottleneck"])
        self.assertIn("prepared residency", row["generic_runtime_target"])
        self.assertIn("Goal3169", row["evidence_refs"])
        self.assertFalse(row["release_authorized"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["rt_core_speedup_claim_authorized"])
        self.assertFalse(row["true_zero_copy_claim_authorized"])

    def test_gap_map_still_validates_after_barnes_hut_refresh(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["public_speedup_claim_authorized"])
        self.assertFalse(validation["rt_core_speedup_claim_authorized"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])

    def test_report_records_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3169",
            "Barnes-Hut / RT-BarnesHut style",
            "grouped-vector typed-stream front door",
            "native typed aggregate-frontier producer",
            "`release_authorized: False`",
            "does not authorize RT-BarnesHut paper reproduction",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
