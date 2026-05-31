from __future__ import annotations

import os
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
HIT_STREAM_HANDOFF = ROOT / "src/rtdsl/hit_stream_handoff.py"
REPORT = ROOT / "docs/reports/goal2756_reusable_hit_stream_device_output_buffers_2026-05-31.md"


class Goal2756ReusableHitStreamDeviceOutputBuffersTest(unittest.TestCase):
    def test_native_abi_accepts_caller_owned_output_device_columns(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        symbol = "rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns"
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn("uint64_t ray_ids_device_ptr", prelude)
        self.assertIn("uint64_t primitive_ids_device_ptr", prelude)
        self.assertIn("run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_optix", api)
        self.assertIn("run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_impl_optix", workloads)
        self.assertIn("caller_owned_output && max_rows != 0", workloads)
        self.assertIn("caller-owned hit-stream output columns require nonzero device pointers", workloads)
        self.assertIn("columns_out->owner_handle = owner.release();", workloads)
        self.assertIn("if (!caller_owned_output && owner)", workloads)

    def test_python_runtime_exposes_reusable_buffer_path_and_metadata(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        handoff = HIT_STREAM_HANDOFF.read_text(encoding="utf-8")

        self.assertIn("OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_INTO_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertIn("PreparedOptixHitStreamDeviceColumnBuffers", runtime)
        self.assertIn("prepare_ray_triangle_hit_stream_device_column_buffers", runtime)
        self.assertIn("ray_triangle_hit_stream_into_device_columns", runtime)
        self.assertIn("prepare_generic_device_resident_hit_stream_columns", runtime)
        self.assertIn("caller_owned_output_buffers=True", runtime)
        self.assertIn("reusable_output_buffers_used=True", runtime)
        self.assertIn('producer_consumer_stream_ordering="host_synchronized_before_consumer"', runtime)
        self.assertIn('"true_zero_copy_authorized": False', handoff)
        self.assertIn('"caller_owned_output_buffers"', handoff)
        self.assertIn('"reusable_output_buffers_used"', handoff)

    def test_report_records_claim_boundary_and_pod_artifact(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("goal2756_reusable_hit_stream_device_output_buffers_69_30_85_171_2026-05-31.json", report)
        self.assertIn("pointer_identity_preserved", report)
        self.assertIn("host_synchronization_used", report)
        self.assertIn("true_zero_copy_authorized", report)
        self.assertIn("This goal does not authorize", report)
        self.assertIn("public speedup claims", report)

    def test_static_path_does_not_add_app_shaped_native_names(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (PRELUDE, API, WORKLOADS, OPTIX_RUNTIME, HIT_STREAM_HANDOFF)
        )
        snippets = "\n".join(
            line
            for line in text.splitlines()
            if "hit_stream" in line or "HitStream" in line or "caller_owned_output" in line
        )
        for forbidden in ("raydb", "sql", "database", "dbscan", "rayjoin", "hausdorff"):
            self.assertNotIn(forbidden, snippets.lower())

    def test_runtime_smoke_reuses_caller_owned_cuda_tensors_when_optix_available(self) -> None:
        if not os.environ.get("RTDL_OPTIX_LIBRARY") and not (ROOT / "build/librtdl_optix.so").exists():
            self.skipTest("OptiX backend library is not configured")
        try:
            import torch
        except Exception as exc:  # pragma: no cover - local non-CUDA hosts skip here.
            self.skipTest(f"torch unavailable: {exc}")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        import rtdsl as rt
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
        ray = Ray3D(id=7, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0)

        with rt.prepare_optix_static_triangle_scene_3d((triangle,)) as scene:
            buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(4)
            try:
                handoff = scene.ray_triangle_hit_stream_into_device_columns((ray,), buffers)
                self.assertEqual(handoff.row_count, 1)
                self.assertFalse(handoff.overflow)
                self.assertIs(handoff.owner, buffers)
                self.assertEqual(handoff.ray_ids.data_ptr(), buffers.ray_ids.data_ptr())
                self.assertEqual(handoff.primitive_ids.data_ptr(), buffers.primitive_ids.data_ptr())
                self.assertEqual(handoff.ray_ids.cpu().tolist(), [7])
                self.assertEqual(handoff.primitive_ids.cpu().tolist(), [0])
                metadata = handoff.to_metadata()
                self.assertTrue(metadata["caller_owned_output_buffers"])
                self.assertTrue(metadata["reusable_output_buffers_used"])
                self.assertEqual(metadata["neutral_buffer_seams"][0]["lifetime_state"], "caller_retained")
                self.assertFalse(metadata["neutral_buffer_seams"][0]["native_producer"])
                self.assertTrue(metadata["host_synchronization_used"])
                self.assertFalse(metadata["true_zero_copy_authorized"])
            finally:
                buffers.close()


if __name__ == "__main__":
    unittest.main()
