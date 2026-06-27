import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_secondary_platform_gate.py"
STRATEGY = ROOT / "docs" / "rebuild" / "v3" / "v3_secondary_platform_strategy_2026-06-21.md"


class V3PhoenixSecondaryPlatformGateTest(unittest.TestCase):
    def run_gate(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return json.loads(completed.stdout)

    def test_lx1_is_compatibility_evidence_not_rt_performance_evidence(self):
        payload = self.run_gate()
        self.assertEqual(payload["tool"], "v3_phoenix_secondary_platform_gate")
        self.assertEqual(payload["status"], "compatibility_confirmed_hardware_scope_waiver_reviewed_not_release")
        self.assertTrue(payload["secondary_compatibility_confirmed"])
        self.assertFalse(payload["secondary_rt_performance_confirmation_authorized"])
        self.assertTrue(payload["secondary_rt_hardware_scope_waiver_reviewed"])
        self.assertTrue(payload["secondary_platform_closes_release_blocker"])
        self.assertEqual(payload["secondary_platform_closes_release_blocker_method"], "reviewed_hardware_scoped_waiver")
        self.assertEqual(
            payload["secondary_platform_closes_release_blocker_scope"],
            "single_rtx_4000_ada_driver_550_127_05_pod",
        )
        self.assertEqual(payload["hardware_performance_scope"], "single_rtx_4000_ada_driver_550_127_05_pod")
        self.assertFalse(payload["multi_gpu_performance_portability_claim_authorized"])
        self.assertFalse(payload["release_authorized"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertIn("reviewed single-RTX hardware-scope waiver", payload["accepted_secondary_role"])
        self.assertIn("second RT-core performance confirmation", payload["rejected_secondary_role"])

    def test_gate_preserves_gtx_1070_no_rt_boundary(self):
        payload = self.run_gate()
        classification = payload["evidence"]["classification"]
        self.assertEqual(classification["gpu"], "NVIDIA GeForce GTX 1070")
        self.assertFalse(classification["has_rt_cores_for_claims"])
        self.assertFalse(classification["all_app_performance_suite_rerun_on_lx1"])
        self.assertFalse(classification["paired_v2_v3_performance_suite_rerun_on_lx1"])
        self.assertTrue(all(item["gtx_1070"] for item in payload["evidence"]["hosts"]))
        self.assertTrue(all(item["ok"] for item in payload["evidence"]["v3_rebuild_matrices"]))
        self.assertTrue(all(item["ok"] for item in payload["evidence"]["source_tree_doctors"]))
        self.assertTrue(all(item["pass"] for item in payload["evidence"]["wording_gates"]))
        self.assertTrue(payload["evidence"]["gpu_env_gate"]["pass"])

    def test_strategy_doc_matches_machine_gate_boundary(self):
        text = STRATEGY.read_text(encoding="utf-8")
        for phrase in [
            "compatibility_confirmed_hardware_scope_waiver_reviewed_not_release",
            "secondary_rt_performance_confirmation_authorized: false",
            "secondary_rt_hardware_scope_waiver_reviewed: true",
            "secondary_platform_closes_release_blocker: true",
            "secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver",
            "secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod",
            "multi_gpu_performance_portability_claim_authorized: false",
            "GTX 1070-class hardware has no RT cores",
            "single_rtx_4000_ada_driver_550_127_05_pod",
            "Goal-Level Decision Audit",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
