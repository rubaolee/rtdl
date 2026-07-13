from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.optix_runtime import OptixNativeDevicePairColumnOutput


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "device_column_row_buffer.py"


class _FakeNumbaCudaInt64Column:
    __module__ = "numba.cuda.cudadrv.devicearray"
    dtype = "int64"
    shape = (3,)

    def __init__(self, ptr: int) -> None:
        self._ptr = int(ptr)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (self._ptr, False),
            "version": 3,
            "device": 0,
        }


class Goal4942DeviceColumnRowBufferHandoffTest(unittest.TestCase):
    def test_contract_reuses_existing_device_column_and_neutral_handoff_lines(self) -> None:
        contract = rt.describe_device_column_row_buffer_contract()

        self.assertEqual(rt.DEVICE_COLUMN_ROW_BUFFER_CONTRACT_VERSION, contract["contract_version"])
        self.assertTrue(contract["reuses_v2_5_hit_stream_device_columns"])
        self.assertTrue(contract["reuses_v2_6_neutral_partner_handoff"])
        self.assertEqual(("cupy", "numba"), contract["supported_partner_handoff"])
        self.assertFalse(contract["torch_carrier_required"])
        self.assertFalse(contract["app_specific_schema_allowed"])
        self.assertFalse(contract["true_zero_copy_claim_authorized"])
        self.assertFalse(contract["public_speedup_claim_authorized"])

    def test_numba_device_columns_plan_through_v2_6_neutral_path_without_torch(self) -> None:
        row_buffer = rt.prepare_device_column_row_buffer(
            {
                "left_id": _FakeNumbaCudaInt64Column(0x494200),
                "right_id": _FakeNumbaCudaInt64Column(0x494800),
            },
            producer="generic_lsi_pair_id_rows",
        )
        packet = rt.prepare_device_column_row_buffer_partner_handoff(
            row_buffer,
            partner="numba",
            consumer="numba_partner_continuation",
        )
        neutral_validation = rt.validate_v2_6_neutral_partner_handoff(packet["neutral_handoff"])

        self.assertEqual("accept", packet["status"])
        self.assertEqual("accept", neutral_validation["status"])
        self.assertEqual("numba", packet["selected_partner"])
        self.assertTrue(packet["all_columns_device_resident"])
        self.assertTrue(packet["device_resident_candidate"])
        self.assertFalse(packet["materializes_host_rows_for_bridge"])
        self.assertFalse(packet["torch_conversion_used"])
        self.assertFalse(packet["torch_carrier_used"])
        self.assertFalse(packet["true_zero_copy_claim_authorized"])
        self.assertEqual(rt.V2_6_NEUTRAL_PARTNER_HANDOFF_VERSION, packet["neutral_handoff"]["contract_version"])
        self.assertEqual(2, packet["neutral_handoff"]["runtime_observed_descriptor_count"])

    def test_existing_hit_stream_handoff_can_be_adapted_to_generic_row_buffer(self) -> None:
        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=rt.RtdlRawCudaColumn("ray_ids", "int64", 0x514200, 3),
            primitive_ids=rt.RtdlRawCudaColumn("primitive_ids", "int64", 0x514800, 3),
            row_count=3,
            capacity=8,
            backend="optix",
            native_device_column_output_proven_on_hardware=True,
            caller_owned_output_buffers=True,
            reusable_output_buffers_used=True,
            producer_consumer_stream_ordering="host_synchronized_before_consumer",
        )
        row_buffer = rt.device_column_row_buffer_from_hit_stream_handoff(hit_columns)
        packet = rt.prepare_device_column_row_buffer_partner_handoff(row_buffer, partner="numba")

        self.assertEqual("accept", packet["status"])
        self.assertEqual(3, row_buffer.row_count)
        self.assertEqual(("ray_ids", "primitive_ids"), tuple(row_buffer.columns.keys()))
        self.assertEqual("native_device_columns", row_buffer.source_mode)
        self.assertTrue(row_buffer.device_resident_candidate)
        self.assertFalse(row_buffer.materializes_host_rows_for_bridge)
        self.assertEqual(
            "host_synchronized_before_consumer",
            row_buffer.producer_consumer_stream_ordering,
        )
        metadata = row_buffer.to_metadata()
        self.assertTrue(metadata["native_device_column_output_proven_on_hardware"])
        self.assertTrue(metadata["reuses_v2_5_device_column_contract"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_native_lsi_pair_columns_can_be_adapted_to_generic_row_buffer(self) -> None:
        native_output = OptixNativeDevicePairColumnOutput(
            library=object(),
            owner=object(),
            left_ids_device_ptr=0x614200,
            right_ids_device_ptr=0x614800,
            row_count=4,
            capacity=8,
            candidate_event_count=4,
            overflow=False,
            device_ordinal=0,
            traversal_seconds=0.125,
            native_symbol="rtdl_optix_prepared_segment_pair_candidate_device_columns",
        )
        row_buffer = rt.device_column_row_buffer_from_native_pair_columns(native_output)
        packet = rt.prepare_device_column_row_buffer_partner_handoff(row_buffer, partner="numba")

        self.assertEqual("accept", packet["status"])
        self.assertEqual(("left_id", "right_id"), tuple(row_buffer.columns.keys()))
        self.assertEqual(4, row_buffer.row_count)
        self.assertTrue(row_buffer.device_resident_candidate)
        self.assertEqual("native_device_columns", row_buffer.source_mode)
        self.assertFalse(row_buffer.materializes_host_rows_for_bridge)
        self.assertTrue(row_buffer.native_device_column_output_proven_on_hardware)
        self.assertEqual({"rt_traversal": 0.125}, row_buffer.phase_timing_seconds)
        self.assertFalse(packet["true_zero_copy_claim_authorized"])

    def test_host_materialized_rows_fail_closed_for_device_resident_handoff(self) -> None:
        row_buffer = rt.prepare_device_column_row_buffer(
            {"left_id": [1, 2, 3]},
            producer="host_reference_lsi_rows",
            source_mode="host_rows_to_columns_bridge",
            materializes_host_rows_for_bridge=True,
        )
        packet = rt.plan_device_column_row_buffer_partner_handoff(row_buffer, partner="numba")

        self.assertEqual("reject", packet["status"])
        self.assertTrue(packet["materializes_host_rows_for_bridge"])
        self.assertIn("host-materialized", " ".join(packet["errors"]))
        self.assertFalse(packet["true_zero_copy_claim_authorized"])
        with self.assertRaisesRegex(ValueError, "host-materialized"):
            rt.prepare_device_column_row_buffer_partner_handoff(row_buffer, partner="numba")

    def test_row_count_mismatch_and_empty_inputs_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one named column"):
            rt.prepare_device_column_row_buffer({}, row_count=0, producer="empty")
        with self.assertRaisesRegex(ValueError, "length must match row_count"):
            rt.prepare_device_column_row_buffer(
                {"left_id": _FakeNumbaCudaInt64Column(0x524200)},
                row_count=2,
                producer="bad_shape",
            )

    def test_symbols_are_importable_but_not_star_exports(self) -> None:
        for name in (
            "DEVICE_COLUMN_ROW_BUFFER_CONTRACT_VERSION",
            "RtdlDeviceColumnRowBuffer",
            "describe_device_column_row_buffer_contract",
            "prepare_device_column_row_buffer",
            "device_column_row_buffer_from_hit_stream_handoff",
            "device_column_row_buffer_from_native_pair_columns",
            "plan_device_column_row_buffer_partner_handoff",
            "prepare_device_column_row_buffer_partner_handoff",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)

    def test_adapter_source_has_no_rayjoin_or_output_identity(self) -> None:
        source = RUNTIME.read_text(encoding="utf-8").lower()

        for forbidden in ("rayjoin", "polygon", "overlay", "output_chain", "authorofficial"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
