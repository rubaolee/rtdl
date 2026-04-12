import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class _FakePostgis3DCursor:
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
        if "ST_3DDWithin" in sql:
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
                for distance, neighbor_id in candidates[:k_max]:
                    rows.append((query_point.id, neighbor_id, distance))
            rows.sort(key=lambda row: (row[0], row[2], row[1]))
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


class _FakePostgis3DConnection:
    def __init__(self):
        self.query_points = ()
        self.search_points = ()
        self.executed_sql = []

    def cursor(self):
        return _FakePostgis3DCursor(self)

    def close(self):
        return


class Goal281Postgis3DFixedRadiusBaselineTest(unittest.TestCase):
    def test_postgis_3d_sql_contains_expected_3d_predicates(self) -> None:
        sql = rt.build_postgis_fixed_radius_neighbors_3d_sql()
        self.assertIn("ST_3DDWithin", sql)
        self.assertIn("ST_3DDistance", sql)
        self.assertIn("ROW_NUMBER() OVER", sql)

    def test_postgis_3d_runner_matches_python_reference(self) -> None:
        query_points = (
            rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
            rt.Point3D(id=2, x=2.0, y=0.0, z=0.0),
        )
        search_points = (
            rt.Point3D(id=10, x=0.2, y=0.0, z=0.0),
            rt.Point3D(id=11, x=2.2, y=0.0, z=0.0),
            rt.Point3D(id=12, x=0.0, y=0.0, z=3.0),
        )
        connection = _FakePostgis3DConnection()
        rows = rt.run_postgis_fixed_radius_neighbors_3d(
            connection,
            query_points,
            search_points,
            radius=0.5,
            k_max=2,
        )
        python_rows = rt.fixed_radius_neighbors_cpu(
            query_points,
            search_points,
            radius=0.5,
            k_max=2,
        )
        self.assertEqual(rows, python_rows)
        self.assertTrue(any("geometry(PointZ, 0)" in sql for sql in connection.executed_sql))
        self.assertTrue(any("CREATE INDEX rtdl_query_points3d_tmp_geom_gist" in sql for sql in connection.executed_sql))
        self.assertTrue(any("CREATE INDEX rtdl_search_points3d_tmp_geom_gist" in sql for sql in connection.executed_sql))

    def test_postgis_3d_runner_obeys_k_max(self) -> None:
        query_points = (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),)
        search_points = (
            rt.Point3D(id=10, x=0.1, y=0.0, z=0.0),
            rt.Point3D(id=11, x=0.2, y=0.0, z=0.0),
            rt.Point3D(id=12, x=0.3, y=0.0, z=0.0),
        )
        connection = _FakePostgis3DConnection()
        rows = rt.run_postgis_fixed_radius_neighbors_3d(
            connection,
            query_points,
            search_points,
            radius=1.0,
            k_max=2,
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(tuple(row["neighbor_id"] for row in rows), (10, 11))


if __name__ == "__main__":
    unittest.main()
