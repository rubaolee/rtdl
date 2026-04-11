import math
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
import rtdsl.baseline_runner as baseline_runner
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from examples.reference.rtdl_knn_rows_reference import make_knn_rows_authored_case
from examples.reference.rtdl_knn_rows_reference import make_natural_earth_knn_rows_case


class _FakeKDTree:
    def __init__(self, points):
        self._points = tuple(points)

    def query(self, query_point, k):
        qx, qy = query_point
        distances = []
        for index, (x, y) in enumerate(self._points):
            distances.append((math.hypot(x - qx, y - qy), index))
        distances.sort(key=lambda item: (item[0], item[1]))
        top = distances[:k]
        if k == 1:
            return top[0][0], top[0][1]
        return [item[0] for item in top], [item[1] for item in top]


class _FakePostgisCursor:
    def __init__(self, connection):
        self._connection = connection
        self._rows = []
        self._executed_sql = connection.executed_sql

    def execute(self, sql, params=None):
        self._executed_sql.append(sql.strip())
        if "CREATE TEMP TABLE" in sql:
            return
        if "CREATE INDEX" in sql or sql.strip().startswith("ANALYZE"):
            return
        if "CROSS JOIN LATERAL" in sql:
            (k,) = params
            rows = []
            for query_point in self._connection.query_points:
                candidates = []
                for search_point in self._connection.search_points:
                    distance = math.hypot(search_point.x - query_point.x, search_point.y - query_point.y)
                    candidates.append((distance, search_point.id))
                candidates.sort(key=lambda item: (item[0], item[1]))
                for rank, (distance, neighbor_id) in enumerate(candidates[:k], start=1):
                    rows.append((query_point.id, neighbor_id, distance, rank))
            rows.sort(key=lambda row: (row[0], row[3]))
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
        self.executed_sql = []

    def cursor(self):
        return _FakePostgisCursor(self)

    def close(self):
        self.closed = True


class Goal207KnnRowsExternalBaselinesTest(unittest.TestCase):
    def test_scipy_baseline_matches_python_reference_on_authored_case(self) -> None:
        case = make_knn_rows_authored_case()
        scipy_rows = rt.run_scipy_knn_rows(
            case["query_points"],
            case["search_points"],
            k=3,
            tree_factory=_FakeKDTree,
        )
        python_rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(scipy_rows, python_rows)

    def test_scipy_baseline_sorts_out_of_order_query_ids(self) -> None:
        rows = rt.run_scipy_knn_rows(
            (
                rt.Point(id=20, x=3.0, y=0.0),
                rt.Point(id=10, x=0.0, y=0.0),
            ),
            (
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=0.4, y=0.0),
                rt.Point(id=3, x=3.0, y=0.0),
            ),
            k=3,
            tree_factory=_FakeKDTree,
        )
        self.assertEqual(tuple(row["query_id"] for row in rows), (10, 10, 10, 20, 20, 20))

    def test_postgis_sql_contains_expected_nearest_order_shape(self) -> None:
        sql = rt.build_postgis_knn_rows_sql()
        self.assertIn("CROSS JOIN LATERAL", sql)
        self.assertIn("<->", sql)
        self.assertIn("neighbor_rank", sql)
        self.assertIn("ORDER BY query_id, neighbor_rank", sql)

    def test_postgis_runner_matches_python_reference_with_fake_connection(self) -> None:
        case = make_knn_rows_authored_case()
        connection = _FakePostgisConnection()
        rows = rt.run_postgis_knn_rows(
            connection,
            case["query_points"],
            case["search_points"],
            k=3,
        )
        python_rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(rows, python_rows)
        self.assertTrue(any("CREATE INDEX rtdl_query_points_tmp_geom_gist" in sql for sql in connection.executed_sql))
        self.assertTrue(any("CREATE INDEX rtdl_search_points_tmp_geom_gist" in sql for sql in connection.executed_sql))

    def test_baseline_runner_supports_scipy_backend(self) -> None:
        case = make_knn_rows_authored_case()
        python_rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        with patch.object(
            baseline_runner,
            "run_scipy_knn_rows",
            return_value=python_rows,
        ):
            payload = rt.run_baseline_case(
                knn_rows_reference,
                "authored_knn_rows_minimal",
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
                knn_rows_reference,
                "authored_knn_rows_minimal",
                backend="postgis",
                postgis_dsn="dbname=fake",
            )
        self.assertTrue(payload["parity"])
        self.assertIn("postgis_rows", payload)

    def test_natural_earth_case_runs_through_fake_scipy_baseline(self) -> None:
        case = make_natural_earth_knn_rows_case()
        scipy_rows = rt.run_scipy_knn_rows(
            case["query_points"],
            case["search_points"],
            k=3,
            tree_factory=_FakeKDTree,
        )
        python_rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(scipy_rows, python_rows)


if __name__ == "__main__":
    unittest.main()
