from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"
REPORT = ROOT / "docs" / "reports" / "goal3798_rayjoin_future_todo_lsi_status_cleanup_2026-06-07.md"


class Goal3798RayJoinFutureTodoLsiStatusCleanupTest(unittest.TestCase):
    def test_future_todo_marks_lsi_performance_blocker_superseded(self) -> None:
        text = TODO.read_text(encoding="utf-8")
        self.assertIn("Goals3725, 3729, and 3733 superseded the old LSI performance blocker", text)
        self.assertIn("3.291x", text)
        self.assertIn("generic grouped-range direct exact-count front door", text)
        self.assertIn("bottleneck to overlay active-count", text)
        self.assertNotIn("Performance remains open: RTDL's exact prepared LSI query", text)
        self.assertNotIn("The next major RayJoin LSI work should be", text)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3798 RayJoin Future TODO LSI Status Cleanup", text)
        self.assertIn("Goal3725", text)
        self.assertIn("Goal3729", text)
        self.assertIn("Goal3733", text)
        self.assertIn("does not authorize public RayJoin speedup claims", text)
        self.assertIn("app-specific native-engine logic", text)


if __name__ == "__main__":
    unittest.main()
