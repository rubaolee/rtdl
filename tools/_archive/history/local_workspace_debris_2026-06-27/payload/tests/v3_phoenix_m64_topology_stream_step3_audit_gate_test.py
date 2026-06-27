import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m64_topology_stream_step3_audit_gate_2026-06-23.md"
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m64_topology_stream_step3_audit_gate_2026-06-23.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_m64_topology_stream_step3_audit_gate_recorded_review_2026-06-23.md"
)
ANTIGRAVITY_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "antigravity_phoenix_v3_m64_topology_stream_step3_audit_gate_review_2026-06-23.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m64_topology_stream_step3_audit_gate_3ai_consensus_2026-06-23.md"
)
AUDIT = ROOT / "docs" / "reports" / "phoenix_v3_m64_goal_completion_audit_2026-06-23.md"


class V3PhoenixM64TopologyStreamStep3AuditGateTest(unittest.TestCase):
    def test_step3_audit_requires_bridge_only_for_topology_set_a(self) -> None:
        source = PREPARED_EXECUTION.read_text(encoding="utf-8")
        audit_start = source.index("def audit_prepared_execution_session_metadata")
        continuation_start = source.index("def audit_prepared_execution_continuation_metadata", audit_start)
        audit_body = source[audit_start:continuation_start]

        self.assertIn("topology_stream_set_a_candidate", audit_body)
        self.assertIn('set_a_probe_candidate and "topology_stream" in primitive_family', audit_body)
        self.assertIn("not topology_stream_set_a_candidate", audit_body)
        self.assertIn("topology_stream_m3_bridge_ready", audit_body)
        self.assertIn("complete_non_authorizing_topology_stream_m3_bridge", audit_body)
        self.assertIn('"status": "accept_step3_ready" if step3_ready else "incomplete_step3_audit"', audit_body)

    def test_m64_reviews_and_consensus_accept_without_authorization(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, CLAUDE_REVIEW, ANTIGRAVITY_REVIEW, CONSENSUS, AUDIT):
            text = path.read_text(encoding="utf-8")
            lower_text = text.lower()
            self.assertIn(
                "accept_m64_topology_stream_step3_audit_gate_continue_local_step2_no_pod_no_release",
                text,
            )
            self.assertIn("v3 release", lower_text)
            self.assertIn("all-app", lower_text)
            self.assertIn("paid pod", lower_text)
            self.assertIn("public speedup", lower_text)
            self.assertIn("true-zero-copy", lower_text)
            self.assertIn("v4", lower_text)
            self.assertNotIn("release_ready", text)

        consensus = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn(
            "m64_topology_stream_step3_audit_gate_3ai_accept_continue_local_step2_no_pod_no_release",
            consensus,
        )
        audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn("m64_goal_complete_3ai_accept_continue_local_step2_no_pod_no_release", audit)
        self.assertIn("Carry-Forward", audit)


if __name__ == "__main__":
    unittest.main()
