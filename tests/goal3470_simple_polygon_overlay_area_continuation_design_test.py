from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3470_simple_polygon_overlay_area_continuation_design_2026-06-05.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal3470SimplePolygonOverlayAreaContinuationDesignTest(unittest.TestCase):
    def test_report_records_general_overlay_design(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Generic Simple-Polygon Overlay-Area Continuation",
            "convex-only continuation is a fast path",
            "left_ordinal",
            "intersection_area_f64",
            "General simple-polygon continuation",
            "unsupported topology fails closed",
            "RayJoin remains a benchmark app",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_keeps_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "no release claim",
            "public speedup",
            "RTDL-beats-RayJoin",
            "full-overlay claims remain blocked",
            "engine should not contain RayJoin",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_future_todo_captures_nonconvex_overlay_requirement(self) -> None:
        text = TODO.read_text(encoding="utf-8")

        for phrase in (
            "RayJoin General Simple-Polygon Overlay Area",
            "4,375 of 4,543 active relation rows require general-overlay handling",
            "convex clipping continuation",
            "simple-polygon overlay-area continuation",
            "arbitrary user-defined clipping kernels belong to the later v3.0 extension lane",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
