import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POINT_TEST = ROOT / "tests" / "v3_phoenix_prepared_execution_session_runner_test.py"
SEGMENT_TEST = ROOT / "tests" / "v3_phoenix_spatial_segment_intersection_runner_wiring_test.py"
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_2026-06-23.md"
)
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_2026-06-23.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_recorded_review_2026-06-23.md"
)
ANTIGRAVITY_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "antigravity_phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_review_2026-06-23.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_3ai_consensus_2026-06-23.md"
)
AUDIT = ROOT / "docs" / "reports" / "phoenix_v3_m65_goal_completion_audit_2026-06-23.md"


class V3PhoenixM65TopologyStreamStep3NegativeHardeningGateTest(unittest.TestCase):
    def test_point_location_exercises_all_m64_negative_variants(self) -> None:
        text = POINT_TEST.read_text(encoding="utf-8")

        for marker in (
            "partial_phase_table",
            "bad_bridge_contract",
            "bad_bridge_status",
            "bridge_public_row_authorized",
            "bridge_m7_authorized",
        ):
            self.assertIn(marker, text)

        self.assertIn('broken_audit["status"], "incomplete_step3_audit"', text)
        self.assertIn('broken_audit["topology_stream_m3_bridge_ready"]', text)
        self.assertIn("complete_non_authorizing_topology_stream_m3_bridge", text)

    def test_segment_intersection_exercises_all_m64_negative_variants(self) -> None:
        text = SEGMENT_TEST.read_text(encoding="utf-8")

        self.assertIn("audit_prepared_execution_session_metadata", text)
        for marker in (
            "partial_phase_table",
            "bad_bridge_contract",
            "bad_bridge_status",
            "bridge_public_row_authorized",
            "bridge_m7_authorized",
        ):
            self.assertIn(marker, text)
        self.assertIn('broken_audit["status"], "incomplete_step3_audit"', text)
        self.assertIn('broken_audit["topology_stream_m3_bridge_ready"]', text)
        self.assertIn("complete_non_authorizing_topology_stream_m3_bridge", text)

    def test_m65_reviews_and_consensus_accept_without_authorization(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, CLAUDE_REVIEW, ANTIGRAVITY_REVIEW, CONSENSUS, AUDIT):
            text = path.read_text(encoding="utf-8")
            lower_text = text.lower()
            self.assertIn(
                "accept_m65_topology_stream_step3_negative_hardening_continue_local_no_pod_no_release",
                text,
            )
            self.assertIn("v3 release", lower_text)
            self.assertIn("all-app", lower_text)
            self.assertIn("paid pod", lower_text)
            self.assertIn("public speedup", lower_text)
            self.assertIn("true-zero-copy", lower_text)
            self.assertNotIn("release_ready", text)

        consensus = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn(
            "m65_topology_stream_step3_negative_hardening_3ai_accept_continue_local_no_pod_no_release",
            consensus,
        )
        audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn("m65_goal_complete_3ai_accept_continue_local_no_pod_no_release", audit)
        self.assertIn("Carry-Forward", audit)


if __name__ == "__main__":
    unittest.main()
