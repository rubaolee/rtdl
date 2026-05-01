from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal846ActiveRtxClaimGateTest(unittest.TestCase):
    def test_active_gate_filters_to_mandatory_active_baselines(self) -> None:
        module = __import__("scripts.goal846_active_rtx_claim_gate", fromlist=["build_active_claim_gate"])
        payload = module.build_active_claim_gate()
        self.assertEqual(payload["row_count"], 8)
        self.assertEqual(payload["required_artifact_count"], 12)
        self.assertEqual(payload["valid_artifact_count"], 12)
        self.assertEqual(payload["missing_artifact_count"], 0)
        self.assertEqual(payload["invalid_artifact_count"], 0)
        self.assertEqual(payload["skipped_optional_or_deferred_count"], 10)
        self.assertEqual(payload["status"], "ok")

    def test_outlier_and_dbscan_skip_optional_reference_rows(self) -> None:
        module = __import__("scripts.goal846_active_rtx_claim_gate", fromlist=["build_active_claim_gate"])
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_active_claim_gate()["rows"]
        }
        outlier = rows[("outlier_detection", "prepared_fixed_radius_density_summary")]
        dbscan = rows[("dbscan_clustering", "prepared_fixed_radius_core_flags")]
        self.assertEqual(len(outlier["blocking_checks"]), 2)
        self.assertEqual(len(outlier["skipped_checks"]), 1)
        self.assertEqual(outlier["skipped_checks"][0]["collection_status"], "optional_dependency_or_reference_required")
        self.assertEqual(len(dbscan["blocking_checks"]), 2)
        self.assertEqual(len(dbscan["skipped_checks"]), 1)
        self.assertEqual(dbscan["skipped_checks"][0]["collection_status"], "optional_dependency_or_reference_required")

    def test_robot_row_is_green_after_linux_artifact_refresh(self) -> None:
        module = __import__("scripts.goal846_active_rtx_claim_gate", fromlist=["build_active_claim_gate"])
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_active_claim_gate()["rows"]
        }
        robot = rows[("robot_collision_screening", "prepared_pose_flags")]
        self.assertEqual(robot["row_status"], "ok")
        self.assertEqual(len(robot["blocking_checks"]), 2)
        self.assertTrue(all(item["status"] == "valid" for item in robot["blocking_checks"]))

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "gate.json"
            output_md = Path(tmpdir) / "gate.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal846_active_rtx_claim_gate.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("Goal846 Active RTX Claim Gate", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ok")
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
