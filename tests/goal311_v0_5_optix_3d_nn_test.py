import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from tests.rtdl_sorting_test import optix_available


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_3d_optix_goal311():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_rows_3d_optix_goal311():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_rows_3d_optix_goal311():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@unittest.skipUnless(optix_available(), "OptiX is not available in the current environment")
class Goal311V05Optix3DNnTest(unittest.TestCase):
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
            ),
        }

    def test_run_optix_matches_python_reference_for_3d_fixed_radius(self) -> None:
        case = self._case()
        optix_rows = rt.run_optix(fixed_radius_neighbors_3d_optix_goal311, **case)
        python_rows = rt.run_cpu_python_reference(fixed_radius_neighbors_3d_optix_goal311, **case)
        self.assertEqual(len(optix_rows), len(python_rows))
        for optix_row, python_row in zip(optix_rows, python_rows):
            self.assertEqual(optix_row["query_id"], python_row["query_id"])
            self.assertEqual(optix_row["neighbor_id"], python_row["neighbor_id"])
            self.assertTrue(math.isclose(optix_row["distance"], python_row["distance"], rel_tol=1e-6, abs_tol=1e-6))

    def test_run_optix_matches_python_reference_for_3d_bounded_knn(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_optix(bounded_knn_rows_3d_optix_goal311, **case),
            rt.run_cpu_python_reference(bounded_knn_rows_3d_optix_goal311, **case),
        )

    def test_run_optix_matches_python_reference_for_3d_knn(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_optix(knn_rows_3d_optix_goal311, **case),
            rt.run_cpu_python_reference(knn_rows_3d_optix_goal311, **case),
        )

    def test_prepared_optix_matches_direct_for_3d_knn(self) -> None:
        case = self._case()
        prepared = rt.prepare_optix(knn_rows_3d_optix_goal311)
        self.assertEqual(prepared.run(**case), rt.run_optix(knn_rows_3d_optix_goal311, **case))


if __name__ == "__main__":
    unittest.main()
