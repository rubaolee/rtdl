import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2141_rtdl_hausdorff_application_acceleration_synthesis_2026-05-16.md"


class Goal2141RtdlHausdorffApplicationAccelerationSynthesisTest(unittest.TestCase):
    def test_synthesis_records_strong_bounded_result(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("round complete, with bounded acceptance", text)
        self.assertIn("52 measured artifact rows", text)
        self.assertIn("6x to 14x", text)
        self.assertIn("RTDL engine remains app-agnostic for this work | `accept`", text)
        self.assertIn("RTDL universally beats all possible CUDA implementations | `not-claimed`", text)
        self.assertIn("Full X-HD paper reproduction | `not-claimed`", text)
        self.assertIn("v2.0 release authorization | `not-authorized-here`", text)

    def test_synthesis_links_component_reports_and_reviews(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for goal in ("goal2132", "goal2134", "goal2136", "goal2139"):
            self.assertIn(goal, text)
        for review in ("goal2133", "goal2135", "goal2137", "goal2140"):
            self.assertIn(review, text)


if __name__ == "__main__":
    unittest.main()
