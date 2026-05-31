from __future__ import annotations

import os
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2772_gemini_review_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_consensus_2026-05-31.md"


class Goal2772HitStreamEventOrderedGroupedRicherReductionsTest(unittest.TestCase):
    def test_grouped_kernel_adds_min_max_first_last_fields(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        source_start = runtime.index("_HIT_STREAM_EVENT_ORDERED_GROUPED_RAY_ID_REDUCTION_CUPY_SOURCE")
        source_end = runtime.index("@functools.lru_cache(maxsize=1)", source_start)
        source = runtime[source_start:source_end]

        self.assertIn("group_primitive_id_min[g] = missing", source)
        self.assertIn("group_primitive_id_max[g] = 0ull", source)
        self.assertIn("group_first_hit_row_index[g] = missing", source)
        self.assertIn("group_last_hit_row_index[g] = 0ull", source)
        self.assertIn("group_first_primitive_id[g] = missing", source)
        self.assertIn("group_last_primitive_id[g] = missing", source)
        self.assertIn("atomicMin(&group_primitive_id_min[group_id], primitive)", source)
        self.assertIn("atomicMax(&group_primitive_id_max[group_id], primitive)", source)
        self.assertIn("atomicMin(&group_first_hit_row_index[group_id], i)", source)
        self.assertIn("atomicMax(&group_last_hit_row_index[group_id], i)", source)
        self.assertIn("i == group_first_hit_row_index[group_id]", source)
        self.assertIn("i == group_last_hit_row_index[group_id]", source)
        self.assertIn("group_primitive_id_max[g] = missing", source)

    def test_group_buffers_expose_richer_generic_output_columns(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        cls_start = runtime.index("class PreparedOptixHitStreamGroupedReductionBuffers")
        cls_end = runtime.index("class PreparedOptixStaticTriangleScene3D", cls_start)
        cls = runtime[cls_start:cls_end]

        for name in (
            "group_hit_counts",
            "group_primitive_id_sum",
            "group_primitive_id_xor",
            "group_primitive_id_min",
            "group_primitive_id_max",
            "group_first_hit_row_index",
            "group_last_hit_row_index",
            "group_first_primitive_id",
            "group_last_primitive_id",
        ):
            self.assertIn(f"self.{name}", cls)
            self.assertIn(f"self.{name} = None", cls)

    def test_helper_keeps_richer_outputs_device_resident_until_consumer_finishes(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        helper_start = runtime.index("def _run_hit_stream_event_ordered_grouped_ray_id_reduction_cupy")
        helper_end = runtime.index("class PreparedOptixHitStreamDeviceColumnBuffers", helper_start)
        helper = runtime[helper_start:helper_end]

        for name in (
            "group_primitive_id_min",
            "group_primitive_id_max",
            "group_first_hit_row_index",
            "group_last_hit_row_index",
            "group_first_primitive_id",
            "group_last_primitive_id",
        ):
            self.assertIn(f"cp.asarray(group_buffers.{name})", helper)
            self.assertNotIn(f"cp.asnumpy(group_buffers.{name})", helper)
        self.assertIn("streamWaitEvent", helper)
        self.assertIn("grouped_reduction_fields", helper)
        launch_index = helper.index("kernel(\n", helper.index("streamWaitEvent"))
        self.assertLess(helper.index("streamWaitEvent"), launch_index)
        self.assertLess(launch_index, helper.index("consumer_stream.synchronize()"))

    def test_public_method_records_richer_reduction_fields(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        method_start = runtime.index("def ray_triangle_hit_stream_event_ordered_grouped_ray_id_reduction")
        method_end = runtime.index("def ray_triangle_prepared_primitive_grouped_i64_reduction", method_start)
        method = runtime[method_start:method_end]

        self.assertIn('"grouped_reduction_fields": (', method)
        self.assertIn('"primitive_id_min"', method)
        self.assertIn('"primitive_id_max"', method)
        self.assertIn('"first_hit_row_index"', method)
        self.assertIn('"last_hit_row_index"', method)
        self.assertIn('"first_primitive_id_by_row_order"', method)
        self.assertIn('"last_primitive_id_by_row_order"', method)
        self.assertIn('"grouping_key": "ray_id"', method)
        self.assertIn("bounded_event_ordered_grouped_ray_id_reduction_consumer_only", method)
        self.assertIn('"true_zero_copy_authorized": False', method)
        self.assertIn('"public_speedup_claim_authorized": False', method)

    def test_report_records_richer_reduction_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("min/max", report)
        self.assertIn("first/last", report)
        self.assertIn("ray_id", report)
        self.assertIn("CUDA event", report)
        self.assertIn("does not authorize true zero-copy", report)
        self.assertIn("does not authorize public speedup claims", report)

    def test_external_review_and_consensus_recorded(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict", review)
        self.assertIn("Gemini", review)
        self.assertIn("min/max", review)
        self.assertIn("first/last", review)
        self.assertIn("Codex + Gemini consensus accepts Goal2772", consensus)
        self.assertIn("bounded_event_ordered_grouped_ray_id_reduction_consumer_only", consensus)
        self.assertIn("not an unbounded stream", consensus)

    def test_runtime_smoke_richer_grouped_reductions(self) -> None:
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
                self.assertEqual(summary["grouped_reduction_fields"][3:], (
                    "primitive_id_min",
                    "primitive_id_max",
                    "first_hit_row_index",
                    "last_hit_row_index",
                    "first_primitive_id_by_row_order",
                    "last_primitive_id_by_row_order",
                ))
                self.assertEqual(group_buffers.group_hit_counts.cpu().tolist(), [2, 0, 2])
                self.assertEqual(group_buffers.group_primitive_id_min.cpu().tolist(), [0, -1, 0])
                self.assertEqual(group_buffers.group_primitive_id_max.cpu().tolist(), [1, -1, 1])
                self.assertEqual(group_buffers.group_first_hit_row_index.cpu().tolist(), [0, -1, 1])
                self.assertEqual(group_buffers.group_last_hit_row_index.cpu().tolist(), [2, -1, 3])
                self.assertEqual(group_buffers.group_first_primitive_id.cpu().tolist(), [0, -1, 0])
                self.assertEqual(group_buffers.group_last_primitive_id.cpu().tolist(), [1, -1, 1])
                metadata = result["metadata"]
                self.assertEqual(metadata["grouping_key"], "ray_id")
                self.assertIn("primitive_id_min", metadata["grouped_reduction_fields"])
                self.assertIn("last_primitive_id_by_row_order", metadata["grouped_reduction_fields"])
                self.assertFalse(metadata["true_zero_copy_authorized"])
                self.assertFalse(metadata["public_speedup_claim_authorized"])
            finally:
                group_buffers.close()
                hit_buffers.close()


if __name__ == "__main__":
    unittest.main()
