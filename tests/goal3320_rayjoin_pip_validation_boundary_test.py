from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3320_rayjoin_pip_full_dataset_validation_boundary_2026-06-04.md"
MATRIX = ROOT / "docs" / "reports" / "goal3320_rayjoin_pip_device_count_validation_matrix_2026-06-04.json"
SOIL_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3320_rayjoin_pip_batch_executor_auto_stream_br_soil_start256_count512_2026-06-04.json"
)
EXPECTED_COMMIT = "c037f510b89a2effd4eff32d025da1a3c053a0b1"


class Goal3320RayJoinPipValidationBoundaryTest(unittest.TestCase):
    def test_validation_matrix_records_county_boundary_and_soil_success(self) -> None:
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "rtdl.goal3320.rayjoin_pip_device_count_validation_matrix.v1")
        self.assertEqual(data["goal"], 3320)
        self.assertEqual(data["rtdl_commit"], EXPECTED_COMMIT)
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
        self.assertEqual(data["query_axis"], "z_point")

        rows = {Path(row["dataset"]).name: row for row in data["rows"]}
        self.assertEqual(set(rows), {"br_county.cdb", "br_county_start256_count512.cdb", "br_soil_start256_count512.cdb"})

        full_county = rows["br_county.cdb"]
        self.assertEqual(full_county["exact_count"], 47262)
        self.assertEqual(full_county["device_filtered_prepared_points_scalar_count"], 47554)
        self.assertEqual(full_county["point_id_count_device_columns_count"], 47554)
        self.assertIs(full_county["device_filtered_prepared_points_matches_exact"], False)
        self.assertIs(full_county["point_id_count_device_columns_matches_exact"], False)

        county_slice = rows["br_county_start256_count512.cdb"]
        self.assertEqual(county_slice["exact_count"], 1417)
        self.assertEqual(county_slice["device_filtered_prepared_points_scalar_count"], 1429)
        self.assertEqual(county_slice["point_id_count_device_columns_count"], 1429)
        self.assertIs(county_slice["device_filtered_prepared_points_matches_exact"], False)
        self.assertIs(county_slice["point_id_count_device_columns_matches_exact"], False)

        soil_slice = rows["br_soil_start256_count512.cdb"]
        self.assertEqual(soil_slice["exact_count"], 1471)
        self.assertEqual(soil_slice["device_filtered_prepared_points_scalar_count"], 1471)
        self.assertEqual(soil_slice["point_id_count_device_columns_count"], 1471)
        self.assertIs(soil_slice["device_filtered_prepared_points_matches_exact"], True)
        self.assertIs(soil_slice["point_id_count_device_columns_matches_exact"], True)

        for authorized in data["claim_boundary"].values():
            self.assertIs(authorized, False)

    def test_soil_executor_artifact_is_fast_exact_and_bounded(self) -> None:
        data = json.loads(SOIL_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["rtdl_commit"], EXPECTED_COMMIT)
        self.assertEqual(data["dataset"], "/root/rtdl_goal3293/data/rayjoin_public_cdb/br_soil_start256_count512.cdb")
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
        self.assertEqual(data["exact_count"], 1471)
        self.assertEqual(data["batch_stream_count"], "auto")
        self.assertTrue(data["batch_executor"])

        rows = {row["request_count"]: row for row in data["batch_rows"]}
        self.assertEqual(set(rows), {8, 16, 32, 64})
        self.assertEqual(rows[8]["batch_stream_count_effective"], 4)
        self.assertEqual(rows[16]["batch_stream_count_effective"], 8)
        self.assertEqual(rows[32]["batch_stream_count_effective"], 8)
        self.assertEqual(rows[64]["batch_stream_count_effective"], 16)
        self.assertLess(rows[32]["per_request_ms_median"], 0.014)
        self.assertLess(rows[64]["per_request_ms_median"], 0.013)
        for row in rows.values():
            self.assertEqual(row["count_first"], 1471)
            self.assertEqual(row["count_last"], 1471)
            self.assertEqual(row["native_modes"], ["prepared_points_device_filtered_batch_executor_run"])

        for authorized in data["claim_boundary"].values():
            self.assertIs(authorized, False)

    def test_report_states_generic_boundary_and_required_followup(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3320 - RayJoin PIP Full-Dataset Validation Boundary", text)
        self.assertIn("This is a correctness boundary, not a timing failure.", text)
        self.assertIn("mismatch", text)
        self.assertIn("face/topology-aware closed-shape membership primitive", text)
        self.assertIn("validated-domain preflight", text)
        self.assertIn("not a whole RayJoin workload claim", text)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized`: false", text)


if __name__ == "__main__":
    unittest.main()

