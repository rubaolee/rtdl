from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3461_v2_8_runtime_gap_after_large_relation_oracle_2026-06-05.md"


class Goal3461V28RuntimeGapAfterLargeRelationOracleTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_large_relation_oracle(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        for phrase in (
            "public-CDB scale evidence",
            "large public-CDB relation content",
            "native-fidelity float32 host oracle",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_best_path"])

        for phrase in (
            "Goal3459 added public-CDB scale evidence",
            "Goal3460 proved large public-CDB relation id/flag/ordinal content",
            "exact overlay-area continuation for non-integer, non-orthogonal polygons",
            "boundary-witness ownership",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_bottleneck"])

        for goal in ("Goal3459", "Goal3460"):
            with self.subTest(goal=goal):
                self.assertIn(goal, spatial["evidence_refs"])

        self.assertNotIn(
            "large-scale content-reference oracles beyond counts/grouping/bounds-area",
            spatial["current_bottleneck"],
        )

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
            "Goal3461",
            "public-CDB relation id/flag/ordinal content matched",
            "non-integer coordinates and diagonal edges",
            "older integer-grid exact-area helper cannot be used",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
