from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3787_post_hiprt_closeout_regression_packet_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3787_post_hiprt_closeout_regression_a5000.json"


class Goal3787PostHiprtCloseoutRegressionPacketTest(unittest.TestCase):
    def test_artifact_records_clean_combined_pod_regression(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal3787")
        self.assertEqual(artifact["git_commit"], "6660d6352eebf9d212d573095862417bda4c681b")
        self.assertIn("NVIDIA RTX A5000", artifact["gpu"])
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        self.assertTrue(artifact["focused_tests_passed"])
        self.assertEqual(artifact["focused_test_module_count"], 32)
        self.assertIn("Ran 176 tests", artifact["test_output_tail"])
        self.assertIn("OK", artifact["test_output_tail"])
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertEqual(artifact["scoped_source_dirty_detail"], "")

    def test_artifact_records_current_parity_and_adequacy_state(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["parity_validation"]["status"], "accept")
        self.assertEqual(artifact["parity_validation"]["errors"], [])
        self.assertEqual(artifact["parity_summary"]["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(artifact["parity_summary"]["stage_counts"]["needs_generic_hiprt_extension"], 0)
        self.assertEqual(artifact["parity_summary"]["stage_counts"]["compatibility_only_not_amd_perf_ready"], 0)
        self.assertEqual(artifact["adequacy_version"], "rtdl.v2_10.benchmark_adequacy_after_goal3785.v1")
        self.assertEqual(artifact["adequacy_validation"]["status"], "accept")
        self.assertEqual(artifact["adequacy_validation"]["errors"], [])
        self.assertEqual(artifact["adequacy_summary"]["numba_reference_needed_apps"], [])
        self.assertEqual(artifact["adequacy_summary"]["adequacy_counts"]["strong"], 3)
        self.assertEqual(artifact["adequacy_summary"]["adequacy_counts"]["adequate"], 7)
        self.assertEqual(artifact["adequacy_summary"]["adequacy_counts"]["needs_major_followup"], 0)

    def test_claim_boundary_and_report_are_non_authorizing(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3787", report)
        self.assertIn("Ran 176 tests", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)
        self.assertIn("Goal3785 runner", report)


if __name__ == "__main__":
    unittest.main()
