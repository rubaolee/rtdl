import sys
import unittest
import os
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
import rtdsl.vulkan_runtime as vulkan_runtime
from examples.rtdl_language_reference import county_soil_overlay_reference
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from examples.rtdl_goal10_reference import point_nearest_segment_reference
from examples.rtdl_goal10_reference import segment_polygon_hitcount_reference
from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference
from rtdsl.baseline_contracts import compare_baseline_rows

def vulkan_available():
    """Simple check if Vulkan library can be loaded and a version queried."""
    try:
        rt.vulkan_version()
        return True
    except Exception:
        return False

class RtDslVulkanLoaderTest(unittest.TestCase):
    def tearDown(self) -> None:
        vulkan_runtime._load_vulkan_library.cache_clear()

    def test_run_vulkan_rejects_invalid_result_mode(self) -> None:
        with self.assertRaises(ValueError):
            rt.run_vulkan(county_zip_join_reference, result_mode="tuple", left=(), right=())

    def test_find_vulkan_library_rejects_missing_env_path(self) -> None:
        with mock.patch.dict(os.environ, {"RTDL_VULKAN_LIB": "/tmp/does-not-exist-vulkan.so"}, clear=False):
            with self.assertRaises(FileNotFoundError):
                vulkan_runtime._find_vulkan_library()

    def test_find_vulkan_library_reports_missing_library(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(vulkan_runtime.platform, "system", return_value="Linux"):
                with mock.patch.object(vulkan_runtime.Path, "exists", return_value=False):
                    with mock.patch.object(vulkan_runtime.ctypes.util, "find_library", return_value=None):
                        with self.assertRaises(FileNotFoundError):
                            vulkan_runtime._find_vulkan_library()


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

    def test_prepare_vulkan_bind_run_matches_cpu(self) -> None:
        left = (
            {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},
        )
        right = (
            {"id": 10, "x0": 0.0, "y0": 2.0, "x1": 2.0, "y1": 0.0},
        )
        prepared = rt.prepare_vulkan(county_zip_join_reference)
        bound = prepared.bind(left=left, right=right)
        self.assertIsInstance(bound, rt.PreparedVulkanExecution)
        self.assertTrue(
            compare_baseline_rows(
                "lsi",
                rt.run_cpu(county_zip_join_reference, left=left, right=right),
                bound.run(),
            )
        )

    def test_run_vulkan_raw_mode_returns_row_view(self) -> None:
        left = (
            {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},
        )
        right = (
            {"id": 10, "x0": 0.0, "y0": 2.0, "x1": 2.0, "y1": 0.0},
        )
        rows = rt.run_vulkan(
            county_zip_join_reference,
            result_mode="raw",
            left=left,
            right=right,
        )
        self.assertIsInstance(rows, rt.VulkanRowView)
        self.assertGreaterEqual(len(rows), 1)
        self.assertEqual(
            rows.to_dict_rows(),
            rt.run_vulkan(county_zip_join_reference, left=left, right=right),
        )
        rows.close()
        self.assertTrue(rows._closed)

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

    def test_run_vulkan_segment_polygon_hitcount_matches_cpu(self) -> None:
        segments = (
            {"id": 1, "x0": -1.0, "y0": 1.0, "x1": 3.0, "y1": 1.0},
            {"id": 2, "x0": 5.0, "y0": 5.0, "x1": 6.0, "y1": 6.0},
        )
        polygons = (
            {"id": 10, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
            {"id": 11, "vertices": ((4.0, 4.0), (7.0, 4.0), (7.0, 7.0), (4.0, 7.0))},
        )
        self.assertTrue(
            compare_baseline_rows(
                "segment_polygon_hitcount",
                rt.run_cpu(segment_polygon_hitcount_reference, segments=segments, polygons=polygons),
                rt.run_vulkan(segment_polygon_hitcount_reference, segments=segments, polygons=polygons),
            )
        )

    def test_run_vulkan_point_nearest_segment_matches_cpu(self) -> None:
        points = (
            {"id": 100, "x": 0.5, "y": 0.5},
            {"id": 101, "x": 3.5, "y": 1.0},
        )
        segments = (
            {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 0.0, "y1": 2.0},
            {"id": 2, "x0": 4.0, "y0": 0.0, "x1": 4.0, "y1": 2.0},
        )
        self.assertTrue(
            compare_baseline_rows(
                "point_nearest_segment",
                rt.run_cpu(point_nearest_segment_reference, points=points, segments=segments),
                rt.run_vulkan(point_nearest_segment_reference, points=points, segments=segments),
            )
        )

if __name__ == "__main__":
    unittest.main()
