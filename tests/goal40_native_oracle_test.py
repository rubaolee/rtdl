import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_goal10_reference import make_fixture_point_nearest_segment_case
from examples.rtdl_goal10_reference import make_fixture_segment_polygon_case
from examples.rtdl_goal10_reference import point_nearest_segment_reference
from examples.rtdl_goal10_reference import segment_polygon_hitcount_reference
from examples.rtdl_language_reference import county_soil_overlay_reference
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference


class Goal40NativeOracleTest(unittest.TestCase):
    def test_oracle_version_available(self) -> None:
        self.assertEqual(rt.oracle_version(), (0, 1, 0))

    def test_run_cpu_matches_python_reference_for_language_workloads(self) -> None:
        lsi_case = {
            "left": (
                {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},
                {"id": 2, "x0": 0.0, "y0": 1.0, "x1": 2.0, "y1": 1.0},
            ),
            "right": (
                {"id": 10, "x0": 0.0, "y0": 2.0, "x1": 2.0, "y1": 0.0},
                {"id": 11, "x0": 1.0, "y0": -1.0, "x1": 1.0, "y1": 3.0},
            ),
        }
        pip_case = {
            "points": (
                {"id": 100, "x": 0.5, "y": 0.5},
                {"id": 101, "x": 2.0, "y": 1.0},
            ),
            "polygons": (
                {"id": 200, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
            ),
        }
        overlay_case = {
            "left": (
                {"id": 300, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
            ),
            "right": (
                {"id": 301, "vertices": ((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))},
            ),
        }
        ray_case = {
            "rays": (
                {"id": 1, "ox": 0.0, "oy": 0.0, "dx": 1.0, "dy": 0.0, "tmax": 10.0},
                {"id": 2, "ox": 0.0, "oy": 0.0, "dx": 0.0, "dy": 1.0, "tmax": 3.0},
            ),
            "triangles": (
                {"id": 10, "x0": 2.0, "y0": -1.0, "x1": 3.0, "y1": 1.0, "x2": 4.0, "y2": -1.0},
                {"id": 11, "x0": -1.0, "y0": 2.0, "x1": 1.0, "y1": 2.0, "x2": 0.0, "y2": 4.0},
            ),
        }

        self.assertEqual(
            rt.run_cpu(county_zip_join_reference, **lsi_case),
            rt.run_cpu_python_reference(county_zip_join_reference, **lsi_case),
        )
        self.assertEqual(
            rt.run_cpu(point_in_counties_reference, **pip_case),
            rt.run_cpu_python_reference(point_in_counties_reference, **pip_case),
        )
        self.assertEqual(
            rt.run_cpu(county_soil_overlay_reference, **overlay_case),
            rt.run_cpu_python_reference(county_soil_overlay_reference, **overlay_case),
        )
        self.assertEqual(
            rt.run_cpu(ray_triangle_hitcount_reference, **ray_case),
            rt.run_cpu_python_reference(ray_triangle_hitcount_reference, **ray_case),
        )

    def test_run_cpu_matches_python_reference_for_goal10_workloads(self) -> None:
        segment_case = make_fixture_segment_polygon_case()
        point_case = make_fixture_point_nearest_segment_case()

        self.assertEqual(
            rt.run_cpu(segment_polygon_hitcount_reference, **segment_case),
            rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **segment_case),
        )

        native_rows = rt.run_cpu(point_nearest_segment_reference, **point_case)
        python_rows = rt.run_cpu_python_reference(point_nearest_segment_reference, **point_case)
        self.assertEqual(len(native_rows), len(python_rows))
        for native_row, python_row in zip(native_rows, python_rows):
            self.assertEqual(native_row["point_id"], python_row["point_id"])
            self.assertEqual(native_row["segment_id"], python_row["segment_id"])
            self.assertTrue(math.isclose(native_row["distance"], python_row["distance"], rel_tol=1e-12, abs_tol=1e-12))
