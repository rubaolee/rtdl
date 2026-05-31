from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
HIT_STREAM_HANDOFF = ROOT / "src/rtdsl/hit_stream_handoff.py"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs/reports/goal2760_hit_stream_async_promotion_requirements_2026-05-31.md"


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
            "data": (0x276020, False),
            "version": 3,
        }

    def data_ptr(self):
        return 0x276020

    def tolist(self):
        return [1.0]

    def __iter__(self):
        return iter((1.0,))


def _hit_columns() -> rt.RtdlHitStreamColumnHandoff:
    return rt.prepare_generic_device_resident_hit_stream_columns(
        ray_ids=_FakeCudaInt64Column(0, 0x276000),
        primitive_ids=_FakeCudaInt64Column(0, 0x276010),
        row_count=1,
        capacity=1,
        backend="optix",
        producer_consumer_stream_ordering="host_synchronized_before_consumer",
        native_device_column_output_proven_on_hardware=True,
        caller_owned_output_buffers=True,
        reusable_output_buffers_used=True,
    )


def _payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=_FakeCudaInt64Column(0, 0x276018),
        primitive_values=_FakeCudaFloat64Column(),
        primitive_count=1,
        group_count=1,
        source_mode="typed_payload_columns",
        group_id_bounds_validation="caller_asserted",
    )


class Goal2760HitStreamAsyncPromotionRequirementsTest(unittest.TestCase):
    def test_async_promotion_requirements_are_exported_and_fail_closed(self) -> None:
        requirements = rt.describe_v2_5_hit_stream_async_promotion_requirements()

        self.assertEqual(
            requirements["contract_version"],
            rt.GENERIC_HIT_STREAM_ASYNC_PROMOTION_REQUIREMENTS_VERSION,
        )
        self.assertEqual(
            requirements["current_runtime_ordering_state"],
            "host_synchronized_before_consumer",
        )
        self.assertFalse(requirements["current_runtime_async_promotion_authorized"])
        self.assertFalse(requirements["current_runtime_true_zero_copy_authorized"])
        self.assertFalse(requirements["current_runtime_has_completion_event_handle"])
        self.assertFalse(requirements["current_runtime_has_same_stream_handle"])
        self.assertIn("completion_event_handle_with_lifetime_owner", requirements["required_native_abi_extensions"])
        self.assertIn("device_resident_row_count_ptr", requirements["required_native_abi_extensions"])
        self.assertIn("no cuStreamSynchronize on the producer path before partner launch", requirements["required_pod_validation"])

    def test_current_handoff_and_transfer_metadata_expose_sync_blocker(self) -> None:
        handoff = _hit_columns()
        metadata = handoff.to_metadata()
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            handoff,
            _payload_columns(),
            operation="segmented_count_i64",
            partner="triton",
        )

        self.assertEqual(metadata["producer_consumer_stream_ordering"], "host_synchronized_before_consumer")
        self.assertTrue(metadata["host_synchronization_used"])
        self.assertEqual(metadata["row_count_scalar_visibility"], "host_visible_after_producer_synchronization")
        self.assertFalse(metadata["device_resident_row_count_for_partner"])
        self.assertFalse(metadata["completion_event_handle_available"])
        self.assertFalse(metadata["same_stream_handle_available"])
        self.assertFalse(metadata["async_partner_continuation_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertEqual(plan["row_count_scalar_visibility"], "host_visible_after_producer_synchronization")
        self.assertFalse(plan["device_resident_row_count_for_partner"])
        self.assertFalse(plan["completion_event_handle_available"])
        self.assertFalse(plan["async_partner_continuation_authorized"])
        self.assertFalse(plan["true_zero_copy_authorized"])

    def test_native_and_python_paths_remain_host_synchronized_before_return(self) -> None:
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        function_start = workloads.index(
            "run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_impl_optix"
        )
        function_end = workloads.index(
            "run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_optix",
            function_start,
        )
        function = workloads[function_start:function_end]

        self.assertIn("CUstream stream = 0;", function)
        self.assertIn("cuStreamSynchronize(stream)", function)
        self.assertLess(function.index("cuStreamSynchronize(stream)"), function.index("download(&attempted_rows"))
        self.assertLess(function.index("cuStreamSynchronize(stream)"), function.index("download(&overflow"))

        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        device_start = runtime.index("def ray_triangle_hit_stream_device_columns(")
        into_start = runtime.index("def ray_triangle_hit_stream_into_device_columns(")
        method_end = runtime.index("def ray_triangle_prepared_primitive_grouped_i64_reduction", into_start)
        methods = runtime[device_start:method_end]
        self.assertEqual(methods.count('producer_consumer_stream_ordering="host_synchronized_before_consumer"'), 2)
        self.assertNotIn('producer_consumer_stream_ordering="same_stream"', methods)
        self.assertNotIn('producer_consumer_stream_ordering="producer_event_waited_by_consumer"', methods)

    def test_report_records_current_blocker_and_next_abi_requirements(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("host_synchronized_before_consumer", report)
        self.assertIn("completion_event_handle_with_lifetime_owner", report)
        self.assertIn("device_resident_row_count_ptr", report)
        self.assertIn("device_resident_overflow_ptr", report)
        self.assertIn("This goal does not authorize true zero-copy", report)
        self.assertIn("no public speedup claim", report)


if __name__ == "__main__":
    unittest.main()
