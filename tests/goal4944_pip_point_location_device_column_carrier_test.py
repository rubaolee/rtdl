from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


@dataclass
class FakePointLocationIdColumns:
    field_name: str
    ids_device_ptr: int
    row_count: int
    capacity: int
    device_ordinal: int = 0
    dtype: str = "uint32"
    native_symbol: str = "rtdl_optix_prepared_directed_segment_point_location_2d_device_face_id_columns"
    traversal_seconds: float = 0.125
    overflow: bool = False

    @property
    def device_resident(self) -> bool:
        return self.ids_device_ptr > 0 and self.capacity > 0 and not self.overflow


class Goal4944PipPointLocationDeviceColumnCarrierTest(unittest.TestCase):
    def test_native_api_exposes_generic_point_location_id_column_symbols(self) -> None:
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        api = OPTIX_API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("struct RtdlNativePointLocationDeviceIdColumns", prelude)
        self.assertIn("ids_device_ptr", prelude)
        for symbol in (
            "rtdl_optix_prepared_directed_segment_point_location_2d_device_segment_id_columns",
            "rtdl_optix_prepared_directed_segment_point_location_2d_device_face_id_columns",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)

        self.assertIn("DevPtr d_face_ids", workloads)
        self.assertIn("prepared_points->d_face_ids.ptr", workloads)
        self.assertIn("prepared_rayjoin_cdb_point_location_2d_device_id_columns_optix", workloads)

    def test_python_carrier_methods_are_generic_and_do_not_replace_legacy_count_methods(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("class OptixPointLocationDeviceIdColumnOutput", runtime)
        self.assertIn("def segment_id_device_columns(", runtime)
        self.assertIn("def face_id_device_columns(", runtime)
        self.assertIn("def write_segment_ids_device_points(", runtime)
        self.assertIn("def write_face_ids_device_points(", runtime)
        self.assertIn("producer_primitive\": \"directed_segment_point_location_2d", runtime)
        self.assertNotIn("overlay_chain", runtime[runtime.index("class OptixPointLocationDeviceIdColumnOutput"):runtime.index("@dataclass", runtime.index("class OptixPointLocationDeviceIdColumnOutput") + 1)])

    def test_uint32_raw_cuda_column_and_layer1_adapter_accept_point_location_ids(self) -> None:
        raw = rt.RtdlRawCudaColumn("face_id", "uint32", 0x494400, 5, device_id=0)
        self.assertEqual(raw.__cuda_array_interface__["typestr"], "<u4")

        fake = FakePointLocationIdColumns("face_id", 0x494400, 5, 5)
        row_buffer = rt.device_column_row_buffer_from_point_location_id_columns(fake)
        metadata = row_buffer.to_metadata()

        self.assertEqual(row_buffer.row_count, 5)
        self.assertEqual(tuple(row_buffer.columns.keys()), ("face_id",))
        self.assertTrue(metadata["device_resident_candidate"])
        self.assertEqual(metadata["engine_boundary"], "generic_app_agnostic_primitive_output_columns")
        self.assertFalse(metadata["app_specific_schema_allowed"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

        handoff = rt.plan_device_column_row_buffer_partner_handoff(row_buffer, partner="numba")
        self.assertEqual(handoff["status"], "accept")
        self.assertEqual(handoff["selected_partner"], "numba")

    def test_layer1_adapter_rejects_app_specific_point_location_columns(self) -> None:
        fake = FakePointLocationIdColumns("overlay_chain_id", 0x494400, 5, 5)
        with self.assertRaises(ValueError):
            rt.device_column_row_buffer_from_point_location_id_columns(fake)


if __name__ == "__main__":
    unittest.main()
