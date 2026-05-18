import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2315_rayjoin_v2_0_bounded_closure_2026-05-17.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal2315RayjoinV20BoundedClosureTest(unittest.TestCase):
    def test_closure_report_records_user_and_research_position(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("closed-for-v2.0-with-boundary", text)
        self.assertIn("prepared generic segment-pair intersection", text)
        self.assertIn("prepared generic point/closed-shape membership", text)
        self.assertIn("0.010123", text)
        self.assertIn("0.008657", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("v2.0 is released", text)

    def test_future_todo_captures_deferred_rayjoin_work(self) -> None:
        text = TODO.read_text(encoding="utf-8")
        self.assertIn("RayJoin-Style Work After v2.0 Closure", text)
        self.assertIn("Treat the RayJoin-style v2.0 project as closed", text)
        self.assertIn("device-resident row streams / continuations", text)
        self.assertIn("Do not block the v2.0 release lane on beating RayJoin RT", text)


if __name__ == "__main__":
    unittest.main()
