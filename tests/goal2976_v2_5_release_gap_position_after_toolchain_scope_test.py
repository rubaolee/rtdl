from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2976_v2_5_release_gap_position_after_toolchain_scope_2026-06-01.md"
TRIAGE = ROOT / "docs" / "reports" / "goal2973_current_packet_with_toolchain_scope_pod" / "goal2973_triage.json"


class Goal2976V25ReleaseGapPositionAfterToolchainScopeTest(unittest.TestCase):
    def test_report_preserves_current_position_without_release_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2976",
            "Goal2973 seven-app packet",
            "0` performance targets",
            "Goal2974 Gemini `accept`",
            "Goal2975 Claude `accept`",
            "Second-architecture or multivendor",
            "does not authorize v2.5 release",
        ):
            self.assertIn(phrase, text)

    def test_current_triage_still_has_zero_performance_targets(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))

        self.assertEqual("pass", triage["status"])
        self.assertEqual([], triage["performance_targets"])
        self.assertIsNone(triage["top_priority"])
        self.assertEqual(10, len(triage["apps"]))

    def test_readiness_accepts_but_keeps_release_claims_blocked(self) -> None:
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertFalse(packet["claim_authorization"]["public_speedup_claim_authorized"])
        self.assertFalse(packet["claim_authorization"]["broad_rt_core_speedup_claim_authorized"])
        self.assertIn("v2_5_release", packet["blocked_actions"])


if __name__ == "__main__":
    unittest.main()
