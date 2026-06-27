import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V3PhoenixM51LibRtsAuthorizedRunbookGateTest(unittest.TestCase):
    def test_runbook_is_fail_closed_and_non_authorizing(self) -> None:
        runbook = (
            ROOT
            / "docs"
            / "rebuild"
            / "v3"
            / "phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn("runbook_ready_no_run_not_authorized", runbook)
        self.assertIn("authorize_m47_one_focused_librts_stability_pod_run", runbook)
        self.assertIn("Do not execute", runbook)
        self.assertIn("Dry-Run Command", runbook)
        self.assertIn("--execute", runbook)
        self.assertIn("M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED", runbook)
        self.assertIn("Do not infer V2.14 from the current tree", runbook)
        self.assertIn("Do not copy back only the summary", runbook)
        self.assertIn("no paid POD spend", runbook)
        self.assertIn("no focused POD spend", runbook)
        self.assertIn("no V3 release", runbook)

    def test_review_packet_and_helper_are_registered(self) -> None:
        call = (
            ROOT
            / "docs"
            / "reviews"
            / "call_for_review_phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md"
        ).read_text(encoding="utf-8")
        debt = (
            ROOT
            / "docs"
            / "reviews"
            / "phoenix_v3_claude_review_debt_register_2026-06-23.md"
        ).read_text(encoding="utf-8")
        handoff = (
            ROOT
            / "docs"
            / "handoff"
            / "PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md"
        ).read_text(encoding="utf-8")

        self.assertIn("accept_m51_runbook_no_run", call)
        self.assertIn("reject_m51_accidentally_authorizes_pod", call)
        self.assertIn("Debt 10: M51 LibRTS Authorized-Run Runbook", debt)
        self.assertIn(
            "run_claude_phoenix_v3_m51_librts_authorized_runbook_review_2026_06_23.ps1",
            debt,
        )
        self.assertIn("phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md", handoff)


if __name__ == "__main__":
    unittest.main()
