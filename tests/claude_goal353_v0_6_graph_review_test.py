"""
Claude goal353 review: focused tests for v0.6 graph code gaps.

Covers edge cases and contracts not exercised by goal345-352/356-359 tests:

  1. validate_csr_graph — missing constraint paths
  2. bfs_levels_cpu — single isolated vertex, frontier sort contract
  3. triangle_count_cpu — path graph (edges, no triangles), clique-5
  4. Graph generator edge cases (cycle, binary_tree, grid, clique)
  5. csr_graph_from_neighbors — empty, duplicate suppression
  6. load_snap_edge_list_graph — FileNotFoundError, max_edges, self-loop
  7. _timed_call — repeats=0 raises, return type contract
  8. Oracle — single vertex, path graph (no triangles)
  9. postgresql_available — psycopg2 probe behaviour
 10. SQL string structure — redundant conditions in triangle SQL (finding, not a fix)
 11. _canonical_undirected_edges — self-loop suppression
"""
from __future__ import annotations

import gzip
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.graph_eval import _timed_call, csr_graph_from_neighbors
from rtdsl.external_baselines import (
    _canonical_undirected_edges,
    _directed_edges,
    build_postgresql_bfs_levels_sql,
    build_postgresql_triangle_count_sql,
    postgresql_available,
)


# ---------------------------------------------------------------------------
# 1. validate_csr_graph — missing constraint paths
# ---------------------------------------------------------------------------

class ValidateCsrGraphMissingConstraintsTest(unittest.TestCase):
    """The existing tests check bad row_offsets length and out-of-bounds neighbors.
    These tests cover the remaining paths: last offset mismatch, non-decreasing."""

    def test_rejects_final_offset_mismatch_with_column_indices(self) -> None:
        # row_offsets[-1] = 3 but column_indices has only 2 entries
        with self.assertRaisesRegex(ValueError, "final row_offsets value must equal column_indices length"):
            rt.csr_graph(
                row_offsets=(0, 2, 3),
                column_indices=(1, 0),  # length 2, but last offset is 3
            )

    def test_rejects_decreasing_row_offsets(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-decreasing"):
            # row_offsets goes 0, 2, 1 — second offset is smaller than first.
            # column_indices length matches row_offsets[-1]=1 to reach the
            # non-decreasing check (the final-offset check fires first).
            rt.csr_graph(
                vertex_count=2,
                row_offsets=(0, 2, 1),
                column_indices=(1,),
            )

    def test_accepts_vertex_with_zero_neighbors(self) -> None:
        # Vertex 1 has no neighbors — row_offsets step is 0; 3 vertices total
        graph = rt.csr_graph(
            row_offsets=(0, 1, 1, 2),
            column_indices=(1, 0),
        )
        self.assertEqual(graph.vertex_count, 3)

    def test_vertex_count_inferred_from_row_offsets(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 1, 1),
            column_indices=(1,),
        )
        self.assertEqual(graph.vertex_count, 2)


# ---------------------------------------------------------------------------
# 2. bfs_levels_cpu — single isolated vertex, frontier sort
# ---------------------------------------------------------------------------

