import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixed_radius_neighbors_authored_case
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixture_fixed_radius_neighbors_case
from tests.rtdsl_vulkan_test import vulkan_available


def _normalize(rows):
    return sorted(rows, key=lambda row: (row["query_id"], row["distance"], row["neighbor_id"]))


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_zero_radius_reference():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.0, k_max=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_truncated_reference():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@unittest.skipUnless(vulkan_available(), "Vulkan is not available in the current environment")
class Goal218FixedRadiusNeighborsVulkanTest(unittest.TestCase):
    def test_run_vulkan_matches_python_reference_on_authored_case(self) -> None:
        case = make_fixed_radius_neighbors_authored_case()
        vulkan_rows = _normalize(rt.run_vulkan(fixed_radius_neighbors_reference, **case))
        python_rows = _normalize(rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case))
        self.assertEqual(len(vulkan_rows), len(python_rows))
        for vulkan_row, python_row in zip(vulkan_rows, python_rows):
            self.assertEqual(vulkan_row["query_id"], python_row["query_id"])
            self.assertEqual(vulkan_row["neighbor_id"], python_row["neighbor_id"])
            self.assertTrue(math.isclose(vulkan_row["distance"], python_row["distance"], rel_tol=1e-6, abs_tol=1e-6))

    def test_run_vulkan_matches_python_reference_on_fixture_case(self) -> None:
        case = make_fixture_fixed_radius_neighbors_case()
        vulkan_rows = _normalize(rt.run_vulkan(fixed_radius_neighbors_reference, **case))
        python_rows = _normalize(rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case))
        self.assertEqual(len(vulkan_rows), len(python_rows))
        self.assertTrue(vulkan_rows)
        for vulkan_row, python_row in zip(vulkan_rows, python_rows):
            self.assertEqual(vulkan_row["query_id"], python_row["query_id"])
            self.assertEqual(vulkan_row["neighbor_id"], python_row["neighbor_id"])
            self.assertTrue(math.isclose(vulkan_row["distance"], python_row["distance"], rel_tol=1e-6, abs_tol=1e-6))

    def test_run_vulkan_matches_cpu_on_out_of_order_queries(self) -> None:
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
        vulkan_rows = rt.run_vulkan(fixed_radius_neighbors_reference, **case)
        self.assertEqual(tuple(row["query_id"] for row in vulkan_rows), (10, 10, 20))
        self.assertEqual(
            tuple(row["neighbor_id"] for row in vulkan_rows),
            tuple(row["neighbor_id"] for row in cpu_rows),
        )
        for vulkan_row, cpu_row in zip(vulkan_rows, cpu_rows):
            self.assertTrue(math.isclose(vulkan_row["distance"], cpu_row["distance"], rel_tol=1e-6, abs_tol=1e-6))

    def test_zero_radius_keeps_only_exact_matches(self) -> None:
        rows = rt.run_vulkan(
            fixed_radius_neighbors_zero_radius_reference,
            query_points=(
                rt.Point(id=10, x=0.0, y=0.0),
                rt.Point(id=20, x=2.0, y=0.0),
            ),
            search_points=(
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=0.001, y=0.0),
                rt.Point(id=3, x=2.0, y=0.0),
            ),
        )
        self.assertEqual(
            tuple((row["query_id"], row["neighbor_id"]) for row in rows),
            ((10, 1), (20, 3)),
        )

    def test_empty_inputs_return_no_rows(self) -> None:
        rows = rt.run_vulkan(
            fixed_radius_neighbors_reference,
            query_points=(),
            search_points=(rt.Point(id=1, x=0.0, y=0.0),),
        )
        self.assertEqual(len(rows), 0)
        rows = rt.run_vulkan(
            fixed_radius_neighbors_reference,
            query_points=(rt.Point(id=1, x=0.0, y=0.0),),
            search_points=(),
        )
        self.assertEqual(len(rows), 0)

    def test_k_max_truncates_to_closest_neighbors(self) -> None:
        rows = rt.run_vulkan(
            fixed_radius_neighbors_truncated_reference,
            query_points=(rt.Point(id=7, x=0.0, y=0.0),),
            search_points=(
                rt.Point(id=10, x=0.1, y=0.0),
                rt.Point(id=20, x=0.2, y=0.0),
                rt.Point(id=30, x=0.3, y=0.0),
                rt.Point(id=40, x=0.4, y=0.0),
            ),
        )
        self.assertEqual(
            tuple((row["query_id"], row["neighbor_id"]) for row in rows),
            ((7, 10), (7, 20)),
        )

    def test_run_vulkan_raw_mode_returns_expected_fields(self) -> None:
        case = make_fixed_radius_neighbors_authored_case()
        rows = rt.run_vulkan(fixed_radius_neighbors_reference, result_mode="raw", **case)
        try:
            self.assertEqual(rows.field_names, ("query_id", "neighbor_id", "distance"))
            self.assertEqual(len(rows), len(rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)))
        finally:
            rows.close()

    def test_output_ordering_contract(self) -> None:
        # Verify rows are grouped by ascending query_id, then within each group
        # ordered by ascending distance, then ascending neighbor_id.
        case = {
            "query_points": (
                rt.Point(id=5, x=0.0, y=0.0),
                rt.Point(id=2, x=1.0, y=0.0),
            ),
            "search_points": (
                rt.Point(id=10, x=0.1, y=0.0),
                rt.Point(id=20, x=0.2, y=0.0),
                rt.Point(id=30, x=0.3, y=0.0),
                rt.Point(id=1,  x=1.1, y=0.0),
                rt.Point(id=2,  x=1.2, y=0.0),
            ),
        }
        vulkan_rows = rt.run_vulkan(fixed_radius_neighbors_reference, **case)
        cpu_rows    = rt.run_cpu(fixed_radius_neighbors_reference, **case)
        self.assertEqual(len(vulkan_rows), len(cpu_rows))
        for vr, cr in zip(vulkan_rows, cpu_rows):
            self.assertEqual(vr["query_id"], cr["query_id"])
            self.assertEqual(vr["neighbor_id"], cr["neighbor_id"])
            self.assertTrue(math.isclose(vr["distance"], cr["distance"], rel_tol=1e-6, abs_tol=1e-6))
        # query_ids must be non-decreasing
        query_ids = [r["query_id"] for r in vulkan_rows]
        self.assertEqual(query_ids, sorted(query_ids))

    def test_large_coordinate_boundary_case_keeps_interior_neighbor(self) -> None:
        case = {
            "query_points": (
                rt.Point(id=1, x=2994.268071, y=1470.581977),
            ),
            "search_points": (
                rt.Point(id=10, x=2994.268071, y=1470.581977),
                rt.Point(id=20, x=2994.168071, y=1470.581977),
                rt.Point(id=30, x=2993.900014, y=1470.920398),
            ),
        }
        cpu_rows = rt.run_cpu(fixed_radius_neighbors_reference, **case)
        vulkan_rows = rt.run_vulkan(fixed_radius_neighbors_reference, **case)
        self.assertEqual(tuple(row["neighbor_id"] for row in cpu_rows), (10, 20, 30))
        self.assertEqual(tuple(row["neighbor_id"] for row in vulkan_rows), (10, 20, 30))
        self.assertTrue(math.isclose(vulkan_rows[-1]["distance"], cpu_rows[-1]["distance"], rel_tol=1e-12, abs_tol=1e-12))


if __name__ == "__main__":
    unittest.main()
