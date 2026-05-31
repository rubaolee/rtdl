from __future__ import annotations

import os
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2769_hit_stream_same_stream_row_reduction_consumer_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2769_gemini_review_hit_stream_row_reduction_consumer_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2769_hit_stream_same_stream_row_reduction_consumer_consensus_2026-05-31.md"


class Goal2769HitStreamSameStreamRowReductionConsumerTest(unittest.TestCase):
    def test_cupy_kernel_reduces_all_stored_rows_on_device(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        source_start = runtime.index("_HIT_STREAM_SAME_STREAM_ROW_REDUCTION_SUMMARY_CUPY_SOURCE")
        source_end = runtime.index("@functools.lru_cache", source_start)
        source = runtime[source_start:source_end]

        self.assertIn("rtdl_hit_stream_same_stream_row_reduction_summary_u64", source)
        self.assertIn("const unsigned long long observed_rows = row_count[0]", source)
        self.assertIn("const unsigned long long stored_rows", source)
        self.assertIn("i < stored_rows", source)
        self.assertIn("ray_ids[i]", source)
        self.assertIn("primitive_ids[i]", source)
        self.assertIn("atomicAdd(&summary[4], ray)", source)
        self.assertIn("atomicAdd(&summary[5], primitive)", source)
        self.assertIn("atomicXor(&summary[6], ray)", source)
        self.assertIn("atomicMin(&summary[8], ray)", source)
        self.assertIn("atomicMax(&summary[9], ray)", source)

    def test_python_helper_uses_external_stream_and_no_row_materialization(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        helper_start = runtime.index("def _run_hit_stream_same_stream_row_reduction_summary_cupy")
        helper_end = runtime.index("class PreparedOptixHitStreamDeviceColumnBuffers", helper_start)
        helper = runtime[helper_start:helper_end]

        self.assertIn("cp.cuda.ExternalStream", helper)
        self.assertIn("with external_stream:", helper)
        self.assertIn("cp.asarray(output_buffers.ray_ids)", helper)
        self.assertIn("cp.asarray(output_buffers.primitive_ids)", helper)
        self.assertIn("cp.asarray(output_buffers.row_count)", helper)
        self.assertIn("(256,)", helper)
        self.assertLess(helper.index("kernel("), helper.index("external_stream.synchronize()"))
        self.assertLess(helper.index("kernel("), helper.index("cp.asnumpy(summary)"))
        self.assertNotIn("cp.asnumpy(output_buffers.ray_ids)", helper)
        self.assertNotIn("cp.asnumpy(output_buffers.primitive_ids)", helper)

    def test_public_method_records_reduction_boundary(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        method_start = runtime.index("def ray_triangle_hit_stream_same_stream_row_reduction_summary")
        method_end = runtime.index("def ray_triangle_prepared_primitive_grouped_i64_reduction", method_start)
        method = runtime[method_start:method_end]

        self.assertIn("bounded_same_stream_row_reduction_consumer_only", method)
        self.assertIn('"device_resident_row_reduction_for_partner": True', method)
        self.assertIn('"host_row_materialization_before_consumer": False', method)
        self.assertIn('"host_scalar_read_before_consumer": False', method)
        self.assertIn('"query_rays_still_packed_on_host": True', method)
        self.assertIn('"true_zero_copy_authorized": False', method)
        self.assertIn('"public_speedup_claim_authorized": False', method)

    def test_report_records_scope_and_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("all stored hit rows", report)
        self.assertIn("row reduction", report)
        self.assertIn("same CUDA stream", report)
        self.assertIn("does not authorize true zero-copy", report)
        self.assertIn("does not authorize public speedup claims", report)

    def test_external_review_and_consensus_recorded(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict", review)
        self.assertIn("accept", review)
        self.assertIn("independent Gemini review", review)
        self.assertIn("row reduction", consensus)
        self.assertIn("Codex + Gemini consensus accepts Goal2769 with boundary", consensus)
        self.assertIn("bounded_same_stream_row_reduction_consumer_only", consensus)
        self.assertIn("not an unbounded stream", consensus)

    def test_runtime_smoke_reduces_two_hit_rows_before_materialization(self) -> None:
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

        triangles = (
            Triangle3D(
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
            ),
            Triangle3D(
                id=1,
                x0=0.0,
                y0=0.0,
                z0=1.0,
                x1=1.0,
                y1=0.0,
                z1=1.0,
                x2=0.0,
                y2=1.0,
                z2=1.0,
            ),
        )
        ray = Ray3D(id=11, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0)

        with rt.prepare_optix_static_triangle_scene_3d(triangles) as scene:
            buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(4)
            try:
                result = scene.ray_triangle_hit_stream_same_stream_row_reduction_summary((ray,), buffers)
                summary = result["summary"]
                self.assertEqual(summary["row_count"], 2)
                self.assertEqual(summary["stored_row_count"], 2)
                self.assertEqual(summary["ray_id_sum_mod_u64"], 22)
                self.assertEqual(summary["primitive_id_sum_mod_u64"], 1)
                self.assertEqual(summary["ray_id_xor"], 0)
                self.assertEqual(summary["primitive_id_xor"], 1)
                self.assertEqual(summary["min_ray_id"], 11)
                self.assertEqual(summary["max_ray_id"], 11)
                self.assertEqual(summary["min_primitive_id"], 0)
                self.assertEqual(summary["max_primitive_id"], 1)
                self.assertTrue(summary["status_ok"])
                metadata = result["metadata"]
                self.assertEqual(
                    metadata["async_partner_continuation_authorization_scope"],
                    "bounded_same_stream_row_reduction_consumer_only",
                )
                self.assertFalse(metadata["host_scalar_read_before_consumer"])
                self.assertFalse(metadata["host_row_materialization_before_consumer"])
                self.assertTrue(metadata["device_resident_row_reduction_for_partner"])
                self.assertFalse(metadata["true_zero_copy_authorized"])
            finally:
                buffers.close()


if __name__ == "__main__":
    unittest.main()