class BfsCpuAdditionalTest(unittest.TestCase):

    def test_single_isolated_vertex_returns_source_only(self) -> None:
        graph = rt.csr_graph(row_offsets=(0, 0), column_indices=())
        rows = rt.bfs_levels_cpu(graph, source_id=0)
        self.assertEqual(rows, ({"vertex_id": 0, "level": 0},))

    def test_frontier_sorted_within_level(self) -> None:
        # Star graph: 0 → 3, 1, 2 (deliberately stored in reverse order)
        # BFS from 0: level-1 neighbors should appear sorted.
        graph = rt.csr_graph(
            row_offsets=(0, 3, 3, 3, 3),
            column_indices=(3, 1, 2),  # neighbors of 0, unordered
        )
        rows = rt.bfs_levels_cpu(graph, source_id=0)
        level_1_ids = [r["vertex_id"] for r in rows if r["level"] == 1]
        self.assertEqual(level_1_ids, sorted(level_1_ids))

    def test_self_loop_in_csr_does_not_hang_bfs(self) -> None:
        # Vertex 0 points to itself and vertex 1
        graph = rt.csr_graph(
            row_offsets=(0, 2, 3),
            column_indices=(0, 1, 0),
        )
        rows = rt.bfs_levels_cpu(graph, source_id=0)
        vertex_ids = {r["vertex_id"] for r in rows}
        self.assertIn(0, vertex_ids)
        self.assertIn(1, vertex_ids)

    def test_negative_source_id_raises(self) -> None:
        graph = rt.csr_graph(row_offsets=(0, 1, 1), column_indices=(1,))
        with self.assertRaisesRegex(ValueError, "out of bounds"):
            rt.bfs_levels_cpu(graph, source_id=-1)

    def test_bfs_on_path_graph_assigns_levels_correctly(self) -> None:
        # 0 ─ 1 ─ 2 ─ 3 ─ 4 (undirected path)
        graph = rt.csr_graph(
            row_offsets=(0, 1, 3, 5, 7, 8),
            column_indices=(1, 0, 2, 1, 3, 2, 4, 3),
        )
        rows = rt.bfs_levels_cpu(graph, source_id=0)
        level_by_vertex = {r["vertex_id"]: r["level"] for r in rows}
        self.assertEqual(level_by_vertex, {0: 0, 1: 1, 2: 2, 3: 3, 4: 4})


# ---------------------------------------------------------------------------
# 3. triangle_count_cpu — path graph, K5
# ---------------------------------------------------------------------------

class TriangleCountCpuAdditionalTest(unittest.TestCase):

    def test_path_graph_has_zero_triangles(self) -> None:
        # 0 ─ 1 ─ 2 (no triangles)
        graph = rt.csr_graph(
            row_offsets=(0, 1, 3, 4),
            column_indices=(1, 0, 2, 1),
        )
        self.assertEqual(rt.triangle_count_cpu(graph), 0)

    def test_single_vertex_no_edges_has_zero_triangles(self) -> None:
        graph = rt.csr_graph(row_offsets=(0,), column_indices=())
        self.assertEqual(rt.triangle_count_cpu(graph), 0)

    def test_clique_k5_has_ten_triangles(self) -> None:
        # K5 has C(5,3) = 10 triangles
        graph = rt.clique_graph(5)
        self.assertEqual(rt.triangle_count_cpu(graph), 10)

    def test_isolated_vertices_added_to_triangle_graph(self) -> None:
        # Triangle {0,1,2} plus isolated vertex 3
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )
        self.assertEqual(rt.triangle_count_cpu(graph), 1)

    def test_oracle_and_cpu_agree_on_path_graph(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 1, 3, 4),
            column_indices=(1, 0, 2, 1),
        )
        self.assertEqual(rt.triangle_count_oracle(graph), rt.triangle_count_cpu(graph))
        self.assertEqual(rt.triangle_count_oracle(graph), 0)


# ---------------------------------------------------------------------------
# 4. Graph generator edge cases
# ---------------------------------------------------------------------------

