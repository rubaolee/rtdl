from __future__ import annotations

import unittest

import rtdsl as rt


class _FakeCudaDevice:
    type = "cuda"
    index = 0


class _FakeCudaInt64Column:
    dtype = "int64"
    shape = (2,)
    device = _FakeCudaDevice()

    def __init__(self, values, ptr=0x275000) -> None:
        self._values = tuple(values)
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
        return list(self._values)

    def __iter__(self):
        return iter(self._values)


class _FakeCudaFloat64Column:
    dtype = "float64"
    shape = (2,)
    device = _FakeCudaDevice()

    def __init__(self, values, ptr=0x278000) -> None:
        self._values = tuple(values)
        self._ptr = int(ptr)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<f8",
            "data": (self._ptr, False),
            "version": 3,
        }

    def data_ptr(self):
        return self._ptr

    def tolist(self):
        return list(self._values)

    def __iter__(self):
        return iter(self._values)


def _hit_columns(ordering: str) -> rt.RtdlHitStreamColumnHandoff:
    return rt.prepare_generic_device_resident_hit_stream_columns(
        ray_ids=_FakeCudaInt64Column((0, 1), ptr=0x275000),
        primitive_ids=_FakeCudaInt64Column((0, 1), ptr=0x276000),
        row_count=2,
        capacity=2,
        backend="optix",
        producer_consumer_stream_ordering=ordering,
    )


def _payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=_FakeCudaInt64Column((0, 1), ptr=0x277000),
        primitive_values=_FakeCudaFloat64Column((10.0, 20.0), ptr=0x278000),
        primitive_count=2,
        group_count=2,
        source_mode="typed_payload_columns",
        group_id_bounds_validation="caller_asserted",
    )


class Goal2750HitStreamTransferStreamOrderingGateTest(unittest.TestCase):
    def test_not_proven_ordering_blocks_triton_device_consumer(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            _hit_columns("not_proven"),
            _payload_columns(),
            operation="segmented_sum_f64",
            partner="triton",
        )

        self.assertEqual(plan["status"], "stream_ordering_proof_required")
        self.assertEqual(plan["runtime_action"], "requires_stream_ordering_proof_before_device_consumer")
        self.assertTrue(plan["current_inputs_device_ready"])
        self.assertTrue(plan["device_consumer_requires_stream_ordering"])
        self.assertTrue(plan["stream_ordering_blocks_device_consumer"])
        self.assertFalse(plan["execution_allowed_without_copy"])
        self.assertFalse(plan["executable_preview_available"])
        self.assertFalse(plan["true_zero_copy_authorized"])

    def test_event_ordered_and_host_synchronized_inputs_are_allowed_but_not_promoted(self) -> None:
        for ordering in ("producer_event_waited_by_consumer", "host_synchronized_before_consumer"):
            with self.subTest(ordering=ordering):
                plan = rt.plan_v2_5_hit_stream_partner_transfer(
                    _hit_columns(ordering),
                    _payload_columns(),
                    operation="segmented_sum_f64",
                    partner="triton",
                )

                self.assertEqual(plan["status"], "torch_carrier_preview")
                self.assertEqual(plan["producer_consumer_stream_ordering"], ordering)
                self.assertTrue(plan["stream_synchronization_proven"])
                self.assertFalse(plan["stream_ordering_blocks_device_consumer"])
                self.assertTrue(plan["execution_allowed_without_copy"])
                self.assertFalse(plan["true_zero_copy_authorized"])
                self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_descriptor_partners_also_fail_closed_without_ordering_proof(self) -> None:
        for partner in ("cupy", "numba"):
            with self.subTest(partner=partner):
                plan = rt.plan_v2_5_hit_stream_partner_transfer(
                    _hit_columns("not_proven"),
                    _payload_columns(),
                    operation="segmented_count_i64",
                    partner=partner,
                )

                self.assertEqual(plan["status"], "stream_ordering_proof_required")
                self.assertTrue(plan["stream_ordering_blocks_device_consumer"])
                self.assertFalse(plan["execution_allowed_without_copy"])
                self.assertEqual(plan["runtime_action"], "requires_stream_ordering_proof_before_device_consumer")


if __name__ == "__main__":
    unittest.main()
