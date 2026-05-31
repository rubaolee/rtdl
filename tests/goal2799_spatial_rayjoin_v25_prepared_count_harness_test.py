from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2799_spatial_rayjoin_v25_prepared_count_harness.py"
REPORT = ROOT / "docs" / "reports" / "goal2799_spatial_rayjoin_v2_5_prepared_count_harness_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2799_spatial_rayjoin_v2_5_prepared_count_harness_consensus_2026-05-31.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2799_pod_artifacts"
    / "spatial_rayjoin_v25_prepared_count_optix_fixture.json"
)


class Goal2799SpatialRayJoinV25PreparedCountHarnessTest(unittest.TestCase):
    def test_harness_uses_existing_prepared_optix_count_route(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("run_rayjoin_prepared_optix_workload", text)
        self.assertIn("run_rayjoin_workload", text)
        self.assertIn('"pip"', text)
        self.assertIn('"lsi"', text)
        self.assertIn('"overlay_seed"', text)
        self.assertIn("tier_a_count_or_parity_only", text)
        self.assertIn("row_overlay_continuation_deferred_tier_b", text)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized", text)

    def test_manifest_records_goal2799_spatial_rayjoin_count_status(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        row = next(app for app in manifest["apps"] if app["app_id"] == "spatial_rayjoin")

        self.assertEqual(row["tier"], "A")
        self.assertEqual(row["canonical_harness_status"], "ready_with_goal2799_prepared_count_harness")
        self.assertIn("count_or_parity", row["benchmark_track"])
        self.assertIn("deferred Tier B", row["parity_target"])
        self.assertIn("Goal2799", row["pod_evidence_status"])
        self.assertIn("deferred Tier B", row["next_action"])
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")

    def test_pod_artifact_records_all_three_rayjoin_count_workloads(self) -> None:
        text = POD_ARTIFACT.read_text(encoding="utf-8")

        self.assertIn('"status": "pass"', text)
        for workload in ("pip", "lsi", "overlay_seed"):
            self.assertIn(f'"workload": "{workload}"', text)
        self.assertIn('"matches_cpu_reference": true', text)
        self.assertIn('"uses_prepared_optix_rt_backend": true', text)
        self.assertIn('"paper_reproduction_claim_authorized": false', text)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": false', text)

    def test_report_and_consensus_keep_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Spatial RayJoin v2.5 Prepared Count Harness", report)
        self.assertIn("Goal2799", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("Tier A count/parity", report)
        self.assertIn("deferred Tier B", report)


if __name__ == "__main__":
    unittest.main()
