from __future__ import annotations

import os
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2771_gemini_review_hit_stream_event_ordered_grouped_reduction_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_consensus_2026-05-31.md"


class Goal2771HitStreamEventOrderedGroupedReductionConsumerTest(unittest.TestCase):
    def test_grouped_kernel_reduces_by_generic_ray_id_columns(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        source_start = runtime.index("_HIT_STREAM_EVENT_ORDERED_GROUPED_RAY_ID_REDUCTION_CUPY_SOURCE")
        source_end = runtime.index("@functools.lru_cache(maxsize=1)", source_start)
        source = runtime[source_start:source_end]

        self.assertIn("rtdl_hit_stream_event_ordered_grouped_ray_id_reduction_u64", source)
        self.assertIn("const long long* ray_ids", source)
        self.assertIn("const long long* primitive_ids", source)
        self.assertIn("group_hit_counts[g] = 0ull", source)
        self.assertIn("group_primitive_id_sum[g] = 0ull", source)
        self.assertIn("group_primitive_id_xor[g] = 0ull", source)
        self.assertIn("const long long group_id_signed = ray_ids[i]", source)
        self.assertIn("group_id_signed < 0ll", source)
        self.assertIn("group_id >= group_count", source)
        self.assertIn("atomicAdd(&group_hit_counts[group_id], 1ull)", source)
        self.assertIn("atomicAdd(&group_primitive_id_sum[group_id], primitive)", source)
        self.assertIn("atomicXor(&group_primitive_id_xor[group_id], primitive)", source)
        self.assertIn("atomicAdd(&summary[6], 1ull)", source)
        self.assertIn("atomicAdd(&summary[7], count)", source)

    def test_cupy_helper_waits_on_event_before_grouped_kernel(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        helper_start = runtime.index("def _run_hit_stream_event_ordered_grouped_ray_id_reduction_cupy")
        helper_end = runtime.index("class PreparedOptixHitStreamDeviceColumnBuffers", helper_start)
        helper = runtime[helper_start:helper_end]

        self.assertIn("cp.cuda.Stream(non_blocking=True)", helper)
        self.assertIn("streamWaitEvent", helper)
        self.assertIn("producer_event_ptr", helper)
        self.assertIn("cp.asarray(hit_buffers.ray_ids)", helper)
        self.assertIn("cp.asarray(hit_buffers.primitive_ids)", helper)
        self.assertIn("cp.asarray(group_buffers.group_hit_counts)", helper)
        self.assertIn("cp.asarray(group_buffers.group_primitive_id_sum)", helper)
        self.assertIn("cp.asarray(group_buffers.group_primitive_id_xor)", helper)
        self.assertIn("kernel(", helper)
        launch_index = helper.index("kernel(\n", helper.index("streamWaitEvent"))
        self.assertLess(helper.index("streamWaitEvent"), launch_index)
        self.assertLess(launch_index, helper.index("consumer_stream.synchronize()"))
        self.assertLess(launch_index, helper.index("cp.asnumpy(summary)"))
        self.assertNotIn("cp.asnumpy(hit_buffers.ray_ids)", helper)
        self.assertNotIn("cp.asnumpy(hit_buffers.primitive_ids)", helper)
        self.assertNotIn("cp.asnumpy(group_buffers.group_hit_counts)", helper)

    def test_public_method_records_grouped_event_ordering_boundary(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        method_start = runtime.index("def ray_triangle_hit_stream_event_ordered_grouped_ray_id_reduction")
        method_end = runtime.index("def ray_triangle_prepared_primitive_grouped_i64_reduction", method_start)
        method = runtime[method_start:method_end]

        self.assertIn("torch.cuda.Event(blocking=False)", method)
        self.assertIn("producer_event.record(producer_stream)", method)
        self.assertIn("producer_event.cuda_event", method)
        self.assertIn("bounded_event_ordered_grouped_ray_id_reduction_consumer_only", method)
        self.assertIn('"producer_consumer_stream_ordering": "cuda_event_cross_stream"', method)
        self.assertIn('"cuda_event_cross_stream_ordering_proven": True', method)
        self.assertIn('"cuda_event_wait_inserted_before_consumer": True', method)
        self.assertIn('"device_resident_grouped_reduction_for_partner": True', method)
        self.assertIn('"grouping_key": "ray_id"', method)
        self.assertIn('"grouped_output_columns_written_on_device": True', method)
        self.assertIn('"host_scalar_read_before_consumer": False', method)
        self.assertIn('"host_row_materialization_before_consumer": False', method)
        self.assertIn('"query_rays_still_packed_on_host": True', method)
        self.assertIn('"true_zero_copy_authorized": False', method)
        self.assertIn('"public_speedup_claim_authorized": False', method)

    def test_report_records_scope_and_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("grouped reduction", report)
        self.assertIn("ray_id", report)
        self.assertIn("CUDA event", report)
        self.assertIn("cross-stream", report)
        self.assertIn("does not authorize true zero-copy", report)
        self.assertIn("does not authorize public speedup claims", report)

    def test_external_review_and_consensus_recorded(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict", review)
        self.assertIn("Gemini Review", review)
        self.assertIn("grouped", review)
        self.assertIn("ray_id", review)
        self.assertIn("Codex + Gemini consensus accepts Goal2771", consensus)
        self.assertIn("bounded_event_ordered_grouped_ray_id_reduction_consumer_only", consensus)
        self.assertIn("not an unbounded stream", consensus)

    def test_runtime_smoke_event_ordered_grouped_reduction(self) -> None:
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
        rays = (
            Ray3D(id=0, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0),
            Ray3D(id=1, ox=2.0, oy=2.0, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0),
            Ray3D(id=2, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0),
        )

        with rt.prepare_optix_static_triangle_scene_3d(triangles) as scene:
            hit_buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(8)
            group_buffers = scene.prepare_ray_triangle_hit_stream_grouped_reduction_buffers(3)
            try:
                result = scene.ray_triangle_hit_stream_event_ordered_grouped_ray_id_reduction(
                    rays,
                    hit_buffers,
                    group_buffers,
                    deduplicate_primitives=False,
                )
                summary = result["summary"]
                self.assertEqual(summary["row_count"], 4)
                self.assertEqual(summary["stored_row_count"], 4)
                self.assertEqual(summary["hit_event_count"], 4)
                self.assertEqual(summary["invalid_group_id_row_count"], 0)
                self.assertEqual(summary["populated_group_count"], 2)
                self.assertEqual(summary["valid_group_reduced_row_count"], 4)
                self.assertTrue(summary["grouped_output_columns_written_on_device"])
                self.assertTrue(summary["cuda_event_wait_inserted_before_consumer"])
                self.assertTrue(summary["status_ok"])
                self.assertEqual(group_buffers.group_hit_counts.cpu().tolist(), [2, 0, 2])
                self.assertEqual(group_buffers.group_primitive_id_sum.cpu().tolist(), [1, 0, 1])
                self.assertEqual(group_buffers.group_primitive_id_xor.cpu().tolist(), [1, 0, 1])

                metadata = result["metadata"]
                self.assertEqual(metadata["producer_consumer_stream_ordering"], "cuda_event_cross_stream")
                self.assertEqual(metadata["grouping_key"], "ray_id")
                self.assertEqual(
                    metadata["async_partner_continuation_authorization_scope"],
                    "bounded_event_ordered_grouped_ray_id_reduction_consumer_only",
                )
                self.assertTrue(metadata["cuda_event_cross_stream_ordering_proven"])
                self.assertTrue(metadata["cuda_event_wait_inserted_before_consumer"])
                self.assertTrue(metadata["producer_cuda_event_ptr_nonzero"])
                self.assertTrue(metadata["producer_cuda_stream_ptr_nonzero"])
                self.assertTrue(metadata["consumer_cuda_stream_ptr_nonzero"])
                self.assertTrue(metadata["device_resident_grouped_reduction_for_partner"])
                self.assertFalse(metadata["host_scalar_read_before_consumer"])
                self.assertFalse(metadata["host_row_materialization_before_consumer"])
                self.assertFalse(metadata["true_zero_copy_authorized"])
            finally:
                group_buffers.close()
                hit_buffers.close()


if __name__ == "__main__":
    unittest.main()
