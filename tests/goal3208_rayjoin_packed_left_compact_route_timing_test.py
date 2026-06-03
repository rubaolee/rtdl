from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3208_rayjoin_packed_left_compact_route_timing_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3208_rayjoin_packed_left_compact_route_timing_2026-06-03.md"
GOAL3203 = ROOT / "docs" / "reports" / "goal3203_rayjoin_compact_route_count_only_timing_2026-06-03.json"
GOAL3205 = ROOT / "docs" / "reports" / "goal3205_rayjoin_reusable_compact_route_timing_2026-06-03.json"


class Goal3208RayJoinPackedLeftCompactRouteTimingTest(unittest.TestCase):
    def test_artifact_records_packed_left_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3208)
        self.assertEqual(data["commit"], "b97553c0")
        self.assertEqual(data["route"], "prepared_optix_compact_grouped_count_reuse/run_packed_left")
        self.assertFalse(data["include_rows_measured"])
        self.assertTrue(data["validation_pass_include_rows"])
        self.assertEqual(data["repeats_per_scale"], 11)
        self.assertEqual([row["n_left"] for row in data["rows"]], [512, 1024, 2048, 4096])

        for row in data["rows"]:
            self.assertTrue(row["all_match_expected_counts"])
            self.assertEqual(row["expected_pair_count"], row["n_left"] * row["n_right"])
            self.assertEqual(row["validation_count_sum"], row["expected_pair_count"])
            self.assertEqual(len(row["measurements"]), 11)
            self.assertGreater(row["pack_left_once_seconds"], 0.0)
            self.assertGreater(row["prepare_static_scene_paid_once_seconds"], 0.0)
            for measurement in row["measurements"]:
                self.assertEqual(measurement["row_count"], row["expected_pair_count"])
                self.assertEqual(measurement["compact_row_count"], row["n_left"])
                self.assertFalse(measurement["has_rows"])
                self.assertTrue(measurement["device_resident"])
                self.assertNotIn("query_pack_sec", measurement["phases_sec"])
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

    def test_packed_left_route_improves_representative_medians(self) -> None:
        one_shot = {
            row["n_left"]: row["median_total_seconds"]
            for row in json.loads(GOAL3203.read_text(encoding="utf-8"))["rows"]
        }
        prepared = {
            row["n_left"]: row["median_total_seconds"]
            for row in json.loads(GOAL3205.read_text(encoding="utf-8"))["rows"]
        }
        packed = {
            row["n_left"]: row["median_total_seconds"]
            for row in json.loads(ARTIFACT.read_text(encoding="utf-8"))["rows"]
        }

        for scale in (512, 1024, 2048, 4096):
            self.assertLess(packed[scale], one_shot[scale])
            self.assertLess(packed[scale], prepared[scale])

    def test_report_records_packed_left_boundary_and_next_target(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "pack_rayjoin_optix_compact_grouped_count_left_segments",
            "run_packed_left",
            "right-side preparation reuse matters",
            "left-side packing reuse matters",
            "candidate device-column traversal",
            "0.012753259390592575",
            "without adding RayJoin-specific native logic",
            "not a public speedup claim",
            "true_zero_copy_claim_authorized: False",
            "rayjoin_paper_reproduction_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
