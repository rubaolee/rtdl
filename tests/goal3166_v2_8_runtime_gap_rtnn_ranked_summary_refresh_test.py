from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_2026-06-03.md"


class Goal3166V28RuntimeGapRtnnRankedSummaryRefreshTest(unittest.TestCase):
    def test_rtnn_gap_row_records_goal3165_front_door_and_remaining_residency_gap(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        row = rows["rtnn"]

        self.assertIn("v2.8 ranked-summary typed-stream front door", row["current_best_path"])
        self.assertIn("grouped top-k/arg continuation", row["current_best_path"])
        self.assertIn("torch/triton", row["partner_position"])
        self.assertIn("numba supports grouped argmin/argmax", row["partner_position"])
        self.assertIn("ranked-summary top-k handoff now has a generic front door", row["current_bottleneck"])
        self.assertIn("native typed producer evidence", row["current_bottleneck"])
        self.assertIn("prepared packed-column residency", row["generic_runtime_target"])
        self.assertIn("Goal3165", row["evidence_refs"])
        self.assertFalse(row["release_authorized"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["rt_core_speedup_claim_authorized"])
        self.assertFalse(row["true_zero_copy_claim_authorized"])

    def test_gap_map_still_validates_after_rtnn_refresh(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["public_speedup_claim_authorized"])
        self.assertFalse(validation["rt_core_speedup_claim_authorized"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])

    def test_report_records_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3165",
            "RTNN neighbor search",
            "ranked-summary typed-stream front door",
            "prepared packed-column residency",
            "`release_authorized: False`",
            "does not authorize RTNN paper reproduction",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
