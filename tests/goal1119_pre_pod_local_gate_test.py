from __future__ import annotations

import unittest


class Goal1119PrePodLocalGateTest(unittest.TestCase):
    def test_gate_says_pod_is_next_blocker(self) -> None:
        module = __import__("scripts.goal1119_pre_pod_local_gate", fromlist=["build_gate"])
        payload = module.build_gate()

        self.assertTrue(payload["ready_for_pod"])
        self.assertEqual(payload["blockers"], [])
        self.assertIn("run scripts/goal1116_current_source_rtx_rerun_runner.sh", payload["next_action"])
        self.assertTrue(payload["checks"]["intake_has_no_public_claim"])

    def test_gate_checks_current_contracts(self) -> None:
        module = __import__("scripts.goal1119_pre_pod_local_gate", fromlist=["build_gate"])
        checks = module.build_gate()["checks"]

        self.assertTrue(checks["facility_uses_recentered_contract"])
        self.assertTrue(checks["barnes_uses_radius_0_1"])
        self.assertTrue(checks["barnes_uses_depth_8"])
        self.assertTrue(checks["robot_uses_packed_8m_timing"])
        self.assertTrue(checks["runner_logs_output"])
        self.assertTrue(checks["intake_exists_and_blocks_until_pod"])


if __name__ == "__main__":
    unittest.main()
