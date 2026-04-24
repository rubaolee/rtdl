from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal902_app_by_app_rt_usage_and_next_moves_2026-04-24.md"


class Goal902AppByAppRtUsageReportTest(unittest.TestCase):
    def test_report_exists_and_covers_every_public_app(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for app in rt.public_apps():
            with self.subTest(app=app):
                self.assertIn(app, text)

    def test_report_has_required_app_analysis_dimensions(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "what the app is for",
            "what core operations it performs",
            "how RT is used today",
            "how RT should be used but is not fully used yet",
            "the next move plan",
            "Current RT use",
            "Not-yet RT use",
            "Next move",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_preserves_cloud_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("This is not cloud evidence and not a performance claim", text)
        self.assertIn("requires real RTX artifacts", text)
        self.assertIn("single-session cloud runbook", text)
        self.assertIn("do not make broad DB claims", text)
        self.assertIn("Full DBSCAN clustering speedup is not claimed", text)


if __name__ == "__main__":
    unittest.main()
