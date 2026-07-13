from __future__ import annotations

import unittest

import rtdsl as rt


class _FakeCudaInt64Column:
    dtype = "int64"
    shape = (4,)

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


class _CloseOwner:
    def __init__(self) -> None:
        self.close_count = 0

    def close(self) -> None:
        self.close_count += 1


class Goal5043PublicDeviceColumnBufferContractTest(unittest.TestCase):
    def test_public_symbols_are_exported_without_promoting_old_adapter_names(self) -> None:
        for name in (
            "DEVICE_COLUMN_BUFFER_CONTRACT_VERSION",
            "DEVICE_COLUMN_BUFFER_API_MATURITY",
            "DEVICE_COLUMN_BUFFER_OWNER_LIFETIME_STATES",
            "DeviceColumnBuffer",
            "describe_device_column_buffer_contract",
            "device_column_buffer",
            "device_column_buffer_from_row_buffer",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertIn(name, rt.__all__)

        for old_internal in (
            "RtdlDeviceColumnRowBuffer",
            "prepare_device_column_row_buffer",
            "device_column_row_buffer_from_native_pair_columns",
            "device_column_row_buffer_from_point_location_id_columns",
        ):
            self.assertTrue(hasattr(rt, old_internal))
            self.assertNotIn(old_internal, rt.__all__)

    def test_contract_preserves_four_state_stream_ordering_and_no_self_declared_residency(self) -> None:
        contract = rt.describe_device_column_buffer_contract()

        self.assertEqual(rt.DEVICE_COLUMN_BUFFER_CONTRACT_VERSION, contract["contract_version"])
        self.assertEqual(
            (
                "not_proven",
                "same_stream",
                "producer_event_waited_by_consumer",
                "host_synchronized_before_consumer",
            ),
            contract["stream_ordering_states"],
        )
        self.assertTrue(contract["device_residency_derived_from_metadata"])
        self.assertFalse(contract["self_declared_residency_allowed"])
        self.assertFalse(contract["app_specific_schema_allowed"])
        self.assertFalse(contract["true_zero_copy_claim_authorized"])
        self.assertFalse(contract["public_speedup_claim_authorized"])

    def test_device_residency_is_derived_from_column_interfaces(self) -> None:
        buffer = rt.device_column_buffer(
            {"left_id": _FakeCudaInt64Column(0x504300), "right_id": _FakeCudaInt64Column(0x504380)},
            producer="generic_pair_columns",
            producer_consumer_stream_ordering="same_stream",
            native_device_column_output_proven_on_hardware=True,
        )

        metadata = buffer.to_metadata()
        self.assertTrue(buffer.device_resident_candidate)
        self.assertTrue(metadata["device_resident_candidate"])
        self.assertTrue(metadata["native_device_column_output_proven_on_hardware"])
        self.assertFalse(metadata["materializes_host_rows_for_bridge"])
        self.assertFalse(metadata["residency_self_declared"])
        self.assertEqual("same_stream", metadata["producer_consumer_stream_ordering"])
        self.assertTrue(metadata["stream_synchronization_proven"])
        self.assertEqual(("left_id", "right_id"), metadata["columns"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_host_materialized_buffer_fails_device_resident_partner_handoff(self) -> None:
        buffer = rt.device_column_buffer(
            {"left_id": [1, 2, 3]},
            producer="host_reference_columns",
            source_mode="host_rows_to_columns_bridge",
            materializes_host_rows_for_bridge=True,
        )

        metadata = buffer.to_metadata()
        self.assertFalse(metadata["device_resident_candidate"])
        self.assertTrue(metadata["materializes_host_rows_for_bridge"])

        packet = buffer.plan_partner_handoff(partner="numba")
        self.assertEqual("reject", packet["status"])
        self.assertTrue(packet["public_device_column_buffer"]["materializes_host_rows_for_bridge"])
        with self.assertRaisesRegex(ValueError, "host-materialized"):
            buffer.prepare_partner_handoff(partner="numba")

    def test_context_manager_closes_owned_owner_once(self) -> None:
        owner = _CloseOwner()
        with rt.device_column_buffer(
            {"left_id": _FakeCudaInt64Column(0x514300)},
            producer="owned_column",
            owner=owner,
            owner_lifetime="owned_close_on_buffer_close",
        ) as buffer:
            self.assertFalse(buffer.closed)
            self.assertEqual(0, owner.close_count)

        self.assertTrue(buffer.closed)
        self.assertEqual(1, owner.close_count)
        buffer.close()
        self.assertEqual(1, owner.close_count)

    def test_invalid_state_and_mismatched_rows_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "stream ordering state"):
            rt.device_column_buffer(
                {"left_id": _FakeCudaInt64Column(0x524300)},
                producer="bad_stream",
                producer_consumer_stream_ordering="event_ordered",
            )
        with self.assertRaisesRegex(ValueError, "length must match row_count"):
            rt.device_column_buffer(
                {"left_id": _FakeCudaInt64Column(0x524380)},
                row_count=3,
                producer="bad_length",
            )
        with self.assertRaisesRegex(ValueError, "owner_lifetime"):
            rt.device_column_buffer(
                {"left_id": _FakeCudaInt64Column(0x524400)},
                producer="bad_owner_lifetime",
                owner_lifetime="app_decides",
            )


if __name__ == "__main__":
    unittest.main()
