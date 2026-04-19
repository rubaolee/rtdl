from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import prepare_hiprt_graph_csr


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_match_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


def graph_fixture() -> rt.CSRGraph:
    return rt.csr_graph(
        row_offsets=(0, 2, 4, 6, 7, 7),
        column_indices=(1, 2, 0, 2, 0, 1, 4),
    )


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal567HiprtPreparedGraphTest(unittest.TestCase):
    def test_direct_prepared_graph_matches_bfs_cpu_reference_for_multiple_batches(self) -> None:
        graph = graph_fixture()
        batches = (
            ((rt.FrontierVertex(vertex_id=0, level=0),), (0,)),
            ((rt.FrontierVertex(vertex_id=1, level=1), rt.FrontierVertex(vertex_id=3, level=1)), (0, 1, 3)),
        )
        with prepare_hiprt_graph_csr(graph) as prepared:
            for frontier, visited in batches:
                self.assertEqual(
                    prepared.bfs_expand(frontier, visited, dedupe=True),
                    rt.bfs_expand_cpu(graph, frontier, visited, dedupe=True),
                )

    def test_direct_prepared_graph_matches_triangle_cpu_reference_for_multiple_batches(self) -> None:
        graph = graph_fixture()
        batches = (
            (rt.EdgeSeed(0, 1), rt.EdgeSeed(0, 2), rt.EdgeSeed(1, 2)),
            (rt.EdgeSeed(1, 0), rt.EdgeSeed(2, 0)),
        )
        with prepare_hiprt_graph_csr(graph) as prepared:
            for seeds in batches:
                self.assertEqual(
                    prepared.triangle_match(seeds, order="id_ascending", unique=True),
                    rt.triangle_probe_cpu(graph, seeds, order="id_ascending", unique=True),
                )

    def test_high_level_prepare_hiprt_matches_bfs_cpu_reference(self) -> None:
        graph = graph_fixture()
        with rt.prepare_hiprt(bfs_kernel, graph=graph) as prepared:
            frontier = (rt.FrontierVertex(vertex_id=0, level=0),)
            visited = (0,)
            self.assertEqual(
                prepared.run(frontier=frontier, visited=visited),
                rt.run_cpu_python_reference(bfs_kernel, graph=graph, frontier=frontier, visited=visited),
            )

    def test_high_level_prepare_hiprt_matches_triangle_cpu_reference(self) -> None:
        graph = graph_fixture()
        with rt.prepare_hiprt(triangle_match_kernel, graph=graph) as prepared:
            seeds = (rt.EdgeSeed(0, 1), rt.EdgeSeed(0, 2), rt.EdgeSeed(1, 2))
            self.assertEqual(
                prepared.run(seeds=seeds),
                rt.run_cpu_python_reference(triangle_match_kernel, graph=graph, seeds=seeds),
            )


if __name__ == "__main__":
    unittest.main()
