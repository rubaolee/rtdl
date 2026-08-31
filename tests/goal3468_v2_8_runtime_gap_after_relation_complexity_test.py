from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3468_v2_8_runtime_gap_after_relation_complexity_2026-06-05.md"


class Goal3468V28RuntimeGapAfterRelationComplexityTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_complexity_evidence(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        for phrase in (
            "generic CuPy relation complexity columns",
            "4,375 of 4,543",
            "general simple-polygon overlay path",
            "convex-only clip fast path",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_best_path"])

        for phrase in (
            "Goal3467 classified active relation complexity",
            "only 168 both-convex rows",
            "max active pair vertex count of 1,132",
            "mostly nonconvex polygons",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_bottleneck"])

        self.assertIn("Goal3467", spatial["evidence_refs"])
        self.assertIn("general simple-polygon overlay-area continuation", spatial["generic_runtime_target"])

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

    def test_report_records_design_consequence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3468",
            "4,375 rows require general-overlay handling",
            "convex-only clipping continuation",
            "exact-overlay gap",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
