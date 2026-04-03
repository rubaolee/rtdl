from __future__ import annotations

import unittest

from scripts.goal47_optix_goal41_large_checks import lsi_pairs
from scripts.goal47_optix_goal41_large_checks import pip_rows
from scripts.goal47_optix_goal41_large_checks import render_markdown


class Goal47OptixGoal41LargeChecksTest(unittest.TestCase):
    def test_pair_and_pip_helpers_sort(self) -> None:
        self.assertEqual(
            lsi_pairs(({"left_id": 2, "right_id": 1}, {"left_id": 1, "right_id": 3})),
            [(1, 3), (2, 1)],
        )
        self.assertEqual(
            pip_rows(
                (
                    {"point_id": 3, "polygon_id": 1, "contains": 0},
                    {"point_id": 1, "polygon_id": 2, "contains": 1},
                )
            ),
            [(1, 2, 1), (3, 1, 0)],
        )

    def test_render_markdown_includes_both_families(self) -> None:
        summary = {
            "host_label": "lx1",
            "optix_version": (9, 0, 0),
            "county_zipcode": {
                "county_feature_count": 441,
                "zipcode_feature_count": 7035,
                "county_chain_count": 1612,
                "zipcode_chain_count": 10144,
                "lsi": {"pair_parity": True, "cpu_sec": 1.0, "optix_sec": 2.0, "cpu_row_count": 3},
                "pip": {"row_parity": True, "cpu_sec": 4.0, "optix_sec": 5.0, "cpu_row_count": 6},
            },
            "blockgroup_waterbodies": {
                "blockgroup_feature_count": 279,
                "waterbodies_feature_count": 172,
                "blockgroup_chain_count": 287,
                "waterbodies_chain_count": 248,
                "lsi": {"pair_parity": True, "cpu_sec": 7.0, "optix_sec": 8.0, "cpu_row_count": 9},
                "pip": {"row_parity": True, "cpu_sec": 10.0, "optix_sec": 11.0, "cpu_row_count": 12},
            },
        }
        text = render_markdown(summary)
        self.assertIn("County/Zipcode", text)
        self.assertIn("BlockGroup/WaterBodies", text)
        self.assertIn("OptiX version", text)


if __name__ == "__main__":
    unittest.main()
