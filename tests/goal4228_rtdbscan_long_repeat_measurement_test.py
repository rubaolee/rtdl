from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4228_rtdbscan_long_repeat_rtx4000ada" / "summary.json"
PAYLOAD = (
    ROOT
    / "docs"
    / "reports"
    / "goal4228_rtdbscan_long_repeat_rtx4000ada"
    / "clustered3d_65536_repeat20.stdout.json"
)
REPORT = ROOT / "docs" / "reports" / "goal4228_rtdbscan_long_repeat_measurement_2026-06-09.md"


class Goal4228RtdbscanLongRepeatMeasurementTest(unittest.TestCase):
    def test_long_repeat_clears_hot_path_floor_on_current_policy(self) -> None:
        summary = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(summary["schema"], "rtdl.goal4228.rtdbscan_long_repeat.v2")
        self.assertEqual(summary["commit"], "21d5af1d")
        self.assertEqual(summary["tracked_worktree_status_excluding_artifact_dir"], [])
        self.assertEqual(summary["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")
        self.assertEqual(summary["grouped_stream_continuation_pass_count"], 1)
        self.assertEqual(summary["repeat"], 20)
        self.assertEqual(summary["warmup"], 2)
        self.assertTrue(summary["hot_path_duration_target_met"])
        self.assertGreater(summary["elapsed_sec_total"], 1.0)

    def test_payload_and_report_keep_claims_closed(self) -> None:
        payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
        summary = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual(payload["metadata"]["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "amd_performance_claim_authorized",
        ):
            self.assertFalse(summary[key], key)
        self.assertIn("not a public performance claim", report)


if __name__ == "__main__":
    unittest.main()
