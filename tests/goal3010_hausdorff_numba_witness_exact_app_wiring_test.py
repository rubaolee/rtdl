from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt
from examples.v2_0.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_distance_app as hausdorff


REPO_ROOT = Path(__file__).resolve().parents[1]
APP = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_distance_app.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3010_hausdorff_numba_witness_exact_app_wiring_2026-06-01.md"


class Goal3010HausdorffNumbaWitnessExactAppWiringTest(unittest.TestCase):
    def test_app_wires_explicit_numba_witness_mode(self) -> None:
        source = APP.read_text(encoding="utf-8")

        for phrase in (
            "partner_numba_witness_exact",
            "_run_partner_numba_witness_exact_directed",
            "group_argmin_then_global_argmax_partner_columns",
            'partner="numba"',
            "host_score_row_materialization_used",
            "rt_core_accelerated",
            "RT traversal is not called in this exact dense path",
        ):
            self.assertIn(phrase, source)

    def test_report_blocks_claims_and_explains_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "exact dense partner-continuation path",
            "not an RT-core path",
            "host_score_row_materialization_used: True",
            "rt_core_accelerated: False",
            "does not authorize",
            "v2.6 release",
            "Numba speedup wording",
            "RT-core speedup wording",
            "true-zero-copy wording",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_numba_mode_matches_oracle_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable Hausdorff Numba validation")

        payload = hausdorff.run_app("partner_numba_witness_exact", copies=2)

        self.assertEqual(payload["backend"], "partner_numba_witness_exact")
        self.assertEqual(payload["partner"], "numba")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["partner_reference_contract"], "generic_group_argmin_then_global_argmax_with_witness")
        self.assertTrue(payload["host_score_row_materialization_used"])
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertFalse(payload["claim_boundary"]["numba_speedup_claim_authorized"])
        self.assertIn(
            "grouped_argmin_f64",
            payload["directed_a_to_b"]["v2_6_numba_partner_continuation_operations"],
        )
        self.assertIn(
            "grouped_argmax_f64",
            payload["directed_a_to_b"]["v2_6_numba_partner_continuation_operations"],
        )


if __name__ == "__main__":
    unittest.main()
