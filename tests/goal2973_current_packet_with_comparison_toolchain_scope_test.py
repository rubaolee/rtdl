from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2973_current_packet_with_comparison_toolchain_scope_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2973_current_packet_with_toolchain_scope_pod"
SUMMARY = ARTIFACT_DIR / "goal2855_summary.json"
TRIAGE = ARTIFACT_DIR / "goal2973_triage.json"


class Goal2973CurrentPacketWithComparisonToolchainScopeTest(unittest.TestCase):
    def test_packet_passes_cleanly_with_scope_guard(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        scope = summary["runner_metadata"]["toolchain"]["comparison_toolchain_scope"]

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual("63158f6db0a2248d203476633ea9f5171a0b596b", summary["source_commit"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertEqual([], summary["runner_metadata"]["source_dirty"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertEqual(
            "rtdl.goal2972.comparison_toolchain_scope.v1",
            scope["scope_version"],
        )
        self.assertTrue(scope["native_optix_stack_observed"])
        self.assertTrue(scope["observed_stack_complete_for_current_packet"])
        self.assertFalse(scope["compiler_flag_alignment_proven"])
        self.assertFalse(scope["cross_compiler_fairness_claim_authorized"])
        self.assertFalse(scope["public_speedup_wording_authorized"])
        self.assertFalse(scope["release_authorized"])

    def test_triage_remains_zero_target(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))

        self.assertEqual("pass", triage["status"])
        self.assertEqual("Goal2973 current packet performance triage", triage["goal"])
        self.assertEqual("Goal2902 v2.5 current packet performance triage", triage["triage_schema"])
        self.assertEqual(10, len(triage["apps"]))
        self.assertEqual([], triage["performance_targets"])
        self.assertIsNone(triage["top_priority"])
        self.assertEqual({}, triage["claim_boundary_violations"])

    def test_report_documents_boundary_and_second_arch_gap(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2973",
            "comparison-toolchain scope guard",
            "Compiler flag alignment proven",
            "public speedup wording",
            "second-architecture or multivendor performance check",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_readiness_index_points_to_goal2973_packet(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        runner = packet["current_canonical_runner"]
        triage = packet["current_packet_perf_triage"]
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertTrue(runner["summary_path"].endswith("goal2855_summary.json"))
        self.assertIn("goal2973_current_packet_with_toolchain_scope_pod", runner["summary_path"])
        self.assertEqual("pass", runner["status"])
        scope = runner["runner_metadata"]["toolchain"]["comparison_toolchain_scope"]
        self.assertEqual(
            "rtdl.goal2972.comparison_toolchain_scope.v1",
            scope["scope_version"],
        )
        self.assertFalse(scope["compiler_flag_alignment_proven"])
        self.assertIn("goal2973_current_packet_with_toolchain_scope_pod", triage["path"])
        self.assertTrue(
            packet["external_review_presence"][
                "docs/reviews/goal2974_gemini_review_goal2972_2973_toolchain_scope_2026-06-01.md"
            ]
        )
        self.assertTrue(
            packet["external_review_presence"][
                "docs/reviews/goal2975_claude_review_goal2972_2973_toolchain_scope_2026-06-01.md"
            ]
        )
        self.assertEqual(0, triage["performance_target_count"])
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])


if __name__ == "__main__":
    unittest.main()
