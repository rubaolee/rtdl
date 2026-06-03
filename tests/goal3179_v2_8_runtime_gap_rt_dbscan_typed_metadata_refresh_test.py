from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3179_v2_8_runtime_gap_rt_dbscan_typed_metadata_refresh_2026-06-03.md"
)


class Goal3179V28RuntimeGapRTDBSCANTypedMetadataRefreshTest(unittest.TestCase):
    def test_rt_dbscan_gap_row_promotes_goal3158_from_future_gap_to_current_evidence(self) -> None:
        row = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}["rt_dbscan"]

        self.assertIn("typed adjacency/grouped-stream producer metadata from Goal3158", row["current_best_path"])
        self.assertIn("typed producer metadata now exists", row["current_bottleneck"])
        self.assertIn("broader partner conformance", row["current_bottleneck"])
        self.assertIn("larger device-resident continuation coverage", row["current_bottleneck"])
        self.assertEqual(
            row["generic_runtime_target"],
            "fixed-radius graph component front door plus typed adjacency/grouped-stream producer metadata",
        )
        self.assertIn("Goal3158", row["evidence_refs"])
        self.assertIn("Goal3179", row["evidence_refs"])

    def test_rt_dbscan_gap_row_still_blocks_release_claims(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()
        row = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}["rt_dbscan"]

        self.assertEqual(validation["status"], "accept", validation)
        self.assertFalse(row["release_authorized"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["rt_core_speedup_claim_authorized"])
        self.assertFalse(row["true_zero_copy_claim_authorized"])
        self.assertFalse(row["automatic_partner_selection_allowed"])

    def test_report_records_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3158",
            "typed producer metadata now exists",
            "broader partner conformance",
            "larger device-resident continuation coverage",
            "`release_authorized: False`",
            "`true_zero_copy_claim_authorized: False`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
