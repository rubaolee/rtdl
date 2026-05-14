from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2039_embree_cpu_partner_all_thread_local_linux_evidence_2026-05-14.md"
REPORT_JSON = ROOT / "docs" / "reports" / "goal2039_embree_cpu_partner_all_thread_local_linux_evidence_2026-05-14.json"
SMOKE_SUMMARY = ROOT / "docs" / "reports" / "goal2037_embree_cpu_partner_all_thread_local_linux_smoke_8df10007" / "summary.json"
LARGE_SUMMARY = ROOT / "docs" / "reports" / "goal2039_embree_cpu_partner_all_thread_local_linux_large_repaired" / "summary.json"
ROBOT_ROW = ROOT / "docs" / "reports" / "goal2039_embree_cpu_partner_all_thread_local_linux_large_repaired" / "rows" / "robot_collision_screening.json"


class Goal2039EmbreeCpuPartnerEvidenceTest(unittest.TestCase):
    def test_evidence_reports_exist_and_keep_claim_boundaries(self) -> None:
        self.assertTrue(REPORT.exists())
        self.assertTrue(REPORT_JSON.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Status: `accept-with-boundary`", text)
        self.assertIn("must not claim", text)
        self.assertIn("v2.0 release readiness", text)
        self.assertIn("true host zero-copy for every row", text)
        data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(data["verdict"], "accept-with-boundary")
        self.assertFalse(data["interpretation"]["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(data["interpretation"]["claim_boundary"]["broad_all_app_speedup_claim_authorized"])

    def test_smoke_and_large_artifacts_cover_all_rows(self) -> None:
        smoke = json.loads(SMOKE_SUMMARY.read_text(encoding="utf-8"))
        large = json.loads(LARGE_SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(smoke["row_count"], 16)
        self.assertEqual(large["row_count"], 16)
        self.assertEqual(smoke["status_counts"], {"pass": 16})
        self.assertEqual(large["status_counts"], {"pass": 16})
        self.assertEqual(large["environment"]["logical_cpu_count"], 8)
        self.assertEqual(large["environment"]["python_modules"]["numpy"], "2.4.4")
        self.assertIsNone(large["environment"]["python_modules"]["torch"])
        self.assertIsNone(large["environment"]["python_modules"]["numba"])

    def test_large_robot_row_uses_perf_only_validation_boundary(self) -> None:
        robot = json.loads(ROBOT_ROW.read_text(encoding="utf-8"))
        self.assertEqual(robot["status"], "pass")
        self.assertIn("--skip-validation", robot["command"])
        self.assertLess(robot["timing"]["median_s"], 2.0)
        self.assertIn("validation_mode", robot["last_payload_summary_keys"])
        self.assertIn("matches_oracle", robot["last_payload_summary_keys"])

    def test_large_matrix_preserves_known_weak_rows(self) -> None:
        data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        medians = data["large"]["median_seconds_by_app"]
        self.assertGreater(medians["facility_knn_assignment"], 60.0)
        self.assertGreater(medians["polygon_pair_overlap_area_rows"], 10.0)
        self.assertGreater(medians["hausdorff_distance"], 100.0)
        self.assertGreater(medians["ann_candidate_search"], 30.0)
        self.assertLess(medians["segment_polygon_hitcount"], 1.0)
        self.assertLess(medians["robot_collision_screening"], 2.0)


if __name__ == "__main__":
    unittest.main()
