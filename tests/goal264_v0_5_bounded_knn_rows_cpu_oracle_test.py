import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_rows_oracle_reference():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=0.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


class Goal264V05BoundedKnnRowsCpuOracleTest(unittest.TestCase):
    def test_run_cpu_matches_python_reference_for_bounded_knn_rows(self) -> None:
        case = {
            "query_points": (
                rt.Point(id=100, x=0.0, y=0.0),
                rt.Point(id=101, x=3.0, y=0.0),
            ),
            "search_points": (
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=0.3, y=0.0),
                rt.Point(id=3, x=-0.3, y=0.0),
                rt.Point(id=4, x=3.2, y=0.0),
                rt.Point(id=5, x=4.0, y=0.0),
            ),
        }
        expected = rt.run_cpu_python_reference(bounded_knn_rows_oracle_reference, **case)
        actual = rt.run_cpu(bounded_knn_rows_oracle_reference, **case)
        self.assertEqual(actual, expected)

    def test_rows_are_radius_bounded_and_ranked(self) -> None:
        rows = rt.run_cpu(
            bounded_knn_rows_oracle_reference,
            query_points=(rt.Point(id=10, x=0.0, y=0.0),),
            search_points=(
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=0.4, y=0.0),
                rt.Point(id=3, x=0.8, y=0.0),
            ),
        )
        self.assertEqual(
            rows,
            (
                {"query_id": 10, "neighbor_id": 1, "distance": 0.0, "neighbor_rank": 1},
                {"query_id": 10, "neighbor_id": 2, "distance": 0.4, "neighbor_rank": 2},
            ),
        )


if __name__ == "__main__":
    unittest.main()
