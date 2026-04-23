import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt
from examples import rtdl_graph_analytics_app
from examples import rtdl_graph_bfs
from examples import rtdl_graph_triangle_count


ROOT = Path(__file__).resolve().parents[1]


class Goal814GraphOptixRtCoreHonestyGateTest(unittest.TestCase):
    def test_graph_app_metadata_remains_host_indexed_fallback(self) -> None:
        self.assertEqual(
            rt.app_engine_support("graph_analytics", "optix").status,
            "direct_cli_compatibility_fallback",
        )
        self.assertEqual(
            rt.optix_app_performance_support("graph_analytics").performance_class,
            "host_indexed_fallback",
        )
        self.assertEqual(
            rt.optix_app_benchmark_readiness("graph_analytics").status,
            "needs_native_kernel_tuning",
        )
        self.assertEqual(
            rt.rt_core_app_maturity("graph_analytics").current_status,
            "needs_rt_core_redesign",
        )

    def test_graph_app_require_rt_core_fails_before_running_optix(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "host-indexed fallback"):
            rtdl_graph_analytics_app.run_app("optix", "all", require_rt_core=True)

    def test_component_apps_require_rt_core_fail_before_running_optix(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "graph_bfs OptiX path is host-indexed fallback"):
            rtdl_graph_bfs.run_backend("optix", require_rt_core=True)
        with self.assertRaisesRegex(RuntimeError, "graph_triangle_count OptiX path is host-indexed fallback"):
            rtdl_graph_triangle_count.run_backend("optix", require_rt_core=True)

    def test_require_rt_core_is_optix_only(self) -> None:
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            rtdl_graph_analytics_app.run_app("embree", "bfs", require_rt_core=True)

    def test_cpu_summary_output_records_no_rt_core_acceleration(self) -> None:
        payload = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            "all",
            copies=2,
            output_mode="summary",
        )
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertEqual(payload["sections"]["bfs"]["summary"]["discovered_edge_count"], 4)
        self.assertEqual(payload["sections"]["triangle_count"]["summary"]["triangle_count"], 2)

    def test_cli_require_rt_core_exits_nonzero_without_optix_library(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "examples/rtdl_graph_analytics_app.py",
                "--backend",
                "optix",
                "--require-rt-core",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("host-indexed fallback", result.stderr)


if __name__ == "__main__":
    unittest.main()
