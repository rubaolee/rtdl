from __future__ import annotations

import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_polygon_exclusive():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    refined = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(boundary_mode="exclusive", result_mode="positive_hits"),
    )
    return rt.emit(refined, fields=["point_id", "polygon_id", "contains"])


POINTS = (
    rt.Point(id=1, x=0.5, y=0.5),
)

POLYGONS = (
    rt.Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
)


class Goal91BackendBoundarySupportTest(unittest.TestCase):
    def test_lowering_rejects_exclusive_boundary_mode_for_native_backends(self) -> None:
        with self.assertRaisesRegex(ValueError, "boundary_mode='inclusive'"):
            rt.lower_to_execution_plan(rt.compile_kernel(point_in_polygon_exclusive))

    def test_exclusive_boundary_kernel_still_compiles_before_lowering_guard(self) -> None:
        compiled = rt.compile_kernel(point_in_polygon_exclusive)
        self.assertEqual(compiled.refine_op.predicate.options["boundary_mode"], "exclusive")


if __name__ == "__main__":
    unittest.main()
