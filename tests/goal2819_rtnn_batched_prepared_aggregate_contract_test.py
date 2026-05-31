from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2819_rtnn_batched_prepared_aggregate_contract_2026-05-31.md"


class Goal2819RtnnBatchedPreparedAggregateContractTest(unittest.TestCase):
    def test_native_batch_abi_is_generic_and_app_agnostic(self) -> None:
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        symbol = "rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch"
        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn(
            "aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix",
            workloads,
        )
        self.assertIn("const double* radii", workloads)
        self.assertIn("const size_t* k_values", workloads)
        self.assertIn("RtdlFixedRadiusRankedNeighborAggregate* aggregates_out", workloads)

        start = workloads.index(
            "aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix"
        )
        end = workloads.index("static void run_prepared_fixed_radius_neighbors_grid_3d_optix", start)
        body = workloads[start:end]

        self.assertIn("DevPtr d_aggregates", body)
        self.assertIn("cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_direct.fn", body)
        self.assertEqual(body.count("cuStreamSynchronize(nullptr)"), 1)
        self.assertIn("download(aggregates_out, d_aggregates.ptr, request_count)", body)
        self.assertNotIn("rtnn", body.lower())

    def test_python_runtime_exposes_validated_batch_method(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def aggregate_ranked_summary_prepared_queries_batch", runtime)
        self.assertIn("prepared query aggregate batch currently supports precision='float32'", runtime)
        self.assertIn("request[\"radius\"]", runtime)
        self.assertIn("request[\"k_max\"]", runtime)
        self.assertIn("rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch", runtime)
        self.assertIn("ctypes.POINTER(ctypes.c_double)", runtime)
        self.assertIn("ctypes.POINTER(ctypes.c_size_t)", runtime)
        self.assertIn("prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_direct", runtime)

    def test_runner_exposes_controlled_batch_mode_without_promoting_claims(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("ranked-summary-aggregate-prepared-query-batch-float32", runner)
        self.assertIn("aggregate_request_count", runner)
        self.assertIn("aggregate_ranked_summary_prepared_queries_batch", runner)
        self.assertIn('"aggregate_requests_batched"', runner)
        self.assertIn('"rtdl_speedup_claim_authorized": False', runner)
        self.assertIn('"broad_rt_core_speedup_claim_authorized": False', runner)

    def test_report_defers_pod_claims_and_names_measurement_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("implementation-pending-pod-evidence", report)
        self.assertIn("one native crossing", report)
        self.assertIn("per-request amortized timing", report)
        self.assertIn("must not be compared to a single CuPy call", report)
        self.assertIn("No pod performance claim is authorized until clean pod artifacts exist", report)
        self.assertIn("No native app-specific engine customization is introduced", report)


if __name__ == "__main__":
    unittest.main()
