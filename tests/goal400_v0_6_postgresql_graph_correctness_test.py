import os
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.graph_reference import bfs_expand_cpu
from rtdsl.graph_reference import triangle_probe_cpu
from tests.rtdl_sorting_test import optix_available
from tests.rtdsl_embree_test import embree_available
from tests.rtdsl_vulkan_test import vulkan_available


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_expand_reference():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_probe_reference():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


class _FakePostgresqlCursor:
    def __init__(self, connection):
        self._connection = connection
        self._rows = []
        self._executed_sql = connection.executed_sql

    def execute(self, sql, params=None):
        text = sql.strip()
        self._executed_sql.append(text)
        if "CREATE TEMP TABLE" in text or "CREATE INDEX" in text or text.startswith("ANALYZE"):
            return
        if text.startswith("WITH candidates AS") or text.startswith("SELECT\n    f.vertex_id AS src_vertex"):
            rows = bfs_expand_cpu(
                self._connection.graph,
                tuple(rt.FrontierVertex(vertex_id=vertex_id, level=level) for _, vertex_id, level in self._connection.frontier_rows),
                tuple(sorted(self._connection.visited_vertices)),
                dedupe=("DISTINCT ON (dst_vertex)" in text),
            )
            self._rows = [
                (row["src_vertex"], row["dst_vertex"], row["level"])
                for row in rows
            ]
            return
        if text.startswith("WITH triangles AS") or text.startswith("SELECT\n    s.u AS u"):
            rows = triangle_probe_cpu(
                self._connection.graph,
                tuple(rt.EdgeSeed(u=u, v=v) for _, u, v in self._connection.seed_rows),
                order="id_ascending",
                unique=("SELECT DISTINCT" in text),
            )
            self._rows = [
                (row["u"], row["v"], row["w"])
                for row in rows
            ]
            return
        raise AssertionError(f"unexpected SQL: {text}")

    def executemany(self, sql, payload):
        rows = list(payload)
        if "INSERT INTO rtdl_graph_edges_tmp" in sql:
            self._connection.edge_rows = tuple((int(src), int(dst)) for src, dst in rows)
            max_vertex = 0
            for src, dst in self._connection.edge_rows:
                max_vertex = max(max_vertex, src, dst)
            adjacency = {vertex_id: [] for vertex_id in range(max_vertex + 1)}
            for src, dst in self._connection.edge_rows:
                adjacency[src].append(dst)
            row_offsets = [0]
            column_indices = []
            for vertex_id in range(max_vertex + 1):
                column_indices.extend(adjacency[vertex_id])
                row_offsets.append(len(column_indices))
            self._connection.graph = rt.csr_graph(
                row_offsets=tuple(row_offsets),
                column_indices=tuple(column_indices),
            )
            return
        if "INSERT INTO rtdl_frontier_tmp" in sql:
            self._connection.frontier_rows = tuple((int(pos), int(vertex_id), int(level)) for pos, vertex_id, level in rows)
            return
        if "INSERT INTO rtdl_visited_tmp" in sql:
            self._connection.visited_vertices = {int(vertex_id) for (vertex_id,) in rows}
            return
        if "INSERT INTO rtdl_edge_seeds_tmp" in sql:
            self._connection.seed_rows = tuple((int(pos), int(u), int(v)) for pos, u, v in rows)
            return
        raise AssertionError(f"unexpected executemany SQL: {sql}")

    def fetchall(self):
        return list(self._rows)

    def close(self):
        return


class _FakePostgresqlConnection:
    def __init__(self):
        self.executed_sql = []
        self.edge_rows = ()
        self.frontier_rows = ()
        self.visited_vertices = set()
        self.seed_rows = ()
        self.graph = rt.csr_graph(row_offsets=(0,), column_indices=(), vertex_count=0)

    def cursor(self):
        return _FakePostgresqlCursor(self)


