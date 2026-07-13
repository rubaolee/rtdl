from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"


class Goal4943LsiPipDeviceColumnProducerAuditTest(unittest.TestCase):
    def test_lsi_has_python_visible_native_pair_column_producer_and_layer1_adapter(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def candidate_device_columns(", runtime)
        self.assertIn("OptixNativeDevicePairColumnOutput", runtime)
        self.assertTrue(hasattr(rt, "device_column_row_buffer_from_native_pair_columns"))
        self.assertNotIn("device_column_row_buffer_from_native_pair_columns", rt.__all__)

    def test_pip_gap_is_superseded_by_goal4944_pointer_carrier(self) -> None:
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        for symbol in (
            "rtdl_optix_count_prepared_directed_segment_point_location_2d_device_points",
            "rtdl_optix_write_prepared_directed_segment_point_location_2d_device_segment_ids",
            "rtdl_optix_write_prepared_directed_segment_point_location_2d_device_face_ids",
            "rtdl_optix_prepared_directed_segment_point_location_2d_device_segment_id_columns",
            "rtdl_optix_prepared_directed_segment_point_location_2d_device_face_id_columns",
        ):
            self.assertIn(symbol, prelude)

        self.assertIn("class OptixPointLocationDeviceIdColumnOutput", runtime)
        self.assertIn("def segment_id_device_columns(", runtime)
        self.assertIn("def face_id_device_columns(", runtime)
        self.assertTrue(hasattr(rt, "device_column_row_buffer_from_point_location_id_columns"))
        self.assertNotIn("device_column_row_buffer_from_point_location_id_columns", rt.__all__)

    def test_audit_boundary_remains_no_speedup_or_zero_copy_claim(self) -> None:
        contract = rt.describe_device_column_row_buffer_contract()

        self.assertFalse(contract["public_speedup_claim_authorized"])
        self.assertFalse(contract["true_zero_copy_claim_authorized"])
        self.assertEqual("experimental_reuse_adapter_no_release_claim", contract["api_maturity"])


if __name__ == "__main__":
    unittest.main()
