from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2159_rayjoin_public_cdb_runner_and_warm_state_audit_2026-05-16.md"
GOAL2157 = ROOT / "docs" / "reports" / "goal2157_rayjoin_public_cdb_nonzero_lsi_slice_evidence_2026-05-16.md"
SINGLE = ROOT / "docs" / "reports" / "goal2159_rayjoin_public_cdb_runner_count192_pod_2026-05-16.json"
WARM = ROOT / "docs" / "reports" / "goal2159_rayjoin_public_cdb_runner_count128_192_pod_2026-05-16.json"


class Goal2159RayjoinPublicCdbRunnerAndWarmStateAuditTest(unittest.TestCase):
    def test_report_records_conservative_and_warm_state_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "reusable runner implemented",
            "Conservative Single-Case Runner Result",
            "1.05x",
            "Multi-Case Warm-State Result",
            "5.28x",
            "public wording should use the conservative single-case result",
            "without an explicit warmed-session benchmark protocol",
            "v2.0 release authorization",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_goal2157_report_has_followup_correction(self) -> None:
        text = GOAL2157.read_text(encoding="utf-8")

        self.assertIn("Goal2159 Follow-Up Correction", text)
        self.assertIn("safest public-facing interpretation", text)

    def test_runner_artifacts_capture_warm_state_sensitivity(self) -> None:
        single = json.loads(SINGLE.read_text(encoding="utf-8"))
        warm = json.loads(WARM.read_text(encoding="utf-8"))

        self.assertEqual(single["commit"], "b521b1d4463575269dd7ce84b926d5116a8bd5f7")
        self.assertEqual(warm["commit"], "b521b1d4463575269dd7ce84b926d5116a8bd5f7")
        self.assertFalse(single["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])
        self.assertFalse(warm["claim_boundary"]["v2_0_release_authorized"])

        single_case = single["cases"]["lsi_county256_soil256_count192"]["backends"]
        warm_case = warm["cases"]["lsi_county256_soil256_count192"]["backends"]

        self.assertTrue(single_case["optix"]["all_parity_vs_cpu_python_reference"])
        self.assertTrue(warm_case["optix"]["all_parity_vs_cpu_python_reference"])
        self.assertLess(single_case["optix"]["app_elapsed_sec_median"], single_case["embree"]["app_elapsed_sec_median"])
        self.assertLess(warm_case["optix"]["app_elapsed_sec_median"], single_case["optix"]["app_elapsed_sec_median"])


if __name__ == "__main__":
    unittest.main()
