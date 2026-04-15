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


class Goal389V06RtGraphBfsTruthPathTest(unittest.TestCase):
    def _graph(self):
        return rt.csr_graph(
            row_offsets=(0, 2, 4, 5, 5),
            column_indices=(1, 2, 2, 3, 3),
        )

    def test_graph_surface_exports_exist(self) -> None:
        self.assertEqual(rt.GraphCSR.name, "graph_csr")
        self.assertEqual(rt.VertexFrontier.name, "vertex_frontier")
        self.assertEqual(rt.VertexSet.name, "vertex_set")
        predicate = rt.bfs_discover(visited="visited", dedupe=True)
        self.assertEqual(predicate.name, "bfs_discover")
        self.assertEqual(predicate.options["visited_input"], "visited")

    def test_compile_kernel_preserves_graph_mode_and_predicate(self) -> None:
        compiled = rt.compile_kernel(bfs_expand_reference)
        self.assertEqual(tuple(item.geometry.name for item in compiled.inputs), ("vertex_frontier", "graph_csr", "vertex_set"))
        self.assertEqual(compiled.candidates.mode, "graph_expand")
        self.assertEqual(compiled.refine_op.predicate.name, "bfs_discover")
        self.assertEqual(compiled.emit_op.fields, ("src_vertex", "dst_vertex", "level"))

    def test_python_reference_expands_frontier_with_dedupe_and_visited_filter(self) -> None:
        rows = rt.run_cpu_python_reference(
            bfs_expand_reference,
            frontier=(rt.FrontierVertex(vertex_id=0, level=0), rt.FrontierVertex(vertex_id=1, level=0)),
            graph=self._graph(),
            visited=(0, 1),
        )
        self.assertEqual(
            rows,
            (
                {"src_vertex": 0, "dst_vertex": 2, "level": 1},
                {"src_vertex": 1, "dst_vertex": 3, "level": 1},
            ),
        )

    def test_python_reference_accepts_mapping_inputs(self) -> None:
        rows = rt.run_cpu_python_reference(
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

    def test_graph_validation_rejects_bad_offsets(self) -> None:
        with self.assertRaisesRegex(ValueError, "final row_offset must equal edge_count"):
            rt.validate_csr_graph(
                rt.CSRGraph(
                    row_offsets=(0, 1, 1),
                    column_indices=(1, 2),
                    vertex_count=2,
                )
            )

    def test_python_reference_rejects_invalid_frontier_vertex(self) -> None:
        with self.assertRaisesRegex(ValueError, "frontier vertex_id must be a valid graph vertex"):
            rt.run_cpu_python_reference(
                bfs_expand_reference,
                frontier=((9, 0),),
                graph=self._graph(),
                visited=(),
            )

    def test_run_cpu_matches_python_reference_for_bfs_expand(self) -> None:
        inputs = {
            "frontier": ((0, 0),),
            "graph": self._graph(),
            "visited": (),
        }
        self.assertEqual(
            rt.run_cpu(bfs_expand_reference, **inputs),
            rt.run_cpu_python_reference(bfs_expand_reference, **inputs),
        )


if __name__ == "__main__":
    unittest.main()
