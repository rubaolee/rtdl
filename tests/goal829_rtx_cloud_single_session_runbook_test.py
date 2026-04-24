from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "rtx_cloud_single_session_runbook.md"


class Goal829RtxCloudSingleSessionRunbookTest(unittest.TestCase):
    def test_runbook_enforces_local_readiness_before_pod(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("goal824_pre_cloud_rtx_readiness_gate.py", text)
        self.assertIn('"valid": true', text)
        self.assertIn("Do not start a pod for one app at a time.", text)

    def test_runbook_uses_one_shot_runner_and_artifact_audit(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("goal769_rtx_pod_one_shot.py", text)
        self.assertIn("goal762_rtx_cloud_artifact_report_latest.json", text)
        self.assertIn("cloud_claim_contract", text)
        self.assertIn("required_phase_groups", text)
        self.assertIn("needs_attention", text)

    def test_runbook_has_deferred_batch_controls_and_shutdown_rule(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("--include-deferred", text)
        for app in (
            "graph_analytics",
            "service_coverage_gaps",
            "event_hotspot_screening",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "hausdorff_distance",
            "ann_candidate_search",
            "facility_knn_assignment",
            "barnes_hut_force_app",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            with self.subTest(app=app):
                self.assertIn(f"--only {app}", text)
        self.assertIn("After copying artifacts back, stop or terminate the pod.", text)
        self.assertIn("does not authorize public RTX speedup claims", text)

    def test_runbook_separates_active_and_deferred_evidence(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("Run the active one-shot command first", text)
        self.assertIn("release-grade active evidence", text)
        self.assertIn("exploratory/deferred gates", text)
        self.assertIn("The deferred batch is allowed to expose failures", text)


if __name__ == "__main__":
    unittest.main()
