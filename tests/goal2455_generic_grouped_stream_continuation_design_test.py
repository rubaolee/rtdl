from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2455_generic_grouped_stream_continuation_design_2026-05-19.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal2455GenericGroupedStreamContinuationDesignTest(unittest.TestCase):
    def test_design_keeps_next_primitive_generic_and_bounded(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("grouped_stream_continuation", report)
        self.assertIn("generic_fixed_radius_grouped_component_continuation_3d", report)
        self.assertIn("No DBSCAN-native symbol", report)
        self.assertIn("No hidden dispatcher", report)
        self.assertIn("needs-more-evidence", report)

    def test_future_todo_points_to_goal2455(self) -> None:
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("Goal2455 captured the design target", todo)
        self.assertIn("generic fixed-radius grouped component continuation", todo)


if __name__ == "__main__":
    unittest.main()
