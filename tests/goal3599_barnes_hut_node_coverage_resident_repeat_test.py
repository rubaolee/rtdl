from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3599_barnes_hut_node_coverage_resident_repeat_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3599_barnes_hut_node_coverage_resident_repeat_2026-06-06.md"


class Goal3599BarnesHutNodeCoverageResidentRepeatTest(unittest.TestCase):
    def test_artifact_is_current_clean_resident_repeat_evidence(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3599.barnes_hut_node_coverage_resident_repeat_a5000.v1")
        self.assertEqual(payload["git_status_short"], "")
        self.assertEqual(payload["body_count"], 8192)
        self.assertEqual(payload["backend"], "optix")
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertTrue(payload["matches_oracle"])
        self.assertTrue(payload["oracle_decision_matches"])
        self.assertTrue(payload["oracle_identity_matches"])
        self.assertEqual(payload["repeat_protocol"]["repeat"], 1300)
        self.assertEqual(payload["repeat_protocol"]["warmup"], 20)
        self.assertGreater(payload["repeat_protocol"]["measured_query_total_sec"], 10.0)
        self.assertLess(payload["run_phases"]["query_fixed_radius_threshold_reached_count_sec"], 0.01)
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])

    def test_report_positions_result_without_fake_v23_ratio(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "closes the \"silent partial row\" problem",
            "does not by itself create a clean v2.9-vs-v2.3 ratio",
            "v2.3 does not expose the same resident repeat API",
            "Total measured hot query sec | 11.637928869",
            "old Goal3536 Barnes-Hut row should no longer be treated as silently partial",
            "does not authorize",
            "RT-BarnesHut paper reproduction",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
