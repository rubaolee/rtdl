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
        self.assertIn("Goal1850 lifts the witness contract to the first app-level adapter", text)
        self.assertIn("Goal1853 adds the stronger caller-supplied PyTorch/CuPy GPU-column version", text)
        self.assertIn("Goal1856 adds the first same-contract v2.0-vs-v1.8 timing row", text)
        self.assertIn("Goal1859 adds a second app-level OptiX partner adapter", text)
        self.assertIn("host/Python count materialization remains explicit", text)
        self.assertIn("Goal1861 upgrades that hit-count path", text)
        self.assertIn("app count columns stay partner-owned", text)
        self.assertIn("first v2.0 OptiX app adapter and timing row exist", text)
        self.assertIn("first narrow same-contract timing row", text)
        self.assertIn("segment_polygon_anyhit_rows", text)
        self.assertIn("segment_polygon_hitcount", text)


if __name__ == "__main__":
    unittest.main()
