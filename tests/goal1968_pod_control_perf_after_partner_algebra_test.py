from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1968_pod_control_perf_after_partner_algebra_2026-05-14.md"
NO_OPTIX_SUMMARY = ROOT / "docs" / "reports" / "goal1968_pod_no_optix_control_perf" / "summary.json"
EMBREE_POLYGON = ROOT / "docs" / "reports" / "goal1968_pod_embree_polygon_control_perf.json"


class Goal1968PodControlPerfAfterPartnerAlgebraTest(unittest.TestCase):
    def test_no_optix_summary_records_positive_and_blocked_rows(self) -> None:
        summary = json.loads(NO_OPTIX_SUMMARY.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in summary["results"]}

        self.assertEqual(summary["status"], "pass")
        self.assertFalse(summary["claim_boundary"]["v2_0_release_authorized"])
        self.assertLess(rows["database_analytics"]["v2_vs_v1_8_ratio"], 1.0)
        self.assertLess(rows["graph_analytics"]["v2_vs_v1_8_ratio"], 1.0)
        self.assertGreater(rows["polygon_pair_overlap_area_rows"]["v2_vs_v1_8_ratio"], 100.0)
        self.assertGreater(rows["polygon_set_jaccard"]["v2_vs_v1_8_ratio"], 100.0)
        for row in rows.values():
            self.assertTrue(row["matches_v1_8_python_rtdl_oracle"])

    def test_embree_candidate_polygon_is_correct_but_still_slower(self) -> None:
        payload = json.loads(EMBREE_POLYGON.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in payload["results"]}

        self.assertEqual(payload["candidate_backend"], "embree")
        self.assertTrue(payload["all_match_v1_8_python_rtdl_oracle"])
        self.assertGreater(rows["polygon_pair_overlap_area_rows"]["v2_vs_v1_8_ratio"], 1.0)
        self.assertGreater(rows["polygon_set_jaccard"]["v2_vs_v1_8_ratio"], 1.0)
        for row in rows.values():
            self.assertTrue(row["matches_v1_8_python_rtdl_oracle"])

    def test_report_keeps_claim_boundary_and_names_optix_blocker(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("OptiX status: blocked", text)
        self.assertIn("Embree `3.12.2`", text)
        self.assertIn("v2.0 release readiness", text)
        self.assertIn("broad RT-core speedup", text)
        self.assertIn("better reusable shape/set reduction", text)
        self.assertIn("--candidate-backend optix", text)


if __name__ == "__main__":
    unittest.main()
