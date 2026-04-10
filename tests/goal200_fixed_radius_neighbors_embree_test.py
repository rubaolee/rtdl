import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixed_radius_neighbors_authored_case
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixture_fixed_radius_neighbors_case
from tests._embree_support import embree_available


@unittest.skipUnless(embree_available(), "Embree runtime is not available")
class Goal200FixedRadiusNeighborsEmbreeTest(unittest.TestCase):
    def test_run_embree_matches_python_reference_on_authored_case(self) -> None:
        case = make_fixed_radius_neighbors_authored_case()
        embree_rows = rt.run_embree(fixed_radius_neighbors_reference, **case)
        python_rows = rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)
        self.assertEqual(len(embree_rows), len(python_rows))
        for embree_row, python_row in zip(embree_rows, python_rows):
            self.assertEqual(embree_row["query_id"], python_row["query_id"])
            self.assertEqual(embree_row["neighbor_id"], python_row["neighbor_id"])
            self.assertTrue(math.isclose(embree_row["distance"], python_row["distance"], rel_tol=1e-12, abs_tol=1e-12))

    def test_run_embree_matches_python_reference_on_fixture_case(self) -> None:
        case = make_fixture_fixed_radius_neighbors_case()
        embree_rows = rt.run_embree(fixed_radius_neighbors_reference, **case)
        python_rows = rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)
        self.assertEqual(len(embree_rows), len(python_rows))
        self.assertTrue(embree_rows)
        for embree_row, python_row in zip(embree_rows, python_rows):
            self.assertEqual(embree_row["query_id"], python_row["query_id"])
            self.assertEqual(embree_row["neighbor_id"], python_row["neighbor_id"])
            self.assertTrue(math.isclose(embree_row["distance"], python_row["distance"], rel_tol=1e-12, abs_tol=1e-12))

    def test_run_embree_matches_cpu_on_out_of_order_queries(self) -> None:
        case = {
            "query_points": (
                rt.Point(id=20, x=3.0, y=0.0),
                rt.Point(id=10, x=0.0, y=0.0),
            ),
            "search_points": (
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=3.0, y=0.0),
                rt.Point(id=3, x=0.25, y=0.0),
            ),
        }
        cpu_rows = rt.run_cpu(fixed_radius_neighbors_reference, **case)
        embree_rows = rt.run_embree(fixed_radius_neighbors_reference, **case)
        self.assertEqual(cpu_rows, embree_rows)
        self.assertEqual(tuple(row["query_id"] for row in embree_rows), (10, 10, 20))

    def test_run_embree_raw_mode_returns_expected_fields(self) -> None:
        case = make_fixed_radius_neighbors_authored_case()
        rows = rt.run_embree(fixed_radius_neighbors_reference, result_mode="raw", **case)
        try:
            self.assertEqual(rows.field_names, ("query_id", "neighbor_id", "distance"))
            self.assertEqual(len(rows), len(rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)))
        finally:
            rows.close()

    def test_baseline_runner_embree_backend_supports_fixed_radius_neighbors(self) -> None:
        payload = rt.run_baseline_case(
            fixed_radius_neighbors_reference,
            "authored_fixed_radius_neighbors_minimal",
            backend="embree",
        )
        self.assertEqual(payload["workload"], "fixed_radius_neighbors")
        self.assertIn("embree_rows", payload)
        self.assertEqual(tuple(row["neighbor_id"] for row in payload["embree_rows"][:3]), (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
