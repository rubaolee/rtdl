from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3451_v2_8_runtime_gap_after_relation_columns_content_2026-06-05.md"


class Goal3451V28RuntimeGapAfterRelationColumnsContentTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_relation_columns_and_grouped_count(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        for phrase in (
            "generic resident active relation columns",
            "left/right ids plus segment/containment dependency flags",
            "generic compact grouped-count continuation by id",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_best_path"])

        for phrase in (
            "Goal3447/3449 added resident active relation columns plus generic grouped-count continuation",
            "Goal3450 proved the resident relation column content",
            "exact polygon relation witnesses",
            "overlay-area continuation",
            "large-scale content-reference oracles",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, spatial["current_bottleneck"])

        for goal in ("Goal3447", "Goal3448", "Goal3449", "Goal3450"):
            with self.subTest(goal=goal):
                self.assertIn(goal, spatial["evidence_refs"])

    def test_spatial_rayjoin_gap_row_keeps_boundaries_closed(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()
        spatial = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}["spatial_rayjoin"]

        self.assertEqual(validation["status"], "accept", validation)
        self.assertIn("bounded witness continuation", spatial["generic_runtime_target"])
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

    def test_report_records_status_correction_and_remaining_work(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3451",
            "status-map correction",
            "generic resident active relation columns",
            "sparse-id content correctness",
            "exact relation witnesses",
            "overlay-area continuation",
            "does not authorize",
            "app-specific native-engine logic",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
