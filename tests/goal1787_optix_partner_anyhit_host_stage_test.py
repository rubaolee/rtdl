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


def _torch_columns(device: str = "cuda:0"):
    import torch

    rays_np, triangles_np = _numpy_columns()
    rays = {
        name: torch.as_tensor(value, device=device)
        for name, value in rays_np.items()
    }
    triangles = {
        name: torch.as_tensor(value, device=device)
        for name, value in triangles_np.items()
    }
    return rays, triangles


def _cupy_columns():
    import cupy

    rays_np, triangles_np = _numpy_columns()
    rays = {name: cupy.asarray(value) for name, value in rays_np.items()}
    triangles = {name: cupy.asarray(value) for name, value in triangles_np.items()}
    return rays, triangles


class Goal1787OptixPartnerAnyHitHostStageTest(unittest.TestCase):
    def setUp(self) -> None:
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("NumPy is required for partner host staging")

    def test_partner_pack_metadata_for_numpy_columns_is_host_stage(self) -> None:
        rays, triangles = _numpy_columns()
        packed = rt.pack_optix_ray_triangle_any_hit_2d_partner_inputs(rays, triangles)
        self.assertEqual(packed["rays"].count, 2)
        self.assertEqual(packed["triangles"].count, 1)
        self.assertEqual(packed["metadata"]["transfer_mode"], "host_stage")
        self.assertEqual(packed["metadata"]["source_protocols"], ("numpy",))
        self.assertEqual(packed["metadata"]["source_devices"], ("cpu:0",))
        self.assertFalse(packed["metadata"]["true_zero_copy_authorized"])
        self.assertTrue(packed["metadata"]["partner_tensor_handoff_authorized"])
        self.assertFalse(packed["metadata"]["rt_core_speedup_claim_authorized"])

    def test_partner_pack_rejects_missing_and_rank_two_columns(self) -> None:
        import numpy as np

        rays, triangles = _numpy_columns()
        del rays["tmax"]
        with self.assertRaisesRegex(ValueError, "missing rays partner columns"):
            rt.pack_optix_ray_triangle_any_hit_2d_partner_inputs(rays, triangles)

        rays, triangles = _numpy_columns()
        rays["ox"] = np.asarray([[0.0, 1.0]], dtype=np.float64)
        with self.assertRaisesRegex(ValueError, "one-dimensional"):
            rt.pack_optix_ray_triangle_any_hit_2d_partner_inputs(rays, triangles)

    def test_partner_optix_anyhit_executes_when_backend_available(self) -> None:
        rays, triangles = _numpy_columns()
        try:
            result = rt.run_optix_partner_ray_triangle_any_hit_2d(rays, triangles)
        except (OSError, RuntimeError) as exc:
            self.skipTest(f"OptiX backend is not available in this environment: {exc}")
        self.assertEqual(result["transfer_mode"], "host_stage")
        self.assertEqual(result["source_protocols"], ("numpy",))
        self.assertEqual(result["ray_count"], 2)
        self.assertEqual(result["triangle_count"], 1)
        self.assertEqual(result["hit_count"], 1)
        self.assertFalse(result["true_zero_copy_authorized"])
        self.assertFalse(result["rt_core_speedup_claim_authorized"])

    def test_partner_optix_anyhit_executes_from_torch_cuda_when_available(self) -> None:
        if importlib.util.find_spec("torch") is None:
            self.skipTest("PyTorch is not installed in this dev environment")
        import torch

        if not torch.cuda.is_available():
            self.skipTest("PyTorch CUDA is not available in this dev environment")
        rays, triangles = _torch_columns()
        try:
            result = rt.run_optix_partner_ray_triangle_any_hit_2d(rays, triangles)
        except (OSError, RuntimeError) as exc:
            self.skipTest(f"OptiX backend is not available in this environment: {exc}")
        self.assertEqual(result["transfer_mode"], "host_stage")
        self.assertEqual(result["source_protocols"], ("torch",))
        self.assertEqual(result["source_devices"], ("cuda:0",))
        self.assertEqual(result["hit_count"], 1)
        self.assertFalse(result["true_zero_copy_authorized"])

    def test_partner_optix_anyhit_executes_from_cupy_cuda_when_available(self) -> None:
        if importlib.util.find_spec("cupy") is None:
            self.skipTest("CuPy is not installed in this dev environment")
        import cupy

        try:
            if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
                self.skipTest("CuPy is installed, but no CUDA devices are visible")
        except Exception as exc:
            self.skipTest(f"CuPy CUDA device query failed: {type(exc).__name__}: {exc}")
        rays, triangles = _cupy_columns()
        try:
            result = rt.run_optix_partner_ray_triangle_any_hit_2d(rays, triangles)
        except (OSError, RuntimeError) as exc:
            self.skipTest(f"OptiX backend is not available in this environment: {exc}")
        self.assertEqual(result["transfer_mode"], "host_stage")
        self.assertEqual(result["source_protocols"], ("cupy",))
        self.assertEqual(result["source_devices"], ("cuda:0",))
        self.assertEqual(result["hit_count"], 1)
        self.assertFalse(result["true_zero_copy_authorized"])


if __name__ == "__main__":
    unittest.main()
