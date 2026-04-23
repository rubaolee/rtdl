import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal818_rtx_app_claim_gate_summary_2026-04-23.md"


class Goal818RtxClaimGateSummaryTest(unittest.TestCase):
    def test_report_mentions_every_public_app(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for app in rt.public_apps():
            with self.subTest(app=app):
                self.assertIn(f"`{app}`", text)

    def test_report_records_gate_goal_sequence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for goal in ("Goal813", "Goal814", "Goal815", "Goal816", "Goal817", "Goal819"):
            with self.subTest(goal=goal):
                self.assertIn(goal, text)

    def test_report_preserves_cloud_batch_policy(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Do not restart a paid cloud pod per app",
            "55 tests OK",
            "excluded/gated apps must not be benchmarked as RT-core claims",
            "machine-readable statuses",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
