from __future__ import annotations

import json
import pathlib
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET,
    plan_rt_dbscan_continuation_execution,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2452_rt_dbscan_full_adjacency_planner_budget_2026-05-19.md"
SUMMARY = ROOT / "docs" / "reports" / "goal2452_rt_dbscan_full_vs_chunked_adjacency_probe" / "summary.json"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"


class Goal2452RtDbscanFullAdjacencyPlannerBudgetTest(unittest.TestCase):
    def test_default_budget_promotes_clustered_32768_to_full_adjacency(self) -> None:
        self.assertEqual(DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET, 160_000_000)

        plan = plan_rt_dbscan_continuation_execution("clustered3d", 32768)
        self.assertEqual(plan["selected_mode"], "optix_rt_core_adjacency_cupy_components_3d")
        self.assertTrue(plan["full_stream_fits_budget"])
        self.assertIn("Goal2452", plan["evidence_goals"])

        forced_grouped = plan_rt_dbscan_continuation_execution(
            "clustered3d",
            32768,
            directed_edge_budget=64_000_000,
        )
        self.assertEqual(forced_grouped["selected_mode"], "optix_rt_core_grouped_stream_cupy_components_3d")
        self.assertFalse(forced_grouped["full_stream_fits_budget"])

    def test_pod_artifact_supports_full_stream_policy(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        ratio = float(summary["full_over_chunked_time_ratio"])

        self.assertLess(ratio, 0.2)
        self.assertTrue(summary["full_adjacency"]["signatures_match"])
        self.assertTrue(summary["chunked_adjacency"]["signatures_match"])

    def test_docs_keep_plan_explain_and_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn("160,000,000", report)
        self.assertIn("not an invisible", report)
        self.assertIn("accept-with-boundary", report)
        self.assertIn("Goal2452 raised the default directed-edge budget", readme)
        self.assertIn("--adjacency-edge-budget", readme)


if __name__ == "__main__":
    unittest.main()
