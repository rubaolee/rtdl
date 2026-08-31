from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3157_v2_8_runtime_gap_rt_dbscan_front_door_refresh_2026-06-03.md"
)


def _rt_dbscan_row() -> dict[str, object]:
    rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
    return rows["rt_dbscan"]


class Goal3157V28RuntimeGapRTDBSCANFrontDoorRefreshTest(unittest.TestCase):
    def test_rt_dbscan_gap_row_records_front_door_current_state(self) -> None:
        row = _rt_dbscan_row()

        self.assertIn("v2.8 fixed-radius graph component front door", row["current_best_path"])
        self.assertIn("OptiX+CuPy grouped-stream path", row["current_best_path"])
        self.assertIn("explicit v2.8 front door", row["partner_position"])
        self.assertIn("typed producer metadata", row["current_bottleneck"])
        self.assertIn("broader partner conformance", row["current_bottleneck"])
        self.assertEqual(
            row["generic_runtime_target"],
            "fixed-radius graph component front door plus typed adjacency/grouped-stream producer metadata",
        )
        for goal in ("Goal3154", "Goal3155", "Goal3156"):
            with self.subTest(goal=goal):
                self.assertIn(goal, row["evidence_refs"])

    def test_rt_dbscan_gap_row_preserves_claim_boundaries(self) -> None:
        row = _rt_dbscan_row()

        self.assertFalse(row["app_specific_engine_logic_allowed"])
        self.assertFalse(row["automatic_partner_selection_allowed"])
        self.assertFalse(row["release_authorized"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["rt_core_speedup_claim_authorized"])
        self.assertFalse(row["true_zero_copy_claim_authorized"])

    def test_runtime_gap_validator_still_accepts_matrix(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(validation["app_count"], 10)
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["public_speedup_claim_authorized"])
        self.assertFalse(validation["rt_core_speedup_claim_authorized"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])

    def test_report_documents_superseded_goal3151_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3157",
            "Goal3151 correctly recorded",
            "superseded for current RT-DBSCAN status by Goal3157",
            "fixed-radius/core-summary primitives + v2.8 fixed-radius graph component front door",
            "broader partner conformance is still open",
            "release_authorized: False",
            "public_speedup_claim_authorized: False",
            "rt_core_speedup_claim_authorized: False",
            "true_zero_copy_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
