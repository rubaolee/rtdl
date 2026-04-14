import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class _FakePostgresqlBfsCursor:
    def __init__(self, connection):
        self._connection = connection
        self._rows = []
        self._executed_sql = connection.executed_sql

    def execute(self, sql, params=None):
        sql_text = sql.strip()
        self._executed_sql.append(sql_text)
        if "CREATE TEMP TABLE" in sql_text:
            return
        if "CREATE INDEX" in sql_text or sql_text.startswith("ANALYZE"):
            return
        if "WITH RECURSIVE bfs" in sql_text:
            (source_id,) = params
            self._rows = list(
                (row["vertex_id"], row["level"])
                for row in rt.bfs_levels_cpu(self._connection.graph, source_id=source_id)
            )

    def executemany(self, sql, payload):
        rows = list(payload)
        if "INSERT INTO rtdl_graph_edges_tmp" in sql:
            self._connection.loaded_edges = tuple((int(src), int(dst)) for src, dst in rows)
            return
        raise AssertionError(f"unexpected executemany SQL: {sql}")

    def fetchall(self):
        return list(self._rows)

    def close(self):
        return


class _FakePostgresqlBfsConnection:
    def __init__(self, graph):
        self.graph = graph
        self.loaded_edges = ()
        self.executed_sql = []

    def cursor(self):
        return _FakePostgresqlBfsCursor(self)


class Goal348PostgresqlBfsBaselineTest(unittest.TestCase):
    def test_postgresql_bfs_sql_contains_recursive_cte(self) -> None:
        sql = rt.build_postgresql_bfs_levels_sql()
        self.assertIn("WITH RECURSIVE bfs", sql)
        self.assertIn("MIN(level)", sql)
        self.assertIn("ORDER BY level, vertex_id", sql)

    def test_postgresql_bfs_runner_matches_python_truth_path(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 5, 6, 6),
            column_indices=(1, 2, 0, 3, 0, 4),
        )
        connection = _FakePostgresqlBfsConnection(graph)

        rows = rt.run_postgresql_bfs_levels(connection, graph, source_id=0)

        self.assertEqual(rows, rt.bfs_levels_cpu(graph, source_id=0))
        self.assertTrue(any("CREATE TEMP TABLE rtdl_graph_edges_tmp" in sql for sql in connection.executed_sql))
        self.assertTrue(any("WITH RECURSIVE bfs" in sql for sql in connection.executed_sql))
        self.assertEqual(connection.loaded_edges[:3], ((0, 1), (0, 2), (1, 0)))


if __name__ == "__main__":
    unittest.main()
