from __future__ import annotations

import json
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2319_v2_0_final_cleanup_release_candidate_2026-05-18.md"
MATRIX = ROOT / "docs" / "reports" / "goal2068_final_v2_0_release_matrix.json"
GATE = ROOT / "docs" / "reports" / "goal2069_v2_0_pre_release_gate.json"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal2319V20FinalCleanupReleaseCandidateTest(unittest.TestCase):
    def test_report_records_current_head_release_cleanup_without_publishing(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("current-head-release-candidate", text)
        self.assertIn("does not publish, tag, or announce v2.0", text)
        self.assertIn("fresh Claude review", text)
        self.assertIn("fresh Gemini review", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("not yet", text)
        self.assertIn("released", text)

    def test_final_matrix_uses_post_streaming_evidence(self) -> None:
        payload = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(payload["mixed_apps"], [])
        self.assertTrue(payload["post_goal2085_streaming_evidence"])
        self.assertTrue(payload["release_claim_boundary"]["all_current_optix_rt_rows_have_measured_v2_speedup"])
        ratios = payload["measured_ratio_summary"]
        self.assertTrue(ratios["all_current_optix_rt_ratios_below_1"])
        self.assertEqual(16, len(ratios["optix_rt_rows"]))

    def test_pre_release_gate_is_currently_green_but_not_release_authorization(self) -> None:
        payload = json.loads(GATE.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["gate_tests"]["summary"], "40 tests, 1 skipped")
        self.assertFalse(payload["release_claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["release_claim_boundary"]["whole_app_speedup_claim_authorized"])

    def test_native_diagnostic_environment_names_are_generic(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_PROFILE", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_DEVICE_PREFILTER", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_ONE_PASS_COMPACT", text)
        self.assertNotIn("RTDL_OPTIX_PIP_PROFILE", text)
        self.assertNotIn("RTDL_OPTIX_PIP_DISABLE_DEVICE_PREFILTER", text)
        self.assertNotIn("RTDL_OPTIX_PIP_DISABLE_ONE_PASS_COMPACT", text)
        self.assertFalse(re.search(r"\brtdl_optix_pip_profile\b", text))


if __name__ == "__main__":
    unittest.main()
