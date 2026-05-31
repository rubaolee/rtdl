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
REPORT = ROOT / "docs/reports/goal2764_hit_stream_same_stream_status_consumer_2026-05-31.md"


class Goal2764HitStreamSameStreamStatusConsumerTest(unittest.TestCase):
    def test_native_async_stream_abi_has_lifetime_owner_and_no_producer_sync(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        symbol = (
            "rtdl_optix_static_triangle_scene_3d_"
            "ray_triangle_hit_stream_into_device_columns_with_status_on_stream"
        )
        release_symbol = "rtdl_optix_release_ray_triangle_hit_stream_async_launch"

        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn(release_symbol, prelude)
        self.assertIn(release_symbol, api)
        self.assertIn("NativeRayTriangleHitStreamAsyncLaunchOwner", workloads)
        self.assertIn("release_ray_triangle_hit_stream_async_launch_optix", workloads)

        function_start = workloads.index(
            "run_prepared_static_triangle_scene_3d_"
            "ray_triangle_hit_stream_into_device_columns_with_status_on_stream_optix"
        )
        function_end = workloads.index(
            "static void release_ray_triangle_hit_stream_device_columns_optix",
            function_start,
        )
        function = workloads[function_start:function_end]
        self.assertIn("CUstream stream = reinterpret_cast<CUstream>", function)
        self.assertIn("cuMemsetD8Async(row_count_ptr", function)
        self.assertIn("cuMemsetD32Async(overflow_ptr", function)
        self.assertIn("optixLaunch", function)
        self.assertIn("columns_out->owner_handle = owner.release()", function)
        self.assertNotIn("cuStreamSynchronize(stream)", function)
        self.assertNotIn("download(", function)

    def test_python_runtime_exposes_same_stream_cupy_status_consumer(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        handoff = HIT_STREAM_HANDOFF.read_text(encoding="utf-8")

        self.assertIn("OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_INTO_DEVICE_COLUMNS_WITH_STATUS_ON_STREAM_SYMBOL", runtime)
        self.assertIn("OPTIX_RELEASE_RAY_TRIANGLE_HIT_STREAM_3D_ASYNC_LAUNCH_SYMBOL", runtime)
        self.assertIn("ray_triangle_hit_stream_same_stream_status_summary", runtime)
        self.assertIn("cp.cuda.ExternalStream", runtime)
        self.assertIn("rtdl_hit_stream_same_stream_status_summary_u64", runtime)
        self.assertIn('"producer_consumer_stream_ordering": "same_stream"', runtime)
        self.assertIn('"producer_host_synchronization_used": False', runtime)
        self.assertIn('"host_scalar_read_before_consumer": False', runtime)
        self.assertIn('"async_partner_continuation_authorization_scope"', runtime)
        self.assertIn('"stream_lifetime_contract"', runtime)
        self.assertIn('"true_zero_copy_authorized": False', runtime)
        self.assertIn('"current_runtime_has_bounded_same_stream_status_consumer": True', handoff)
        self.assertIn('"general_async_partner_continuation_authorized": False', handoff)

    def test_requirement_descriptor_tracks_narrow_promotion_not_general_release_claim(self) -> None:
        requirements = rt.describe_v2_5_hit_stream_async_promotion_requirements()

        self.assertEqual(requirements["current_bounded_status_consumer_ordering_state"], "same_stream")
        self.assertTrue(requirements["current_runtime_has_same_stream_handle"])
        self.assertTrue(requirements["current_runtime_has_device_resident_row_count_for_partner"])
        self.assertTrue(requirements["current_runtime_has_device_resident_overflow_for_partner"])
        self.assertTrue(requirements["current_runtime_has_bounded_same_stream_status_consumer"])
        self.assertFalse(requirements["general_async_partner_continuation_authorized"])
        self.assertFalse(requirements["current_runtime_true_zero_copy_authorized"])
        self.assertFalse(requirements["current_runtime_public_speedup_claim_authorized"])

    def test_report_records_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("same-stream", report)
        self.assertIn("CuPy RawKernel", report)
        self.assertIn("no producer-side host scalar sync", report)
        self.assertIn("does not authorize true zero-copy", report)
        self.assertIn("does not authorize public speedup claims", report)

    def test_runtime_smoke_uses_device_status_without_preconsumer_host_scalar_sync(self) -> None:
        if not os.environ.get("RTDL_OPTIX_LIBRARY") and not (ROOT / "build/librtdl_optix.so").exists():
            self.skipTest("OptiX backend library is not configured")
        try:
            import cupy  # noqa: F401
            import torch
        except Exception as exc:  # pragma: no cover - local non-CUDA hosts skip here.
            self.skipTest(f"CUDA partner dependencies unavailable: {exc}")
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
                result = scene.ray_triangle_hit_stream_same_stream_status_summary((ray,), buffers)
                summary = result["summary"]
                metadata = result["metadata"]

                self.assertEqual(summary["row_count"], 1)
                self.assertEqual(summary["hit_event_count"], 1)
                self.assertFalse(summary["overflow"])
                self.assertEqual(summary["bounded_row_count"], 1)
                self.assertEqual(summary["first_ray_id"], 11)
                self.assertEqual(summary["first_primitive_id"], 0)
                self.assertTrue(summary["status_ok"])
                self.assertTrue(summary["consumer_read_status_on_device"])
                self.assertFalse(summary["host_scalar_read_before_consumer"])
                self.assertEqual(int(buffers.row_count.cpu().item()), 1)
                self.assertEqual(int(buffers.hit_event_count.cpu().item()), 1)
                self.assertEqual(int(buffers.overflow.cpu().item()), 0)

                self.assertEqual(metadata["producer_consumer_stream_ordering"], "same_stream")
                self.assertTrue(metadata["stream_synchronization_proven"])
                self.assertTrue(metadata["zero_copy_compatible_stream_ordering"])
                self.assertFalse(metadata["producer_host_synchronization_used"])
                self.assertFalse(metadata["host_scalar_read_before_consumer"])
                self.assertTrue(metadata["bounded_partner_consumer_executed"])
                self.assertTrue(metadata["async_partner_continuation_authorized"])
                self.assertEqual(
                    metadata["async_partner_continuation_authorization_scope"],
                    "bounded_same_stream_status_consumer_only",
                )
                self.assertFalse(metadata["general_partner_continuation_authorized"])
                self.assertIn("stream must remain valid", metadata["stream_lifetime_contract"])
                self.assertFalse(metadata["true_zero_copy_authorized"])
                self.assertFalse(metadata["public_speedup_claim_authorized"])
            finally:
                buffers.close()

    def test_runtime_smoke_reports_overflow_through_device_status(self) -> None:
        if not os.environ.get("RTDL_OPTIX_LIBRARY") and not (ROOT / "build/librtdl_optix.so").exists():
            self.skipTest("OptiX backend library is not configured")
        try:
            import cupy  # noqa: F401
            import torch
        except Exception as exc:  # pragma: no cover - local non-CUDA hosts skip here.
            self.skipTest(f"CUDA partner dependencies unavailable: {exc}")
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
            buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(0)
            try:
                result = scene.ray_triangle_hit_stream_same_stream_status_summary(
                    (ray,),
                    buffers,
                    max_rows=0,
                )
                summary = result["summary"]
                metadata = result["metadata"]

                self.assertEqual(summary["row_count"], 1)
                self.assertEqual(summary["hit_event_count"], 1)
                self.assertTrue(summary["overflow"])
                self.assertEqual(summary["bounded_row_count"], 0)
                self.assertIsNone(summary["first_ray_id"])
                self.assertIsNone(summary["first_primitive_id"])
                self.assertFalse(summary["status_ok"])
                self.assertFalse(summary["host_scalar_read_before_consumer"])
                self.assertEqual(metadata["producer_consumer_stream_ordering"], "same_stream")
                self.assertFalse(metadata["producer_host_synchronization_used"])
                self.assertFalse(metadata["true_zero_copy_authorized"])
            finally:
                buffers.close()


if __name__ == "__main__":
    unittest.main()
