import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m54_one_focused_librts_stability_pod_authorization_2026-06-23.md"
)


class V3PhoenixM54LibRTSAuthorizationPacketGateTest(unittest.TestCase):
    def _required_input_paths(self, packet: str) -> list[str]:
        section = packet.split("## Required Review Inputs", 1)[1].split("## P1 Items", 1)[0]
        return re.findall(r"^- `([^`]+)`", section, flags=re.MULTILINE)

    def test_m54_required_review_inputs_exist(self) -> None:
        packet = PACKET.read_text(encoding="utf-8")
        inputs = self._required_input_paths(packet)

        self.assertGreaterEqual(len(inputs), 8)
        self.assertIn(
            "docs/reports/phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md",
            inputs,
        )
        self.assertNotIn(
            "docs/reports/phoenix_v3_m52_pod_surface_audit_2026-06-23.md",
            inputs,
        )

        missing = [path for path in inputs if not (ROOT / path).exists()]
        self.assertEqual([], missing)

    def test_m54_packet_is_review_only_until_exact_verdict(self) -> None:
        packet = PACKET.read_text(encoding="utf-8")

        self.assertIn("draft_review_packet_not_authorized", packet)
        self.assertIn("does not authorize execution by itself", packet)
        self.assertIn("authorize_m47_one_focused_librts_stability_pod_run", packet)
        self.assertIn("M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED", packet)
        self.assertIn("If the verdict is not exactly", packet)
        self.assertIn("the token must remain\nblocked", packet)

    def test_m54_carries_p1_and_non_authorization_boundaries(self) -> None:
        packet = PACKET.read_text(encoding="utf-8")

        for phrase in (
            "A real V2.14 root must be supplied",
            "Explicit Linux/POD Python paths must be supplied",
            "no V3 release",
            "no all-app benchmark run",
            "no broad paid POD campaign",
            "no public speedup wording",
            "no broad V3-over-V2 claim",
            "no V4 work",
            "no embedding",
            "no C ABI",
            "no true zero-copy claim",
        ):
            self.assertIn(phrase, packet)

    def test_m54_external_reviews_and_consensus_keep_one_run_boundary(self) -> None:
        claude = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m54_one_focused_librts_stability_pod_authorization_recorded_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m54_goal_completion_audit_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m54_goal_completion_3ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn("authorize_m47_one_focused_librts_stability_pod_run", claude)
        self.assertIn(
            "accept_m54_goal_complete_authorization_narrow_one_run_no_release",
            antigravity,
        )
        self.assertIn(
            "m54_goal_complete_3ai_consensus_one_focused_run_authorized_no_release",
            consensus,
        )
        self.assertIn("M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED", consensus)
        self.assertIn("no second or subsequent M47 run", consensus)
        self.assertIn("no V3 release", consensus)
        self.assertIn("no all-app benchmark run", consensus)
        self.assertIn("no public speedup wording", consensus)
        self.assertIn("no watch-row closure without a later external review", consensus)

    def test_current_handoff_records_m54_without_broadening_scope(self) -> None:
        handoff = (
            ROOT
            / "docs"
            / "handoff"
            / "PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md"
        ).read_text(encoding="utf-8")

        self.assertIn("M54 status: completed by 3-AI consensus", handoff)
        self.assertIn("M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED", handoff)
        self.assertIn("failed_check_count=0", handoff)
        self.assertIn("does not authorize V3 release", handoff)
        self.assertIn("all-app", handoff)


if __name__ == "__main__":
    unittest.main()
