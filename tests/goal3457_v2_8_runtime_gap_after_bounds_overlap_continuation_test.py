from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3457_v2_8_runtime_gap_after_bounds_overlap_continuation_2026-06-05.md"


class Goal3457V28RuntimeGapAfterBoundsOverlapContinuationTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_ordinals_and_bounds_area_continuation(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        for phrase in (
            "zero-based ordinal columns",
            "sparse ids safe for payload indexing",
            "CuPy bounds-overlap area continuation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_best_path"])

        for phrase in (
            "Goal3455 added ordinal columns",
            "Goal3456 proved a generic CuPy bounds-overlap area continuation",
            "Remaining work is exact polygon relation witnesses",
            "exact overlay-area continuation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_bottleneck"])

        for goal in ("Goal3455", "Goal3456"):
            with self.subTest(goal=goal):
                self.assertIn(goal, spatial["evidence_refs"])

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

    def test_report_records_remaining_exact_overlay_gap(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3457",
            "real payload-consumption milestone",
            "not exact polygon overlay area",
            "exact polygon relation witnesses",
            "exact overlay-area continuation",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
