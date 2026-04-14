import sys
import unittest

sys.path.insert(0, "src")

import rtdsl as rt


class Goal345BfsTruthPathTest(unittest.TestCase):
    def test_bfs_levels_cpu_returns_deterministic_level_rows(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 5, 6, 6),
            column_indices=(
                1, 2,
                0, 3,
                0,
                4,
            ),
        )

        rows = rt.bfs_levels_cpu(graph, source_id=0)

        self.assertEqual(
            rows,
            (
                {"vertex_id": 0, "level": 0},
                {"vertex_id": 1, "level": 1},
                {"vertex_id": 2, "level": 1},
                {"vertex_id": 3, "level": 2},
                {"vertex_id": 4, "level": 3},
            ),
        )

    def test_bfs_levels_cpu_raises_for_out_of_bounds_source(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 1, 1),
            column_indices=(1,),
        )

        with self.assertRaisesRegex(ValueError, "out of bounds"):
            rt.bfs_levels_cpu(graph, source_id=2)

    def test_csr_graph_rejects_bad_row_offsets(self) -> None:
        # Length must be <= vertex_count + 1
        with self.assertRaisesRegex(ValueError, "length must not exceed vertex_count \\+ 1"):
            rt.csr_graph(
                vertex_count=1,
                row_offsets=(0, 1, 2), # Too long (V=1 needs max 2, got 3)
                column_indices=(0, 0),
            )

    def test_csr_graph_rejects_out_of_bounds_neighbor(self) -> None:
        with self.assertRaisesRegex(ValueError, "out-of-bounds"):
            rt.csr_graph(
                row_offsets=(0, 1, 1),
                column_indices=(2,),
            )


    def test_csr_graph_rejects_row_offsets_not_starting_at_zero(self) -> None:
        with self.assertRaisesRegex(ValueError, "must start at 0"):
            rt.csr_graph(
                row_offsets=(1, 2, 3),
                column_indices=(1, 0),
            )

    def test_bfs_levels_cpu_returns_only_reachable_vertices(self) -> None:
        # Two disconnected components: 0-1 and 2-3.
        graph = rt.csr_graph(
            row_offsets=(0, 1, 2, 3, 4),
            column_indices=(1, 0, 3, 2),
        )

        rows = rt.bfs_levels_cpu(graph, source_id=0)

        vertex_ids = {row["vertex_id"] for row in rows}
        self.assertEqual(vertex_ids, {0, 1})
        self.assertNotIn(2, vertex_ids)
        self.assertNotIn(3, vertex_ids)


if __name__ == "__main__":
    unittest.main()
