from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixed_radius_neighbors_authored_case
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixture_fixed_radius_neighbors_case
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_natural_earth_fixed_radius_neighbors_case


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal198FixedRadiusNeighborsTruthPathTest(unittest.TestCase):
    def test_fixed_radius_neighbors_cpu_authored_rows(self) -> None:
        case = make_fixed_radius_neighbors_authored_case()
        rows = rt.fixed_radius_neighbors_cpu(
            case["query_points"],
            case["search_points"],
            radius=0.5,
            k_max=3,
        )
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["query_id"], 100)
        self.assertEqual(rows[0]["neighbor_id"], 1)
        self.assertTrue(math.isclose(rows[0]["distance"], 0.0, abs_tol=1e-12))
        self.assertEqual(rows[1]["neighbor_id"], 2)
        self.assertEqual(rows[2]["neighbor_id"], 3)
        self.assertTrue(math.isclose(rows[1]["distance"], 0.3, rel_tol=1e-9, abs_tol=1e-9))
        self.assertTrue(math.isclose(rows[2]["distance"], 0.3, rel_tol=1e-9, abs_tol=1e-9))
        self.assertEqual(rows[3]["query_id"], 101)
        self.assertEqual(rows[3]["neighbor_id"], 4)
        self.assertTrue(math.isclose(rows[3]["distance"], 0.2, rel_tol=1e-9, abs_tol=1e-9))

    def test_cpu_python_reference_runs_fixed_radius_neighbors_kernel(self) -> None:
        case = make_fixed_radius_neighbors_authored_case()
        rows = rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)
        self.assertEqual(tuple(row["neighbor_id"] for row in rows[:3]), (1, 2, 3))
        self.assertEqual(rows[-1]["query_id"], 101)
        self.assertEqual(rows[-1]["neighbor_id"], 4)

    def test_fixture_case_runs_on_cpu_python_reference(self) -> None:
        case = make_fixture_fixed_radius_neighbors_case()
        rows = rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)
        self.assertTrue(rows)
        self.assertTrue(all("query_id" in row and "neighbor_id" in row and "distance" in row for row in rows))

    def test_natural_earth_loader_and_case(self) -> None:
        points = rt.load_natural_earth_populated_places_geojson(
            REPO_ROOT / "tests" / "fixtures" / "public" / "natural_earth_populated_places_sample.geojson"
        )
        self.assertEqual(tuple(point.id for point in points), (101, 102, 103, 104))
        case = make_natural_earth_fixed_radius_neighbors_case()
        rows = rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["query_id"], 101)
        self.assertEqual(rows[1]["query_id"], 102)

    def test_baseline_runner_supports_fixed_radius_neighbors(self) -> None:
        payload = rt.run_baseline_case(
            fixed_radius_neighbors_reference,
            "authored_fixed_radius_neighbors_minimal",
            backend="cpu_python_reference",
        )
        self.assertEqual(payload["workload"], "fixed_radius_neighbors")
        self.assertEqual(
            tuple(payload["cpu_python_reference_rows"][index]["neighbor_id"] for index in range(3)),
            (1, 2, 3),
        )


if __name__ == "__main__":
    unittest.main()
