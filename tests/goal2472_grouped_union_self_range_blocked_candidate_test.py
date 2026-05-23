from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal2472_grouped_union_self_range_blocked_candidate_2026-05-20.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"
POD_RUNNER = ROOT / "scripts" / "goal2467_grouped_stream_baseline_pod_runner.py"
POD_GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2472_gemini_review_self_range_blocked_candidate_pod_2026-05-21.md"
POD_CONSENSUS = ROOT / "docs" / "reviews" / "goal2472_codex_gemini_consensus_self_range_blocked_candidate_pod_2026-05-21.md"


class Goal2472GroupedUnionSelfRangeBlockedCandidateTest(unittest.TestCase):
    def test_native_adds_generic_self_range_symbol_without_dbscan_vocabulary(self) -> None:
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        symbol = "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs"

        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn("apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_optix", workloads)
        self.assertIn("query_start", api + prelude + workloads)
        self.assertIn("device_search + query_start", workloads)
        self.assertIn("prepared search device buffer is missing", workloads)
        native_slice = workloads[
            workloads.index("apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_optix"):
            workloads.index("static void launch_prepared_fixed_radius_grouped_union_3d_device_outputs_optix")
        ]
        self.assertNotIn("dbscan", native_slice.lower())
        self.assertNotIn("cluster", native_slice.lower())

    def test_python_runtime_exposes_range_method_and_metadata_boundary(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_SYMBOL", runtime)
        self.assertIn("def apply_device_grouped_union_self_range(", runtime)
        self.assertIn("query_range_policy", runtime)
        self.assertIn("explicit_contiguous_prepared_search_range", runtime)
        self.assertIn("grouped_union_blocked_candidate", runtime)
        self.assertIn("prepared_search_points_self_query_device_range", runtime)
        self.assertIn("predicate_flags and fallback_candidate_out must both be omitted only for all-items mode", runtime)

    def test_partner_adapter_uses_range_only_for_explicit_query_blocks(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        start = adapters.index("class PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D")
        end = adapters.index("def prepare_optix_cupy_radius_graph_components_3d", start)
        grouped = adapters[start:end]

        self.assertIn("grouped_union_query_block_size", grouped)
        self.assertIn("use_query_blocks", grouped)
        self.assertIn("apply_device_grouped_union_self_range", grouped)
        self.assertIn("prepared_rt_core_grouped_union_3d_self_query_blocked_ranges", grouped)
        self.assertIn("grouped_union_query_blocked_candidate", grouped)
        self.assertIn("performance_claim_authorized", grouped)
        self.assertNotIn("dbscan", grouped.lower())

    def test_benchmark_app_exposes_explicit_blocked_modes_not_default_dispatch(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn("DEFAULT_GROUPED_UNION_QUERY_BLOCK_SIZE", app)
        self.assertIn("optix_rt_core_grouped_stream_blocked_cupy_components_3d", app)
        self.assertIn("optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d", app)
        self.assertIn("--grouped-union-query-block-size", app)
        self.assertIn("grouped_union_query_blocked_candidate", app)
        self.assertIn("prepared_rt_core_grouped_union_3d_self_query_blocked_ranges", app)
        self.assertIn("column-signature mode does not materialize Python rows", app)
        self.assertNotIn('"planned_rt_dbscan": "optix_rt_core_grouped_stream_blocked', app)

    def test_report_and_todo_keep_candidate_as_unclaimed_runtime_work(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("No DBSCAN-specific native ABI was added", report)
        self.assertIn("not a release or speed claim", report)
        self.assertIn("not yet the final segmented proposal-reduction implementation", report)
        self.assertIn("Pod validation shows range blocking hurts", report)
        self.assertIn("should not be promoted", report)
        self.assertIn("Goal2472", todo)
        self.assertIn("self-query range", todo)

    def test_pod_review_consensus_rejects_query_chunking_as_optimization(self) -> None:
        review = POD_GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = POD_CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Blocking Issues: None", review)
        self.assertIn("refutes query-range blocking as a performance optimization", review)
        self.assertIn("performance optimization to promote", consensus)
        self.assertIn("Do not spend more time trying to optimize this workload by adding", consensus)

    def test_pod_runner_can_compare_blocked_query_range_candidate(self) -> None:
        runner = POD_RUNNER.read_text(encoding="utf-8")

        self.assertIn("--grouped-union-query-block-size", runner)
        self.assertIn("grouped_union_query_block_size", runner)
        self.assertIn("native_goal2472_query_range_candidate", runner)
        self.assertIn("goal2472_performance_claim_authorized", runner)


if __name__ == "__main__":
    unittest.main()
