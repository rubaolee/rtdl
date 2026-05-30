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

    def __init__(self, values) -> None:
        self._values = tuple(values)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (0xC000, False),
            "version": 3,
        }

    def data_ptr(self):
        return 0xC000

    def tolist(self):
        return list(self._values)

    def __iter__(self):
        return iter(self._values)


class _FakeCudaFloat64Column:
    dtype = "float64"
    shape = (2,)
    device = _FakeCudaDevice()

    def __init__(self, values) -> None:
        self._values = tuple(values)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<f8",
            "data": (0xD000, False),
            "version": 3,
        }

    def data_ptr(self):
        return 0xD000

    def tolist(self):
        return list(self._values)

    def __iter__(self):
        return iter(self._values)


def _reference_hit_columns() -> rt.RtdlHitStreamColumnHandoff:
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


def _host_bridge_hit_columns() -> rt.RtdlHitStreamColumnHandoff:
    return rt.RtdlHitStreamColumnHandoff(
        ray_ids=(0, 1),
        primitive_ids=(0, 1),
        row_count=2,
        capacity=2,
        overflow=False,
        backend="cpu",
        source_mode="host_rows_to_columns_bridge",
        phase_timing_seconds={},
        materializes_host_rows_for_bridge=True,
    )


def _device_hit_columns() -> rt.RtdlHitStreamColumnHandoff:
    return rt.prepare_generic_device_resident_hit_stream_columns(
        ray_ids=_FakeCudaInt64Column((0, 1)),
        primitive_ids=_FakeCudaInt64Column((0, 1)),
        row_count=2,
        capacity=2,
        backend="optix",
    )


def _host_payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.prepare_generic_typed_primitive_payload_columns(
        (3, 4),
        (10.0, 20.0),
        group_count=5,
    )


def _device_payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=_FakeCudaInt64Column((3, 4)),
        primitive_values=_FakeCudaFloat64Column((10.0, 20.0)),
        primitive_count=2,
        group_count=5,
        source_mode="typed_payload_columns",
        group_id_bounds_validation="caller_asserted",
    )


class Goal2698HitStreamPartnerContinuationPlanTest(unittest.TestCase):
    def test_reference_plan_allows_host_reference_without_copy_claim(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_continuation(
            _reference_hit_columns(),
            _host_payload_columns(),
            operation="segmented_sum_f64",
            partner="reference",
        )

        self.assertEqual(plan["selected_partner"], rt.V2_5_REFERENCE_PARTNER)
        self.assertTrue(plan["current_inputs_satisfy_device_requirements"])
        self.assertFalse(plan["copy_or_host_stage_required"])
        self.assertFalse(plan["fail_closed"])
        self.assertEqual(plan["runtime_action"], "plan_available")
        self.assertFalse(plan["true_zero_copy_authorized"])
        self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_host_bridge_to_triton_requires_explicit_copy_or_host_stage(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_continuation(
            _host_bridge_hit_columns(),
            _host_payload_columns(),
            operation="segmented_sum_f64",
            partner="triton",
        )

        self.assertEqual(plan["selected_partner"], rt.V2_5_PRIMARY_PARTNER)
        self.assertFalse(plan["current_inputs_device_ready"])
        self.assertFalse(plan["current_inputs_satisfy_device_requirements"])
        self.assertTrue(plan["copy_or_host_stage_required"])
        self.assertFalse(plan["fail_closed"])
        self.assertEqual(plan["runtime_action"], "host_stage_or_copy_must_be_explicit")

    def test_device_columns_to_triton_are_plan_ready_but_still_pod_gated(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_continuation(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="segmented_sum_f64",
            partner="triton",
        )

        self.assertTrue(plan["current_inputs_device_ready"])
        self.assertTrue(plan["current_inputs_satisfy_device_requirements"])
        self.assertFalse(plan["copy_or_host_stage_required"])
        self.assertTrue(plan["pod_validation_required"])
        self.assertEqual(
            plan["runtime_action"],
            "requires_sm70_pod_validation_before_performance_claim",
        )
        self.assertFalse(plan["true_zero_copy_authorized"])
        self.assertFalse(plan["support_cell"]["public_speedup_claim_authorized"])

    def test_unsupported_partner_operation_fails_closed(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_continuation(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="grouped_argmin_f64",
            partner="numba",
        )

        self.assertEqual(plan["selected_partner"], rt.V2_5_FALLBACK_PARTNER)
        self.assertFalse(plan["support_cell"]["supported"])
        self.assertTrue(plan["fail_closed"])
        self.assertEqual(plan["runtime_action"], "fail_closed_unsupported_partner_operation")

    def test_planner_is_experimental_not_star_export(self) -> None:
        self.assertTrue(hasattr(rt, "plan_v2_5_hit_stream_partner_continuation"))
        self.assertNotIn("plan_v2_5_hit_stream_partner_continuation", rt.__all__)


if __name__ == "__main__":
    unittest.main()
