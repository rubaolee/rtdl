from __future__ import annotations

import unittest

import rtdsl as rt
from examples.rtdl_language_reference import county_zip_join_reference


class Goal32LsiSortSweepTest(unittest.TestCase):
    def test_localized_band_dataset_stays_parity_clean(self) -> None:
        left = []
        right = []
        for i in range(120):
            band = i % 12
            x = float(band) * 10.0
            y = float(i // 12) * 0.02
            left.append(rt.Segment(id=i + 1, x0=x, y0=y, x1=x + 0.8, y1=y + 0.6))
        for i in range(220):
            band = i % 12
            x = float(band) * 10.0 + 0.4
            y = float(i // 12) * 0.015
            right.append(rt.Segment(id=i + 1, x0=x, y0=y - 0.5, x1=x, y1=y + 0.5))

        cpu_rows = rt.run_cpu(
            county_zip_join_reference,
            left=tuple(left),
            right=tuple(right),
        )
        embree_rows = rt.run_embree(
            county_zip_join_reference,
            left=tuple(left),
            right=tuple(right),
        )
        cpu_pairs = {(row["left_id"], row["right_id"]) for row in cpu_rows}
        embree_pairs = {(row["left_id"], row["right_id"]) for row in embree_rows}
        self.assertEqual(embree_pairs, cpu_pairs)


if __name__ == "__main__":
    unittest.main()
