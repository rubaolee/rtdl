from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3195_compact_grouped_count_timing_probe_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3195_compact_grouped_count_timing_probe_2026-06-03.md"


class Goal3195CompactGroupedCountTimingProbeTest(unittest.TestCase):
    def test_artifact_records_bounded_internal_timing_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3195)
        self.assertEqual(data["commit"], "3483020a")
        self.assertEqual([row["n_left"] for row in data["rows"]], [512, 1024, 2048])
        for row in data["rows"]:
            self.assertTrue(row["all_match_exact_rows"])
            self.assertTrue(row["compact_device_resident"])
            self.assertEqual(row["candidate_row_count"], row["expected_pair_count"])
            self.assertEqual(row["candidate_event_count"], row["expected_pair_count"])
            self.assertEqual(row["compact_row_count"], row["n_left"])
            self.assertLess(row["compact_device_columns_seconds_including_validation_copy"], row["exact_rows_host_materialized_seconds"])
        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

    def test_report_records_scope_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "internal timing probe",
            "not a public speedup claim",
            "compact resident grouped-count columns",
            "validation copy",
            "2048 x 2048",
            "5.909632220864296",
            "0.01623670384287834",
            "release_authorized: False",
            "public_speedup_claim_authorized: False",
            "true_zero_copy_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
