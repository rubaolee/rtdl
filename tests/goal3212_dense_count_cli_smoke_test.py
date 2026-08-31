from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3212_dense_count_cli_smoke_2026-06-03.json"


class Goal3212DenseCountCliSmokeTest(unittest.TestCase):
    def test_cli_smoke_records_dense_count_route(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["execution_route"], "prepared_optix_left_id_dense_count_reuse")
        self.assertEqual(
            data["summary"]["output_contract"],
            "segment_segment_intersection_count_by_left_id_dense_device_column",
        )
        self.assertEqual(data["row_count"], data["summary"]["intersection_count"])
        self.assertNotIn("rows", data)
        self.assertTrue(data["dense_left_id_count_columns"]["device_resident"])
        self.assertEqual(data["dense_left_id_count_columns"]["source_row_count"], data["row_count"])
        self.assertEqual(
            data["dense_left_id_count_columns"]["native_symbol"],
            "rtdl_optix_prepared_segment_pair_left_id_count_device_columns",
        )
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["full_rayjoin_reproduction"])


if __name__ == "__main__":
    unittest.main()
