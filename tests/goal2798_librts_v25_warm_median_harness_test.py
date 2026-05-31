from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2798_librts_v25_warm_median_harness.py"
REPORT = ROOT / "docs" / "reports" / "goal2798_librts_v2_5_warm_median_harness_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2798_librts_v2_5_warm_median_harness_consensus_2026-05-31.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2798_pod_artifacts"
    / "librts_v25_warm_median_optix_4096_2048.json"
)


class Goal2798LibRTSV25WarmMedianHarnessTest(unittest.TestCase):
    def test_harness_uses_prepared_optix_aabb_queries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepare_optix_aabb_index_2d", text)
        self.assertIn("prepare_optix_aabb_point_queries_2d", text)
        self.assertIn("prepare_optix_aabb_box_queries_2d", text)
        self.assertIn("count_prepared_queries", text)
        self.assertIn("public_speedup_claim_authorized", text)

    def test_manifest_records_goal2798_warm_median_status(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        row = next(app for app in manifest["apps"] if app["app_id"] == "librts_spatial_index")

        self.assertEqual(row["tier"], "C")
        self.assertEqual(row["canonical_harness_status"], "ready_with_goal2798_warm_median_harness")
        self.assertEqual(row["required_partner_operations"], ())
        self.assertIn("Goal2798", row["pod_evidence_status"])
        self.assertIn("no-regression", row["next_action"])
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")

    def test_pod_artifact_records_all_three_aabb_operations(self) -> None:
        text = POD_ARTIFACT.read_text(encoding="utf-8")

        self.assertIn('"status": "pass"', text)
        for operation in ("point_contains", "range_contains", "range_intersects"):
            self.assertIn(f'"operation": "{operation}"', text)
        self.assertIn('"matches_cpu_reference": true', text)
        self.assertIn('"rt_core_accelerated": true', text)
        self.assertIn('"public_speedup_claim_authorized": false', text)

    def test_report_and_consensus_keep_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("LibRTS v2.5 Warm Median Harness", report)
        self.assertIn("Goal2798", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("not a public speedup claim", report)
        self.assertIn("Tier C", report)


if __name__ == "__main__":
    unittest.main()
