from __future__ import annotations

import os
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src/native/optix/rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2767_hit_stream_async_input_upload_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2767_gemini_review_hit_stream_async_input_upload_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2767_hit_stream_async_input_upload_consensus_2026-05-31.md"


class Goal2767HitStreamAsyncInputUploadTest(unittest.TestCase):
    def test_core_exposes_stream_ordered_upload_helper(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("void upload_async", core)
        self.assertIn("cuMemcpyHtoDAsync", core)
        self.assertIn("CUstream stream", core)

    def test_async_launch_owner_preserves_pinned_host_staging(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        owner_start = workloads.index("struct NativeRayTriangleHitStreamAsyncLaunchOwner")
        owner_end = workloads.index("struct RayAnyHitGroupFlags3DLaunchParams", owner_start)
        owner = workloads[owner_start:owner_end]

        self.assertIn("void* host_rays", owner)
        self.assertIn("void* host_params", owner)
        self.assertIn("cuMemFreeHost(host_params)", owner)
        self.assertIn("cuMemFreeHost(host_rays)", owner)
        self.assertLess(owner.index("cuStreamSynchronize(producer_stream)"), owner.index("cuMemFreeHost(host_params)"))

    def test_on_stream_path_uses_async_h2d_for_rays_and_params(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        function_start = workloads.index(
            "run_prepared_static_triangle_scene_3d_"
            "ray_triangle_hit_stream_into_device_columns_with_status_on_stream_optix"
        )
        function_end = workloads.index(
            "static void release_ray_triangle_hit_stream_device_columns_optix",
            function_start,
        )
        function = workloads[function_start:function_end]

        self.assertIn("cuMemAllocHost(&owner->host_rays", function)
        self.assertIn("cuMemAllocHost(&owner->host_params", function)
        self.assertIn("std::memcpy(owner->host_rays", function)
        self.assertIn("std::memcpy(owner->host_params", function)
        self.assertIn("upload_async(owner->rays", function)
        self.assertIn("upload_async(\n        owner->params", function)
        self.assertNotIn("upload(owner->rays", function)
        self.assertNotIn("upload(owner->params", function)
        self.assertNotIn("cuStreamSynchronize(stream)", function)
        self.assertNotIn("download(", function)

    def test_python_metadata_records_async_input_upload_boundary(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn('"producer_input_upload_mode": "stream_ordered_pinned_host_to_device_async"', runtime)
        self.assertIn('"producer_input_upload_host_blocking_cuda_copy": False', runtime)
        self.assertIn('"query_rays_still_packed_on_host": True', runtime)
        self.assertIn('"true_zero_copy_authorized": False', runtime)
        self.assertIn('"public_speedup_claim_authorized": False', runtime)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("pinned host staging", report)
        self.assertIn("cuMemcpyHtoDAsync", report)
        self.assertIn("stream-ordered", report)
        self.assertIn("does not authorize true zero-copy", report)
        self.assertIn("does not authorize public speedup claims", report)

    def test_external_review_and_consensus_recorded(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict: accept-with-boundary", review)
        self.assertIn("independent Gemini review", review)
        self.assertIn("Pinned Host Staging Lifetime", review)
        self.assertIn("query_rays_still_packed_on_host = True", review)
        self.assertIn("Codex + Gemini consensus accepts Goal2767 with boundary", consensus)
        self.assertIn("same_stream_hit_stream_input_upload", consensus)
        self.assertIn("not true zero-copy", consensus)

    def test_runtime_smoke_still_executes_same_stream_consumer(self) -> None:
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
                self.assertEqual(result["summary"]["row_count"], 1)
                self.assertEqual(result["summary"]["first_ray_id"], 11)
                metadata = result["metadata"]
                self.assertEqual(
                    metadata["producer_input_upload_mode"],
                    "stream_ordered_pinned_host_to_device_async",
                )
                self.assertFalse(metadata["producer_input_upload_host_blocking_cuda_copy"])
                self.assertTrue(metadata["query_rays_still_packed_on_host"])
                self.assertFalse(metadata["true_zero_copy_authorized"])
            finally:
                buffers.close()


if __name__ == "__main__":
    unittest.main()