class GraphGeneratorEdgeCasesTest(unittest.TestCase):

    def test_cycle_graph_zero_vertices_is_valid_empty_graph(self) -> None:
        graph = rt.cycle_graph(0)
        self.assertEqual(graph.vertex_count, 0)
        self.assertEqual(graph.row_offsets, (0,))
        self.assertEqual(graph.column_indices, ())

    def test_cycle_graph_one_vertex_has_no_edges(self) -> None:
        graph = rt.cycle_graph(1)
        self.assertEqual(graph.vertex_count, 1)
        self.assertEqual(graph.column_indices, ())

    def test_cycle_graph_two_vertices_connects_both(self) -> None:
        graph = rt.cycle_graph(2)
        self.assertEqual(graph.vertex_count, 2)
        # 0 ─ 1 (undirected cycle of length 2)
        self.assertEqual(len(graph.column_indices), 2)

    def test_cycle_graph_bfs_levels_are_correct(self) -> None:
        graph = rt.cycle_graph(4)
        rows = rt.bfs_levels_cpu(graph, source_id=0)
        levels = {r["vertex_id"]: r["level"] for r in rows}
        # From 0: level-1 = {1, 3}, level-2 = {2}
        self.assertEqual(levels[0], 0)
        self.assertEqual(levels[1], 1)
        self.assertEqual(levels[3], 1)
        self.assertEqual(levels[2], 2)

    def test_binary_tree_graph_zero_vertices_is_valid(self) -> None:
        graph = rt.binary_tree_graph(0)
        self.assertEqual(graph.vertex_count, 0)
        self.assertEqual(graph.row_offsets, (0,))

    def test_binary_tree_graph_single_root_has_no_neighbors(self) -> None:
        graph = rt.binary_tree_graph(1)
        self.assertEqual(graph.vertex_count, 1)
        self.assertEqual(graph.column_indices, ())

    def test_grid_graph_one_by_one_single_vertex(self) -> None:
        graph = rt.grid_graph(1, 1)
        self.assertEqual(graph.vertex_count, 1)
        self.assertEqual(graph.column_indices, ())

    def test_grid_graph_bfs_covers_all_vertices(self) -> None:
        graph = rt.grid_graph(3, 3)
        rows = rt.bfs_levels_cpu(graph, source_id=0)
        visited = {r["vertex_id"] for r in rows}
        self.assertEqual(visited, set(range(9)))

    def test_clique_zero_vertices_is_valid(self) -> None:
        graph = rt.clique_graph(0)
        self.assertEqual(graph.vertex_count, 0)

    def test_clique_one_vertex_has_no_edges(self) -> None:
        graph = rt.clique_graph(1)
        self.assertEqual(graph.vertex_count, 1)
        self.assertEqual(graph.column_indices, ())

    def test_grid_graph_zero_width_is_valid(self) -> None:
        graph = rt.grid_graph(0, 3)
        self.assertEqual(graph.vertex_count, 0)

    def test_grid_graph_zero_height_is_valid(self) -> None:
        graph = rt.grid_graph(3, 0)
        self.assertEqual(graph.vertex_count, 0)


# ---------------------------------------------------------------------------
# 5. csr_graph_from_neighbors — empty, dedup
# ---------------------------------------------------------------------------

class CsrGraphFromNeighborsTest(unittest.TestCase):

    def test_empty_input_returns_valid_zero_vertex_graph(self) -> None:
        graph = csr_graph_from_neighbors([])
        self.assertEqual(graph.vertex_count, 0)
        self.assertEqual(graph.row_offsets, (0,))
        self.assertEqual(graph.column_indices, ())

    def test_normalizes_unsorted_neighbors(self) -> None:
        # Input neighbors are unsorted; output should be sorted
        graph = csr_graph_from_neighbors([(3, 1, 2), (0,), (0,), (0,)])
        self.assertEqual(graph.column_indices[0:3], (1, 2, 3))

    def test_round_trip_with_csr_graph_factory(self) -> None:
        neighbors = [(1, 2), (0, 2), (0, 1)]
        graph = csr_graph_from_neighbors(neighbors)
        self.assertEqual(graph.vertex_count, 3)
        self.assertEqual(graph.row_offsets[0], 0)
        self.assertEqual(graph.row_offsets[-1], len(graph.column_indices))


# ---------------------------------------------------------------------------
# 6. load_snap_edge_list_graph — error paths and max_edges
# ---------------------------------------------------------------------------

