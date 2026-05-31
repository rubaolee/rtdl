from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2807_v2_5_broad_sweep_v2_4_claim_boundary_alignment_2026-05-31.md"
)
GOAL2659_TEST = ROOT / "tests" / "goal2659_v2_4_benchmark_protocol_integration_test.py"


class Goal2807V25BroadSweepClaimBoundaryAlignmentTest(unittest.TestCase):
    def test_goal2659_raydb_timing_keeps_promotion_false(self) -> None:
        source = GOAL2659_TEST.read_text(encoding="utf-8")

        self.assertIn('self.assertFalse(timing["promoted_performance_path"])', source)
        self.assertIn('self.assertTrue(timing["same_phase_contract_as_basis"])', source)
        self.assertNotIn('self.assertTrue(timing["promoted_performance_path"])', source)

    def test_report_records_broad_pod_sweep_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2807", text)
        self.assertIn("100 v2.4/v2.5-era test modules", text)
        self.assertIn("Ran 477 tests", text)
        self.assertIn("OK (skipped=1)", text)
        self.assertIn("does not authorize", text)
        self.assertIn("public speedup wording", text)
        self.assertIn("true-zero-copy wording", text)


if __name__ == "__main__":
    unittest.main()
