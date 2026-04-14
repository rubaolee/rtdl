import sys
import unittest

sys.path.insert(0, "src")

import rtdsl as rt


class Goal346TriangleCountTruthPathTest(unittest.TestCase):
    def test_triangle_count_cpu_counts_single_triangle_once(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6),
            column_indices=(
                1, 2,
                0, 2,
                0, 1,
            ),
        )

        self.assertEqual(rt.triangle_count_cpu(graph), 1)

    def test_triangle_count_cpu_returns_zero_for_empty_graph(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0,),
            column_indices=(),
        )

        self.assertEqual(rt.triangle_count_cpu(graph), 0)

    def test_triangle_count_cpu_counts_two_separate_triangles(self) -> None:
        # Two disconnected triangles: {0,1,2} and {3,4,5}.
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 8, 10, 12),
            column_indices=(
                1, 2,
                0, 2,
                0, 1,
                4, 5,
                3, 5,
                3, 4,
            ),
        )
        self.assertEqual(rt.triangle_count_cpu(graph), 2)

    def test_triangle_count_cpu_rejects_unsorted_neighbor_lists(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6),
            column_indices=(
                2, 1,
                0, 2,
                0, 1,
            ),
        )

        with self.assertRaisesRegex(ValueError, "strictly ascending neighbor lists"):
            rt.triangle_count_cpu(graph)


if __name__ == "__main__":
    unittest.main()
