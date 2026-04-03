from __future__ import annotations

import unittest

from scripts.goal45_optix_county_zipcode import render_markdown
from scripts.goal45_optix_county_zipcode import summarize_times


class Goal45OptixCountyZipcodeTest(unittest.TestCase):
    def test_default_ladder_matches_reported_goal(self) -> None:
        from scripts.goal45_optix_county_zipcode import parse_args
        import argparse

        argv = argparse._sys.argv[:]
        try:
            argparse._sys.argv = [
                "goal45_optix_county_zipcode.py",
                "--county-dir",
                "county",
                "--zipcode-dir",
                "zipcode",
                "--output-dir",
                "out",
            ]
            args = parse_args()
        finally:
            argparse._sys.argv = argv
        self.assertEqual(args.sizes, "4,5,6,8,10,12")

    def test_summarize_times_uses_median(self) -> None:
        summary = summarize_times([1.0, 3.0, 2.0])
        self.assertEqual(summary["min_sec"], 1.0)
        self.assertEqual(summary["median_sec"], 2.0)
        self.assertEqual(summary["max_sec"], 3.0)
        self.assertEqual(summary["mean_sec"], 2.0)

    def test_render_markdown_lists_accepted_and_rejected_points(self) -> None:
        summary = {
            "host_label": "gpu-host",
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
                    "slice_label": "1x8",
                    "selection": {"estimated_total_segments": 1530},
                    "lsi": {
                        "exact_row_parity": True,
                        "cpu_times": {"median_sec": 0.2},
                        "optix_jit_sec": 0.5,
                        "optix_warm_times": {"median_sec": 0.01},
                    },
                    "pip": {
                        "exact_row_parity": True,
                        "cpu_times": {"median_sec": 0.002},
                        "optix_jit_sec": 0.4,
                        "optix_warm_times": {"median_sec": 0.0003},
                    },
                }
            ],
            "rejected_points": [
                {
                    "slice_label": "1x12",
                    "lsi": {"exact_row_parity": False},
                    "pip": {"exact_row_parity": True},
                }
            ],
        }
        text = render_markdown(summary)
        self.assertIn("`1x8`", text)
        self.assertIn("`1x12` rejected", text)


if __name__ == "__main__":
    unittest.main()
