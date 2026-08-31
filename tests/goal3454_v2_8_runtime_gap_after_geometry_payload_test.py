from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3454_v2_8_runtime_gap_after_geometry_payload_2026-06-05.md"


class Goal3454V28RuntimeGapAfterGeometryPayloadTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_geometry_payload_columns(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        for phrase in (
            "generic shape-pair geometry payload columns",
            "explicit witness/area continuations",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_best_path"])

        for phrase in (
            "Goal3453 exposed generic left/right geometry payload columns",
            "Goal3456 proved a generic CuPy bounds-overlap area continuation",
            "exact polygon relation witnesses",
            "exact overlay-area continuation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_bottleneck"])

        self.assertIn("Goal3453", spatial["evidence_refs"])

    def test_gap_map_still_blocks_all_claims(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()
        rows = rt.v2_8_benchmark_runtime_gap_matrix()

        self.assertEqual(validation["status"], "accept", validation)
        for row in rows:
            with self.subTest(app=row["benchmark_app"]):
                self.assertFalse(row["app_specific_engine_logic_allowed"])
                self.assertFalse(row["automatic_partner_selection_allowed"])
                self.assertFalse(row["release_authorized"])
                self.assertFalse(row["public_speedup_claim_authorized"])
                self.assertFalse(row["rt_core_speedup_claim_authorized"])
                self.assertFalse(row["true_zero_copy_claim_authorized"])

    def test_report_records_next_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3454",
            "resident generic geometry payload columns",
            "not authorize",
            "bounded generic witness/area continuation",
            "full polygon overlay area requires a later exact continuation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
