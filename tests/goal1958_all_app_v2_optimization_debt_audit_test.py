from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1958_all_app_v2_optimization_debt_audit_2026-05-14.md"
MATRIX = ROOT / "docs" / "reports" / "goal1930_all_app_v2_matrix_2026-05-13.json"
ANALYSIS = ROOT / "docs" / "reports" / "goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json"


class Goal1958AllAppV2OptimizationDebtAuditTest(unittest.TestCase):
    def test_report_covers_all_tracked_apps_and_remaining_debt_patterns(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

        for row in matrix["rows"]:
            self.assertIn(f"`{row['app']}`", text)
        for phrase in (
            "Metric-table graph continuation is fixed",
            "Threshold proxies for richer app semantics",
            "Row materialization",
            "Exact polygon/set reductions",
            "Partner reduction primitive set",
        ):
            self.assertIn(phrase, text)

    def test_matrix_no_longer_has_blank_control_rows_after_goal1957(self) -> None:
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        statuses = {row["comparison_status"] for row in matrix["rows"]}

        self.assertNotIn("evidence-only-control", statuses)
        self.assertIn("pod-evidence-collected-bounded", statuses)
        self.assertEqual(matrix["row_count"], 16)
        self.assertFalse(matrix["release_claim_boundary"]["v2_0_release_authorized"])

    def test_analysis_identifies_remaining_non_ideal_rows(self) -> None:
        analysis = json.loads(ANALYSIS.read_text(encoding="utf-8"))
        classes = {row["app"]: row["classification"] for row in analysis["rows"]}

        self.assertEqual(classes["facility_knn_assignment"], "positive-bounded-exact")
        self.assertEqual(classes["graph_analytics"], "positive-bounded")
        self.assertEqual(classes["polygon_pair_overlap_area_rows"], "positive-bounded")
        self.assertEqual(classes["polygon_set_jaccard"], "positive-bounded")
        self.assertEqual(classes["hausdorff_distance"], "positive-bounded-exact")
        self.assertEqual(classes["ann_candidate_search"], "positive-bounded-exact")
        self.assertEqual(classes["barnes_hut_force_app"], "positive-bounded-exact")
        self.assertEqual(classes["dbscan_clustering"], "positive-bounded-exact")
        self.assertEqual(analysis["classification_counts"]["positive"], 7)
        self.assertEqual(analysis["classification_counts"]["positive-bounded"], 3)
        self.assertEqual(analysis["classification_counts"]["positive-bounded-exact"], 5)
        self.assertFalse(analysis["claim_boundary"]["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
