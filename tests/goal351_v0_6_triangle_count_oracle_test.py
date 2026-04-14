import sys
import unittest

sys.path.insert(0, "src")

import rtdsl as rt


class Goal351TriangleCountOracleTest(unittest.TestCase):
    def test_triangle_count_oracle_matches_truth_path(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 3, 6, 9, 12),
            column_indices=(
                1, 2, 3,
                0, 2, 3,
                0, 1, 3,
                0, 1, 2,
            ),
        )

        expected = rt.triangle_count_cpu(graph)
        actual = rt.triangle_count_oracle(graph)

        self.assertEqual(actual, expected)

    def test_triangle_count_oracle_rejects_unsorted_neighbor_lists(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6),
            column_indices=(
                2, 1,
                0, 2,
                0, 1,
            ),
        )

        with self.assertRaisesRegex(RuntimeError, "strictly ascending neighbor lists"):
            rt.triangle_count_oracle(graph)

    def test_triangle_count_oracle_rejects_self_loops(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 1, 2, 3),
            column_indices=(0, 1, 2), # Self-loops
        )
        with self.assertRaisesRegex(RuntimeError, "does not support self-loops"):
            rt.triangle_count_oracle(graph)

    def test_triangle_count_oracle_rejects_multiedges(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 3, 4),
            column_indices=(
                1, 1, # Multiedge
                0,
                0,
            ),
        )
        # Multiedges result in non-strictly-ascending neighbor lists.
        with self.assertRaisesRegex(RuntimeError, "strictly ascending neighbor lists"):
            rt.triangle_count_oracle(graph)

    def test_triangle_count_oracle_handling_large_vertex_ids(self) -> None:
        # Verify 32-bit boundary for triangle counting.
        graph = rt.csr_graph(
            vertex_count=4294967295,
            row_offsets=(0, 2, 4, 6),
            column_indices=(
                1, 4294967294,
                0, 4294967294,
                0, 1,
            ),
        )
        # Undirected triangle (0, 1, 4294967294)
        self.assertEqual(rt.triangle_count_oracle(graph), 1)

if __name__ == "__main__":
    unittest.main()
