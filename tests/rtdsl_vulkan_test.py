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
from scripts.goal69_pip_positive_hit_performance import point_in_counties_positive_hits

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

    # ── Goal 78: positive-hit sparse redesign tests ──────────────────────────

    def test_run_vulkan_pip_positive_hits_parity(self) -> None:
        """Positive-hit Vulkan PIP must match CPU positive-hit row-for-row."""
        points = (
            {"id": 100, "x": 0.5, "y": 0.5},   # inside polygon 200
            {"id": 101, "x": 3.0, "y": 3.0},   # outside polygon 200
            {"id": 102, "x": 1.0, "y": 1.0},   # inside polygon 200
        )
        polygons = (
            {"id": 200, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
        )
        cpu_rows = rt.run_cpu(point_in_counties_positive_hits, points=points, polygons=polygons)
        gpu_rows = rt.run_vulkan(point_in_counties_positive_hits, points=points, polygons=polygons)
        self.assertTrue(compare_baseline_rows("pip", cpu_rows, gpu_rows))

    def test_run_vulkan_pip_positive_hits_only_contains_ones(self) -> None:
        """All rows returned by positive-hit mode must have contains == 1."""
        points = (
            {"id": 10, "x": 0.5, "y": 0.5},
            {"id": 11, "x": 5.0, "y": 5.0},
            {"id": 12, "x": 1.5, "y": 1.5},
        )
        polygons = (
            {"id": 20, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
            {"id": 21, "vertices": ((4.0, 4.0), (6.0, 4.0), (6.0, 6.0), (4.0, 6.0))},
        )
        rows = rt.run_vulkan(point_in_counties_positive_hits, points=points, polygons=polygons)
        self.assertGreater(len(rows), 0, "expected at least one positive hit")
        for row in rows:
            self.assertEqual(row["contains"], 1,
                             f"positive-hit row must have contains=1, got {row}")

    def test_run_vulkan_pip_positive_hits_row_shape(self) -> None:
        """Positive-hit rows must have exactly the fields point_id, polygon_id, contains."""
        points = ({"id": 1, "x": 0.5, "y": 0.5},)
        polygons = (
            {"id": 2, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
        )
        rows = rt.run_vulkan(point_in_counties_positive_hits, points=points, polygons=polygons)
        self.assertEqual(len(rows), 1)
        self.assertEqual(set(rows[0].keys()), {"point_id", "polygon_id", "contains"})

    def test_run_vulkan_pip_full_matrix_unchanged_after_redesign(self) -> None:
        """Full-matrix PIP behavior must remain unchanged by the positive-hit redesign."""
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
                rt.run_vulkan(point_in_counties_reference, points=points, polygons=polygons),
            )
        )

    def test_run_vulkan_pip_positive_hits_no_false_positives(self) -> None:
        """Positive-hit output must not include pairs where the point is outside the polygon."""
        points = (
            {"id": 1, "x": 0.5, "y": 0.5},   # inside
            {"id": 2, "x": 2.5, "y": 2.5},   # outside
            {"id": 3, "x": 10.0, "y": 10.0}, # far outside
        )
        polygons = (
            {"id": 10, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
        )
        rows = rt.run_vulkan(point_in_counties_positive_hits, points=points, polygons=polygons)
        point_ids_returned = {r["point_id"] for r in rows}
        self.assertIn(1, point_ids_returned, "point 1 (inside) must be returned")
        self.assertNotIn(2, point_ids_returned, "point 2 (outside) must not be returned")
        self.assertNotIn(3, point_ids_returned, "point 3 (far outside) must not be returned")

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
