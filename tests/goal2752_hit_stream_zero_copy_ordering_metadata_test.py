from __future__ import annotations

import unittest

import rtdsl as rt


class _FakeCudaDevice:
    type = "cuda"
    index = 0


class _FakeCudaInt64Column:
    dtype = "int64"
    shape = (1,)
    device = _FakeCudaDevice()

    def __init__(self, value: int, ptr: int) -> None:
        self._value = int(value)
        self._ptr = int(ptr)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (self._ptr, False),
            "version": 3,
        }

    def data_ptr(self):
        return self._ptr

    def tolist(self):
        return [self._value]

    def __iter__(self):
        return iter((self._value,))


class _FakeCudaFloat64Column:
    dtype = "float64"
    shape = (1,)
    device = _FakeCudaDevice()

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<f8",
            "data": (0x275200, False),
            "version": 3,
        }

    def data_ptr(self):
        return 0x275200

    def tolist(self):
        return [1.0]

    def __iter__(self):
        return iter((1.0,))


def _hit_columns(ordering: str) -> rt.RtdlHitStreamColumnHandoff:
    return rt.prepare_generic_device_resident_hit_stream_columns(
        ray_ids=_FakeCudaInt64Column(0, 0x275000),
        primitive_ids=_FakeCudaInt64Column(0, 0x275100),
        row_count=1,
        capacity=1,
        backend="optix",
        producer_consumer_stream_ordering=ordering,
    )


def _payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=_FakeCudaInt64Column(0, 0x275180),
        primitive_values=_FakeCudaFloat64Column(),
        primitive_count=1,
        group_count=1,
        source_mode="typed_payload_columns",
        group_id_bounds_validation="caller_asserted",
    )


class Goal2752HitStreamZeroCopyOrderingMetadataTest(unittest.TestCase):
    def test_host_synchronized_is_safe_but_not_zero_copy_compatible_ordering(self) -> None:
        metadata = _hit_columns("host_synchronized_before_consumer").to_metadata()
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            _hit_columns("host_synchronized_before_consumer"),
            _payload_columns(),
            operation="segmented_count_i64",
            partner="triton",
        )

        self.assertTrue(metadata["stream_synchronization_proven"])
        self.assertTrue(metadata["host_synchronization_used"])
        self.assertFalse(metadata["event_or_same_stream_ordering_proven"])
        self.assertFalse(metadata["zero_copy_compatible_stream_ordering"])
        self.assertTrue(plan["host_synchronization_used"])
        self.assertFalse(plan["zero_copy_compatible_stream_ordering"])
        self.assertTrue(plan["execution_allowed_without_copy"])
        self.assertFalse(plan["true_zero_copy_authorized"])

    def test_event_and_same_stream_ordering_are_future_zero_copy_compatible_but_not_authorized(self) -> None:
        for ordering in rt.GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES:
            with self.subTest(ordering=ordering):
                metadata = _hit_columns(ordering).to_metadata()
                plan = rt.plan_v2_5_hit_stream_partner_transfer(
                    _hit_columns(ordering),
                    _payload_columns(),
                    operation="segmented_count_i64",
                    partner="triton",
                )

                self.assertTrue(metadata["stream_synchronization_proven"])
                self.assertFalse(metadata["host_synchronization_used"])
                self.assertTrue(metadata["event_or_same_stream_ordering_proven"])
                self.assertTrue(metadata["zero_copy_compatible_stream_ordering"])
                self.assertTrue(plan["zero_copy_compatible_stream_ordering"])
                self.assertFalse(plan["true_zero_copy_authorized"])
                self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_native_output_metadata_uses_same_ordering_classification(self) -> None:
        output = rt.RtdlNativeDeviceHitStreamOutput(
            ray_ids_device_ptr=0x275000,
            primitive_ids_device_ptr=0x275100,
            row_count=1,
            capacity=1,
            overflow=False,
            hit_event_count=1,
            native_device_column_output_proven_on_hardware=True,
            producer_consumer_stream_ordering="host_synchronized_before_consumer",
        )
        metadata = output.to_metadata()

        self.assertTrue(metadata["stream_synchronization_proven"])
        self.assertTrue(metadata["host_synchronization_used"])
        self.assertFalse(metadata["zero_copy_compatible_stream_ordering"])
        self.assertFalse(metadata["true_zero_copy_authorized"])


if __name__ == "__main__":
    unittest.main()
