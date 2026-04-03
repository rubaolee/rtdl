import sys
import unittest
import os

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_language_reference import county_soil_overlay_reference
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference
from rtdsl.baseline_contracts import compare_baseline_rows

def vulkan_available():
    """Simple check if Vulkan library can be loaded and a version queried."""
    try:
        rt.vulkan_version()
        return True
    except Exception:
        return False

class RtDslVulkanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not vulkan_available():
            raise unittest.SkipTest("Vulkan is not available or RTDL Vulkan library not found")

    def test_vulkan_version_is_available(self) -> None:
        version = rt.vulkan_version()
        # We expect 0.1.0 based on Claude's report
        self.assertEqual(version[0], 0)
        self.assertEqual(version[1], 1)

    def test_run_vulkan_lsi_matches_cpu(self) -> None:
        left = (
            {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},
            {"id": 2, "x0": 2.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},
        )
        right = (
            {"id": 10, "x0": 0.0, "y0": 2.0, "x1": 2.0, "y1": 0.0},
        )
        self.assertTrue(
            compare_baseline_rows(
                "lsi",
                rt.run_cpu(county_zip_join_reference, left=left, right=right),
                rt.run_vulkan(county_zip_join_reference, left=left, right=right)
            )
        )

    def test_run_vulkan_pip_matches_cpu(self) -> None:
        points = (
            {"id": 100, "x": 0.5, "y": 0.5},
            {"id": 101, "x": 3.0, "y": 3.0},
        )
        polygons = (
            {"id": 200, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
        )
        self.assertTrue(
            compare_baseline_rows(
                "pip",
                rt.run_cpu(point_in_counties_reference, points=points, polygons=polygons),
                rt.run_vulkan(point_in_counties_reference, points=points, polygons=polygons)
            )
        )

    def test_run_vulkan_overlay_matches_cpu(self) -> None:
        left = (
            {"id": 300, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
        )
        right = (
            {"id": 301, "vertices": ((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))},
        )
        self.assertTrue(
            compare_baseline_rows(
                "overlay",
                rt.run_cpu(county_soil_overlay_reference, left=left, right=right),
                rt.run_vulkan(county_soil_overlay_reference, left=left, right=right)
            )
        )

    def test_run_vulkan_ray_hitcount_matches_cpu(self) -> None:
        rays = (
            {"id": 1, "ox": 0.0, "oy": 0.0, "dx": 1.0, "dy": 0.0, "tmax": 10.0},
            {"id": 2, "ox": 0.0, "oy": 0.0, "dx": 0.0, "dy": 1.0, "tmax": 2.0},
        )
        triangles = (
            {"id": 10, "x0": 2.0, "y0": -1.0, "x1": 3.0, "y1": 1.0, "x2": 4.0, "y2": -1.0},
            {"id": 11, "x0": 6.0, "y0": -1.0, "x1": 7.0, "y1": 1.0, "x2": 8.0, "y2": -1.0},
            {"id": 12, "x0": -1.0, "y0": 3.0, "x1": 1.0, "y1": 3.0, "x2": 0.0, "y2": 4.0},
        )
        self.assertTrue(
            compare_baseline_rows(
                "ray_tri_hitcount",
                rt.run_cpu(ray_triangle_hitcount_reference, rays=rays, triangles=triangles),
                rt.run_vulkan(ray_triangle_hitcount_reference, rays=rays, triangles=triangles)
            )
        )

if __name__ == "__main__":
    unittest.main()
