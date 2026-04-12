import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_rows_3d_native_goal296():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


class Goal296V05Native3DKnnOracleTest(unittest.TestCase):
    def test_run_cpu_matches_python_reference_for_3d_knn_rows(self) -> None:
        case = {
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
        expected = rt.run_cpu_python_reference(knn_rows_3d_native_goal296, **case)
        actual = rt.run_cpu(knn_rows_3d_native_goal296, **case)
        self.assertEqual(actual, expected)

    def test_run_cpu_orders_ties_by_neighbor_id_for_3d_knn_rows(self) -> None:
        case = {
            "query_points": (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),),
            "search_points": (
                rt.Point3D(id=8, x=1.0, y=0.0, z=0.0),
                rt.Point3D(id=7, x=0.0, y=1.0, z=0.0),
                rt.Point3D(id=6, x=0.0, y=0.0, z=2.0),
            ),
        }
        actual = rt.run_cpu(knn_rows_3d_native_goal296, **case)
        self.assertEqual(
            actual,
            (
                {"query_id": 1, "neighbor_id": 7, "distance": 1.0, "neighbor_rank": 1},
                {"query_id": 1, "neighbor_id": 8, "distance": 1.0, "neighbor_rank": 2},
            ),
        )


if __name__ == "__main__":
    unittest.main()
