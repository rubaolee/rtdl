import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_soil_overlay_reference
from examples.reference.rtdl_language_reference import county_zip_join_reference
from examples.reference.rtdl_language_reference import point_in_counties_reference
from examples.reference.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference


class RtDslSimulatorTest(unittest.TestCase):
    def test_run_cpu_lsi_matches_reference(self) -> None:
        left = (
            {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 2.0, "y1": 2.0, "chain_id": 9},
        )
        right = (
            {"id": 2, "x0": 0.0, "y0": 2.0, "x1": 2.0, "y1": 0.0, "chain_id": 10},
        )

        results = rt.run_cpu(county_zip_join_reference, left=left, right=right)
        expected = rt.lsi_cpu(
            (rt.Segment(id=1, x0=0.0, y0=0.0, x1=2.0, y1=2.0),),
            (rt.Segment(id=2, x0=0.0, y0=2.0, x1=2.0, y1=0.0),),
        )

        self.assertEqual(results, expected)
        self.assertEqual(tuple(results[0].keys()), ("left_id", "right_id", "intersection_point_x", "intersection_point_y"))

    def test_run_cpu_pip_matches_reference(self) -> None:
        points = (
            {"id": 10, "x": 0.5, "y": 0.5, "source_chain_id": 99},
            {"id": 11, "x": 3.0, "y": 3.0, "source_chain_id": 100},
        )
        polygons = (
            {"id": 20, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
        )

        results = rt.run_cpu(point_in_counties_reference, points=points, polygons=polygons)
        expected = rt.pip_cpu(
            (
                rt.Point(id=10, x=0.5, y=0.5),
                rt.Point(id=11, x=3.0, y=3.0),
            ),
            (
                rt.Polygon(id=20, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
            ),
        )

        self.assertEqual(results, expected)
        self.assertEqual(tuple(results[0].keys()), ("point_id", "polygon_id", "contains"))

    def test_run_cpu_overlay_matches_reference(self) -> None:
        left = (
            rt.Polygon(id=1, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
        )
        right = (
            rt.Polygon(id=2, vertices=((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))),
        )

        compiled = rt.compile_kernel(county_soil_overlay_reference)
        results = rt.run_cpu(compiled, left=left, right=right)
        expected = rt.overlay_compose_cpu(left, right)

        self.assertEqual(results, expected)
        self.assertEqual(tuple(results[0].keys()), ("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"))

    def test_run_cpu_ray_hitcount_matches_reference(self) -> None:
        rays = (
            {"id": 1, "ox": 0.0, "oy": 0.0, "dx": 1.0, "dy": 0.0, "tmax": 10.0},
            {"id": 2, "ox": 0.0, "oy": 0.0, "dx": 0.0, "dy": 1.0, "tmax": 2.0},
        )
        triangles = (
            {"id": 10, "x0": 2.0, "y0": -1.0, "x1": 3.0, "y1": 1.0, "x2": 4.0, "y2": -1.0},
            {"id": 11, "x0": 6.0, "y0": -1.0, "x1": 7.0, "y1": 1.0, "x2": 8.0, "y2": -1.0},
            {"id": 12, "x0": -1.0, "y0": 3.0, "x1": 1.0, "y1": 3.0, "x2": 0.0, "y2": 4.0},
        )

        results = rt.run_cpu(ray_triangle_hitcount_reference, rays=rays, triangles=triangles)
        expected = rt.ray_triangle_hit_count_cpu(
            (
                rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
                rt.Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=2.0),
            ),
            (
                rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),
                rt.Triangle(id=11, x0=6.0, y0=-1.0, x1=7.0, y1=1.0, x2=8.0, y2=-1.0),
                rt.Triangle(id=12, x0=-1.0, y0=3.0, x1=1.0, y1=3.0, x2=0.0, y2=4.0),
            ),
        )

        self.assertEqual(results, expected)
        self.assertEqual(tuple(results[0].keys()), ("ray_id", "hit_count"))

    def test_run_cpu_rejects_missing_inputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing RTDL simulator inputs: right"):
            rt.run_cpu(county_zip_join_reference, left=())

    def test_run_cpu_rejects_unexpected_inputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "unexpected RTDL simulator inputs: extra"):
            rt.run_cpu(county_zip_join_reference, left=(), right=(), extra=())

    def test_run_cpu_rejects_polygon_records_without_vertices(self) -> None:
        with self.assertRaisesRegex(ValueError, "logical polygon records with `id` and `vertices`"):
            rt.run_cpu(
                point_in_counties_reference,
                points=({"id": 1, "x": 0.0, "y": 0.0},),
                polygons=({"id": 2, "vertex_offset": 0, "vertex_count": 4},),
            )

    def test_run_cpu_rejects_non_float_approx_precision(self) -> None:
        @rt.kernel(backend="rtdl", precision="exact")
        def exact_kernel():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(
                hits,
                fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
            )

        with self.assertRaisesRegex(ValueError, "precision='float_approx'"):
            rt.run_cpu(exact_kernel, left=(), right=())


if __name__ == "__main__":
    unittest.main()
