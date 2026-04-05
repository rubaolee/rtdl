from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import optix_runtime


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


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_counties_full_matrix():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    refined = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(boundary_mode="inclusive", result_mode="full_matrix"),
    )
    return rt.emit(refined, fields=["point_id", "polygon_id", "contains"])


POINTS = (
    {"id": 1, "x": 0.25, "y": 0.25},
    {"id": 2, "x": 5.0, "y": 5.0},
)

POLYGONS = (
    {"id": 10, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
)


class _FakeRowView:
    def __init__(self, records):
        self.records = tuple(records)
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def to_dict_rows(self):
        return self.records


class Goal99OptixColdPreparedRun1WinTest(unittest.TestCase):
    def setUp(self) -> None:
        self.compiled_positive = rt.compile_kernel(point_in_counties_positive_hits)
        self.compiled_full = rt.compile_kernel(point_in_counties_full_matrix)

    def test_bind_warms_positive_hit_execution_before_first_timed_run(self) -> None:
        calls: list[str] = []
        library = object()

        def fake_call(compiled, packed_inputs, passed_library):
            self.assertIs(compiled, self.compiled_positive)
            self.assertIs(passed_library, library)
            calls.append("run_raw")
            return _FakeRowView(({"point_id": 1, "polygon_id": 10, "contains": 1},))

        with mock.patch.object(optix_runtime, "_load_optix_library", return_value=library), mock.patch.object(
            optix_runtime,
            "_pack_for_geometry",
            side_effect=lambda geometry_name, payload: payload,
        ), mock.patch.object(
            optix_runtime,
            "_call_pip_optix_packed",
            side_effect=fake_call,
        ):
            prepared = optix_runtime.prepare_optix(self.compiled_positive)
            bound = prepared.bind(points=POINTS, polygons=POLYGONS)
            self.assertEqual(calls, ["run_raw"])
            rows = bound.run()

        self.assertEqual(calls, ["run_raw", "run_raw"])
        self.assertEqual(rows, ({"point_id": 1, "polygon_id": 10, "contains": 1},))

    def test_bind_does_not_warm_non_positive_hit_execution(self) -> None:
        calls: list[str] = []
        library = object()

        def fake_call(compiled, packed_inputs, passed_library):
            self.assertIs(compiled, self.compiled_full)
            self.assertIs(passed_library, library)
            calls.append("run_raw")
            return _FakeRowView(({"point_id": 1, "polygon_id": 10, "contains": 1},))

        with mock.patch.object(optix_runtime, "_load_optix_library", return_value=library), mock.patch.object(
            optix_runtime,
            "_pack_for_geometry",
            side_effect=lambda geometry_name, payload: payload,
        ), mock.patch.object(
            optix_runtime,
            "_call_pip_optix_packed",
            side_effect=fake_call,
        ):
            prepared = optix_runtime.prepare_optix(self.compiled_full)
            bound = prepared.bind(points=POINTS, polygons=POLYGONS)
            self.assertEqual(calls, [])
            rows = bound.run()

        self.assertEqual(calls, ["run_raw"])
        self.assertEqual(rows, ({"point_id": 1, "polygon_id": 10, "contains": 1},))


if __name__ == "__main__":
    unittest.main()
