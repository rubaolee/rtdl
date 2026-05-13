from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1843_v2_0_vs_v1_8_total_perf_readiness_2026-05-13.md"


class Goal1843V20VsV18TotalPerfReadinessTest(unittest.TestCase):
    def test_report_keeps_total_perf_comparison_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Status: `planning-evidence`", text)
        self.assertIn("not yet ready for a total v2.0-vs-v1.8 performance table", text)
        self.assertIn("does not authorize v2.0 release wording", text)
        self.assertIn("3-AI consensus", text)

    def test_all_public_apps_are_classified_for_both_active_engines(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for app in rt.public_apps():
            with self.subTest(app=app):
                self.assertIn(f"`{app}`", text)
        self.assertIn("Embree v2.0 readiness", text)
        self.assertIn("OptiX v2.0 readiness", text)

    def test_v2_0_evidence_is_narrowly_scoped_to_goal1838(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal1838 proves one real OptiX partner zero-copy slice", text)
        self.assertIn("prepared 2-D ray/triangle any-hit primitive", text)
        self.assertIn("No public app has yet been rewritten end-to-end as a v2.0 partner app", text)
        self.assertIn("segment_polygon_anyhit_rows", text)


if __name__ == "__main__":
    unittest.main()
