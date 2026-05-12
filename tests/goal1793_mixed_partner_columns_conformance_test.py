from __future__ import annotations

import importlib.util
import unittest

import rtdsl as rt


def _numpy_columns():
    import numpy as np

    rays = {
        "ids": np.asarray([0, 1], dtype=np.uint32),
        "ox": np.asarray([-0.25, 2.0], dtype=np.float64),
        "oy": np.asarray([0.25, 2.0], dtype=np.float64),
        "dx": np.asarray([1.0, 1.0], dtype=np.float64),
        "dy": np.asarray([0.0, 0.0], dtype=np.float64),
        "tmax": np.asarray([2.0, 2.0], dtype=np.float64),
    }
    triangles = {
        "ids": np.asarray([0], dtype=np.uint32),
        "x0": np.asarray([0.0], dtype=np.float64),
        "y0": np.asarray([0.0], dtype=np.float64),
        "x1": np.asarray([1.0], dtype=np.float64),
        "y1": np.asarray([0.0], dtype=np.float64),
        "x2": np.asarray([0.0], dtype=np.float64),
        "y2": np.asarray([1.0], dtype=np.float64),
    }
    return rays, triangles


class Goal1793MixedPartnerColumnsConformanceTest(unittest.TestCase):
    def setUp(self) -> None:
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("NumPy is required for partner host staging")

    def test_numpy_and_cupy_columns_can_mix_at_pack_boundary_when_cupy_available(self) -> None:
        if importlib.util.find_spec("cupy") is None:
            self.skipTest("CuPy is not installed in this dev environment")
        import cupy

        try:
            if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
                self.skipTest("CuPy is installed, but no CUDA devices are visible")
        except Exception as exc:
            self.skipTest(f"CuPy CUDA device query failed: {type(exc).__name__}: {exc}")

        rays, triangles_np = _numpy_columns()
        triangles = {name: cupy.asarray(value) for name, value in triangles_np.items()}
        packed = rt.pack_optix_ray_triangle_any_hit_2d_partner_inputs(rays, triangles)

        self.assertEqual(packed["metadata"]["source_protocols"], ("cupy", "numpy"))
        self.assertEqual(packed["metadata"]["source_devices"], ("cpu:0", "cuda:0"))
        self.assertEqual(packed["metadata"]["transfer_mode"], "host_stage")
        self.assertFalse(packed["metadata"]["true_zero_copy_authorized"])
        self.assertEqual(packed["rays"].count, 2)
        self.assertEqual(packed["triangles"].count, 1)

    def test_torch_and_numpy_columns_can_mix_at_execution_boundary_when_available(self) -> None:
        if importlib.util.find_spec("torch") is None:
            self.skipTest("PyTorch is not installed in this dev environment")
        import torch

        if not torch.cuda.is_available():
            self.skipTest("PyTorch CUDA is not available in this dev environment")

        rays_np, triangles = _numpy_columns()
        rays = {name: torch.as_tensor(value, device="cuda:0") for name, value in rays_np.items()}
        try:
            result = rt.run_optix_partner_ray_triangle_any_hit_2d(rays, triangles)
        except (OSError, RuntimeError) as exc:
            self.skipTest(f"OptiX backend is not available in this environment: {exc}")

        self.assertEqual(result["source_protocols"], ("numpy", "torch"))
        self.assertEqual(result["source_devices"], ("cpu:0", "cuda:0"))
        self.assertEqual(result["hit_count"], 1)
        self.assertEqual(result["transfer_mode"], "host_stage")
        self.assertFalse(result["rt_core_speedup_claim_authorized"])
        self.assertIn("partner_phase_timings_s", result)


if __name__ == "__main__":
    unittest.main()
