from __future__ import annotations

import math
import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import bounded_knn_rows_3d_hiprt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import knn_rows_3d_hiprt


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_3d_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_3d_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_3d_kmax_over_cap_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=65))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_3d_k_over_cap_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
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
class Goal549Hiprt3DKnnTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[rt.Point3D, ...]]:
        return {
            "query_points": (
                rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=20, x=5.0, y=0.0, z=0.0),
            ),
            "search_points": (
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.6),
                rt.Point3D(id=3, x=0.0, y=0.8, z=0.0),
                rt.Point3D(id=4, x=5.0, y=0.0, z=0.9),
                rt.Point3D(id=5, x=8.0, y=0.0, z=0.0),
            ),
        }

    def assert_rows_close(self, left, right) -> None:
        self.assertEqual(len(left), len(right))
        for left_row, right_row in zip(left, right):
            self.assertEqual(left_row["query_id"], right_row["query_id"])
            self.assertEqual(left_row["neighbor_id"], right_row["neighbor_id"])
            self.assertEqual(left_row["neighbor_rank"], right_row["neighbor_rank"])
            self.assertTrue(
                math.isclose(left_row["distance"], right_row["distance"], rel_tol=1e-6, abs_tol=1e-6),
                (left_row, right_row),
            )

    def test_direct_bounded_knn_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        hiprt_rows = bounded_knn_rows_3d_hiprt(
            case["query_points"],
            case["search_points"],
            radius=1.0,
            k_max=2,
        )
        cpu_rows = rt.run_cpu_python_reference(bounded_knn_3d_kernel, **case)
        self.assert_rows_close(hiprt_rows, cpu_rows)

    def test_direct_knn_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        hiprt_rows = knn_rows_3d_hiprt(
            case["query_points"],
            case["search_points"],
            k=2,
        )
        cpu_rows = rt.run_cpu_python_reference(knn_3d_kernel, **case)
        self.assert_rows_close(hiprt_rows, cpu_rows)

    def test_run_hiprt_matches_cpu_reference_for_3d_bounded_knn(self) -> None:
        case = self._case()
        self.assert_rows_close(
            rt.run_hiprt(bounded_knn_3d_kernel, **case),
            rt.run_cpu_python_reference(bounded_knn_3d_kernel, **case),
        )

    def test_run_hiprt_matches_cpu_reference_for_3d_knn(self) -> None:
        case = self._case()
        self.assert_rows_close(
            rt.run_hiprt(knn_3d_kernel, **case),
            rt.run_cpu_python_reference(knn_3d_kernel, **case),
        )


class Goal549Hiprt3DKnnBoundaryTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[rt.Point3D, ...]]:
        points = (
            rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
            rt.Point3D(id=2, x=1.0, y=0.0, z=0.0),
        )
        return {"query_points": points, "search_points": points}

    def test_bounded_knn_rejects_oversized_kmax_before_backend_execution(self) -> None:
        with self.assertRaisesRegex(ValueError, "k_max <= 64"):
            rt.run_hiprt(bounded_knn_3d_kmax_over_cap_kernel, **self._case())

    def test_knn_rejects_oversized_k_before_backend_execution(self) -> None:
        with self.assertRaisesRegex(ValueError, "k_max <= 64"):
            rt.run_hiprt(knn_3d_k_over_cap_kernel, **self._case())


if __name__ == "__main__":
    unittest.main()
