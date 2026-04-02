from __future__ import annotations

import unittest

from scripts.goal36_linux_blockgroup_waterbodies_performance import render_markdown
from scripts.goal36_linux_blockgroup_waterbodies_performance import scale_bbox


class Goal36PerformanceTest(unittest.TestCase):
    def test_scale_bbox_keeps_center(self) -> None:
        bbox = (-10.0, -4.0, 6.0, 8.0)
        scaled = scale_bbox(bbox, 0.5)
        self.assertEqual(scaled, (-6.0, -1.0, 2.0, 5.0))

    def test_render_markdown_includes_accepted_point(self) -> None:
        summary = {
            "host_label": "lx1",
            "seed_bbox_label": "county2300_bbox",
            "seed_bbox": (-1.0, -2.0, 3.0, 4.0),
            "warmup": 0,
            "iterations": 1,
            "accepted_points": [
                {
                    "slice_label": "county2300_s04",
                    "blockgroup": {"feature_count": 96},
                    "waterbodies": {"feature_count": 45},
                    "lsi": {
                        "pair_parity": True,
                        "cpu_times": {"median_sec": 1.0},
                        "embree_times": {"median_sec": 0.25},
                    },
                    "pip": {
                        "row_parity": True,
                        "cpu_times": {"median_sec": 0.5},
                        "embree_times": {"median_sec": 0.2},
                    },
                }
            ],
            "rejected_points": [],
        }
        rendered = render_markdown(summary)
        self.assertIn("county2300_s04", rendered)
        self.assertIn("4.00x", rendered)
        self.assertIn("2.50x", rendered)


if __name__ == "__main__":
    unittest.main()
