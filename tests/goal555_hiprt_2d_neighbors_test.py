from __future__ import annotations

import math
import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import fixed_radius_neighbors_2d_hiprt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import knn_rows_2d_hiprt


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_2d_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.1, k_max=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_2d_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_2d_kmax_over_cap_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.1, k_max=65))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_2d_k_over_cap_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=65))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal555Hiprt2DNeighborsTest(unittest.TestCase):
    def _points(self):
        return (
            rt.Point(id=1, x=0.0, y=0.0),
            rt.Point(id=2, x=1.0, y=0.0),
            rt.Point(id=3, x=0.0, y=1.0),
            rt.Point(id=4, x=3.0, y=0.0),
        )

    def assert_rows_close(self, left, right) -> None:
        self.assertEqual(len(left), len(right))
        for left_row, right_row in zip(left, right):
            self.assertEqual(set(left_row), set(right_row))
            for key in left_row:
                if isinstance(left_row[key], float) or isinstance(right_row[key], float):
                    self.assertTrue(math.isclose(left_row[key], right_row[key], rel_tol=1e-6, abs_tol=1e-6))
                else:
                    self.assertEqual(left_row[key], right_row[key])

    def test_fixed_radius_direct_helper_matches_cpu_reference(self) -> None:
        points = self._points()
        self.assert_rows_close(
            fixed_radius_neighbors_2d_hiprt(points, points, radius=1.1, k_max=4),
            rt.run_cpu_python_reference(fixed_radius_2d_kernel, query_points=points, search_points=points),
        )

    def test_fixed_radius_run_hiprt_matches_cpu_reference(self) -> None:
        points = self._points()
        self.assert_rows_close(
            rt.run_hiprt(fixed_radius_2d_kernel, query_points=points, search_points=points),
            rt.run_cpu_python_reference(fixed_radius_2d_kernel, query_points=points, search_points=points),
        )

    def test_knn_direct_helper_matches_cpu_reference(self) -> None:
        points = self._points()
        self.assert_rows_close(
            knn_rows_2d_hiprt(points, points, k=2),
            rt.run_cpu_python_reference(knn_2d_kernel, query_points=points, search_points=points),
        )

    def test_knn_run_hiprt_matches_cpu_reference(self) -> None:
        points = self._points()
        self.assert_rows_close(
            rt.run_hiprt(knn_2d_kernel, query_points=points, search_points=points),
            rt.run_cpu_python_reference(knn_2d_kernel, query_points=points, search_points=points),
        )

    def test_empty_inputs_return_empty_rows(self) -> None:
        points = self._points()
        self.assertEqual(rt.run_hiprt(fixed_radius_2d_kernel, query_points=(), search_points=points), ())
        self.assertEqual(rt.run_hiprt(fixed_radius_2d_kernel, query_points=points, search_points=()), ())
        self.assertEqual(rt.run_hiprt(knn_2d_kernel, query_points=(), search_points=points), ())
        self.assertEqual(rt.run_hiprt(knn_2d_kernel, query_points=points, search_points=()), ())


class Goal555Hiprt2DNeighborsBoundaryTest(unittest.TestCase):
    def _points(self):
        return (
            rt.Point(id=1, x=0.0, y=0.0),
            rt.Point(id=2, x=1.0, y=0.0),
        )

    def test_fixed_radius_rejects_oversized_kmax_before_backend_execution(self) -> None:
        points = self._points()
        with self.assertRaisesRegex(ValueError, "k_max <= 64"):
            rt.run_hiprt(fixed_radius_2d_kmax_over_cap_kernel, query_points=points, search_points=points)

    def test_knn_rejects_oversized_k_before_backend_execution(self) -> None:
        points = self._points()
        with self.assertRaisesRegex(ValueError, "k_max <= 64"):
            rt.run_hiprt(knn_2d_k_over_cap_kernel, query_points=points, search_points=points)


if __name__ == "__main__":
    unittest.main()
