from __future__ import annotations

import os
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
HIT_STREAM_HANDOFF = ROOT / "src/rtdsl/hit_stream_handoff.py"
REPORT = ROOT / "docs/reports/goal2762_hit_stream_device_status_buffers_2026-05-31.md"


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
            "data": (0x276220, False),
            "version": 3,
        }

    def data_ptr(self):
        return 0x276220

    def tolist(self):
        return [1.0]

    def __iter__(self):
        return iter((1.0,))


def _hit_columns_with_status() -> rt.RtdlHitStreamColumnHandoff:
    return rt.prepare_generic_device_resident_hit_stream_columns(
        ray_ids=_FakeCudaInt64Column(0, 0x276200),
        primitive_ids=_FakeCudaInt64Column(0, 0x276210),
        row_count=1,
        capacity=1,
        backend="optix",
        producer_consumer_stream_ordering="host_synchronized_before_consumer",
        native_device_column_output_proven_on_hardware=True,
        caller_owned_output_buffers=True,
        reusable_output_buffers_used=True,
        row_count_device_ptr=0x276230,
        hit_event_count_device_ptr=0x276238,
        overflow_device_ptr=0x276240,
    )


def _payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=_FakeCudaInt64Column(0, 0x276218),
        primitive_values=_FakeCudaFloat64Column(),
        primitive_count=1,
        group_count=1,
        source_mode="typed_payload_columns",
        group_id_bounds_validation="caller_asserted",
    )


class Goal2762HitStreamDeviceStatusBuffersTest(unittest.TestCase):
    def test_native_abi_accepts_caller_owned_status_device_pointers(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        symbol = "rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status"

        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn(
            "run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_optix",
            workloads,
        )
        for field in (
            "row_count_device_ptr",
            "hit_event_count_device_ptr",
            "overflow_device_ptr",
        ):
            self.assertIn(field, prelude)
            self.assertIn(field, api)
        self.assertIn("caller-owned hit-stream status requires nonzero device pointers", workloads)
        self.assertIn("columns_out->row_count_device_ptr", workloads)
        self.assertIn("lp.row_count = reinterpret_cast<unsigned long long*>(row_count_ptr)", workloads)
        self.assertIn("lp.overflow = reinterpret_cast<uint32_t*>(overflow_ptr)", workloads)

    def test_python_runtime_exposes_status_buffer_path_and_metadata(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        handoff_source = HIT_STREAM_HANDOFF.read_text(encoding="utf-8")

        self.assertIn("OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_INTO_DEVICE_COLUMNS_WITH_STATUS_SYMBOL", runtime)
        self.assertIn("ray_triangle_hit_stream_into_device_columns_with_status", runtime)
        self.assertIn("row_count_device_ptr", runtime)
        self.assertIn("hit_event_count_device_ptr", runtime)
        self.assertIn("overflow_device_ptr", runtime)
        self.assertIn('"device_resident_status_for_partner"', handoff_source)
        self.assertIn('"device_resident_hit_event_count_for_partner"', handoff_source)

    def test_status_pointer_metadata_remains_host_synchronized_not_async(self) -> None:
        handoff = _hit_columns_with_status()
        metadata = handoff.to_metadata()
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            handoff,
            _payload_columns(),
            operation="segmented_count_i64",
            partner="triton",
        )

        self.assertTrue(metadata["device_resident_row_count_for_partner"])
        self.assertTrue(metadata["device_resident_hit_event_count_for_partner"])
        self.assertTrue(metadata["device_resident_overflow_for_partner"])
        self.assertTrue(metadata["device_resident_status_for_partner"])
        self.assertEqual(metadata["row_count_device_ptr"], 0x276230)
        self.assertTrue(metadata["host_synchronization_used"])
        self.assertFalse(metadata["zero_copy_compatible_stream_ordering"])
        self.assertFalse(metadata["async_partner_continuation_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertTrue(plan["device_resident_status_for_partner"])
        self.assertFalse(plan["async_partner_continuation_authorized"])
        self.assertFalse(plan["true_zero_copy_authorized"])

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("device-resident status", report)
        self.assertIn("with_status", report)
        self.assertIn("host_synchronized_before_consumer", report)
        self.assertIn("does not authorize async partner continuation", report)
        self.assertIn("does not authorize true zero-copy", report)

    def test_runtime_smoke_writes_device_status_when_optix_available(self) -> None:
        if not os.environ.get("RTDL_OPTIX_LIBRARY") and not (ROOT / "build/librtdl_optix.so").exists():
            self.skipTest("OptiX backend library is not configured")
        try:
            import torch
        except Exception as exc:  # pragma: no cover - local non-CUDA hosts skip here.
            self.skipTest(f"torch unavailable: {exc}")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        from rtdsl.reference import Ray3D, Triangle3D

        triangle = Triangle3D(
            id=0,
            x0=0.0,
            y0=0.0,
            z0=0.0,
            x1=1.0,
            y1=0.0,
            z1=0.0,
            x2=0.0,
            y2=1.0,
            z2=0.0,
        )
        ray = Ray3D(id=11, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0)

        with rt.prepare_optix_static_triangle_scene_3d((triangle,)) as scene:
            buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(4)
            try:
                handoff = scene.ray_triangle_hit_stream_into_device_columns_with_status((ray,), buffers)
                self.assertEqual(handoff.row_count, 1)
                self.assertFalse(handoff.overflow)
                self.assertEqual(handoff.ray_ids.cpu().tolist(), [11])
                self.assertEqual(handoff.primitive_ids.cpu().tolist(), [0])
                self.assertEqual(int(buffers.row_count.cpu().item()), 1)
                self.assertEqual(int(buffers.hit_event_count.cpu().item()), 1)
                self.assertEqual(int(buffers.overflow.cpu().item()), 0)
                metadata = handoff.to_metadata()
                self.assertEqual(metadata["row_count_device_ptr"], buffers.row_count_device_ptr)
                self.assertTrue(metadata["device_resident_status_for_partner"])
                self.assertTrue(metadata["host_synchronization_used"])
                self.assertFalse(metadata["async_partner_continuation_authorized"])
                self.assertFalse(metadata["true_zero_copy_authorized"])
            finally:
                buffers.close()


if __name__ == "__main__":
    unittest.main()
