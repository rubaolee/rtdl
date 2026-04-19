from __future__ import annotations

import platform
import unittest

import rtdsl as rt


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_match_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    hits = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(hits, fields=["u", "v", "w"])


def triangle_graph() -> rt.CSRGraph:
    return rt.csr_graph(
        row_offsets=(0, 3, 6, 9, 11, 12),
        column_indices=(
            1,
            2,
            3,
            0,
            2,
            3,
            0,
            1,
            4,
            0,
            1,
            2,
        ),
    )


def complete_graph(vertex_count: int) -> rt.CSRGraph:
    row_offsets = [0]
    columns: list[int] = []
    for vertex_id in range(vertex_count):
        columns.extend(neighbor for neighbor in range(vertex_count) if neighbor != vertex_id)
        row_offsets.append(len(columns))
    return rt.csr_graph(row_offsets=tuple(row_offsets), column_indices=tuple(columns))


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal620AppleRtGraphTriangleMatchTest(unittest.TestCase):
    def test_direct_helper_matches_cpu_reference(self) -> None:
        graph = triangle_graph()
        seeds = ((0, 1), (0, 2), (1, 2), (2, 4), (3, 1))
        actual = rt.triangle_match_apple_rt(graph, seeds)
        expected = rt.triangle_probe_cpu(graph, tuple(rt.EdgeSeed(u, v) for u, v in seeds))
        self.assertEqual(actual, expected)

    def test_run_apple_rt_native_only_matches_cpu_reference(self) -> None:
        graph = triangle_graph()
        seeds = ((0, 1), (0, 2), (1, 2), (2, 4))
        actual = rt.run_apple_rt(triangle_match_kernel, native_only=True, seeds=seeds, graph=graph)
        expected = rt.run_cpu_python_reference(triangle_match_kernel, seeds=seeds, graph=graph)
        self.assertEqual(actual, expected)

    def test_duplicate_seeds_respect_unique_option(self) -> None:
        graph = triangle_graph()
        seeds = ((0, 1), (0, 1), (1, 2), (1, 2))
        unique_rows = rt.triangle_match_apple_rt(graph, seeds, unique=True)
        repeated_rows = rt.triangle_match_apple_rt(graph, seeds, unique=False)
        self.assertEqual(unique_rows, ({"u": 0, "v": 1, "w": 2}, {"u": 0, "v": 1, "w": 3}))
        self.assertEqual(
            repeated_rows,
            (
                {"u": 0, "v": 1, "w": 2},
                {"u": 0, "v": 1, "w": 2},
                {"u": 0, "v": 1, "w": 3},
                {"u": 0, "v": 1, "w": 3},
            ),
        )

    def test_empty_inputs_return_empty_rows(self) -> None:
        graph = rt.csr_graph(row_offsets=(0, 0), column_indices=())
        self.assertEqual(rt.triangle_match_apple_rt(graph, ()), ())
        self.assertEqual(rt.triangle_match_apple_rt(graph, ((0, 0),)), ())

    def test_bounded_stress_matches_cpu_reference(self) -> None:
        graph = complete_graph(16)
        seeds = tuple((u, v) for u in range(8) for v in range(u + 1, 12))
        actual = rt.triangle_match_apple_rt(graph, seeds)
        expected = rt.triangle_probe_cpu(graph, tuple(rt.EdgeSeed(u, v) for u, v in seeds))
        self.assertEqual(actual, expected)

    def test_support_matrix_marks_triangle_match_as_metal_compute(self) -> None:
        by_predicate = {row["predicate"]: row for row in rt.apple_rt_support_matrix()}
        self.assertEqual(by_predicate["triangle_match"]["mode"], "native_metal_compute")
        self.assertEqual(by_predicate["triangle_match"]["native_only"], "supported_for_csr_edge_seeds")


if __name__ == "__main__":
    unittest.main()
