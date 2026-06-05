from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3472_v2_8_runtime_gap_after_convex_overlay_fast_path_2026-06-05.md"


class Goal3472V28RuntimeGapAfterConvexOverlayFastPathTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_convex_fast_path(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        for phrase in (
            "convex overlay-area fast path",
            "exact for the 168 supported both-convex rows",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_best_path"])

        for phrase in (
            "Goal3471 implemented a generic convex overlay-area fast path",
            "synthetic 1.0-area fixture exactly",
            "unsupported-nonconvex status",
            "remaining 4,375 rows",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_bottleneck"])

        self.assertIn("Goal3471", spatial["evidence_refs"])

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

    def test_report_records_bounded_interpretation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3472",
            "measured 1.0",
            "supported both-convex rows: 168",
            "unsupported nonconvex rows: 4,375",
            "not full RayJoin overlay closure",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