class Goal400V06PostgresqlGraphCorrectnessTest(unittest.TestCase):
    def _bfs_graph(self):
        return rt.csr_graph(
            row_offsets=(0, 2, 4, 5, 5),
            column_indices=(1, 2, 2, 3, 3),
        )

    def _triangle_graph(self):
        return rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )

    def test_bfs_sql_shape_contains_dedupe_and_indexed_join(self) -> None:
        sql = rt.build_postgresql_bfs_expand_sql()
        self.assertIn("DISTINCT ON (dst_vertex)", sql)
        self.assertIn("JOIN rtdl_graph_edges_tmp AS e", sql)
        self.assertIn("LEFT JOIN rtdl_visited_tmp AS v", sql)
        self.assertIn("ORDER BY level, dst_vertex, src_vertex", sql)

    def test_triangle_sql_shape_contains_intersection_join(self) -> None:
        sql = rt.build_postgresql_triangle_probe_sql()
        self.assertIn("JOIN rtdl_graph_edges_tmp AS eu", sql)
        self.assertIn("JOIN rtdl_graph_edges_tmp AS ev", sql)
        self.assertIn("ev.dst = eu.dst", sql)
        self.assertIn("ORDER BY u, v, w", sql)

    def test_postgresql_bfs_runner_matches_python_reference_with_fake_connection(self) -> None:
        connection = _FakePostgresqlConnection()
        rows = rt.run_postgresql_bfs_expand(
            connection,
            self._bfs_graph(),
            frontier=((0, 0), (1, 0)),
            visited=(0, 1),
        )
        self.assertEqual(
            rows,
            rt.run_cpu_python_reference(
                bfs_expand_reference,
                frontier=((0, 0), (1, 0)),
                graph=self._bfs_graph(),
                visited=(0, 1),
            ),
        )
        self.assertTrue(any("CREATE INDEX rtdl_graph_edges_tmp_src_idx" in sql for sql in connection.executed_sql))
        self.assertTrue(any("CREATE INDEX rtdl_graph_edges_tmp_dst_idx" in sql for sql in connection.executed_sql))
        self.assertTrue(any("CREATE INDEX rtdl_graph_edges_tmp_src_dst_idx" in sql for sql in connection.executed_sql))

    def test_postgresql_triangle_runner_matches_python_reference_with_fake_connection(self) -> None:
        connection = _FakePostgresqlConnection()
        rows = rt.run_postgresql_triangle_probe(
            connection,
            self._triangle_graph(),
            seeds=((0, 1), (1, 2), (0, 2)),
        )
        self.assertEqual(
            rows,
            rt.run_cpu_python_reference(
                triangle_probe_reference,
                seeds=((0, 1), (1, 2), (0, 2)),
                graph=self._triangle_graph(),
            ),
        )
        self.assertTrue(any("CREATE INDEX rtdl_edge_seeds_tmp_uv_idx" in sql for sql in connection.executed_sql))

    @unittest.skipUnless(rt.postgresql_available(), "psycopg2 is not installed in the current environment")
    @unittest.skipUnless(bool(os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")), "RTDL_POSTGRESQL_DSN is not set")
    def test_live_postgresql_bfs_matches_all_available_engines(self) -> None:
        dsn = os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")
        with rt.connect_postgresql(dsn) as connection:
            pg_rows = rt.run_postgresql_bfs_expand(
                connection,
                self._bfs_graph(),
                frontier=((0, 0), (1, 0)),
                visited=(0, 1),
            )
        inputs = {
            "frontier": ((0, 0), (1, 0)),
            "graph": self._bfs_graph(),
            "visited": (0, 1),
        }
        self.assertEqual(pg_rows, rt.run_cpu_python_reference(bfs_expand_reference, **inputs))
        self.assertEqual(pg_rows, rt.run_cpu(bfs_expand_reference, **inputs))
        if embree_available():
            self.assertEqual(pg_rows, rt.run_embree(bfs_expand_reference, **inputs))
        if optix_available():
            self.assertEqual(pg_rows, rt.run_optix(bfs_expand_reference, **inputs))
        if vulkan_available():
            self.assertEqual(pg_rows, rt.run_vulkan(bfs_expand_reference, **inputs))

    @unittest.skipUnless(rt.postgresql_available(), "psycopg2 is not installed in the current environment")
    @unittest.skipUnless(bool(os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")), "RTDL_POSTGRESQL_DSN is not set")
    def test_live_postgresql_triangle_matches_all_available_engines(self) -> None:
        dsn = os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")
        with rt.connect_postgresql(dsn) as connection:
            pg_rows = rt.run_postgresql_triangle_probe(
                connection,
                self._triangle_graph(),
                seeds=((0, 1), (1, 2), (0, 2)),
            )
        inputs = {
            "seeds": ((0, 1), (1, 2), (0, 2)),
            "graph": self._triangle_graph(),
        }
        self.assertEqual(pg_rows, rt.run_cpu_python_reference(triangle_probe_reference, **inputs))
        self.assertEqual(pg_rows, rt.run_cpu(triangle_probe_reference, **inputs))
        if embree_available():
            self.assertEqual(pg_rows, rt.run_embree(triangle_probe_reference, **inputs))
        if optix_available():
            self.assertEqual(pg_rows, rt.run_optix(triangle_probe_reference, **inputs))
        if vulkan_available():
            self.assertEqual(pg_rows, rt.run_vulkan(triangle_probe_reference, **inputs))


if __name__ == "__main__":
    unittest.main()
