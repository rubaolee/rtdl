from __future__ import annotations

import pathlib
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET,
    estimate_rt_dbscan_directed_adjacency_edges,
    plan_rt_dbscan_continuation_execution,
    plan_rt_dbscan_execution,
    run_rt_dbscan_benchmark,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal2437_rt_dbscan_explicit_continuation_planner_2026-05-19.md"


class Goal2437RtDbscanExplicitContinuationPlannerTest(unittest.TestCase):
    def test_continuation_plan_selects_full_or_chunked_from_explicit_budget(self) -> None:
        tiny = plan_rt_dbscan_continuation_execution("tiny", 9)
        self.assertEqual(tiny["selected_mode"], "cpu_reference")
        self.assertTrue(tiny["not_hidden_dispatcher"])
        self.assertFalse(tiny["release_claim_authorized"])

        full = plan_rt_dbscan_continuation_execution("clustered3d", 4096)
        self.assertEqual(full["selected_mode"], "optix_rt_core_adjacency_cupy_components_3d")
        self.assertLessEqual(full["estimated_directed_edge_count"], DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET)
        self.assertTrue(full["full_stream_fits_budget"])

        larger_full = plan_rt_dbscan_continuation_execution("clustered3d", 32768)
        self.assertEqual(larger_full["selected_mode"], "optix_rt_core_adjacency_cupy_components_3d")
        self.assertLessEqual(larger_full["estimated_directed_edge_count"], DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET)
        self.assertTrue(larger_full["full_stream_fits_budget"])

        forced_chunked = plan_rt_dbscan_continuation_execution("clustered3d", 4096, directed_edge_budget=1_000_000)
        self.assertEqual(forced_chunked["selected_mode"], "optix_rt_core_chunked_adjacency_cupy_components_3d")

        forced_full = plan_rt_dbscan_continuation_execution("clustered3d", 32768, directed_edge_budget=200_000_000)
        self.assertEqual(forced_full["selected_mode"], "optix_rt_core_adjacency_cupy_components_3d")

    def test_edge_estimate_is_bounded_by_goal2435_evidence_shape(self) -> None:
        self.assertEqual(estimate_rt_dbscan_directed_adjacency_edges("tiny", 9), 33)
        self.assertGreater(estimate_rt_dbscan_directed_adjacency_edges("clustered3d", 8192), 8_000_000)
        self.assertLess(estimate_rt_dbscan_directed_adjacency_edges("clustered3d", 8192), 9_000_000)

    def test_one_shot_plan_remains_separate_from_continuation_plan(self) -> None:
        one_shot = plan_rt_dbscan_execution("clustered3d", 32768)
        continuation = plan_rt_dbscan_continuation_execution("clustered3d", 32768)

        self.assertEqual(one_shot["selected_mode"], "partner_cupy_prepared_grid_components_3d")
        self.assertEqual(continuation["selected_mode"], "optix_rt_core_adjacency_cupy_components_3d")
        self.assertEqual(
            continuation["policy"],
            "explicit_continuation_plan_from_goal2431_2433_2435_2452_adjacency_evidence",
        )
        self.assertEqual(continuation["evidence_goals"], ["Goal2431", "Goal2433", "Goal2435", "Goal2452"])

    def test_tiny_planned_continuation_executes_without_gpu_and_records_plan(self) -> None:
        payload = run_rt_dbscan_benchmark(
            mode="planned_rt_dbscan_continuation",
            dataset="tiny",
            point_count=None,
            radius=None,
            min_neighbors=None,
            seed=20260519,
            partner="cupy",
            include_rows=False,
            validate=True,
        )

        self.assertEqual(payload["mode"], "planned_rt_dbscan_continuation")
        self.assertEqual(payload["selected_mode"], "cpu_reference")
        self.assertTrue(payload["matches_reference"])
        plan = payload["metadata"]["execution_plan"]
        self.assertEqual(plan["adapter"], "plan_rt_dbscan_continuation_execution")
        self.assertTrue(plan["not_hidden_dispatcher"])
        self.assertFalse(payload["claim_boundary"]["automatic_hidden_dispatcher"])
        self.assertFalse(payload["claim_boundary"]["release_claim_authorized"])

    def test_docs_and_report_describe_plan_explain_boundary(self) -> None:
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("planned_rt_dbscan_continuation", app)
        self.assertIn("plan_rt_dbscan_continuation_execution", app)
        self.assertIn("benchmark_app_plan_explain_not_engine_dispatch", app)
        self.assertIn("Explicit Continuation Plan Mode", readme)
        self.assertIn("not hidden dispatch", readme)
        self.assertIn("full stream fits", readme)
        self.assertIn("accept-with-boundary", report)
        self.assertIn("not a hidden dispatcher", report)
        self.assertIn("does not replace the one-shot", report)


if __name__ == "__main__":
    unittest.main()
