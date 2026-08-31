from __future__ import annotations

from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py"


class RayJoinV4FrontdoorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = runpy.run_path(str(APP))

    def test_three_application_owned_lanes_have_exact_inputs(self):
        build = self.module["build_v4_input"]
        point = build("planar_map.directed_segment_point_location_2d.v1")
        pair = build("planar_map.segment_pair_grouped_range_exact_count_2d.v1")
        grouped = build("logical_events.grouped_i64x2_count_sum.v1")
        self.assertEqual(len(point["expected_rows"]), 5)
        self.assertEqual(pair["expected_pairs"], ((300, 400), (302, 402)))
        self.assertEqual(grouped["expected_rows"], point["expected_rows"])

    def test_complete_timer_and_no_default_selection(self):
        source = APP.read_text()
        self.assertIn("registered_complete_seconds", source)
        self.assertIn("compute_capability=compute_capability", source)
        self.assertNotIn("compute_capability=(6, 1)", source)
        self.assertNotIn("select_default", source)


if __name__ == "__main__":
    unittest.main()
