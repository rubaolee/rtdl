from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from rtdsl.rt_core_optimization_closeout import (
    rt_core_optimization_closeout,
    validate_rt_core_optimization_closeout,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_rt_core_optimization_closeout.py"
REPORT = ROOT / "docs" / "reports" / "goal4342_rt_core_optimization_closeout_2026-06-11.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal4342_rt_core_optimization_closeout_2026-06-11.json"


class Goal4342RtCoreOptimizationCloseoutTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = rt_core_optimization_closeout()

    def test_validation_accepts_current_allpass_pod_evidence(self) -> None:
        validation = validate_rt_core_optimization_closeout()
        self.assertEqual("accept", validation["status"], validation["errors"])
        self.assertEqual(10, self.payload["summary"]["row_count"])
        self.assertEqual(0, self.payload["summary"]["remaining_high_leverage_rt_core_implementation_work_count"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["release_authorized"])

    def test_route_classes_keep_partner_rows_out_of_pure_rt_core_table(self) -> None:
        rows = {row["app"]: row for row in self.payload["rows"]}
        self.assertEqual(rows["spatial_rayjoin"]["comparison_table"], "configured_route_only")
        self.assertEqual(rows["rt_dbscan"]["comparison_table"], "configured_route_only")
        self.assertEqual(rows["barnes_hut"]["route_class"], "numba_partner_only_current_scale_row")
        self.assertEqual(
            rows["barnes_hut"]["comparison_table"],
            "configured_route_only_or_requires_new_pure_rtdl_contract",
        )
        pure_candidates = [
            app
            for app, row in rows.items()
            if row["comparison_table"] == "pure_rtdl_candidate_after_same_contract_embree_pair"
        ]
        self.assertEqual(
            set(pure_candidates),
            {
                "hausdorff_xhd",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "librts_spatial_index",
                "rtnn",
                "triangle_counting",
            },
        )

    def test_floor_statuses_match_current_campaign_boundary(self) -> None:
        rows = {row["app"]: row for row in self.payload["rows"]}
        self.assertEqual(rows["robot_collision"]["hot_path_floor_status"], "floor_met_internal_evidence_only")
        self.assertEqual(rows["raydb_style"]["hot_path_floor_status"], "floor_met_internal_evidence_only")
        self.assertEqual(self.payload["summary"]["floor_met_internal_row_count"], 2)
        self.assertEqual(self.payload["summary"]["smoke_or_internal_row_count"], 8)
        self.assertIn(
            "Most rows remain smoke/internal timing evidence",
            self.payload["summary"]["surprise_findings"][2],
        )

    def test_script_writes_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "rt_core.json"
            out_md = Path(tmp) / "rt_core.md"
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
            self.assertIn("Goal4342", report)
            self.assertIn("No obvious remaining high-leverage", report)
            self.assertIn("Barnes-Hut", report)

    def test_committed_report_and_json_artifact_are_present(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("NVIDIA RT-Core Optimization Closeout", text)
        self.assertIn("configured_route_only", text)
        self.assertEqual("accept", payload["validation"]["status"])
        self.assertEqual(0, payload["summary"]["remaining_high_leverage_rt_core_implementation_work_count"])


if __name__ == "__main__":
    unittest.main()
