import sys
import unittest

sys.path.insert(0, "src")

import rtdsl as rt


class Goal350BfsOracleTest(unittest.TestCase):
    def test_bfs_levels_oracle_matches_truth_path(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 3, 5, 7, 8, 8),
            column_indices=(
                1, 2, 3,
                0, 4,
                0, 4,
                0,
            ),
        )

        expected = rt.bfs_levels_cpu(graph, source_id=0)
        actual = rt.bfs_levels_oracle(graph, source_id=0)

        self.assertEqual(actual, expected)

    def test_bfs_levels_oracle_raises_for_out_of_bounds_source(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 1, 1),
            column_indices=(1,),
        )

        with self.assertRaisesRegex(RuntimeError, "out of bounds"):
            rt.bfs_levels_oracle(graph, source_id=2)


    def test_bfs_levels_oracle_returns_only_reachable_vertices(self) -> None:
        # Two disconnected components: 0-1 and 2-3.
        graph = rt.csr_graph(
            row_offsets=(0, 1, 2, 3, 4),
            column_indices=(1, 0, 3, 2),
        )

        rows = rt.bfs_levels_oracle(graph, source_id=0)

        vertex_ids = {row["vertex_id"] for row in rows}
        self.assertEqual(vertex_ids, {0, 1})
        self.assertNotIn(2, vertex_ids)
        self.assertNotIn(3, vertex_ids)
        self.assertEqual(rows, rt.bfs_levels_cpu(graph, source_id=0))

    def test_bfs_levels_oracle_handling_large_vertex_ids(self) -> None:
        # Verify 32-bit boundary IDs (uint32_t limit is 4,294,967,295)
        # Using a gap to force large IDs without large memory allocation.
        graph = rt.csr_graph(
            vertex_count=4294967295,
            row_offsets=(0, 1, 1, 2),
            column_indices=(2, 4294967294),
        )

        expected = rt.bfs_levels_cpu(graph, source_id=0)
        actual = rt.bfs_levels_oracle(graph, source_id=0)
        self.assertEqual(actual, expected)
        self.assertEqual(actual[1]["vertex_id"], 2)
        self.assertEqual(actual[2]["vertex_id"], 4294967294)
        # Actually CSRGraph stores uint32_t.

    def test_bfs_levels_oracle_rejects_malformed_offsets(self) -> None:
        # Oracle should handle native-level validation of CSR invariants.
        # This is high-stakes since bad offsets cause segfaults in native code.
        with self.assertRaises((RuntimeError, ValueError)):
            # Row offsets should be non-decreasing and end at len(column_indices)
            rt.bfs_levels_oracle(
                rt.csr_graph(
                    vertex_count=2,
                    row_offsets=(0, 2, 1),
                    column_indices=(0, 0)
                ),
                source_id=0,
            )

if __name__ == "__main__":
    unittest.main()