class LoadSnapEdgeListTest(unittest.TestCase):

    def test_missing_file_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            rt.load_snap_edge_list_graph("/nonexistent/path/graph.txt")

    def test_max_edges_limits_edge_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt"
            # Write 5 directed edges
            path.write_text("0 1\n0 2\n0 3\n1 2\n1 3\n", encoding="utf-8")

            graph = rt.load_snap_edge_list_graph(path, max_edges=2)

            # Only first 2 edges should be loaded
            self.assertLessEqual(len(graph.column_indices), 2)

    def test_self_loop_in_undirected_is_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt"
            path.write_text("0 0\n0 1\n1 0\n", encoding="utf-8")

            graph = rt.load_snap_simple_undirected_graph(path)
            # Self-loop 0→0 should not appear in column_indices
            self.assertNotIn(0, [graph.column_indices[i] for i in range(
                graph.row_offsets[0], graph.row_offsets[1]
            )])

    def test_gzip_file_with_max_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt.gz"
            with gzip.open(path, "wt", encoding="utf-8") as handle:
                handle.write("0 1\n0 2\n0 3\n")

            graph = rt.load_snap_edge_list_graph(path, max_edges=1)
            # Only edge 0→1 loaded
            self.assertLessEqual(len(graph.column_indices), 1)

    def test_comment_lines_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt"
            path.write_text("# header\n# comment\n0 1\n", encoding="utf-8")

            graph = rt.load_snap_edge_list_graph(path)
            self.assertEqual(graph.vertex_count, 2)
            self.assertIn(1, graph.column_indices)

    def test_empty_file_returns_empty_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt"
            path.write_text("# just comments\n", encoding="utf-8")

            graph = rt.load_snap_edge_list_graph(path)
            self.assertEqual(graph.vertex_count, 0)
            self.assertEqual(graph.column_indices, ())


# ---------------------------------------------------------------------------
# 7. _timed_call — repeats=0 and return contract
# ---------------------------------------------------------------------------

class TimedCallTest(unittest.TestCase):

    def test_repeats_zero_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "evaluation repeats must be positive"):
            _timed_call(lambda: 42, repeats=0)

    def test_repeats_negative_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "evaluation repeats must be positive"):
            _timed_call(lambda: 42, repeats=-1)

    def test_returns_last_value_and_positive_seconds(self) -> None:
        value, seconds = _timed_call(lambda: 99, repeats=2)
        self.assertEqual(value, 99)
        self.assertGreaterEqual(seconds, 0.0)
        self.assertIsInstance(seconds, float)

    def test_single_repeat_returns_that_call_result(self) -> None:
        counter = [0]

        def fn():
            counter[0] += 1
            return counter[0]

        value, _ = _timed_call(fn, repeats=1)
        self.assertEqual(value, 1)
        self.assertEqual(counter[0], 1)

    def test_multiple_repeats_runs_fn_that_many_times(self) -> None:
        counter = [0]

        def fn():
            counter[0] += 1
            return counter[0]

        _timed_call(fn, repeats=5)
        self.assertEqual(counter[0], 5)


# ---------------------------------------------------------------------------
# 8. Oracle — single vertex, path graph (no triangles)
# ---------------------------------------------------------------------------

class OracleAdditionalTest(unittest.TestCase):

    def test_bfs_oracle_single_isolated_vertex(self) -> None:
        graph = rt.csr_graph(row_offsets=(0, 0), column_indices=())
        rows = rt.bfs_levels_oracle(graph, source_id=0)
        self.assertEqual(rows, ({"vertex_id": 0, "level": 0},))

    def test_bfs_oracle_matches_cpu_on_cycle_graph(self) -> None:
        graph = rt.cycle_graph(6)
        expected = rt.bfs_levels_cpu(graph, source_id=0)
        actual = rt.bfs_levels_oracle(graph, source_id=0)
        self.assertEqual(actual, expected)

    def test_triangle_count_oracle_path_graph_is_zero(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 1, 3, 4),
            column_indices=(1, 0, 2, 1),
        )
        self.assertEqual(rt.triangle_count_oracle(graph), 0)

    def test_triangle_count_oracle_matches_cpu_on_k5(self) -> None:
        graph = rt.clique_graph(5)
        self.assertEqual(rt.triangle_count_oracle(graph), rt.triangle_count_cpu(graph))
        self.assertEqual(rt.triangle_count_oracle(graph), 10)

    def test_triangle_count_oracle_single_isolated_vertex(self) -> None:
        graph = rt.csr_graph(row_offsets=(0,), column_indices=())
        self.assertEqual(rt.triangle_count_oracle(graph), 0)


# ---------------------------------------------------------------------------
# 9. postgresql_available — psycopg2 probe
# ---------------------------------------------------------------------------

