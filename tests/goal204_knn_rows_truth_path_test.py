from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from examples.reference.rtdl_knn_rows_reference import make_fixture_knn_rows_case
from examples.reference.rtdl_knn_rows_reference import make_knn_rows_authored_case
from examples.reference.rtdl_knn_rows_reference import make_natural_earth_knn_rows_case


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal204KnnRowsTruthPathTest(unittest.TestCase):
    def test_knn_rows_cpu_authored_rows(self) -> None:
        case = make_knn_rows_authored_case()
        rows = rt.knn_rows_cpu(
            case["query_points"],
            case["search_points"],
            k=3,
        )
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0]["query_id"], 100)
        self.assertEqual(rows[0]["neighbor_id"], 1)
        self.assertEqual(rows[0]["neighbor_rank"], 1)
        self.assertTrue(math.isclose(rows[0]["distance"], 0.0, abs_tol=1e-12))
        self.assertEqual((rows[1]["neighbor_id"], rows[1]["neighbor_rank"]), (2, 2))
        self.assertEqual((rows[2]["neighbor_id"], rows[2]["neighbor_rank"]), (3, 3))
        self.assertEqual(rows[3]["query_id"], 101)
        self.assertEqual(rows[3]["neighbor_rank"], 1)

    def test_cpu_python_reference_runs_knn_rows_kernel(self) -> None:
        case = make_knn_rows_authored_case()
        rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(tuple(row["neighbor_rank"] for row in rows[:3]), (1, 2, 3))
        self.assertEqual(rows[-1]["query_id"], 101)

    def test_fixture_case_runs_on_cpu_python_reference(self) -> None:
        case = make_fixture_knn_rows_case()
        rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertTrue(rows)
        self.assertTrue(all("neighbor_rank" in row for row in rows))

    def test_natural_earth_loader_and_case(self) -> None:
        points = rt.load_natural_earth_populated_places_geojson(
            REPO_ROOT / "tests" / "fixtures" / "public" / "natural_earth_populated_places_sample.geojson"
        )
        self.assertEqual(tuple(point.id for point in points), (101, 102, 103, 104))
        case = make_natural_earth_knn_rows_case()
        rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0]["neighbor_rank"], 1)

    def test_baseline_runner_supports_knn_rows(self) -> None:
        payload = rt.run_baseline_case(
            knn_rows_reference,
            "authored_knn_rows_minimal",
            backend="cpu_python_reference",
        )
        self.assertEqual(payload["workload"], "knn_rows")
        self.assertEqual(
            tuple(payload["cpu_python_reference_rows"][index]["neighbor_rank"] for index in range(3)),
            (1, 2, 3),
        )

    def test_rows_are_grouped_by_ascending_query_id(self) -> None:
        rows = rt.knn_rows_cpu(
            (
                rt.Point(id=20, x=3.0, y=0.0),
                rt.Point(id=10, x=0.0, y=0.0),
            ),
            (
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=3.0, y=0.0),
            ),
            k=2,
        )
        self.assertEqual(tuple(row["query_id"] for row in rows), (10, 10, 20, 20))
        self.assertEqual(tuple(row["neighbor_rank"] for row in rows[:2]), (1, 2))

    def test_short_result_emits_available_rows_without_padding(self) -> None:
        rows = rt.knn_rows_cpu(
            (rt.Point(id=10, x=1.0, y=1.0),),
            (rt.Point(id=1, x=1.0, y=1.0),),
            k=4,
        )
        self.assertEqual(
            rows,
            ({"query_id": 10, "neighbor_id": 1, "distance": 0.0, "neighbor_rank": 1},),
        )
