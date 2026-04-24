from __future__ import annotations

from pathlib import Path
import unittest

from examples import rtdl_graph_analytics_app
from examples import rtdl_graph_bfs
from examples import rtdl_graph_triangle_count


ROOT = Path(__file__).resolve().parents[1]


class Goal904OptixGraphRayModeTest(unittest.TestCase):
    def test_examples_expose_native_optix_graph_mode_without_rt_core_claim(self) -> None:
        with self.assertRaises(RuntimeError):
            rtdl_graph_bfs.run_backend("optix", require_rt_core=True, optix_graph_mode="native")
        with self.assertRaises(RuntimeError):
            rtdl_graph_triangle_count.run_backend("optix", require_rt_core=True, optix_graph_mode="native")

        payload = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            scenario="all",
            output_mode="summary",
            optix_graph_mode="native",
        )
        self.assertEqual(payload["optix_graph_mode"], "not_applicable")
        self.assertFalse(payload["rt_core_accelerated"])

    def test_native_optix_source_contains_graph_ray_kernels(self) -> None:
        core = (ROOT / "src/native/optix/rtdl_optix_core.cpp").read_text()
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text()
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text()

        self.assertIn("kGraphBfsRayKernelSrc", core)
        self.assertIn("kGraphTriangleRayKernelSrc", core)
        self.assertIn("__constant__ GraphBfsParams params", core)
        self.assertIn("__constant__ GraphTriangleParams params", core)
        self.assertNotIn("bfs_params", core)
        self.assertNotIn("tri_params", core)
        self.assertIn("__raygen__graph_bfs_probe", core)
        self.assertIn("__raygen__graph_triangle_probe", core)
        self.assertIn("__anyhit__graph_bfs_anyhit", core)
        self.assertIn("__anyhit__graph_triangle_anyhit", core)
        self.assertIn('compile_to_ptx(kGraphBfsRayKernelSrc, "graph_bfs_ray_kernel.cu")', workloads)
        self.assertIn(
            'compile_to_ptx(kGraphTriangleRayKernelSrc, "graph_triangle_ray_kernel.cu")',
            workloads,
        )
        self.assertIn("run_bfs_expand_optix_graph_ray", workloads)
        self.assertIn("run_triangle_probe_optix_graph_ray", workloads)
        self.assertIn('std::getenv("RTDL_OPTIX_GRAPH_MODE")', api)
        self.assertIn('std::strcmp(mode, "native") == 0', api)

    def test_default_optix_graph_mode_remains_conservative_until_cloud_gate(self) -> None:
        bfs_payload = rtdl_graph_bfs.run_backend(
            "cpu_python_reference",
            output_mode="summary",
            optix_graph_mode="auto",
        )
        triangle_payload = rtdl_graph_triangle_count.run_backend(
            "cpu_python_reference",
            output_mode="summary",
            optix_graph_mode="auto",
        )
        self.assertEqual(bfs_payload["optix_graph_mode"], "not_applicable")
        self.assertEqual(triangle_payload["optix_graph_mode"], "not_applicable")


if __name__ == "__main__":
    unittest.main()
