from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1025PreCloudRtxAppBatchReadinessTest(unittest.TestCase):
    def test_all_nvidia_target_apps_have_manifest_coverage(self) -> None:
        module = __import__(
            "scripts.goal1025_pre_cloud_rtx_app_batch_readiness",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["public_app_count"], 18)
        self.assertEqual(payload["readiness_counts"]["ready_for_rtx_claim_review"], 16)
        self.assertEqual(payload["readiness_counts"]["exclude_from_rtx_app_benchmark"], 2)
        self.assertEqual(payload["maturity_counts"]["rt_core_ready"], 16)
        self.assertEqual(payload["maturity_counts"]["not_nvidia_rt_core_target"], 2)
        self.assertEqual(payload["missing_nvidia_targets"], [])
        self.assertEqual(payload["unexpected_non_nvidia_targets"], [])
        self.assertEqual(payload["public_wording_blocked_apps"], ["robot_collision_screening"])
        self.assertEqual(len(payload["public_wording_reviewed_apps"]), 7)
        self.assertTrue(payload["has_rtx_hardware_precondition"])
        self.assertTrue(payload["manifest_blocks_speedup_claims"])

    def test_manifest_keeps_batch_policy_and_non_claim_boundary(self) -> None:
        module = __import__(
            "scripts.goal1025_pre_cloud_rtx_app_batch_readiness",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertIn("Do not start a paid pod for one app", payload["cloud_policy"])
        self.assertIn("does not run cloud", payload["boundary"])
        self.assertIn("not GTX 1070", " ".join(payload["manifest_global_preconditions"]))
        self.assertIn("does not authorize RTX speedup claims", payload["manifest_boundary"])
        self.assertGreaterEqual(payload["active_manifest_entry_count"], 8)
        self.assertGreaterEqual(payload["deferred_manifest_entry_count"], 9)
        active_and_deferred = set(payload["active_apps"]) | set(payload["deferred_apps"])
        self.assertIn("database_analytics", active_and_deferred)
        self.assertIn("graph_analytics", active_and_deferred)
        self.assertIn("barnes_hut_force_app", active_and_deferred)

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1025.json"
            output_md = Path(tmpdir) / "goal1025.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1025_pre_cloud_rtx_app_batch_readiness.py",
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
            self.assertIn("Goal1025 Pre-Cloud RTX App Batch Readiness", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("robot_collision_screening", markdown)
            self.assertIn("does not run cloud", markdown)


if __name__ == "__main__":
    unittest.main()
