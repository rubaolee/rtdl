import math
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
import rtdsl.baseline_runner as baseline_runner
from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixed_radius_neighbors_authored_case
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_natural_earth_fixed_radius_neighbors_case


class _FakeKDTree:
    def __init__(self, points):
        self._points = tuple(points)

    def query_ball_point(self, query_point, r):
        qx, qy = query_point
        radius_sq = r * r
        return [
            index
            for index, (x, y) in enumerate(self._points)
            if (x - qx) * (x - qx) + (y - qy) * (y - qy) <= radius_sq
        ]


class _FakePostgisCursor:
    def __init__(self, connection):
        self._connection = connection
        self._rows = []

    def execute(self, sql, params=None):
        if "CREATE TEMP TABLE" in sql:
            return
        if "WITH ranked_neighbors AS" in sql:
            radius, k_max = params
            rows = []
            for query_point in self._connection.query_points:
                candidates = []
                for search_point in self._connection.search_points:
                    distance = math.hypot(search_point.x - query_point.x, search_point.y - query_point.y)
                    if distance <= radius:
                        candidates.append((distance, search_point.id))
                candidates.sort(key=lambda item: (item[0], item[1]))
                for distance, neighbor_id in candidates[:k_max]:
                    rows.append((query_point.id, neighbor_id, distance))
            rows.sort(key=lambda row: (row[0], row[2], row[1]))
            self._rows = rows

    def executemany(self, sql, payload):
        rows = list(payload)
        if "rtdl_query_points_tmp" in sql:
            self._connection.query_points = tuple(
                rt.Point(id=int(row[0]), x=float(row[1]), y=float(row[2])) for row in rows
            )
            return
        if "rtdl_search_points_tmp" in sql:
            self._connection.search_points = tuple(
                rt.Point(id=int(row[0]), x=float(row[1]), y=float(row[2])) for row in rows
            )
            return
        raise AssertionError(f"unexpected executemany SQL: {sql}")

    def fetchall(self):
        return list(self._rows)

    def close(self):
        return


class _FakePostgisConnection:
    def __init__(self):
        self.query_points = ()
        self.search_points = ()
        self.closed = False

    def cursor(self):
        return _FakePostgisCursor(self)

    def close(self):
        self.closed = True


class Goal201FixedRadiusNeighborsExternalBaselinesTest(unittest.TestCase):
    def test_scipy_baseline_matches_python_reference_on_authored_case(self) -> None:
        case = make_fixed_radius_neighbors_authored_case()
        scipy_rows = rt.run_scipy_fixed_radius_neighbors(
            case["query_points"],
            case["search_points"],
            radius=0.5,
            k_max=3,
            tree_factory=_FakeKDTree,
        )
        python_rows = rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)
        self.assertEqual(scipy_rows, python_rows)

    def test_scipy_baseline_sorts_out_of_order_query_ids(self) -> None:
        rows = rt.run_scipy_fixed_radius_neighbors(
            (
                rt.Point(id=20, x=3.0, y=0.0),
                rt.Point(id=10, x=0.0, y=0.0),
            ),
            (
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=3.0, y=0.0),
                rt.Point(id=3, x=0.25, y=0.0),
            ),
            radius=0.5,
            k_max=4,
            tree_factory=_FakeKDTree,
        )
        self.assertEqual(tuple(row["query_id"] for row in rows), (10, 10, 20))

    def test_postgis_sql_contains_expected_radius_and_ranking_shapes(self) -> None:
        sql = rt.build_postgis_fixed_radius_neighbors_sql()
        self.assertIn("ST_DWithin", sql)
        self.assertIn("ROW_NUMBER() OVER", sql)
        self.assertIn("ORDER BY query_id, distance, neighbor_id", sql)

    def test_postgis_runner_matches_python_reference_with_fake_connection(self) -> None:
        case = make_fixed_radius_neighbors_authored_case()
        rows = rt.run_postgis_fixed_radius_neighbors(
            _FakePostgisConnection(),
            case["query_points"],
            case["search_points"],
            radius=0.5,
            k_max=3,
        )
        python_rows = rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)
        self.assertEqual(rows, python_rows)

    def test_baseline_runner_supports_scipy_backend(self) -> None:
        case = make_fixed_radius_neighbors_authored_case()
        python_rows = rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)
        with patch.object(
            baseline_runner,
            "run_scipy_fixed_radius_neighbors",
            return_value=python_rows,
        ):
            payload = rt.run_baseline_case(
                fixed_radius_neighbors_reference,
                "authored_fixed_radius_neighbors_minimal",
                backend="scipy",
            )
        self.assertTrue(payload["parity"])
        self.assertEqual(payload["scipy_rows"], python_rows)

    def test_baseline_runner_supports_postgis_backend(self) -> None:
        with patch.object(
            baseline_runner,
            "connect_postgis",
            return_value=_FakePostgisConnection(),
        ):
            payload = rt.run_baseline_case(
                fixed_radius_neighbors_reference,
                "authored_fixed_radius_neighbors_minimal",
                backend="postgis",
                postgis_dsn="dbname=fake",
            )
        self.assertTrue(payload["parity"])
        self.assertIn("postgis_rows", payload)

    def test_natural_earth_case_runs_through_fake_scipy_baseline(self) -> None:
        case = make_natural_earth_fixed_radius_neighbors_case()
        scipy_rows = rt.run_scipy_fixed_radius_neighbors(
            case["query_points"],
            case["search_points"],
            radius=0.5,
            k_max=3,
            tree_factory=_FakeKDTree,
        )
        python_rows = rt.run_cpu_python_reference(fixed_radius_neighbors_reference, **case)
        self.assertEqual(scipy_rows, python_rows)


if __name__ == "__main__":
    unittest.main()
