from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal2453_rt_dbscan_planner_budget_pod_smoke" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal2453_rt_dbscan_planner_budget_pod_smoke_2026-05-19.md"


class Goal2453RtDbscanPlannerBudgetPodSmokeTest(unittest.TestCase):
    def test_pod_smoke_selects_full_adjacency_by_default(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(summary["selected_mode"], "optix_rt_core_adjacency_cupy_components_3d")
        self.assertEqual(summary["directed_edge_budget"], 160_000_000)
        self.assertLessEqual(summary["estimated_directed_edge_count"], summary["directed_edge_budget"])
        self.assertTrue(summary["full_stream_fits_budget"])
        self.assertTrue(summary["not_hidden_dispatcher"])
        self.assertFalse(summary["claim_boundary"]["automatic_hidden_dispatcher"])
        self.assertFalse(summary["claim_boundary"]["release_claim_authorized"])

    def test_report_records_validation_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("--no-validation", report)
        self.assertIn("not a release claim", report)


if __name__ == "__main__":
    unittest.main()
