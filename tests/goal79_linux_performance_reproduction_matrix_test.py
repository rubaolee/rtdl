from __future__ import annotations

import unittest

from scripts.goal79_linux_performance_reproduction_matrix import summarize


class Goal79LinuxPerformanceReproductionMatrixTest(unittest.TestCase):
    def test_summarize_groups_winners_by_boundary(self) -> None:
        rows = [
            {
                "surface": "county_zipcode",
                "timing_boundary": "end_to_end",
                "postgis_sec": 3.0,
                "embree_sec": 4.0,
                "optix_sec": 5.0,
            },
            {
                "surface": "county_zipcode",
                "timing_boundary": "prepared_execution",
                "backend": "embree",
                "backend_sec_best": 1.0,
                "postgis_sec_best": 2.0,
            },
            {
                "surface": "county_zipcode_selected_cdb",
                "timing_boundary": "cached_repeated_call",
                "backend": "optix",
                "backend_sec_best_repeated": 0.1,
                "postgis_sec_best_repeated": 0.2,
            },
        ]

        winners = summarize(rows)

        self.assertEqual(winners["postgis"], ["county_zipcode:end_to_end"])
        self.assertEqual(winners["embree"], ["county_zipcode:prepared_execution"])
        self.assertEqual(winners["optix"], ["county_zipcode_selected_cdb:cached_repeated_call"])


if __name__ == "__main__":
    unittest.main()
