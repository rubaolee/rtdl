from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2041_embree_cpu_partner_weak_row_repair_2026-05-14.md"
REPORT_JSON = ROOT / "docs" / "reports" / "goal2041_embree_cpu_partner_weak_row_repair_2026-05-14.json"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal2039_embree_cpu_partner_all_thread_local_linux_evidence_2026-05-14.json"
REPAIRED_SUMMARY = ROOT / "docs" / "reports" / "goal2041_embree_cpu_partner_all_thread_large_repaired_v2" / "summary.json"


class Goal2041EmbreeCpuPartnerWeakRowRepairTest(unittest.TestCase):
    def test_report_boundaries_are_explicit(self) -> None:
        self.assertTrue(REPORT.exists())
        self.assertTrue(REPORT_JSON.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Status: `accept-with-boundary`", text)
        self.assertIn("exact K=3 facility fallback ranking", text)
        self.assertIn("exact Hausdorff distance and witness", text)
        self.assertIn("v2.0 release readiness", text)
        data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(data["verdict"], "accept-with-boundary")
        self.assertFalse(data["claim_boundary"]["exact_ranked_knn_solved"])
        self.assertFalse(data["claim_boundary"]["exact_hausdorff_distance_solved"])
        self.assertFalse(data["claim_boundary"]["generic_polygon_overlay_solved"])

    def test_repaired_full_matrix_passes(self) -> None:
        summary = json.loads(REPAIRED_SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["row_count"], 16)
        self.assertEqual(summary["status_counts"], {"pass": 16})
        self.assertEqual(summary["environment"]["logical_cpu_count"], 8)
        self.assertEqual(summary["environment"]["python_modules"]["numpy"], "2.4.4")

    def test_weak_rows_improved_against_goal2039(self) -> None:
        baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))["large"]["median_seconds_by_app"]
        repaired = {
            row["app"]: row["timing"]["median_s"]
            for row in json.loads(REPAIRED_SUMMARY.read_text(encoding="utf-8"))["rows"]
        }
        minimum_speedups = {
            "facility_knn_assignment": 50.0,
            "polygon_pair_overlap_area_rows": 5.0,
            "polygon_set_jaccard": 10.0,
            "hausdorff_distance": 50.0,
            "ann_candidate_search": 40.0,
        }
        for app, minimum_speedup in minimum_speedups.items():
            with self.subTest(app=app):
                self.assertGreater(baseline[app] / repaired[app], minimum_speedup)

    def test_repaired_rows_use_generic_partner_paths(self) -> None:
        summary = json.loads(REPAIRED_SUMMARY.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in summary["rows"]}
        self.assertIn("coverage_threshold_prepared", rows["facility_knn_assignment"]["command"])
        self.assertIn("candidate_threshold_prepared", rows["ann_candidate_search"]["command"])
        self.assertIn("directed_threshold_prepared", rows["hausdorff_distance"]["command"])
        self.assertIn("partner_bbox", rows["polygon_pair_overlap_area_rows"]["command"])
        self.assertIn("partner_bbox", rows["polygon_set_jaccard"]["command"])


if __name__ == "__main__":
    unittest.main()
