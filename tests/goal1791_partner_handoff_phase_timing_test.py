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


class Goal1791PartnerHandoffPhaseTimingTest(unittest.TestCase):
    def setUp(self) -> None:
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("NumPy is required for partner host staging")

    def test_pack_reports_partner_handoff_phase_timings(self) -> None:
        rays, triangles = _numpy_columns()
        packed = rt.pack_optix_ray_triangle_any_hit_2d_partner_inputs(rays, triangles)
        timings = packed["metadata"]["partner_phase_timings_s"]
        self.assertEqual(
            set(timings),
            {
                "descriptor_validation",
                "framework_to_host_staging",
                "packet_packing",
            },
        )
        for value in timings.values():
            self.assertIsInstance(value, float)
            self.assertGreaterEqual(value, 0.0)
        self.assertEqual(packed["metadata"]["transfer_mode"], "host_stage")
        self.assertFalse(packed["metadata"]["true_zero_copy_authorized"])

    def test_execution_reports_python_and_native_timing_buckets_when_optix_available(self) -> None:
        rays, triangles = _numpy_columns()
        try:
            result = rt.run_optix_partner_ray_triangle_any_hit_2d(rays, triangles)
        except (OSError, RuntimeError) as exc:
            self.skipTest(f"OptiX backend is not available in this environment: {exc}")
        timings = result["partner_phase_timings_s"]
        self.assertEqual(
            set(timings),
            {
                "descriptor_validation",
                "framework_to_host_staging",
                "packet_packing",
                "optix_prepare",
                "optix_count_and_scalar_copyback",
            },
        )
        for value in timings.values():
            self.assertIsInstance(value, float)
            self.assertGreaterEqual(value, 0.0)
        self.assertEqual(result["hit_count"], 1)
        self.assertEqual(result["transfer_mode"], "host_stage")
        self.assertFalse(result["rt_core_speedup_claim_authorized"])
        self.assertIn("phase_timings", result)


if __name__ == "__main__":
    unittest.main()
