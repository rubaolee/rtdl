from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3602_v2_9_benchmark_status_after_resident_evidence_2026-06-06.md"
GOAL3595 = ROOT / "docs/reports/goal3595_rayjoin_public_cdb_repeat200_a5000/summary.json"
GOAL3599 = ROOT / "docs/reports/goal3599_barnes_hut_node_coverage_resident_repeat_a5000/summary.json"
GOAL3601_CURRENT = ROOT / "docs/reports/goal3601_librts_same_contract_resident_repeat_a5000/current_summary.json"
GOAL3601_V23 = ROOT / "docs/reports/goal3601_librts_same_contract_resident_repeat_a5000/v23_summary.json"


class Goal3602V29BenchmarkStatusAfterResidentEvidenceTest(unittest.TestCase):
    def test_report_contains_all_ten_benchmark_apps(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for app in (
            "raydb_style",
            "contact_manifold",
            "hausdorff_xhd",
            "triangle_counting",
            "rtnn",
            "rt_dbscan",
            "robot_collision",
            "librts_spatial_index",
            "barnes_hut",
            "spatial_rayjoin",
        ):
            self.assertIn(f"`{app}`", text)

    def test_rayjoin_numbers_match_goal3595_artifact(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        payload = json.loads(GOAL3595.read_text(encoding="utf-8"))

        self.assertEqual(payload["git_status_short"], "")
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertIn("12.8536x", text)
        for phrase in (
            "PIP county512 scalar count",
            "LSI county512-soil512 count",
            "Overlay county512-soil512 count",
            "0.002150856",
            "0.000185231",
            "0.000538940",
            "0.2036x",
            "113.693x",
            "91.742x",
        ):
            self.assertIn(phrase, text)

    def test_barnes_and_librts_numbers_match_artifacts(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        barnes = json.loads(GOAL3599.read_text(encoding="utf-8"))
        current = json.loads(GOAL3601_CURRENT.read_text(encoding="utf-8"))
        v23 = json.loads(GOAL3601_V23.read_text(encoding="utf-8"))

        self.assertEqual(current["git_status_short"], "")
        self.assertEqual(v23["git_status_short"], "")
        self.assertGreaterEqual(
            barnes["repeat_protocol"]["measured_query_total_sec"],
            10.0,
        )
        librts_speedup = (
            v23["repeat_protocol"]["query_summed_median_sec"]
            / current["repeat_protocol"]["query_summed_median_sec"]
        )
        self.assertIn("0.008080567s", text)
        self.assertIn("11.637929s", text)
        self.assertIn(f"{librts_speedup:.6f}x", text)

    def test_boundary_and_interpretation_are_not_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "not a release packet",
            "not one scalar app headline",
            "explicit mixed routing",
            "cannot expose the same resident-repeat API",
            "exact closed-shape membership count",
            "does not authorize",
            "public v2.9 speedup claims",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
