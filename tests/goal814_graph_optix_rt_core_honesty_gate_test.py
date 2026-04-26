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
    def test_graph_app_metadata_records_bounded_rt_paths(self) -> None:
        self.assertEqual(
            rt.app_engine_support("graph_analytics", "optix").status,
            "direct_cli_compatibility_fallback",
        )
        self.assertEqual(
            rt.optix_app_performance_support("graph_analytics").performance_class,
            "optix_traversal",
        )
        self.assertEqual(
            rt.optix_app_benchmark_readiness("graph_analytics").status,
            "ready_for_rtx_claim_review",
        )
        self.assertEqual(
            rt.rt_core_app_maturity("graph_analytics").current_status,
            "rt_core_ready",
        )

    def test_graph_app_require_rt_core_fails_before_running_optix(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "limited to --scenario visibility_edges"):
            rtdl_graph_analytics_app.run_app("optix", "all", require_rt_core=True)

    def test_component_apps_require_rt_core_fail_before_running_optix(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not NVIDIA RT-core traversal"):
            rtdl_graph_bfs.run_backend("optix", require_rt_core=True)
        with self.assertRaisesRegex(RuntimeError, "not NVIDIA RT-core traversal"):
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
        self.assertEqual(payload["sections"]["visibility_edges"]["row_count"], 8)
        self.assertEqual(payload["sections"]["visibility_edges"]["summary"]["visible_edge_count"], 2)
        self.assertEqual(payload["sections"]["visibility_edges"]["summary"]["blocked_edge_count"], 6)

    def test_visibility_edges_is_only_require_rt_core_graph_candidate(self) -> None:
        payload = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            "visibility_edges",
            output_mode="summary",
        )
        self.assertIn("visibility_edges", payload["sections"])
        self.assertEqual(payload["sections"]["visibility_edges"]["row_count"], 4)
        self.assertIn("visibility_edges is an OptiX", payload["honesty_boundary"])
        self.assertIn("native graph-ray mode remains gated", payload["honesty_boundary"])

    def test_optix_visibility_edges_top_level_marks_rt_core_candidate(self) -> None:
        from unittest import mock

        fake_section = {
            "app": "graph_visibility_edges",
            "backend": "optix",
            "copies": 1,
            "output_mode": "summary",
            "row_count": 4,
            "rows": [],
            "summary": {"visible_edge_count": 1, "blocked_edge_count": 3},
            "rt_core_accelerated": True,
        }
        with mock.patch.object(rtdl_graph_analytics_app, "_run_visibility_edges", return_value=fake_section):
            payload = rtdl_graph_analytics_app.run_app(
                "optix",
                "visibility_edges",
                output_mode="summary",
                require_rt_core=True,
            )

        self.assertTrue(payload["rt_core_accelerated"])
        self.assertTrue(payload["ray_tracing_accelerated"])

    def test_optix_visibility_summary_uses_prepared_anyhit_count_not_row_materialization(self) -> None:
        from unittest import mock

        class FakePreparedScene:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return None

            def count(self, prepared_rays):
                return 6

        class FakePreparedRays:
            def __init__(self, rays):
                self.rays = rays

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return None

        with (
            mock.patch.object(
                rtdl_graph_analytics_app.rt,
                "prepare_optix_ray_triangle_any_hit_2d",
                return_value=FakePreparedScene(),
            ) as prepare_scene,
            mock.patch.object(
                rtdl_graph_analytics_app.rt,
                "prepare_optix_rays_2d",
                side_effect=lambda rays: FakePreparedRays(rays),
            ) as prepare_rays,
            mock.patch.object(
                rtdl_graph_analytics_app.rt,
                "visibility_pair_rows",
                side_effect=AssertionError("summary mode should not materialize visibility rows"),
            ),
        ):
            payload = rtdl_graph_analytics_app.run_app(
                "optix",
                "visibility_edges",
                copies=2,
                output_mode="summary",
                require_rt_core=True,
            )

        section = payload["sections"]["visibility_edges"]
        self.assertEqual(section["row_count"], 8)
        self.assertEqual(section["summary"], {"visible_edge_count": 2, "blocked_edge_count": 6})
        self.assertEqual(section["native_continuation_backend"], "optix_prepared_visibility_anyhit_count")
        self.assertTrue(section["native_continuation_active"])
        self.assertEqual(len(prepare_rays.call_args.args[0]), 8)
        prepare_scene.assert_called_once()

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
        self.assertIn("limited to --scenario visibility_edges", result.stderr)


if __name__ == "__main__":
    unittest.main()
