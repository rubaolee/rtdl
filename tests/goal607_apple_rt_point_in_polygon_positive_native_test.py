from __future__ import annotations

import platform
import unittest

import rtdsl as rt


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_polygon_positive_kernel():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive", result_mode="positive_hits"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_polygon_full_matrix_kernel():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive"))
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


def _square(polygon_id: int, x0: float, y0: float, x1: float, y1: float) -> rt.Polygon:
    return rt.Polygon(id=polygon_id, vertices=((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal607AppleRtPointInPolygonPositiveNativeTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[object, ...]]:
        return {
            "points": (
                rt.Point(id=1, x=0.5, y=0.5),
                rt.Point(id=2, x=1.5, y=1.5),
                rt.Point(id=3, x=3.0, y=3.0),
            ),
            "polygons": (
                _square(10, 0.0, 0.0, 1.0, 1.0),
                _square(20, 1.0, 1.0, 2.0, 2.0),
            ),
        }

    def test_positive_hits_native_only_matches_cpu(self) -> None:
        case = self._case()
        actual = rt.run_apple_rt(point_in_polygon_positive_kernel, native_only=True, **case)
        expected = rt.run_cpu_python_reference(point_in_polygon_positive_kernel, **case)
        self.assertEqual(actual, expected)

    def test_direct_positive_helper_matches_cpu(self) -> None:
        case = self._case()
        actual = rt.point_in_polygon_positive_hits_apple_rt(case["points"], case["polygons"])
        expected = rt.pip_cpu(case["points"], case["polygons"], result_mode="positive_hits")
        self.assertEqual(actual, expected)

    def test_full_matrix_remains_non_native(self) -> None:
        with self.assertRaises(NotImplementedError):
            rt.run_apple_rt(point_in_polygon_full_matrix_kernel, native_only=True, **self._case())


if __name__ == "__main__":
    unittest.main()
