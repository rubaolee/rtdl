import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from tests.rtdsl_vulkan_test import vulkan_available


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_expand_reference():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


@unittest.skipUnless(vulkan_available(), "Vulkan is not available in the current environment")
class Goal395V06RtGraphBfsVulkanTest(unittest.TestCase):
    def _graph(self):
        return rt.csr_graph(
            row_offsets=(0, 2, 4, 5, 5),
            column_indices=(1, 2, 2, 3, 3),
        )

    def test_run_vulkan_matches_python_reference_for_bfs_expand(self) -> None:
        inputs = {
            "frontier": (rt.FrontierVertex(vertex_id=0, level=0), rt.FrontierVertex(vertex_id=1, level=0)),
            "graph": self._graph(),
            "visited": (0, 1),
        }
        self.assertEqual(
            rt.run_vulkan(bfs_expand_reference, **inputs),
            rt.run_cpu_python_reference(bfs_expand_reference, **inputs),
        )

    def test_run_vulkan_matches_oracle_for_bfs_expand(self) -> None:
        inputs = {
            "frontier": ((0, 0),),
            "graph": self._graph(),
            "visited": (),
        }
        self.assertEqual(
            rt.run_vulkan(bfs_expand_reference, **inputs),
            rt.run_cpu(bfs_expand_reference, **inputs),
        )

    def test_prepare_vulkan_accepts_graph_bfs_kernel(self) -> None:
        prepared = rt.prepare_vulkan(bfs_expand_reference)
        rows = prepared.run(
            frontier=((0, 0),),
            graph=self._graph(),
            visited=(),
        )
        self.assertEqual(
            rows,
            (
                {"src_vertex": 0, "dst_vertex": 1, "level": 1},
                {"src_vertex": 0, "dst_vertex": 2, "level": 1},
            ),
        )

    def test_run_vulkan_rejects_invalid_frontier_vertex(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "frontier vertex_id must be a valid graph vertex"):
            rt.run_vulkan(
                bfs_expand_reference,
                frontier=((9, 0),),
                graph=self._graph(),
                visited=(),
            )


if __name__ == "__main__":
    unittest.main()
