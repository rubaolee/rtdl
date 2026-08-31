from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2985_rtx4000ada_second_arch_bounded_packet_2026-06-01.md"
)
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2985_second_arch_bounded_packet_pod"


class Goal2985Rtx4000AdaSecondArchBoundedPacketTest(unittest.TestCase):
    def test_summary_is_clean_seven_app_packet_with_bounded_profile(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual(7, summary["expected_artifact_count"])
        self.assertEqual("second_arch_bounded", summary["barnes_hut_case_profile"])
        self.assertIn("not a release shortcut", summary["barnes_hut_case_profile_boundary"])
        self.assertEqual("20b62a3eb21607a4e313b58fd8804de91e681f4e", summary["source_commit"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])

    def test_all_artifacts_pass_and_barnes_hut_command_excludes_8192(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        self.assertTrue(all(row["status"] == "pass" for row in summary["artifacts"].values()))
        barnes_execution = next(row for row in summary["executions"] if row["goal"] == "Goal2803")
        command = " ".join(barnes_execution["command"])
        self.assertIn("--case 512:16", command)
        self.assertIn("--case 2048:32", command)
        self.assertNotIn("8192:32", command)

    def test_barnes_hut_evidence_is_rt_core_accelerated_and_rows_match(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "goal2803_barnes_hut.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual(
            [{"body_count": 512, "bucket_size": 16}, {"body_count": 2048, "bucket_size": 32}],
            payload["cases"],
        )
        self.assertEqual(2, len(payload["membership_rows"]))
        self.assertGreater(payload["min_optix_membership_speedup_vs_embree"], 100.0)
        self.assertGreater(payload["max_optix_membership_speedup_vs_embree"], 500.0)
        for row in payload["membership_rows"]:
            self.assertTrue(row["rows_match_between_backends"])
            self.assertTrue(row["optix_rt_core_accelerated"])
        self.assertEqual("cupy", payload["vector_sum"]["selected_partner"])
        self.assertFalse(payload["vector_sum"]["triton_preview_promoted"])

    def test_report_and_readiness_record_non_authorizing_status(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal2985",
            "second_arch_bounded",
            "7/7",
            "full 8192-body Barnes-Hut Embree CPU baseline remains unmeasured",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2985_rtx4000ada_second_arch_bounded_packet_2026-06-01.md"
            ]
        )
        self.assertIn(
            "triage_goal2985_second_arch_bounded_packet_before_release_packet",
            packet["allowed_next_actions"],
        )
        self.assertEqual("accept", validation["status"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])


if __name__ == "__main__":
    unittest.main()
