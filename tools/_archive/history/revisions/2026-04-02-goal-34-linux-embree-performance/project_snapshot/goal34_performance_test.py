from __future__ import annotations

import unittest

from scripts.goal34_linux_embree_performance import render_markdown
from scripts.goal34_linux_embree_performance import summarize_times


class Goal34PerformanceTest(unittest.TestCase):
    def test_summarize_times_uses_median(self) -> None:
        summary = summarize_times([1.0, 3.0, 2.0])
        self.assertEqual(summary["min_sec"], 1.0)
        self.assertEqual(summary["median_sec"], 2.0)
        self.assertEqual(summary["max_sec"], 3.0)
        self.assertEqual(summary["mean_sec"], 2.0)

    def test_render_markdown_lists_accepted_and_rejected_points(self) -> None:
        summary = {
            "host_label": "test-host",
            "county_page_count": 13,
            "county_feature_count": 3144,
            "county_chain_count": 12273,
            "zipcode_page_count": 130,
            "zipcode_feature_count": 32294,
            "zipcode_chain_count": 49981,
            "warmup": 1,
            "iterations": 3,
            "accepted_points": [
                {
                    "slice_label": "1x5",
                    "selection": {"estimated_total_segments": 772},
                    "lsi": {
                        "pair_parity": True,
                        "cpu_times": {"median_sec": 0.04},
                        "embree_times": {"median_sec": 0.004},
                    },
                    "pip": {
                        "row_parity": True,
                        "cpu_times": {"median_sec": 0.0008},
                        "embree_times": {"median_sec": 0.0005},
                    },
                }
            ],
            "rejected_points": [
                {
                    "slice_label": "1x10",
                    "lsi": {"pair_parity": False},
                    "pip": {"row_parity": True},
                }
            ],
        }
        text = render_markdown(summary)
        self.assertIn("`1x5`", text)
        self.assertIn("`1x10` rejected", text)


if __name__ == "__main__":
    unittest.main()
