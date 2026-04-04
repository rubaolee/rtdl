from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import embree_runtime
from rtdsl import optix_runtime
from rtdsl import vulkan_runtime


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


POINTS_A = (
    {"id": 1, "x": 0.25, "y": 0.25},
    {"id": 2, "x": 1.25, "y": 1.25},
)

POINTS_B = (
    {"id": 1, "x": 0.25, "y": 0.25},
    {"id": 2, "x": 5.0, "y": 5.0},
)

POLYGONS = (
    {"id": 10, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
)


class _FakePreparedExecution:
    def __init__(self, bind_id: int):
        self.bind_id = bind_id

    def run(self):
        return ({"bind_id": self.bind_id},)

    def run_raw(self):
        return self


class _FakePreparedKernel:
    def __init__(self, bind_counter: list[int]):
        self.bind_counter = bind_counter

    def bind(self, **inputs):
        self.bind_counter.append(len(self.bind_counter) + 1)
        return _FakePreparedExecution(self.bind_counter[-1])


class Goal76RuntimePreparedCacheTest(unittest.TestCase):
    def setUp(self) -> None:
        embree_runtime.clear_embree_prepared_cache()
        optix_runtime.clear_optix_prepared_cache()
        vulkan_runtime.clear_vulkan_prepared_cache()
        self.compiled = rt.compile_kernel(point_in_counties_positive_hits)

    def test_embree_reuses_prepared_execution_for_identical_raw_inputs(self) -> None:
        bind_counter: list[int] = []
        with mock.patch.object(
            embree_runtime,
            "prepare_embree",
            side_effect=lambda compiled: _FakePreparedKernel(bind_counter),
        ):
            first = embree_runtime.run_embree(self.compiled, points=POINTS_A, polygons=POLYGONS)
            second = embree_runtime.run_embree(self.compiled, points=POINTS_A, polygons=POLYGONS)
            changed = embree_runtime.run_embree(self.compiled, points=POINTS_B, polygons=POLYGONS)
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)
        self.assertEqual(bind_counter, [1, 2])

    def test_optix_reuses_prepared_execution_for_identical_raw_inputs(self) -> None:
        bind_counter: list[int] = []
        with mock.patch.object(
            optix_runtime,
            "prepare_optix",
            side_effect=lambda compiled: _FakePreparedKernel(bind_counter),
        ):
            first = optix_runtime.run_optix(self.compiled, points=POINTS_A, polygons=POLYGONS)
            second = optix_runtime.run_optix(self.compiled, points=POINTS_A, polygons=POLYGONS)
            changed = optix_runtime.run_optix(self.compiled, points=POINTS_B, polygons=POLYGONS)
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)
        self.assertEqual(bind_counter, [1, 2])

    def test_vulkan_reuses_prepared_execution_for_identical_raw_inputs(self) -> None:
        bind_counter: list[int] = []
        with mock.patch.object(
            vulkan_runtime,
            "prepare_vulkan",
            side_effect=lambda compiled: _FakePreparedKernel(bind_counter),
        ):
            first = vulkan_runtime.run_vulkan(self.compiled, points=POINTS_A, polygons=POLYGONS)
            second = vulkan_runtime.run_vulkan(self.compiled, points=POINTS_A, polygons=POLYGONS)
            changed = vulkan_runtime.run_vulkan(self.compiled, points=POINTS_B, polygons=POLYGONS)
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)
        self.assertEqual(bind_counter, [1, 2])

    def test_cache_clear_forces_rebind(self) -> None:
        bind_counter: list[int] = []
        with mock.patch.object(
            optix_runtime,
            "prepare_optix",
            side_effect=lambda compiled: _FakePreparedKernel(bind_counter),
        ):
            first = optix_runtime.run_optix(self.compiled, points=POINTS_A, polygons=POLYGONS)
            optix_runtime.clear_optix_prepared_cache()
            second = optix_runtime.run_optix(self.compiled, points=POINTS_A, polygons=POLYGONS)
        self.assertNotEqual(first, second)
        self.assertEqual(bind_counter, [1, 2])


if __name__ == "__main__":
    unittest.main()
