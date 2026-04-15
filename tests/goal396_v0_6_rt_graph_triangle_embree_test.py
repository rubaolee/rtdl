import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from tests._embree_support import embree_available


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_probe_reference():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


@unittest.skipUnless(embree_available(), "Embree runtime is not available")
class Goal396V06RtGraphTriangleEmbreeTest(unittest.TestCase):
    def _triangle_graph(self):
        return rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )

    def test_run_embree_matches_python_reference_for_triangle_probe(self) -> None:
        inputs = {
            "seeds": ((0, 1), (1, 2), (0, 2)),
            "graph": self._triangle_graph(),
        }
        self.assertEqual(
            rt.run_embree(triangle_probe_reference, **inputs),
            rt.run_cpu_python_reference(triangle_probe_reference, **inputs),
        )

    def test_run_embree_matches_oracle_for_triangle_probe(self) -> None:
        inputs = {
            "seeds": ((0, 1),),
            "graph": self._triangle_graph(),
        }
        self.assertEqual(
            rt.run_embree(triangle_probe_reference, **inputs),
            rt.run_cpu(triangle_probe_reference, **inputs),
        )

    def test_prepare_embree_accepts_graph_triangle_kernel(self) -> None:
        prepared = rt.prepare_embree(triangle_probe_reference)
        rows = prepared.run(
            seeds=((0, 1),),
            graph=self._triangle_graph(),
        )
        self.assertEqual(rows, ({"u": 0, "v": 1, "w": 2},))

    def test_run_embree_matches_oracle_when_second_endpoint_has_smaller_degree(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 3, 5, 7, 8),
            column_indices=(1, 2, 3, 0, 2, 0, 1, 0),
        )
        inputs = {
            "seeds": ((0, 1),),
            "graph": graph,
        }
        self.assertEqual(
            rt.run_embree(triangle_probe_reference, **inputs),
            rt.run_cpu(triangle_probe_reference, **inputs),
        )

    def test_run_embree_rejects_invalid_seed_vertex(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "edge seed vertices must be valid graph vertex IDs"):
            rt.run_embree(
                triangle_probe_reference,
                seeds=((0, 9),),
                graph=self._triangle_graph(),
            )


if __name__ == "__main__":
    unittest.main()
