from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2805_v2_5_broad_clean_pod_regression_gate_2026-05-31.md"


class Goal2805V25BroadCleanPodRegressionGateTest(unittest.TestCase):
    def test_report_records_clean_pod_gate_result_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2805", text)
        self.assertIn("Commit: 6faf7de8", text)
        self.assertIn("Ran 239 tests in 116.260s", text)
        self.assertIn("OK", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.5 release", text)
        self.assertIn("public speedup claims", text)
        self.assertIn("true-zero-copy claims", text)

    def test_manifest_and_core_v2_5_gates_still_accept(self) -> None:
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_partner_continuation_contract()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_partner_preview_gate()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_partner_support_matrix()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_partner_selection_guidance()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_continuation_determinism_policies()["status"], "accept")


if __name__ == "__main__":
    unittest.main()