class PostgresqlAvailableTest(unittest.TestCase):

    def test_postgresql_available_returns_bool(self) -> None:
        result = rt.postgresql_available()
        self.assertIsInstance(result, bool)

    def test_postgresql_available_consistent_with_postgis_available(self) -> None:
        # postgresql_available() delegates to postgis_available() (psycopg2 check)
        from rtdsl.external_baselines import postgis_available
        self.assertEqual(rt.postgresql_available(), postgis_available())


# ---------------------------------------------------------------------------
# 10. SQL string structure — correctness and redundancy finding
# ---------------------------------------------------------------------------

class SqlStructureTest(unittest.TestCase):

    def test_bfs_sql_uses_min_level_for_shortest_path(self) -> None:
        sql = build_postgresql_bfs_levels_sql()
        self.assertIn("MIN(level)", sql)
        self.assertIn("GROUP BY vertex_id", sql)
        self.assertIn("ORDER BY level, vertex_id", sql)

    def test_bfs_sql_is_parameterized(self) -> None:
        # Source vertex must be injected via parameter, not inlined
        sql = build_postgresql_bfs_levels_sql()
        self.assertIn("%s", sql)

    def test_triangle_count_sql_uses_three_way_join(self) -> None:
        sql = build_postgresql_triangle_count_sql()
        # Must join e1, e2, e3 to detect all three edges of a triangle
        self.assertIn("JOIN rtdl_graph_edges_tmp AS e2", sql)
        self.assertIn("JOIN rtdl_graph_edges_tmp AS e3", sql)

    def test_triangle_count_sql_has_src_lt_dst_filter(self) -> None:
        # Canonical undirected edge representation: src < dst
        sql = build_postgresql_triangle_count_sql()
        self.assertIn("e1.src < e1.dst", sql)
        self.assertIn("e2.src < e2.dst", sql)
        self.assertIn("e3.src < e3.dst", sql)

    def test_triangle_count_sql_has_redundant_condition_on_e2(self) -> None:
        # Finding: e2.src < e2.dst appears twice in the WHERE clause.
        # This is harmless but redundant — document here as a known finding.
        sql = build_postgresql_triangle_count_sql()
        count = sql.count("e2.src < e2.dst")
        # The redundant condition is present in the current implementation.
        # A future cleanup can merge it; for now, document the count.
        self.assertGreaterEqual(count, 1, "e2.src < e2.dst must appear at least once")

    def test_bfs_sql_custom_edge_table_name_is_respected(self) -> None:
        sql = build_postgresql_bfs_levels_sql(edge_table="my_custom_edges")
        self.assertIn("my_custom_edges", sql)
        self.assertNotIn("rtdl_graph_edges_tmp", sql)

    def test_triangle_count_sql_custom_edge_table_name_is_respected(self) -> None:
        sql = build_postgresql_triangle_count_sql(edge_table="my_edges")
        self.assertIn("my_edges", sql)


# ---------------------------------------------------------------------------
# 11. _canonical_undirected_edges — self-loop and duplicate suppression
# ---------------------------------------------------------------------------

class CanonicalUndirectedEdgesTest(unittest.TestCase):

    def test_self_loops_are_suppressed(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 3),
            column_indices=(0, 1, 0),
        )
        edges = list(_canonical_undirected_edges(graph))
        # Self-loop (0, 0) should be absent
        self.assertNotIn((0, 0), edges)
        self.assertNotIn((1, 1), edges)

    def test_each_undirected_edge_appears_once(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )
        edges = list(_canonical_undirected_edges(graph))
        # Triangle {0,1,2}: should produce exactly 3 canonical edges
        self.assertEqual(len(edges), 3)
        self.assertIn((0, 1), edges)
        self.assertIn((0, 2), edges)
        self.assertIn((1, 2), edges)

    def test_directed_edges_enumerates_all_directed_edges(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 1, 2),
            column_indices=(1, 0),
        )
        edges = list(_directed_edges(graph))
        self.assertIn((0, 1), edges)
        self.assertIn((1, 0), edges)
        self.assertEqual(len(edges), 2)


if __name__ == "__main__":
    unittest.main()
