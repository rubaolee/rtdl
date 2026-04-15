import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_probe_reference():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


class Goal392V06RtGraphTriangleOracleTest(unittest.TestCase):
    def _triangle_graph(self):
        return rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )

    def test_run_cpu_matches_python_reference_for_triangle_probe(self) -> None:
        inputs = {
            "seeds": ((0, 1), (1, 2), (0, 2)),
            "graph": self._triangle_graph(),
        }
        self.assertEqual(
            rt.run_cpu(triangle_probe_reference, **inputs),
            rt.run_cpu_python_reference(triangle_probe_reference, **inputs),
        )

    def test_run_cpu_accepts_mapping_inputs_for_triangle_probe(self) -> None:
        rows = rt.run_cpu(
            triangle_probe_reference,
            seeds=({"u": 0, "v": 1},),
            graph={"row_offsets": (0, 2, 4, 6), "column_indices": (1, 2, 0, 2, 0, 1)},
        )
        self.assertEqual(rows, ({"u": 0, "v": 1, "w": 2},))

    def test_run_cpu_rejects_invalid_seed_vertex(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "edge seed vertices must be valid graph vertex IDs"):
            rt.run_cpu(
                triangle_probe_reference,
                seeds=((0, 9),),
                graph=self._triangle_graph(),
            )

    def test_run_cpu_dedupes_duplicate_seed_triangles(self) -> None:
        rows = rt.run_cpu(
            triangle_probe_reference,
            seeds=((0, 1), (0, 1)),
            graph=self._triangle_graph(),
        )
        self.assertEqual(rows, ({"u": 0, "v": 1, "w": 2},))


if __name__ == "__main__":
    unittest.main()
