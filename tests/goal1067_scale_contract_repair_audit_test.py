from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1067ScaleContractRepairAuditTest(unittest.TestCase):
    def test_audit_blocks_hausdorff_and_promotes_only_barnes_after_review(self) -> None:
        module = __import__("scripts.goal1067_scale_contract_repair_audit", fromlist=["build_audit"])
        payload = module.build_audit()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["scale_contract_rows"], 2)
        self.assertEqual(payload["summary"]["blocked_rows"], 1)
        self.assertEqual(payload["summary"]["pod_candidate_after_review_rows"], 1)

        rows = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(rows["hausdorff_distance"]["decision"], "blocked_scale_contract_not_repaired")
        self.assertEqual(rows["hausdorff_distance"]["pod_policy"], "no_pod_until_benchmark_contract_changes")
        self.assertIn("analytic tiled oracle", rows["hausdorff_distance"]["reason"])
        self.assertLess(rows["hausdorff_distance"]["cpu_reference_total_sec"], 0.01)

        barnes = rows["barnes_hut_force_app"]
        self.assertEqual(barnes["decision"], "pod_candidate_after_review")
        self.assertEqual(barnes["recommended_cloud_scale"]["body_count"], 1_000_000)
        self.assertGreaterEqual(barnes["tested_scales"][-1]["cpu_reference_total_sec"], 0.1)
        self.assertTrue(barnes["recommended_cloud_scale"]["skip_validation"])
        self.assertIn("smaller validated RTX pass", barnes["recommended_cloud_scale"]["validation_reference"])
        self.assertIn("2-AI review", barnes["next_local_action"])
        self.assertIn("does not run cloud", payload["boundary"])
        self.assertIn("does not run OptiX", payload["boundary"])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "audit.json"
            output_md = Path(tmpdir) / "audit.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1067_scale_contract_repair_audit.py",
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
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1067 Scale-Contract Repair Audit", markdown)
            self.assertIn("blocked_scale_contract_not_repaired", markdown)
            self.assertIn("pod_candidate_after_review", markdown)


if __name__ == "__main__":
    unittest.main()
