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

    def __init__(self, values, ptr=0x274000) -> None:
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

    def __init__(self, values, ptr=0x274800) -> None:
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


def _host_hit_columns() -> rt.RtdlHitStreamColumnHandoff:
    return rt.RtdlHitStreamColumnHandoff(
        ray_ids=(0, 1),
        primitive_ids=(0, 1),
        row_count=2,
        capacity=2,
        overflow=False,
        backend="cpu",
        source_mode="reference_columns",
        phase_timing_seconds={},
    )


def _host_payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.prepare_generic_typed_primitive_payload_columns(
        (3, 4),
        (10.0, 20.0),
        group_count=5,
    )


def _device_hit_columns() -> rt.RtdlHitStreamColumnHandoff:
    return rt.prepare_generic_device_resident_hit_stream_columns(
        ray_ids=_FakeCudaInt64Column((0, 1), ptr=0x275000),
        primitive_ids=_FakeCudaInt64Column((0, 1), ptr=0x276000),
        row_count=2,
        capacity=2,
        backend="optix",
        producer_consumer_stream_ordering="producer_event_waited_by_consumer",
    )


def _device_payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=_FakeCudaInt64Column((3, 4), ptr=0x277000),
        primitive_values=_FakeCudaFloat64Column((10.0, 20.0), ptr=0x278000),
        primitive_count=2,
        group_count=5,
        source_mode="typed_payload_columns",
        group_id_bounds_validation="caller_asserted",
    )


class Goal2740HitStreamCrossPartnerTransferPlanTest(unittest.TestCase):
    def test_python_reference_host_columns_are_ready_without_copy_claims(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            _host_hit_columns(),
            _host_payload_columns(),
            operation="segmented_sum_f64",
            partner="reference",
        )

        self.assertEqual(plan["contract_version"], rt.GENERIC_HIT_STREAM_PARTNER_TRANSFER_PLAN_VERSION)
        self.assertEqual(plan["selected_partner"], rt.V2_5_REFERENCE_PARTNER)
        self.assertEqual(plan["status"], "host_reference_ready")
        self.assertEqual(plan["carrier_protocol"], "host_columns")
        self.assertTrue(plan["execution_allowed_without_copy"])
        self.assertFalse(plan["copy_or_host_stage_required"])
        self.assertTrue(plan["silent_copy_forbidden"])
        self.assertFalse(plan["true_zero_copy_authorized"])

    def test_python_reference_device_columns_requires_explicit_materialization(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="segmented_sum_f64",
            partner="python_reference",
        )

        self.assertEqual(plan["status"], "explicit_host_materialization_required")
        self.assertEqual(plan["carrier_protocol"], "host_columns")
        self.assertTrue(plan["copy_or_host_stage_required"])
        self.assertFalse(plan["execution_allowed_without_copy"])
        self.assertEqual(plan["runtime_action"], "cpu_reference_requires_explicit_host_materialization")

    def test_triton_device_columns_select_torch_carrier_preview_but_no_claim(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="segmented_sum_f64",
            partner="triton",
        )

        self.assertEqual(plan["selected_partner"], rt.V2_5_PRIMARY_PARTNER)
        self.assertEqual(plan["status"], "torch_carrier_preview")
        self.assertEqual(plan["carrier_protocol"], "cuda_array_interface_to_torch_carrier")
        self.assertTrue(plan["current_inputs_device_ready"])
        self.assertTrue(plan["execution_allowed_without_copy"])
        self.assertTrue(plan["executable_preview_available"])
        self.assertTrue(plan["stream_synchronization_proven"])
        self.assertFalse(plan["true_zero_copy_authorized"])
        self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_cupy_is_descriptor_only_for_current_generic_hit_stream(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="segmented_sum_f64",
            partner="cupy",
        )

        self.assertEqual(plan["selected_partner"], rt.V2_5_CONFORMANCE_PARTNER)
        self.assertEqual(plan["status"], "descriptor_only")
        self.assertEqual(plan["carrier_protocol"], "cuda_array_interface_descriptor")
        self.assertTrue(plan["descriptor_only"])
        self.assertFalse(plan["executable_preview_available"])
        self.assertEqual(plan["runtime_action"], "descriptor_only_no_generic_kernel_execution")

    def test_numba_supported_operation_is_cuda_descriptor_preview(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="segmented_count_i64",
            partner="numba",
        )

        self.assertEqual(plan["selected_partner"], rt.V2_5_FALLBACK_PARTNER)
        self.assertEqual(plan["status"], "cuda_descriptor_preview")
        self.assertTrue(plan["executable_preview_available"])
        self.assertEqual(plan["runtime_action"], "numba_preview_requires_explicit_runtime_validation")

    def test_unsupported_operation_fails_closed_and_is_nested_in_continuation_plan(self) -> None:
        transfer = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="grouped_argmin_f64",
            partner="numba",
        )
        continuation = rt.plan_v2_5_hit_stream_partner_continuation(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="grouped_argmin_f64",
            partner="numba",
        )

        self.assertEqual(transfer["status"], "unsupported_fail_closed")
        self.assertTrue(continuation["fail_closed"])
        self.assertEqual(continuation["partner_transfer_plan"]["status"], "unsupported_fail_closed")
        self.assertFalse(continuation["partner_transfer_plan"]["execution_allowed_without_copy"])

    def test_transfer_plan_symbols_are_experimental_not_star_exported(self) -> None:
        self.assertTrue(hasattr(rt, "plan_v2_5_hit_stream_partner_transfer"))
        self.assertNotIn("plan_v2_5_hit_stream_partner_transfer", rt.__all__)


if __name__ == "__main__":
    unittest.main()
