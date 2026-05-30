import json
import subprocess
import sys
import unittest
from pathlib import Path

from examples.v2_0.research_benchmarks.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as triangle,
)


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "triangle_counting"
    / "rtdl_triangle_counting_benchmark_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal2725_triangle_counting_v2_5_plan_mode_2026-05-30.md"


class Goal2725TriangleCountingV25PlanModeTest(unittest.TestCase):
    def test_v2_5_plan_mode_exposes_manifest_row_without_overclaim(self) -> None:
        payload = triangle.run_app("v2_5_plan")

        self.assertEqual(payload["app"], "triangle_counting")
        self.assertEqual(payload["mode"], "v2_5_plan")
        self.assertEqual(payload["tier"], "A")
        self.assertEqual(payload["preferred_partner"], "triton")
        self.assertEqual(payload["status"], "tier_a_same_contract_plan_not_yet_integrated")
        self.assertIn("segmented_count_i64", payload["v2_5_required_operations"])
        self.assertIn("segmented_sum_f64", payload["v2_5_required_operations"])
        self.assertIn("compact_mask_i64", payload["v2_5_required_operations"])
        self.assertIn("CuPy", payload["same_contract_opponent"])
        self.assertIn("Do not relabel", payload["integration_decision"])
        self.assertFalse(payload["claim_boundary"]["v2_5_triton_benchmark_integrated"])
        self.assertFalse(payload["claim_boundary"]["triton_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["same_contract_parity_claim_authorized"])

    def test_cli_exposes_v2_5_plan_mode(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(APP), "--mode", "v2_5_plan"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["mode"], "v2_5_plan")
        self.assertEqual(payload["preferred_partner"], "triton")
        self.assertFalse(payload["claim_boundary"]["same_contract_parity_claim_authorized"])

    def test_report_records_guardrail(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Triangle Counting v2.5 Plan Mode", text)
        self.assertIn("not already Triton benchmark paths", text)
        self.assertIn("do not relabel", text)
        self.assertIn("sm_70+", text)


if __name__ == "__main__":
    unittest.main()
