import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from tests.rtdsl_vulkan_test import vulkan_available


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_probe_reference():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


@unittest.skipUnless(vulkan_available(), "Vulkan is not available in the current environment")
class Goal398V06RtGraphTriangleVulkanTest(unittest.TestCase):
    def _triangle_graph(self):
        return rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )

    def test_run_vulkan_matches_python_reference_for_triangle_probe(self) -> None:
        inputs = {
            "seeds": ((0, 1), (1, 2), (0, 2)),
            "graph": self._triangle_graph(),
        }
        self.assertEqual(
            rt.run_vulkan(triangle_probe_reference, **inputs),
            rt.run_cpu_python_reference(triangle_probe_reference, **inputs),
        )

    def test_run_vulkan_matches_oracle_for_triangle_probe(self) -> None:
        inputs = {
            "seeds": ((0, 1),),
            "graph": self._triangle_graph(),
        }
        self.assertEqual(
            rt.run_vulkan(triangle_probe_reference, **inputs),
            rt.run_cpu(triangle_probe_reference, **inputs),
        )

    def test_prepare_vulkan_accepts_graph_triangle_kernel(self) -> None:
        prepared = rt.prepare_vulkan(triangle_probe_reference)
        rows = prepared.run(
            seeds=((0, 1),),
            graph=self._triangle_graph(),
        )
        self.assertEqual(rows, ({"u": 0, "v": 1, "w": 2},))

    def test_run_vulkan_rejects_invalid_seed_vertex(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "edge seed vertices must be valid graph vertex IDs"):
            rt.run_vulkan(
                triangle_probe_reference,
                seeds=((0, 9),),
                graph=self._triangle_graph(),
            )


if __name__ == "__main__":
    unittest.main()
