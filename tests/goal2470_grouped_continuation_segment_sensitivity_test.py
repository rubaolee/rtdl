from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2470_grouped_continuation_segment_sensitivity_2026-05-20.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal2470GroupedContinuationSegmentSensitivityTest(unittest.TestCase):
    def test_report_rejects_tiny_segment_native_plan_without_claiming_speedup(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Mac-local design evidence only", report)
        self.assertIn("not a native implementation", report)
        self.assertIn("not a performance claim", report)
        self.assertIn("Small fixed-hit segments are probably not enough", report)
        self.assertIn("64-hit segments reject only 0.06%", report)
        self.assertIn("2,048-hit segments reject about 46%", report)
        self.assertIn("avoid a naive \"many tiny query chunks\"", report)
        self.assertIn("spatial cell, Morton bucket, or query/source locality", report)
        self.assertIn("No native ABI was added", report)
        self.assertIn("No pod timing was collected", report)

    def test_future_todo_records_goal2469_reviewed_boundary_and_next_leap(self) -> None:
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("Goal2469", todo)
        self.assertIn("Codex/Gemini consensus", todo)
        self.assertIn("not a faster native RT primitive claim", todo)
        self.assertIn("current evidence says the next useful work is the grouped continuation leap", todo)


if __name__ == "__main__":
    unittest.main()
