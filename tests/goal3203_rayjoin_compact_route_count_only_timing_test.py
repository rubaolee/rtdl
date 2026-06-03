from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3203_rayjoin_compact_route_count_only_timing_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3203_rayjoin_compact_route_count_only_timing_2026-06-03.md"


class Goal3203RayJoinCompactRouteCountOnlyTimingTest(unittest.TestCase):
    def test_artifact_records_count_only_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3203)
        self.assertEqual(data["commit"], "c4c11f28")
        self.assertEqual(data["route"], "prepared_optix_compact_grouped_count")
        self.assertFalse(data["include_rows_measured"])
        self.assertTrue(data["validation_pass_include_rows"])
        self.assertEqual(data["repeats_per_scale"], 7)
        self.assertEqual([row["n_left"] for row in data["rows"]], [512, 1024, 2048, 4096])

        for row in data["rows"]:
            self.assertTrue(row["all_match_expected_counts"])
            self.assertEqual(row["expected_pair_count"], row["n_left"] * row["n_right"])
            self.assertEqual(row["validation_count_sum"], row["expected_pair_count"])
            self.assertEqual(len(row["measurements"]), 7)
            self.assertGreater(row["median_total_seconds"], 0.0)
            for measurement in row["measurements"]:
                self.assertEqual(measurement["row_count"], row["expected_pair_count"])
                self.assertEqual(measurement["compact_row_count"], row["n_left"])
                self.assertFalse(measurement["has_rows"])
                self.assertTrue(measurement["device_resident"])
                self.assertIn("query_pack_sec", measurement["phases_sec"])
                self.assertIn("prepare_static_scene_sec", measurement["phases_sec"])
                self.assertIn("candidate_device_columns_sec", measurement["phases_sec"])
                self.assertIn("compact_grouped_count_sec", measurement["phases_sec"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["true_zero_copy_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

    def test_report_records_next_engineering_target_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "count-only mode",
            "include_rows=False",
            "one `include_rows=True` pass",
            "measured payloads do not contain a `rows` field",
            "repeated query packing and static right-scene preparation",
            "larger than the compact grouped-count continuation",
            "reusable prepared app route",
            "not a public speedup claim",
            "true_zero_copy_claim_authorized: False",
            "rayjoin_paper_reproduction_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
