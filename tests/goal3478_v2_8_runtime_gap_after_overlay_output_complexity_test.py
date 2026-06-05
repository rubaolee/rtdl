from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3478_v2_8_runtime_gap_after_overlay_output_complexity_2026-06-05.md"
GOAL3477_ARTIFACT = (
    ROOT / "docs" / "reports" / "goal3477_shape_pair_exact_overlay_output_complexity_oracle_pod_2026-06-05.json"
)


class Goal3478V28RuntimeGapAfterOverlayOutputComplexityTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_scalar_and_streamed_split(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        for phrase in (
            "streamed component/vertex output",
            "scalar exact-area first",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_best_path"])

        for phrase in (
            "Goal3477 characterized exact output geometry",
            "609 positive MultiPolygon rows",
            "48 positive GeometryCollection rows",
            "42,314 output vertices",
            "Near-term v2.8 should target scalar exact-area continuation first",
            "later streamed component/vertex contract",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_bottleneck"])

        self.assertIn("Goal3477", spatial["evidence_refs"])

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

    def test_report_records_interpretation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "near-term: GPU-resident scalar exact overlay-area continuation",
            "later: streamed full overlay-geometry output",
            "positive `MultiPolygon` rows: 609",
            "max output vertices in one row: 586",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_goal3477_artifact_is_present(self) -> None:
        self.assertTrue(GOAL3477_ARTIFACT.exists())


if __name__ == "__main__":
    unittest.main()
