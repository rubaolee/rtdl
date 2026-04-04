from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import embree_runtime
from rtdsl import optix_runtime
from rtdsl.reference import Point
from rtdsl.reference import Polygon


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_counties_positive_hits():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    refined = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(boundary_mode="inclusive", result_mode="positive_hits"),
    )
    return rt.emit(refined, fields=["point_id", "polygon_id", "contains"])


POINTS = (
    Point(id=1, x=0.25, y=0.25),
    Point(id=2, x=1.25, y=1.25),
)

POLYGONS = (
    Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
)


class _FakePreparedExecution:
    def run(self):
        return ({"ok": True},)

    def run_raw(self):
        return self


class _FakePreparedKernel:
    def bind(self, **inputs):
        return _FakePreparedExecution()


class Goal80RuntimeIdentityFastPathTest(unittest.TestCase):
    def setUp(self) -> None:
        embree_runtime.clear_embree_prepared_cache()
        optix_runtime.clear_optix_prepared_cache()
        self.compiled = rt.compile_kernel(point_in_counties_positive_hits)

    def test_embree_identity_fast_path_skips_normalize_on_repeated_tuple_inputs(self) -> None:
        with mock.patch.object(embree_runtime, "prepare_embree", return_value=_FakePreparedKernel()), mock.patch.object(
            embree_runtime,
            "_normalize_records",
            side_effect=AssertionError("Embree normalize should not run for canonical tuple fast path"),
        ):
            first = embree_runtime.run_embree(self.compiled, points=POINTS, polygons=POLYGONS)
            second = embree_runtime.run_embree(self.compiled, points=POINTS, polygons=POLYGONS)
        self.assertEqual(first, second)

    def test_optix_identity_fast_path_skips_normalize_on_repeated_tuple_inputs(self) -> None:
        with mock.patch.object(optix_runtime, "prepare_optix", return_value=_FakePreparedKernel()), mock.patch.object(
            optix_runtime,
            "_normalize_records",
            side_effect=AssertionError("OptiX normalize should not run for canonical tuple fast path"),
        ):
            first = optix_runtime.run_optix(self.compiled, points=POINTS, polygons=POLYGONS)
            second = optix_runtime.run_optix(self.compiled, points=POINTS, polygons=POLYGONS)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
