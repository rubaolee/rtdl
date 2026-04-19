from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import point_in_polygon_hiprt


@rt.kernel(backend="rtdl", precision="float_approx")
def pip_kernel():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


def square(poly_id: int, x0: float, y0: float, size: float) -> rt.Polygon:
    return rt.Polygon(
        id=poly_id,
        vertices=((x0, y0), (x0 + size, y0), (x0 + size, y0 + size), (x0, y0 + size)),
    )


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal552HiprtPointInPolygonTest(unittest.TestCase):
    def _case(self):
        return {
            "points": (
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=0.5, y=0.5),
                rt.Point(id=3, x=3.0, y=3.0),
            ),
            "polygons": (
                square(10, -0.25, -0.25, 1.0),
                square(20, 2.0, 2.0, 1.0),
            ),
        }

    def test_direct_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            point_in_polygon_hiprt(case["points"], case["polygons"]),
            rt.run_cpu_python_reference(pip_kernel, **case),
        )

    def test_run_hiprt_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_hiprt(pip_kernel, **case),
            rt.run_cpu_python_reference(pip_kernel, **case),
        )

    def test_empty_inputs_return_empty_rows(self) -> None:
        self.assertEqual(rt.run_hiprt(pip_kernel, points=(), polygons=self._case()["polygons"]), ())
        self.assertEqual(rt.run_hiprt(pip_kernel, points=self._case()["points"], polygons=()), ())


if __name__ == "__main__":
    unittest.main()
