import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_3d_native_goal292():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_rows_3d_native_goal292():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


class Goal292V05Native3DFixedRadiusOracleTest(unittest.TestCase):
    def test_run_cpu_matches_python_reference_for_3d_fixed_radius_neighbors(self) -> None:
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
        expected = rt.run_cpu_python_reference(fixed_radius_neighbors_3d_native_goal292, **case)
        actual = rt.run_cpu(fixed_radius_neighbors_3d_native_goal292, **case)
        self.assertEqual(actual, expected)

    def test_run_cpu_still_rejects_3d_bounded_knn_rows(self) -> None:
        with self.assertRaisesRegex(ValueError, "run_cpu currently supports only 2D point nearest-neighbor records"):
            rt.run_cpu(
                bounded_knn_rows_3d_native_goal292,
                query_points=(rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),),
                search_points=(rt.Point3D(id=2, x=0.0, y=0.0, z=0.5),),
            )


if __name__ == "__main__":
    unittest.main()
