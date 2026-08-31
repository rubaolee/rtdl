from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3199_rayjoin_compact_route_app_timing_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3199_rayjoin_compact_route_app_timing_2026-06-03.md"


class Goal3199RayJoinCompactRouteAppTimingTest(unittest.TestCase):
    def test_artifact_records_bounded_app_route_timing_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3199)
        self.assertEqual(data["commit"], "f0607849")
        self.assertIn("run_rayjoin_prepared_optix_compact_grouped_count_segments", data["description"])
        self.assertEqual([row["n_left"] for row in data["rows"]], [512, 1024, 2048])
        for row in data["rows"]:
            self.assertTrue(row["all_match_expected_counts"])
            self.assertTrue(row["device_resident"])
            self.assertEqual(row["n_left"], row["n_right"])
            self.assertEqual(row["row_count"], row["expected_pair_count"])
            self.assertEqual(row["count_sum"], row["expected_pair_count"])
            self.assertEqual(row["compact_row_count"], row["n_left"])
            self.assertGreater(row["app_route_total_seconds"], 0.0)
            self.assertIn("candidate_device_columns_sec", row["phases_sec"])
            self.assertIn("compact_grouped_count_sec", row["phases_sec"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["true_zero_copy_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["full_rayjoin_reproduction"])

        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

    def test_report_records_scope_warmup_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "app-facing",
            "prepared_optix_compact_grouped_count",
            "dense original left IDs",
            "Python-side left-ID remapping",
            "Includes first-use OptiX/setup warm-up cost",
            "Steady route behavior after warm-up",
            "4194304",
            "2,048 compact grouped",
            "not a public speedup claim",
            "true_zero_copy_claim_authorized: False",
            "rayjoin_paper_reproduction_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
