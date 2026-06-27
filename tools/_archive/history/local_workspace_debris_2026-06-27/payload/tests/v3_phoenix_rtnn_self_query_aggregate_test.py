import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class V3PhoenixRtnnSelfQueryAggregateTest(unittest.TestCase):
    def test_native_exports_generic_self_query_batch_symbol(self) -> None:
        symbol = "rtdl_optix_aggregate_self_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch"
        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, API.read_text(encoding="utf-8"))

        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn(
            "aggregate_self_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix",
            workloads,
        )
        self.assertIn("prepared->d_search ? prepared->d_search->ptr : 0", workloads)
        self.assertIn("prepared->search_points.size()", workloads)
        self.assertIn(
            "aggregate_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_device_queries_optix",
            workloads,
        )

    def test_native_exports_generic_self_query_graph_symbol(self) -> None:
        symbol = "rtdl_optix_prepare_fixed_radius_self_query_ranked_summary_aggregate_batch_graph_3d"
        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, API.read_text(encoding="utf-8"))

        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn(
            "prepare_fixed_radius_self_query_ranked_summary_aggregate_batch_graph_3d_optix",
            workloads,
        )
        self.assertIn("CUdeviceptr d_queries = 0", workloads)
        self.assertIn("bool self_query = false", workloads)
        self.assertIn("prepared->d_search ? prepared->d_search->ptr : 0", workloads)

    def test_python_runtime_wraps_self_query_without_query_handle(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        method_start = runtime.index("def aggregate_ranked_summary_self_query_batch")
        method_end = runtime.index("def prepare_ranked_summary_prepared_queries_batch_graph", method_start)
        method = runtime[method_start:method_end]

        self.assertIn(
            "rtdl_optix_aggregate_self_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch",
            method,
        )
        self.assertIn('"query_source": "prepared_search"', method)
        self.assertNotIn("prepared_queries._handle", method)
        self.assertNotIn("query_points", method)

    def test_python_runtime_wraps_self_query_graph_without_query_handle(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("def prepare_ranked_summary_self_query_batch_graph", runtime)
        self.assertIn(
            "rtdl_optix_prepare_fixed_radius_self_query_ranked_summary_aggregate_batch_graph_3d",
            runtime,
        )
        self.assertIn(
            'self._query_source = "prepared_query" if prepared_queries is not None else "prepared_search"',
            runtime,
        )
        self.assertIn("prepared_queries is None", runtime)

    def test_runner_exposes_explicit_self_query_mode_and_boundary(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        mode = "ranked-summary-aggregate-prepared-self-query-batch-float32"
        graph_mode = "ranked-summary-aggregate-prepared-self-query-batch-graph-float32"
        self.assertIn(mode, runner)
        self.assertIn(graph_mode, runner)
        self.assertIn("self_query_modes = {", runner)
        self.assertIn("prepared_query_graph_modes = {", runner)
        self.assertIn("*prepared_query_graph_modes", runner)
        self.assertIn('"prepared_query_points": result_mode in prepared_query_modes', runner)
        self.assertIn('"prepared_search_as_query_points": result_mode in self_query_modes', runner)
        self.assertIn(
            '"device_resident_query_points": result_mode in prepared_query_modes or result_mode in self_query_modes',
            runner,
        )
        self.assertIn("prepared self-query batch mode requires query_file to be omitted", runner)
        self.assertIn("set query_batch_size to the point count", runner)
        self.assertIn("prepared.aggregate_ranked_summary_self_query_batch", runner)
        self.assertIn("prepared.prepare_ranked_summary_self_query_batch_graph", runner)


if __name__ == "__main__":
    unittest.main()
