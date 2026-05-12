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


class Goal1799PartnerAnyHitPublicDispatchTest(unittest.TestCase):
    def setUp(self) -> None:
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("NumPy is required for partner host staging")

    def test_partner_namespace_dispatches_to_embree_by_default(self) -> None:
        rays, triangles = _numpy_columns()
        try:
            result = rt.partner.run_ray_triangle_any_hit_2d(rays, triangles)
        except (OSError, RuntimeError, ValueError) as exc:
            self.skipTest(f"Embree backend is not available in this environment: {exc}")
        self.assertEqual(result["backend"], "embree")
        self.assertEqual(result["hit_count"], 1)
        self.assertEqual(result["transfer_mode"], "host_stage")
        self.assertFalse(result["true_zero_copy_authorized"])

    def test_top_level_alias_dispatches_to_embree(self) -> None:
        rays, triangles = _numpy_columns()
        try:
            result = rt.run_partner_ray_triangle_any_hit_2d(rays, triangles, backend="embree")
        except (OSError, RuntimeError, ValueError) as exc:
            self.skipTest(f"Embree backend is not available in this environment: {exc}")
        self.assertEqual(result["backend"], "embree")
        self.assertEqual(result["hit_count"], 1)
        self.assertFalse(result["rt_core_speedup_claim_authorized"])

    def test_public_dispatch_can_select_optix_when_backend_available(self) -> None:
        rays, triangles = _numpy_columns()
        try:
            result = rt.run_partner_ray_triangle_any_hit_2d(rays, triangles, backend="optix")
        except (OSError, RuntimeError, ValueError) as exc:
            self.skipTest(f"OptiX backend is not available in this environment: {exc}")
        self.assertEqual(result["hit_count"], 1)
        self.assertEqual(result["transfer_mode"], "host_stage")
        self.assertFalse(result["true_zero_copy_authorized"])

    def test_public_dispatch_rejects_unknown_backend(self) -> None:
        rays, triangles = _numpy_columns()
        with self.assertRaisesRegex(ValueError, "backend must be one of"):
            rt.run_partner_ray_triangle_any_hit_2d(rays, triangles, backend="oracle")


if __name__ == "__main__":
    unittest.main()
