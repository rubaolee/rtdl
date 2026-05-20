from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
OLD_SUMMARY = ROOT / "docs" / "reports" / "goal2459_grouped_stream_threshold_capped_pod" / "summary.json"
NEW_SUMMARY = ROOT / "docs" / "reports" / "goal2461_grouped_stream_self_query_pod" / "summary.json"


class Goal2461GroupedStreamSelfQueryDevicePathTest(unittest.TestCase):
    def test_native_exports_generic_self_query_grouped_union(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        symbol = "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs"

        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn("apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix", workloads)
        self.assertIn("prepared->d_search->ptr", workloads)
        self.assertIn("prepared search device buffer is missing", workloads)
        self.assertNotIn("dbscan", symbol)

    def test_python_runtime_exposes_self_query_device_binding(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn(
            "_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_SYMBOL",
            runtime,
        )
        self.assertIn("def apply_device_grouped_union_self(", runtime)
        self.assertIn("prepared_search_points_self_query_device", runtime)
        self.assertIn("prepared_device_search_points_self_grouped_union_workspaces", runtime)
        self.assertIn("generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces", runtime)
        self.assertIn("ctypes.c_double", runtime)

    def test_grouped_stream_adapter_uses_self_query_path(self) -> None:
        adapters = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        start = adapters.index("class PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D")
        end = adapters.index("def prepare_optix_cupy_radius_graph_components_3d", start)
        grouped_stream_class = adapters[start:end]

        self.assertIn("apply_device_grouped_union_self", grouped_stream_class)
        self.assertNotIn("apply_device_grouped_union(\n            self.point_rows", grouped_stream_class)
        self.assertIn("prepared_rt_core_grouped_union_3d_self_query", grouped_stream_class)
        self.assertIn("prepared_search_points_self_query_device", grouped_stream_class)

    def test_benchmark_app_explains_self_query_grouped_stream(self) -> None:
        app = APP.read_text(encoding="utf-8")
        start = app.index('elif mode == "optix_rt_core_grouped_stream_cupy_components_3d"')
        end = app.index('elif mode == "optix_rt_core_flags_cupy_microcell_graph_components_3d"', start)
        grouped_mode = app[start:end]

        self.assertIn("generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces", grouped_mode)
        self.assertIn("prepared_rt_core_grouped_union_3d_self_query", grouped_mode)
        self.assertIn("prepared_search_points_self_query_device", grouped_mode)
        self.assertIn("Goal2461", app)

    def test_pod_evidence_uses_self_query_and_improves_steady_state(self) -> None:
        old = json.loads(OLD_SUMMARY.read_text(encoding="utf-8"))
        new = json.loads(NEW_SUMMARY.read_text(encoding="utf-8"))
        old_by_count = {int(row["point_count"]): row for row in old["summaries"]}

        for row in new["summaries"]:
            point_count = int(row["point_count"])
            self.assertTrue(row["signatures_match"])
            self.assertLess(row["tail_median_sec"], old_by_count[point_count]["tail_median_sec"])
            steady = row["repeat_rows"][1]
            self.assertEqual(
                steady["grouped_native_symbol"],
                "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs",
            )
            self.assertEqual(
                steady["grouped_transfer_mode"],
                "prepared_device_search_points_self_grouped_union_workspaces",
            )
            self.assertEqual(steady["grouped_query_source"], "prepared_search_points_self_query_device")

        planned = new["planned_65536"]
        self.assertEqual(planned["selected_mode"], "optix_rt_core_grouped_stream_cupy_components_3d")
        self.assertEqual(
            planned["metadata"]["native_engine_summary_contract"],
            "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces",
        )
        self.assertEqual(
            planned["metadata"]["native_execution_path"],
            "prepared_rt_core_grouped_union_3d_self_query",
        )
        self.assertTrue(new["tiny_smoke"]["matches_reference"])


if __name__ == "__main__":
    unittest.main()
