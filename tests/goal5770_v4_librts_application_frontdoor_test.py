from __future__ import annotations

from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps/librts-paper/v4_whole_app.py"


class LibRTSV4FrontdoorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = runpy.run_path(str(APP))

    def test_both_lanes_use_real_wkt_and_match_app_oracle(self):
        build = self.module["build_v4_input"]
        broad = build("aabb_index.prepared_query_2d.v1")
        filtered = build("aabb_overlap.filter_bounded_emit_2d.v1")
        self.assertEqual(len(broad["expected_rows"]), 8)
        self.assertEqual(len(filtered["expected_rows"]), 5)
        self.assertEqual(broad["minimum_overlap"], 0.0)
        self.assertEqual(filtered["minimum_overlap"], 0.75)
        self.assertNotEqual(broad["input_sha256"], filtered["input_sha256"])

    def test_complete_timer_and_explicit_algorithm(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("registered_complete_seconds", source)
        self.assertIn('"default_selected_between_paper_algorithms": False', source)
        self.assertNotIn("select_default", source)
        self.assertIn("tiny_boxes.wkt", source)


if __name__ == "__main__":
    unittest.main()
