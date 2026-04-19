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
def fixed_radius_3d_kernel():
    queries = rt.input("queries", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    points = rt.input("points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(queries, points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.1, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_3d_kernel():
    queries = rt.input("queries", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    points = rt.input("points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(queries, points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.1, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_3d_kernel():
    queries = rt.input("queries", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    points = rt.input("points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(queries, points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def _assert_rows_almost_equal(testcase: unittest.TestCase, actual, expected) -> None:
    testcase.assertEqual(len(actual), len(expected))
    for actual_row, expected_row in zip(actual, expected):
        testcase.assertEqual(set(actual_row), set(expected_row))
        for key, expected_value in expected_row.items():
            actual_value = actual_row[key]
            if isinstance(expected_value, float):
                testcase.assertAlmostEqual(float(actual_value), expected_value, places=5)
            else:
                testcase.assertEqual(actual_value, expected_value)


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal606AppleRtPointNeighbor3DNativeTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[rt.Point3D, ...]]:
        return {
            "queries": (
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=5.0, y=0.0, z=0.0),
            ),
            "points": (
                rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=11, x=0.0, y=0.0, z=0.6),
                rt.Point3D(id=12, x=0.0, y=0.8, z=0.0),
                rt.Point3D(id=13, x=5.0, y=0.0, z=0.9),
            ),
        }

    def test_fixed_radius_native_only_matches_cpu(self) -> None:
        case = self._case()
        actual = rt.run_apple_rt(fixed_radius_3d_kernel, native_only=True, **case)
        expected = rt.run_cpu_python_reference(fixed_radius_3d_kernel, **case)
        _assert_rows_almost_equal(self, actual, expected)

    def test_bounded_knn_native_only_matches_cpu(self) -> None:
        case = self._case()
        actual = rt.run_apple_rt(bounded_knn_3d_kernel, native_only=True, **case)
        expected = rt.run_cpu_python_reference(bounded_knn_3d_kernel, **case)
        _assert_rows_almost_equal(self, actual, expected)

    def test_knn_native_only_matches_cpu(self) -> None:
        case = self._case()
        actual = rt.run_apple_rt(knn_3d_kernel, native_only=True, **case)
        expected = rt.run_cpu_python_reference(knn_3d_kernel, **case)
        _assert_rows_almost_equal(self, actual, expected)

    def test_direct_fixed_radius_helper_matches_cpu(self) -> None:
        case = self._case()
        actual = tuple(rt.fixed_radius_neighbors_3d_apple_rt(case["queries"], case["points"], radius=1.1, k_max=3))
        expected = rt.fixed_radius_neighbors_cpu(case["queries"], case["points"], radius=1.1, k_max=3)
        _assert_rows_almost_equal(self, actual, expected)


if __name__ == "__main__":
    unittest.main()
