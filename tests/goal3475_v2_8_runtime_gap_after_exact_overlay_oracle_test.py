from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3475_v2_8_runtime_gap_after_exact_overlay_oracle_2026-06-05.md"
GOAL3474_ARTIFACT = (
    ROOT / "docs" / "reports" / "goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.json"
)


class Goal3475V28RuntimeGapAfterExactOverlayOracleTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_exact_oracle_target(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        for phrase in (
            "external Shapely/GEOS exact oracle",
            "1,090 positive rows",
            "total exact area 26.08321766231042",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_best_path"])

        for phrase in (
            "Goal3474 added a Shapely/GEOS exact CPU oracle",
            "3,453 zero-area rows",
            "0 topology exceptions",
            "GPU-resident exact overlay-area continuation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_bottleneck"])

        self.assertIn("Goal3474", spatial["evidence_refs"])

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

    def test_report_records_oracle_interpretation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "correctness target, not a runtime win",
            "positive exact-area rows: 1,090",
            "total exact overlay area: 26.08321766231042",
            "convex fast path covers 168 rows",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_goal3474_artifact_is_present(self) -> None:
        self.assertTrue(GOAL3474_ARTIFACT.exists())


if __name__ == "__main__":
    unittest.main()
