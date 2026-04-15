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


class Goal390V06RtGraphTriangleTruthPathTest(unittest.TestCase):
    def _triangle_graph(self):
        return rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )

    def test_triangle_surface_exports_exist(self) -> None:
        self.assertEqual(rt.EdgeSet.name, "edge_set")
        predicate = rt.triangle_match(order="id_ascending", unique=True)
        self.assertEqual(predicate.name, "triangle_match")
        self.assertEqual(predicate.options, {"order": "id_ascending", "unique": True})

    def test_compile_kernel_preserves_intersect_mode_and_predicate(self) -> None:
        compiled = rt.compile_kernel(triangle_probe_reference)
        self.assertEqual(tuple(item.geometry.name for item in compiled.inputs), ("edge_set", "graph_csr"))
        self.assertEqual(compiled.candidates.mode, "graph_intersect")
        self.assertEqual(compiled.refine_op.predicate.name, "triangle_match")
        self.assertEqual(compiled.emit_op.fields, ("u", "v", "w"))

    def test_python_reference_emits_one_triangle_for_seed_batch(self) -> None:
        rows = rt.run_cpu_python_reference(
            triangle_probe_reference,
            seeds=((0, 1), (1, 2), (0, 2)),
            graph=self._triangle_graph(),
        )
        self.assertEqual(rows, ({"u": 0, "v": 1, "w": 2},))

    def test_python_reference_accepts_mapping_inputs(self) -> None:
        rows = rt.run_cpu_python_reference(
            triangle_probe_reference,
            seeds=({"u": 0, "v": 1},),
            graph={"row_offsets": (0, 2, 4, 6), "column_indices": (1, 2, 0, 2, 0, 1)},
        )
        self.assertEqual(rows, ({"u": 0, "v": 1, "w": 2},))

    def test_python_reference_rejects_invalid_seed_vertex(self) -> None:
        with self.assertRaisesRegex(ValueError, "edge seed vertices must be valid graph vertex IDs"):
            rt.run_cpu_python_reference(
                triangle_probe_reference,
                seeds=((0, 9),),
                graph=self._triangle_graph(),
            )

    def test_run_cpu_matches_python_reference_for_triangle_probe(self) -> None:
        inputs = {
            "seeds": ((0, 1),),
            "graph": self._triangle_graph(),
        }
        self.assertEqual(
            rt.run_cpu(triangle_probe_reference, **inputs),
            rt.run_cpu_python_reference(triangle_probe_reference, **inputs),
        )


if __name__ == "__main__":
    unittest.main()
