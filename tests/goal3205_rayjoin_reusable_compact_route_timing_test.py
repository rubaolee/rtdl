from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3205_rayjoin_reusable_compact_route_timing_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3205_rayjoin_reusable_compact_route_timing_2026-06-03.md"
GOAL3203 = ROOT / "docs" / "reports" / "goal3203_rayjoin_compact_route_count_only_timing_2026-06-03.json"


class Goal3205RayJoinReusableCompactRouteTimingTest(unittest.TestCase):
    def test_artifact_records_reusable_prepared_route_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3205)
        self.assertEqual(data["commit"], "da247fe8")
        self.assertEqual(data["route"], "prepared_optix_compact_grouped_count_reuse")
        self.assertFalse(data["include_rows_measured"])
        self.assertTrue(data["validation_pass_include_rows"])
        self.assertEqual(data["repeats_per_scale"], 9)
        self.assertEqual([row["n_left"] for row in data["rows"]], [512, 1024, 2048, 4096])

        for row in data["rows"]:
            self.assertTrue(row["all_match_expected_counts"])
            self.assertEqual(row["expected_pair_count"], row["n_left"] * row["n_right"])
            self.assertEqual(row["validation_count_sum"], row["expected_pair_count"])
            self.assertEqual(len(row["measurements"]), 9)
            self.assertGreater(row["prepare_static_scene_paid_once_seconds"], 0.0)
            self.assertGreater(row["median_total_seconds"], 0.0)
            for measurement in row["measurements"]:
                self.assertEqual(measurement["row_count"], row["expected_pair_count"])
                self.assertEqual(measurement["compact_row_count"], row["n_left"])
                self.assertFalse(measurement["has_rows"])
                self.assertTrue(measurement["device_resident"])
                self.assertIn("query_pack_sec", measurement["phases_sec"])
                self.assertNotIn("prepare_static_scene_sec", measurement["phases_sec"])
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

    def test_reusable_route_improves_representative_one_shot_medians(self) -> None:
        one_shot = {
            row["n_left"]: row["median_total_seconds"]
            for row in json.loads(GOAL3203.read_text(encoding="utf-8"))["rows"]
        }
        reusable = {
            row["n_left"]: row["median_total_seconds"]
            for row in json.loads(ARTIFACT.read_text(encoding="utf-8"))["rows"]
        }

        for scale in (512, 2048, 4096):
            self.assertLess(reusable[scale], one_shot[scale])

    def test_report_records_reuse_boundary_and_next_target(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "right-side scene preparation is now paid once",
            "prepared_optix_compact_grouped_count_reuse",
            "RayJoin route policy, left-ID remapping, and",
            "right-scene reuse are Python app-layer responsibilities",
            "0.02565891481935978s",
            "new bottleneck is query packing",
            "caller-supplied packed segment input contract",
            "public speedup claim",
            "true_zero_copy_claim_authorized: False",
            "rayjoin_paper_reproduction_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
