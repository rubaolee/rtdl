from __future__ import annotations

import os
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ROW_BUFFER = ROOT / "src" / "rtdsl" / "device_column_row_buffer.py"


def _optix_cuda_available() -> bool:
    if not os.environ.get("RTDL_OPTIX_LIBRARY") and not (ROOT / "build/librtdl_optix.so").exists():
        return False
    try:
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class Goal4948NonRayJoinHitStreamNumbaGenericityTest(unittest.TestCase):
    def test_hit_stream_row_buffer_adapter_is_generic(self) -> None:
        source = ROW_BUFFER.read_text(encoding="utf-8")
        start = source.index("def device_column_row_buffer_from_hit_stream_handoff(")
        end = source.index("def device_column_row_buffer_from_native_pair_columns(", start)
        body = source[start:end].lower()

        self.assertIn('"ray_ids"', body)
        self.assertIn('"primitive_ids"', body)
        self.assertIn("source_mode=hit_stream_columns.source_mode", body)
        self.assertIn("materializes_host_rows_for_bridge=hit_stream_columns.materializes_host_rows_for_bridge", body)
        for forbidden in ("rayjoin", "polygon", "overlay", "output_chain", "authorofficial"):
            self.assertNotIn(forbidden, body)

    def test_ray_triangle_hit_stream_device_columns_execute_numba_when_available(self) -> None:
        if not _optix_cuda_available():
            self.skipTest("OptiX + Numba CUDA runtime is not available")
        from rtdsl.reference import Ray3D, Triangle3D

        triangles = (
            Triangle3D(0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
            Triangle3D(1, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0),
            Triangle3D(2, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0, 2.0, 1.0, 0.0),
        )
        rays = (
            Ray3D(0, 0.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
            Ray3D(1, 2.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
            Ray3D(2, 10.0, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
        )

        with rt.prepare_optix_static_triangle_scene_3d(triangles) as scene:
            hit_columns = scene.ray_triangle_hit_stream_device_columns(
                rays,
                max_rows=8,
                deduplicate_primitives=False,
            )
            row_buffer = rt.device_column_row_buffer_from_hit_stream_handoff(
                hit_columns,
                producer="goal4948_ray_triangle_hit_stream",
            )
            result = rt.run_numba_segmented_count_i64(
                row_buffer.columns["ray_ids"],
                group_count=len(rays),
                validate_group_ids=True,
            )

        self.assertEqual(row_buffer.row_count, 3)
        self.assertTrue(row_buffer.device_resident_candidate)
        self.assertFalse(row_buffer.materializes_host_rows_for_bridge)
        self.assertEqual(result["outputs"]["counts"].copy_to_host().tolist(), [2, 1, 0])
        self.assertFalse(result["promoted_performance_path"])
        self.assertFalse(result["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
