from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import triangle_match_hiprt


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_match_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_match_nonunique_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=False))
    return rt.emit(triangles, fields=["u", "v", "w"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


def triangle_graph() -> rt.CSRGraph:
    return rt.csr_graph(
        row_offsets=(0, 2, 4, 6, 6),
        column_indices=(1, 2, 0, 2, 0, 1),
    )


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal558HiprtTriangleMatchTest(unittest.TestCase):
    def test_direct_helper_matches_cpu_reference(self) -> None:
        graph = triangle_graph()
        seeds = (rt.EdgeSeed(0, 1), rt.EdgeSeed(0, 2), rt.EdgeSeed(1, 2))
        self.assertEqual(
            triangle_match_hiprt(graph, seeds, order="id_ascending", unique=True),
            rt.triangle_probe_cpu(graph, seeds, order="id_ascending", unique=True),
        )

    def test_run_hiprt_matches_cpu_reference(self) -> None:
        inputs = {
            "graph": triangle_graph(),
            "seeds": (rt.EdgeSeed(0, 1), rt.EdgeSeed(0, 2), rt.EdgeSeed(1, 2)),
        }
        self.assertEqual(
            rt.run_hiprt(triangle_match_kernel, **inputs),
            rt.run_cpu_python_reference(triangle_match_kernel, **inputs),
        )

    def test_unique_false_matches_cpu_reference_for_duplicate_seeds(self) -> None:
        inputs = {
            "graph": triangle_graph(),
            "seeds": (rt.EdgeSeed(0, 1), rt.EdgeSeed(0, 1)),
        }
        self.assertEqual(
            rt.run_hiprt(triangle_match_nonunique_kernel, **inputs),
            rt.run_cpu_python_reference(triangle_match_nonunique_kernel, **inputs),
        )

    def test_empty_inputs_return_empty_rows(self) -> None:
        self.assertEqual(rt.run_hiprt(triangle_match_kernel, graph=triangle_graph(), seeds=()), ())
        empty_graph = rt.csr_graph(row_offsets=(0, 0), column_indices=())
        self.assertEqual(
            rt.run_hiprt(triangle_match_kernel, graph=empty_graph, seeds=(rt.EdgeSeed(0, 0),)),
            (),
        )


if __name__ == "__main__":
    unittest.main()
