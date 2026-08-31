from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3464_v2_8_runtime_gap_after_relation_witnesses_2026-06-05.md"


class Goal3464V28RuntimeGapAfterRelationWitnessesTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_relation_witnesses(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        for phrase in (
            "generic CuPy witness columns",
            "segment-edge",
            "containment witnesses",
            "every active public-CDB relation row",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_best_path"])

        for phrase in (
            "Goal3463 emitted generic CuPy witness columns",
            "Remaining work is exact overlay-area continuation",
            "exact area/witness policy at serious scale",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_bottleneck"])

        self.assertIn("Goal3463", spatial["evidence_refs"])
        self.assertNotIn("Remaining work is exact polygon relation witnesses", spatial["current_bottleneck"])

    def test_gap_map_still_blocks_claims(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()
        spatial = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}["spatial_rayjoin"]

        self.assertEqual(validation["status"], "accept", validation)
        for field in (
            "app_specific_engine_logic_allowed",
            "automatic_partner_selection_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(spatial[field])

    def test_report_records_precise_remaining_gap(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3464",
            "0 unresolved witness rows",
            "exact relation witnesses are no longer merely pending",
            "exact overlay-area continuation",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
