import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from examples.reference.rtdl_knn_rows_reference import make_fixture_knn_rows_case
from examples.reference.rtdl_knn_rows_reference import make_knn_rows_authored_case
from tests.rtdl_sorting_test import optix_available


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_rows_tied_reference():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@unittest.skipUnless(optix_available(), "OptiX runtime is not available")
class Goal217KnnRowsOptixTest(unittest.TestCase):
    def test_run_optix_matches_python_reference_on_authored_case(self) -> None:
        case = make_knn_rows_authored_case()
        optix_rows = rt.run_optix(knn_rows_reference, **case)
        python_rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(len(optix_rows), len(python_rows))
        for optix_row, python_row in zip(optix_rows, python_rows):
            self.assertEqual(optix_row["query_id"], python_row["query_id"])
            self.assertEqual(optix_row["neighbor_id"], python_row["neighbor_id"])
            self.assertEqual(optix_row["neighbor_rank"], python_row["neighbor_rank"])
            self.assertTrue(math.isclose(optix_row["distance"], python_row["distance"], rel_tol=1e-6, abs_tol=1e-6))

    def test_run_optix_matches_python_reference_on_fixture_case(self) -> None:
        case = make_fixture_knn_rows_case()
        optix_rows = rt.run_optix(knn_rows_reference, **case)
        python_rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(len(optix_rows), len(python_rows))
        self.assertTrue(optix_rows)
        for optix_row, python_row in zip(optix_rows, python_rows):
            self.assertEqual(optix_row["query_id"], python_row["query_id"])
            self.assertEqual(optix_row["neighbor_id"], python_row["neighbor_id"])
            self.assertEqual(optix_row["neighbor_rank"], python_row["neighbor_rank"])
            self.assertTrue(math.isclose(optix_row["distance"], python_row["distance"], rel_tol=1e-6, abs_tol=1e-6))

    def test_run_optix_matches_cpu_on_out_of_order_queries(self) -> None:
        case = {
            "query_points": (
                rt.Point(id=20, x=3.0, y=0.0),
                rt.Point(id=10, x=0.0, y=0.0),
            ),
            "search_points": (
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=0.4, y=0.0),
                rt.Point(id=3, x=3.0, y=0.0),
            ),
        }
        cpu_rows = rt.run_cpu(knn_rows_reference, **case)
        optix_rows = rt.run_optix(knn_rows_reference, **case)
        self.assertEqual(len(cpu_rows), len(optix_rows))
        for cpu_row, optix_row in zip(cpu_rows, optix_rows):
            self.assertEqual(cpu_row["query_id"], optix_row["query_id"])
            self.assertEqual(cpu_row["neighbor_id"], optix_row["neighbor_id"])
            self.assertEqual(cpu_row["neighbor_rank"], optix_row["neighbor_rank"])
            self.assertTrue(math.isclose(cpu_row["distance"], optix_row["distance"], rel_tol=1e-6, abs_tol=1e-6))
        self.assertEqual(tuple(row["query_id"] for row in optix_rows), (10, 10, 10, 20, 20, 20))

    def test_run_optix_tie_breaks_by_neighbor_id(self) -> None:
        case = {
            "query_points": (rt.Point(id=10, x=0.0, y=0.0),),
            "search_points": (
                rt.Point(id=7, x=-1.0, y=0.0),
                rt.Point(id=3, x=1.0, y=0.0),
                rt.Point(id=5, x=2.0, y=0.0),
            ),
        }
        cpu_rows = rt.run_cpu(knn_rows_tied_reference, **case)
        optix_rows = rt.run_optix(knn_rows_tied_reference, **case)
        self.assertEqual(cpu_rows, optix_rows)
        self.assertEqual(tuple(row["neighbor_id"] for row in optix_rows), (3, 7))
        self.assertEqual(tuple(row["neighbor_rank"] for row in optix_rows), (1, 2))

    def test_run_optix_raw_mode_returns_expected_fields(self) -> None:
        case = make_knn_rows_authored_case()
        rows = rt.run_optix(knn_rows_reference, result_mode="raw", **case)
        try:
            self.assertEqual(rows.field_names, ("query_id", "neighbor_id", "distance", "neighbor_rank"))
            self.assertEqual(len(rows), len(rt.run_cpu_python_reference(knn_rows_reference, **case)))
        finally:
            rows.close()


if __name__ == "__main__":
    unittest.main()
