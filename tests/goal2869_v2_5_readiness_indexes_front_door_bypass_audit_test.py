from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2869_v2_5_readiness_indexes_front_door_bypass_audit_2026-05-31.md"
)
BYPASS_REPORT = (
    "docs/reports/"
    "goal2867_v2_5_app_facing_front_door_bypass_audit_2026-05-31.md"
)
GOAL2869_REPORT = (
    "docs/reports/"
    "goal2869_v2_5_readiness_indexes_front_door_bypass_audit_2026-05-31.md"
)
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "handoff"
    / "CALL_FOR_REVIEW_GOAL2868_V2_5_LAST_DAY_WORK_SINCE_CLAUDE_REVIEWS_2026-05-31.md"
)


class Goal2869V25ReadinessIndexesFrontDoorBypassAuditTest(unittest.TestCase):
    def test_readiness_packet_requires_front_door_bypass_audit(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["required_report_presence"][BYPASS_REPORT])
        self.assertTrue(packet["required_report_presence"][GOAL2869_REPORT])
        self.assertEqual((), packet["missing_required_reports"])

    def test_allowed_next_actions_record_review_intake_before_release_packet(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertIn(
            "keep_goal2867_front_door_bypass_audit_green",
            packet["allowed_next_actions"],
        )
        self.assertIn(
            "triage_goal2868_last_day_external_review_before_any_release_packet",
            packet["allowed_next_actions"],
        )
        self.assertIn(
            "request_fresh_3ai_release_review_only_if_user_requests_release",
            packet["allowed_next_actions"],
        )
        self.assertIn("v2_5_release", packet["blocked_actions"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])

    def test_goal2868_review_call_exists_but_is_not_release_consensus(self) -> None:
        text = CALL_FOR_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal2868", text)
        self.assertIn("Do not authorize", text)
        self.assertIn("v2.5 release", text)
        self.assertIn("fresh 3-AI release consensus", text)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2869",
            "Goal2867",
            "Goal2868",
            "front-door bypass audit",
            "not a v2.5 release authorization",
            "not a public speedup claim",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
