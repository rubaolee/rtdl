from __future__ import annotations

import platform
import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_no_dedupe_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=False))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


def graph_fixture() -> rt.CSRGraph:
    return rt.csr_graph(
        row_offsets=(0, 3, 5, 7, 9, 10, 10),
        column_indices=(1, 2, 3, 2, 4, 3, 4, 4, 5, 5),
    )


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal619AppleRtGraphBfsTest(unittest.TestCase):
    def test_direct_bfs_discover_matches_cpu(self) -> None:
        graph = graph_fixture()
        frontier = (rt.FrontierVertex(vertex_id=0, level=0), rt.FrontierVertex(vertex_id=1, level=0))
        visited = (0, 1)
        self.assertEqual(
            rt.bfs_discover_apple_rt(graph, frontier, visited, dedupe=True),
            rt.bfs_expand_cpu(graph, frontier, visited, dedupe=True),
        )

    def test_run_apple_rt_native_only_matches_cpu_reference(self) -> None:
        inputs = {
            "graph": graph_fixture(),
            "frontier": (rt.FrontierVertex(vertex_id=0, level=0), rt.FrontierVertex(vertex_id=1, level=0)),
            "visited": (0, 1),
        }
        self.assertEqual(
            rt.run_apple_rt(bfs_kernel, native_only=True, **inputs),
            rt.run_cpu_python_reference(bfs_kernel, **inputs),
        )

    def test_no_dedupe_mode_matches_cpu_reference(self) -> None:
        inputs = {
            "graph": graph_fixture(),
            "frontier": (rt.FrontierVertex(vertex_id=0, level=0), rt.FrontierVertex(vertex_id=1, level=0)),
            "visited": (0,),
        }
        self.assertEqual(
            rt.run_apple_rt(bfs_no_dedupe_kernel, native_only=True, **inputs),
            rt.run_cpu_python_reference(bfs_no_dedupe_kernel, **inputs),
        )

    def test_bounded_stress_matches_cpu(self) -> None:
        vertex_count = 512
        row_offsets = [0]
        column_indices = []
        for vertex in range(vertex_count):
            neighbors = ((vertex + 1) % vertex_count, (vertex + 7) % vertex_count, (vertex + 31) % vertex_count)
            column_indices.extend(neighbors)
            row_offsets.append(len(column_indices))
        graph = rt.csr_graph(row_offsets=row_offsets, column_indices=column_indices)
        frontier = tuple(rt.FrontierVertex(vertex_id=index * 17, level=2) for index in range(16))
        visited = tuple(range(0, vertex_count, 11))
        self.assertEqual(
            rt.bfs_discover_apple_rt(graph, frontier, visited, dedupe=True),
            rt.bfs_expand_cpu(graph, frontier, visited, dedupe=True),
        )

    def test_empty_frontier_returns_empty(self) -> None:
        self.assertEqual(rt.bfs_discover_apple_rt(graph_fixture(), (), ()), ())

    def test_support_matrix_marks_bfs_as_metal_compute(self) -> None:
        by_predicate = {row["predicate"]: row for row in rt.apple_rt_support_matrix()}
        row = by_predicate["bfs_discover"]
        self.assertEqual(row["mode"], "native_metal_compute")
        self.assertEqual(row["native_only"], "supported_for_csr_frontier_vertex_set")


if __name__ == "__main__":
    unittest.main()
