from __future__ import annotations

import math
import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import prepare_hiprt_fixed_radius_neighbors_3d


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_3d_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal566HiprtPreparedNearestNeighborTest(unittest.TestCase):
    def _search_points(self) -> tuple[rt.Point3D, ...]:
        return (
            rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
            rt.Point3D(id=2, x=0.0, y=0.0, z=0.6),
            rt.Point3D(id=3, x=0.0, y=0.8, z=0.0),
            rt.Point3D(id=4, x=5.0, y=0.0, z=0.9),
            rt.Point3D(id=5, x=8.0, y=0.0, z=0.0),
        )

    def _query_batches(self) -> tuple[tuple[rt.Point3D, ...], ...]:
        return (
            (
                rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=20, x=5.0, y=0.0, z=0.0),
            ),
            (
                rt.Point3D(id=30, x=0.0, y=0.7, z=0.1),
                rt.Point3D(id=40, x=8.1, y=0.0, z=0.0),
            ),
        )

    def assert_rows_close(self, left, right) -> None:
        self.assertEqual(len(left), len(right))
        for left_row, right_row in zip(left, right):
            self.assertEqual(left_row["query_id"], right_row["query_id"])
            self.assertEqual(left_row["neighbor_id"], right_row["neighbor_id"])
            self.assertTrue(
                math.isclose(left_row["distance"], right_row["distance"], rel_tol=1e-6, abs_tol=1e-6),
                (left_row, right_row),
            )

    def test_direct_prepared_helper_matches_cpu_reference_for_multiple_batches(self) -> None:
        search_points = self._search_points()
        with prepare_hiprt_fixed_radius_neighbors_3d(search_points, radius=1.0) as prepared:
            for query_points in self._query_batches():
                hiprt_rows = prepared.run(query_points, k_max=3)
                cpu_rows = rt.run_cpu_python_reference(
                    fixed_radius_3d_kernel,
                    query_points=query_points,
                    search_points=search_points,
                )
                self.assert_rows_close(hiprt_rows, cpu_rows)

    def test_prepared_kernel_matches_cpu_reference_for_multiple_batches(self) -> None:
        search_points = self._search_points()
        with rt.prepare_hiprt(fixed_radius_3d_kernel, search_points=search_points) as prepared:
            for query_points in self._query_batches():
                hiprt_rows = prepared.run(query_points=query_points)
                cpu_rows = rt.run_cpu_python_reference(
                    fixed_radius_3d_kernel,
                    query_points=query_points,
                    search_points=search_points,
                )
                self.assert_rows_close(hiprt_rows, cpu_rows)


if __name__ == "__main__":
    unittest.main()
