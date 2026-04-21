from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from examples import rtdl_event_hotspot_screening


ROOT = Path(__file__).resolve().parents[1]


class Goal723EventHotspotEmbreeSummaryTest(unittest.TestCase):
    def test_event_hotspot_app_exposes_embree_count_summary(self):
        text = (ROOT / "examples/rtdl_event_hotspot_screening.py").read_text(encoding="utf-8")
        self.assertIn("embree_summary_mode", text)
        self.assertIn("count_summary", text)
        self.assertIn("fixed_radius_count_threshold_2d_embree", text)

    def test_count_summary_matches_row_mode(self):
        try:
            rows_result = rtdl_event_hotspot_screening.run_case("embree", copies=8)
            summary_result = rtdl_event_hotspot_screening.run_case(
                "embree",
                copies=8,
                embree_summary_mode="count_summary",
            )
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")

        self.assertEqual(summary_result["neighbor_count_by_event"], rows_result["neighbor_count_by_event"])
        self.assertEqual(summary_result["hotspots"], rows_result["hotspots"])
        self.assertEqual(summary_result["rows"], [])
        self.assertEqual(len(summary_result["summary_rows"]), summary_result["event_count"])
        self.assertEqual(summary_result["embree_summary_mode"], "count_summary")


if __name__ == "__main__":
    unittest.main()
