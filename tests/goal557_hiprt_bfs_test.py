from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import bfs_expand_hiprt
from rtdsl.hiprt_runtime import hiprt_context_probe


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


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


def graph_fixture() -> rt.CSRGraph:
    return rt.csr_graph(
        row_offsets=(0, 2, 4, 5, 5),
        column_indices=(1, 2, 2, 3, 3),
    )


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal557HiprtBfsTest(unittest.TestCase):
    def test_direct_helper_matches_cpu_reference_with_global_dedupe(self) -> None:
        graph = graph_fixture()
        frontier = (
            rt.FrontierVertex(vertex_id=0, level=0),
            rt.FrontierVertex(vertex_id=1, level=0),
        )
        visited = (0, 1)
        self.assertEqual(
            bfs_expand_hiprt(graph, frontier, visited, dedupe=True),
            rt.bfs_expand_cpu(graph, frontier, visited, dedupe=True),
        )

    def test_run_hiprt_matches_cpu_reference(self) -> None:
        inputs = {
            "graph": graph_fixture(),
            "frontier": (
                rt.FrontierVertex(vertex_id=0, level=0),
                rt.FrontierVertex(vertex_id=1, level=0),
            ),
            "visited": (0, 1),
        }
        self.assertEqual(
            rt.run_hiprt(bfs_kernel, **inputs),
            rt.run_cpu_python_reference(bfs_kernel, **inputs),
        )

    def test_dedupe_false_allows_duplicate_discovery(self) -> None:
        inputs = {
            "graph": graph_fixture(),
            "frontier": (
                rt.FrontierVertex(vertex_id=0, level=0),
                rt.FrontierVertex(vertex_id=1, level=0),
            ),
            "visited": (0, 1),
        }
        self.assertEqual(
            rt.run_hiprt(bfs_no_dedupe_kernel, **inputs),
            rt.run_cpu_python_reference(bfs_no_dedupe_kernel, **inputs),
        )

    def test_empty_frontier_and_empty_edges_return_empty_rows(self) -> None:
        graph = graph_fixture()
        self.assertEqual(rt.run_hiprt(bfs_kernel, graph=graph, frontier=(), visited=()), ())
        empty_graph = rt.csr_graph(row_offsets=(0, 0), column_indices=())
        self.assertEqual(
            rt.run_hiprt(
                bfs_kernel,
                graph=empty_graph,
                frontier=(rt.FrontierVertex(vertex_id=0, level=0),),
                visited=(),
            ),
            (),
        )


if __name__ == "__main__":
    unittest.main()
