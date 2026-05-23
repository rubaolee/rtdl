from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2487_robot_collision_project_closeout_2026-05-21.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2487_gemini_review_robot_collision_closeout_2026-05-21.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal2487_claude_review_robot_collision_closeout_2026-05-21.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal2487_codex_gemini_claude_consensus_robot_collision_closeout_2026-05-21.md"


class Goal2487RobotCollisionProjectCloseoutTest(unittest.TestCase):
    def test_closeout_report_summarizes_runtime_design_value(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2487 is complete", report)
        self.assertIn("dynamic transformed query geometry", report)
        self.assertIn("prepared static scene plus changing query batches", report)
        self.assertIn("compact byte-per-group any-hit flags", report)
        self.assertIn("phase-separated timing", report)
        self.assertIn("native engine remains app-agnostic", report)

    def test_closeout_report_bounds_claims_and_deferred_work(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("No paper reproduction claim", report)
        self.assertIn("No authors-code comparison claim", report)
        self.assertIn("No public speedup claim", report)
        self.assertIn("No exact solid-contact claim", report)
        self.assertIn("No continuous/swept support claim", report)
        self.assertIn("Deferred", report)

    def test_external_reviews_and_consensus_approve_closeout(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict: Approved", gemini)
        self.assertIn("Verdict: Approved", claude)
        self.assertIn("Consensus: Approved", consensus)
        self.assertIn("Goal2487 is complete", consensus)


if __name__ == "__main__":
    unittest.main()
