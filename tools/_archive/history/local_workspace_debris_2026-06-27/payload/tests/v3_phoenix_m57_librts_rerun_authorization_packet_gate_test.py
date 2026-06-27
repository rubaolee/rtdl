import unittest
from pathlib import Path

from scripts import v3_phoenix_m47_librts_stability_protocol as m47


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m57_source_signature_gated_librts_rerun_authorization_2026-06-23.md"
)


class V3PhoenixM57LibRTSRerunAuthorizationPacketGateTest(unittest.TestCase):
    def test_m57_packet_is_review_only_until_3ai_authorization(self) -> None:
        packet = PACKET.read_text(encoding="utf-8")

        self.assertIn("draft_review_packet_not_authorized", packet)
        self.assertIn("does not authorize execution by itself", packet)
        self.assertIn("final 3-AI consensus verdict explicitly authorizes it", packet)
        self.assertIn("M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED", packet)
        self.assertEqual(
            "M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED",
            m47.M57_AUTHORIZATION_TOKEN,
        )

    def test_m57_packet_requires_source_signature_gate_before_samples(self) -> None:
        packet = PACKET.read_text(encoding="utf-8")

        self.assertIn("current_librts_set_b_source_signature", packet)
        self.assertIn("Run target-machine dry-run first with `--run-preflight`", packet)
        self.assertIn("failed_checks=[]", packet)
        self.assertIn("If `current_librts_set_b_source_signature` fails", packet)
        self.assertIn("do not run measured samples", packet)
        self.assertIn("exactly 8 paired samples per scenario", packet)
        self.assertIn("unchanged M47 scenario set", packet)

    def test_m57_packet_carries_no_release_or_claim_authorization(self) -> None:
        packet = PACKET.read_text(encoding="utf-8")

        for phrase in (
            "no V3 release",
            "no all-app benchmark run",
            "no broad paid POD campaign",
            "no public speedup wording",
            "no broad V3-over-V2 claim",
            "no V4 work",
            "no embedding",
            "no C ABI",
            "no true zero-copy claim",
            "no watch-row closure",
            "no scenario changes",
            "no sample-count changes",
            "no second M57 run",
        ):
            self.assertIn(phrase, packet)

    def test_m57_requested_verdicts_are_narrow(self) -> None:
        packet = PACKET.read_text(encoding="utf-8")

        self.assertIn("authorize_m57_one_source_signature_gated_librts_rerun", packet)
        self.assertIn("request_m57_changes_before_authorization", packet)
        self.assertIn("reject_m57_rerun_authorization", packet)
        self.assertNotIn("authorize_all_app", packet)
        self.assertNotIn("release_ready", packet)

    def test_m57_external_reviews_and_consensus_authorize_one_run_only(self) -> None:
        claude = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m57_source_signature_gated_librts_rerun_authorization_recorded_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m57_authorization_after_fail_closed_fix_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m57_one_rerun_authorization_3ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")
        audit = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m57_goal_completion_audit_2026-06-23.md"
        ).read_text(encoding="utf-8")

        for text in (claude, antigravity, consensus, audit):
            self.assertIn(
                "M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED",
                text,
            )
            self.assertIn("no V3 release", text)
            self.assertIn("no all-app benchmark run", text)
            self.assertIn("no public speedup wording", text)
            self.assertIn("no watch-row closure", text)
            self.assertIn("no second M57 run", text)

        self.assertIn(
            "authorize_m57_one_source_signature_gated_librts_rerun_after_fail_closed_fix",
            claude,
        )
        self.assertIn(
            "authorize_m57_one_source_signature_gated_librts_rerun_after_fail_closed_fix",
            antigravity,
        )
        self.assertIn(
            "m57_one_source_signature_gated_librts_rerun_authorized_no_release_no_claims",
            consensus,
        )
        self.assertIn("No M57 POD run performed", audit)


if __name__ == "__main__":
    unittest.main()
