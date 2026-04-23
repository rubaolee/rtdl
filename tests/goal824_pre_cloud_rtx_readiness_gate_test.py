import unittest

from scripts.goal824_pre_cloud_rtx_readiness_gate import run_gate


class Goal824PreCloudRtxReadinessGateTest(unittest.TestCase):
    def test_gate_is_valid_without_starting_cloud(self) -> None:
        payload = run_gate()
        self.assertTrue(payload["valid"], payload["invalid_checks"])
        self.assertIn("does not start cloud", payload["boundary"])
        self.assertIn("Start one RTX cloud pod only after this gate is valid", payload["next_cloud_policy"])

    def test_gate_records_active_deferred_and_excluded_counts(self) -> None:
        payload = run_gate()
        manifest = payload["checks"]["manifest"]
        self.assertEqual(manifest["active_count"], 5)
        self.assertEqual(manifest["deferred_count"], 3)
        self.assertEqual(manifest["excluded_count"], 12)
        self.assertEqual(manifest["active_errors"], [])
        self.assertEqual(manifest["missing_excluded"], [])
        self.assertEqual(manifest["missing_deferred"], [])

    def test_gate_includes_dry_run_and_public_command_audit(self) -> None:
        payload = run_gate()
        self.assertTrue(payload["checks"]["public_command_audit"]["valid"])
        self.assertEqual(payload["checks"]["active_runner_dry_run"]["status"], "ok")
        self.assertTrue(payload["checks"]["active_runner_dry_run"]["dry_run"])
        self.assertEqual(payload["checks"]["bootstrap_dry_run"]["status"], "ok")
        self.assertTrue(payload["checks"]["bootstrap_dry_run"]["dry_run"])


if __name__ == "__main__":
    unittest.main()
