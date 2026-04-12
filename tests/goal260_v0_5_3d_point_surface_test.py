import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_3d_reference():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_rows_3d_reference():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


class Goal260V05Point3DSurfaceTest(unittest.TestCase):
    def test_points3d_type_is_exposed(self) -> None:
        self.assertEqual(rt.Point3DLayout.field_names(), ("x", "y", "z", "id"))
        self.assertEqual(rt.Points3D.required_fields, ("x", "y", "z", "id"))

    def test_fixed_radius_neighbors_cpu_supports_point3d(self) -> None:
        rows = rt.fixed_radius_neighbors_cpu(
            (
                rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=20, x=5.0, y=0.0, z=0.0),
            ),
            (
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.6),
                rt.Point3D(id=3, x=0.0, y=0.8, z=0.0),
                rt.Point3D(id=4, x=5.0, y=0.0, z=0.9),
            ),
            radius=1.0,
            k_max=3,
        )
        self.assertEqual(
            rows,
            (
                {"query_id": 10, "neighbor_id": 1, "distance": 0.0},
                {"query_id": 10, "neighbor_id": 2, "distance": 0.6},
                {"query_id": 10, "neighbor_id": 3, "distance": 0.8},
                {"query_id": 20, "neighbor_id": 4, "distance": 0.9},
            ),
        )

    def test_knn_rows_cpu_supports_point3d(self) -> None:
        rows = rt.knn_rows_cpu(
            (rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),),
            (
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.5),
                rt.Point3D(id=3, x=0.0, y=0.8, z=0.0),
            ),
            k=2,
        )
        self.assertEqual(rows[0]["neighbor_id"], 1)
        self.assertEqual(rows[0]["neighbor_rank"], 1)
        self.assertTrue(math.isclose(rows[1]["distance"], 0.5, rel_tol=1e-9, abs_tol=1e-9))
        self.assertEqual(rows[1]["neighbor_rank"], 2)

    def test_run_cpu_python_reference_supports_points3d(self) -> None:
        rows = rt.run_cpu_python_reference(
            fixed_radius_neighbors_3d_reference,
            query_points=(rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),),
            search_points=(
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.5),
            ),
        )
        self.assertEqual(tuple(row["neighbor_id"] for row in rows), (1, 2))

    def test_run_cpu_supports_points3d_for_fixed_radius_neighbors(self) -> None:
        rows = rt.run_cpu(
            fixed_radius_neighbors_3d_reference,
            query_points=(rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),),
            search_points=(
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.5),
            ),
        )
        self.assertEqual(tuple(row["neighbor_id"] for row in rows), (1, 2))

    def test_run_cpu_python_reference_supports_knn_rows_points3d(self) -> None:
        rows = rt.run_cpu_python_reference(
            knn_rows_3d_reference,
            query_points=(rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),),
            search_points=(
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.25),
                rt.Point3D(id=3, x=0.0, y=1.0, z=0.0),
            ),
        )
        self.assertEqual(
            rows,
            (
                {"query_id": 10, "neighbor_id": 1, "distance": 0.0, "neighbor_rank": 1},
                {"query_id": 10, "neighbor_id": 2, "distance": 0.25, "neighbor_rank": 2},
            ),
        )


if __name__ == "__main__":
    unittest.main()
