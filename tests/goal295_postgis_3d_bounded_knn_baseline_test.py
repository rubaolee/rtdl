import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class _FakePostgis3DBoundedKnnCursor:
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
        if "ST_3DDWithin" in sql and "neighbor_rank" in sql:
            radius, k_max = params
            rows = []
            for query_point in self._connection.query_points:
                candidates = []
                for search_point in self._connection.search_points:
                    dx = search_point.x - query_point.x
                    dy = search_point.y - query_point.y
                    dz = search_point.z - query_point.z
                    distance = math.sqrt(dx * dx + dy * dy + dz * dz)
                    if distance <= radius:
                        candidates.append((distance, search_point.id))
                candidates.sort(key=lambda item: (item[0], item[1]))
                for rank, (distance, neighbor_id) in enumerate(candidates[:k_max], start=1):
                    rows.append((query_point.id, neighbor_id, distance, rank))
            rows.sort(key=lambda row: (row[0], row[3]))
            self._rows = rows

    def executemany(self, sql, payload):
        rows = list(payload)
        if "rtdl_query_points3d_tmp" in sql:
            self._connection.query_points = tuple(
                rt.Point3D(id=int(row[0]), x=float(row[1]), y=float(row[2]), z=float(row[3]))
                for row in rows
            )
            return
        if "rtdl_search_points3d_tmp" in sql:
            self._connection.search_points = tuple(
                rt.Point3D(id=int(row[0]), x=float(row[1]), y=float(row[2]), z=float(row[3]))
                for row in rows
            )
            return
        raise AssertionError(f"unexpected executemany SQL: {sql}")

    def fetchall(self):
        return list(self._rows)

    def close(self):
        return


class _FakePostgis3DBoundedKnnConnection:
    def __init__(self):
        self.query_points = ()
        self.search_points = ()
        self.executed_sql = []

    def cursor(self):
        return _FakePostgis3DBoundedKnnCursor(self)

    def close(self):
        return


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_rows_3d_goal295():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


class Goal295Postgis3DBoundedKnnBaselineTest(unittest.TestCase):
    def test_postgis_3d_bounded_knn_sql_contains_expected_3d_predicates(self) -> None:
        sql = rt.build_postgis_bounded_knn_rows_3d_sql()
        self.assertIn("ST_3DDWithin", sql)
        self.assertIn("ST_3DDistance", sql)
        self.assertIn("neighbor_rank", sql)
        self.assertIn("PARTITION BY q.id", sql)

    def test_postgis_3d_bounded_knn_runner_matches_python_reference(self) -> None:
        query_points = (
            rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),
            rt.Point3D(id=20, x=5.0, y=0.0, z=0.0),
        )
        search_points = (
            rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
            rt.Point3D(id=2, x=0.0, y=0.0, z=0.6),
            rt.Point3D(id=3, x=0.0, y=0.8, z=0.0),
            rt.Point3D(id=4, x=5.0, y=0.0, z=0.9),
        )
        connection = _FakePostgis3DBoundedKnnConnection()
        rows = rt.run_postgis_bounded_knn_rows_3d(
            connection,
            query_points,
            search_points,
            radius=1.0,
            k_max=2,
        )
        python_rows = rt.run_cpu_python_reference(
            bounded_knn_rows_3d_goal295,
            query_points=query_points,
            search_points=search_points,
        )
        self.assertEqual(rows, python_rows)
        self.assertTrue(any("geometry(PointZ, 0)" in sql for sql in connection.executed_sql))
        self.assertTrue(any("gist_geometry_ops_nd" in sql for sql in connection.executed_sql))

    def test_postgis_3d_bounded_knn_runner_obeys_k_max_and_rank(self) -> None:
        connection = _FakePostgis3DBoundedKnnConnection()
        rows = rt.run_postgis_bounded_knn_rows_3d(
            connection,
            query_points=(rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),),
            search_points=(
                rt.Point3D(id=10, x=0.1, y=0.0, z=0.0),
                rt.Point3D(id=11, x=0.2, y=0.0, z=0.0),
                rt.Point3D(id=12, x=0.3, y=0.0, z=0.0),
            ),
            radius=1.0,
            k_max=2,
        )
        self.assertEqual(tuple(row["neighbor_id"] for row in rows), (10, 11))
        self.assertEqual(tuple(row["neighbor_rank"] for row in rows), (1, 2))


if __name__ == "__main__":
    unittest.main()
