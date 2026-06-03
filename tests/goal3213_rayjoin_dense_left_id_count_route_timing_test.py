from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3213_rayjoin_dense_left_id_count_route_timing_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3213_rayjoin_dense_left_id_count_route_timing_2026-06-03.md"
GOAL3203 = ROOT / "docs" / "reports" / "goal3203_rayjoin_compact_route_count_only_timing_2026-06-03.json"
GOAL3205 = ROOT / "docs" / "reports" / "goal3205_rayjoin_reusable_compact_route_timing_2026-06-03.json"
GOAL3208 = ROOT / "docs" / "reports" / "goal3208_rayjoin_packed_left_compact_route_timing_2026-06-03.json"


class Goal3213RayJoinDenseLeftIdCountRouteTimingTest(unittest.TestCase):
    def test_artifact_records_dense_count_route_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3213)
        self.assertEqual(data["commit"], "03209c08")
        self.assertEqual(data["route"], "prepared_optix_left_id_dense_count_reuse/run_packed_left_dense_count")
        self.assertFalse(data["include_rows_measured"])
        self.assertTrue(data["validation_pass_include_rows"])
        self.assertEqual(data["repeats_per_scale"], 11)
        self.assertEqual([row["n_left"] for row in data["rows"]], [512, 1024, 2048, 4096])

        for row in data["rows"]:
            self.assertTrue(row["all_match_expected_counts"])
            self.assertEqual(row["expected_pair_count"], row["n_left"] * row["n_right"])
            self.assertEqual(row["validation_count_sum"], row["expected_pair_count"])
            self.assertEqual(len(row["measurements"]), 11)
            for measurement in row["measurements"]:
                self.assertEqual(measurement["row_count"], row["expected_pair_count"])
                self.assertEqual(measurement["left_group_capacity"], row["n_left"])
                self.assertFalse(measurement["has_rows"])
                self.assertTrue(measurement["device_resident"])
                self.assertIn("left_id_count_device_columns_sec", measurement["phases_sec"])
                self.assertNotIn("candidate_device_columns_sec", measurement["phases_sec"])
                self.assertNotIn("query_pack_sec", measurement["phases_sec"])
                self.assertNotIn("prepare_static_scene_sec", measurement["phases_sec"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["true_zero_copy_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

    def test_dense_route_improves_previous_representative_medians(self) -> None:
        one_shot_data = json.loads(GOAL3203.read_text(encoding="utf-8"))
        prepared_data = json.loads(GOAL3205.read_text(encoding="utf-8"))
        packed_compact_data = json.loads(GOAL3208.read_text(encoding="utf-8"))
        dense_data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        for baseline in (one_shot_data, prepared_data, packed_compact_data, dense_data):
            self.assertFalse(baseline["include_rows_measured"])
            self.assertTrue(baseline["validation_pass_include_rows"])

        one_shot = {
            row["n_left"]: row["median_total_seconds"]
            for row in one_shot_data["rows"]
        }
        prepared = {
            row["n_left"]: row["median_total_seconds"]
            for row in prepared_data["rows"]
        }
        packed_compact = {
            row["n_left"]: row["median_total_seconds"]
            for row in packed_compact_data["rows"]
        }
        dense = {
            row["n_left"]: row["median_total_seconds"]
            for row in dense_data["rows"]
        }

        for scale in (512, 1024, 2048, 4096):
            self.assertLess(dense[scale], one_shot[scale])
            self.assertLess(dense[scale], prepared[scale])
            self.assertLess(dense[scale], packed_compact[scale])

    def test_report_records_fused_count_interpretation_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "run_packed_left_dense_count",
            "generic segment-pair count route",
            "not a RayJoin-specific native",
            "0.005745925009250641",
            "should not emit a pair row stream and then reduce it",
            "All four comparison-chain artifacts record `include_rows_measured: false`",
            "counts by remapped left ID during traversal",
            "native code exposes a generic segment-pair count primitive",
            "public_speedup_claim_authorized: False",
            "true_zero_copy_claim_authorized: False",
            "rayjoin_paper_reproduction_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
