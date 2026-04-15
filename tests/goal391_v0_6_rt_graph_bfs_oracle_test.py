import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_expand_reference():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


class Goal391V06RtGraphBfsOracleTest(unittest.TestCase):
    def _graph(self):
        return rt.csr_graph(
            row_offsets=(0, 2, 4, 5, 5),
            column_indices=(1, 2, 2, 3, 3),
        )

    def test_run_cpu_matches_python_reference_for_bfs_expand(self) -> None:
        inputs = {
            "frontier": (rt.FrontierVertex(vertex_id=0, level=0), rt.FrontierVertex(vertex_id=1, level=0)),
            "graph": self._graph(),
            "visited": (0, 1),
        }
        self.assertEqual(
            rt.run_cpu(bfs_expand_reference, **inputs),
            rt.run_cpu_python_reference(bfs_expand_reference, **inputs),
        )

    def test_run_cpu_accepts_mapping_graph_inputs_for_bfs_expand(self) -> None:
        rows = rt.run_cpu(
            bfs_expand_reference,
            frontier=({"vertex_id": 0, "level": 2},),
            graph={
                "row_offsets": (0, 2, 3, 3),
                "column_indices": (1, 2, 2),
            },
            visited=({"vertex_id": 0},),
        )
        self.assertEqual(
            rows,
            (
                {"src_vertex": 0, "dst_vertex": 1, "level": 3},
                {"src_vertex": 0, "dst_vertex": 2, "level": 3},
            ),
        )

    def test_run_cpu_rejects_invalid_frontier_vertex(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "frontier vertex_id must be a valid graph vertex"):
            rt.run_cpu(
                bfs_expand_reference,
                frontier=((9, 0),),
                graph=self._graph(),
                visited=(),
            )

    def test_run_cpu_matches_python_reference_for_triangle_graph_kernel(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def triangle_probe_reference():
            seeds = rt.input("seeds", rt.EdgeSet, role="probe")
            graph = rt.input("graph", rt.GraphCSR, role="build")
            candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
            triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
            return rt.emit(triangles, fields=["u", "v", "w"])

        inputs = {
            "seeds": ((0, 1),),
            "graph": rt.csr_graph(row_offsets=(0, 2, 4), column_indices=(1, 0, 0, 1)),
        }
        self.assertEqual(
            rt.run_cpu(
                triangle_probe_reference,
                **inputs,
            ),
            rt.run_cpu_python_reference(
                triangle_probe_reference,
                **inputs,
            ),
        )


if __name__ == "__main__":
    unittest.main()
