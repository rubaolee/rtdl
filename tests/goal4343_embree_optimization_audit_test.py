from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from rtdsl.embree_optimization_audit import embree_optimization_audit, validate_embree_optimization_audit


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_embree_optimization_audit.py"
REPORT = ROOT / "docs" / "reports" / "goal4343_embree_optimization_audit_2026-06-11.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal4343_embree_optimization_audit_2026-06-11.json"


class Goal4343EmbreeOptimizationAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = embree_optimization_audit()

    def test_validation_accepts_combined_current_evidence(self) -> None:
        validation = validate_embree_optimization_audit()
        self.assertEqual("accept", validation["status"], validation["errors"])
        self.assertEqual(10, self.payload["summary"]["row_count"])
        self.assertTrue(self.payload["summary"]["historical_packet_is_stale_for_current_registry"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["release_authorized"])

    def test_librts_is_only_fully_measured_pair_but_goal4344_scale_rows_are_ready(self) -> None:
        rows = {row["app"]: row for row in self.payload["rows"]}
        ready = [app for app, row in rows.items() if row["comparison_readiness"] == "first_measured_pair_ready"]
        self.assertEqual(["librts_spatial_index"], ready)
        self.assertEqual(rows["librts_spatial_index"]["optimization_status"], "optimized_native_aabb_route_available")
        self.assertEqual(rows["librts_spatial_index"]["artifact_status"], "optimized_goal4340_summary_available")
        self.assertEqual(6, self.payload["summary"]["embree_scale_evidence_ready_count"])
        self.assertEqual(2, self.payload["summary"]["boundary_limited_scale_evidence_ready_count"])
        for app in {
            "hausdorff_xhd",
            "robot_collision",
            "contact_manifold",
            "raydb_style",
            "triangle_counting",
        }:
            self.assertEqual("goal4344_same_contract_scale_probe_pass", rows[app]["artifact_status"])
        self.assertGreater(self.payload["summary"]["librts_query_median_speedup_vs_old_columnar_fallback"], 1000.0)

    def test_rtnn_uses_goal4308_followup_not_stale_numba_artifact(self) -> None:
        rows = {row["app"]: row for row in self.payload["rows"]}
        self.assertEqual(rows["rtnn"]["registry_row_id"], "rtnn_embree_cpu_ann_candidate_quality_reference")
        self.assertEqual(rows["rtnn"]["artifact_status"], "current_followup_pass")
        self.assertEqual(rows["rtnn"]["artifact_row_id"], "rtnn_embree_cpu_ann_candidate_quality_reference")
        self.assertEqual(rows["rtnn"]["historical_artifact_row_id"], "rtnn_numba_cpu_partner_quality_reference")
        self.assertEqual(rows["rtnn"]["comparison_readiness"], "needs_3d_ranked_or_2d_ann_contract_choice")

    def test_audit_exposes_remaining_embree_campaign_work(self) -> None:
        self.assertEqual(self.payload["summary"]["same_contract_scale_pair_needed_count"], 0)
        self.assertEqual(self.payload["summary"]["contract_choice_needed_count"], 4)
        rows = {row["app"]: row for row in self.payload["rows"]}
        self.assertEqual(rows["robot_collision"]["comparison_readiness"], "same_scale_boundary_limited_row_ready")
        self.assertEqual(rows["raydb_style"]["comparison_readiness"], "same_scale_boundary_limited_row_ready")
        self.assertEqual(rows["contact_manifold"]["comparison_readiness"], "same_contract_scale_row_ready")
        self.assertEqual(rows["spatial_rayjoin"]["comparison_readiness"], "needs_contract_split_before_optimization")
        self.assertEqual(rows["barnes_hut"]["comparison_readiness"], "needs_contract_choice_before_optimization")

    def test_script_writes_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "embree.json"
            out_md = Path(tmp) / "embree.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            report = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("Goal4343", report)
            self.assertIn("Goal4344 now supplies", report)
            self.assertIn("stale-evidence", report)

    def test_committed_report_and_json_artifact_are_present(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("Embree Optimization Audit", text)
        self.assertIn("Goal4308 RTNN follow-up", text)
        self.assertIn("Goal4344 Embree same-contract scale probe", text)
        self.assertEqual("accept", payload["validation"]["status"])
        self.assertEqual(1, payload["summary"]["optimized_measured_pair_ready_count"])
        self.assertEqual(0, payload["summary"]["same_contract_scale_pair_needed_count"])


if __name__ == "__main__":
    unittest.main()
