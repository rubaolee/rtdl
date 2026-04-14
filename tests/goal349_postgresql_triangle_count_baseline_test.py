import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class _FakePostgresqlTriangleCursor:
    def __init__(self, connection):
        self._connection = connection
        self._row = None
        self._executed_sql = connection.executed_sql

    def execute(self, sql, params=None):
        sql_text = sql.strip()
        self._executed_sql.append(sql_text)
        if "CREATE TEMP TABLE" in sql_text:
            return
        if "CREATE INDEX" in sql_text or sql_text.startswith("ANALYZE"):
            return
        if "SELECT COUNT(*)::BIGINT AS triangle_count" in sql_text:
            self._row = (rt.triangle_count_cpu(self._connection.graph),)

    def executemany(self, sql, payload):
        rows = list(payload)
        if "INSERT INTO rtdl_graph_edges_tmp" in sql:
            self._connection.loaded_edges = tuple((int(src), int(dst)) for src, dst in rows)
            return
        raise AssertionError(f"unexpected executemany SQL: {sql}")

    def fetchone(self):
        return self._row

    def close(self):
        return


class _FakePostgresqlTriangleConnection:
    def __init__(self, graph):
        self.graph = graph
        self.loaded_edges = ()
        self.executed_sql = []

    def cursor(self):
        return _FakePostgresqlTriangleCursor(self)


class Goal349PostgresqlTriangleCountBaselineTest(unittest.TestCase):
    def test_postgresql_triangle_count_sql_contains_edge_join_shape(self) -> None:
        sql = rt.build_postgresql_triangle_count_sql()
        self.assertIn("SELECT COUNT(*)::BIGINT AS triangle_count", sql)
        self.assertIn("JOIN rtdl_graph_edges_tmp AS e2", sql)
        self.assertIn("JOIN rtdl_graph_edges_tmp AS e3", sql)

    def test_postgresql_triangle_count_runner_matches_python_truth_path(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )
        connection = _FakePostgresqlTriangleConnection(graph)

        count = rt.run_postgresql_triangle_count(connection, graph)

        self.assertEqual(count, rt.triangle_count_cpu(graph))
        self.assertTrue(any("CREATE TEMP TABLE rtdl_graph_edges_tmp" in sql for sql in connection.executed_sql))
        self.assertTrue(any("SELECT COUNT(*)::BIGINT AS triangle_count" in sql for sql in connection.executed_sql))
        self.assertEqual(connection.loaded_edges, ((0, 1), (0, 2), (1, 2)))


if __name__ == "__main__":
    unittest.main()
