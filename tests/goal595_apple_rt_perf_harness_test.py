from __future__ import annotations

import unittest

from scripts import goal595_apple_rt_perf_harness as harness


class Goal595AppleRtPerfHarnessTest(unittest.TestCase):
    def test_stats_include_variance_fields(self) -> None:
        stats = harness._stats((3.0, 1.0, 2.0))
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["min_seconds"], 1.0)
        self.assertEqual(stats["median_seconds"], 2.0)
        self.assertEqual(stats["max_seconds"], 3.0)
        self.assertIn("stdev_seconds", stats)

    def test_closest_hit_row_comparison_allows_small_float_delta(self) -> None:
        left = ({"ray_id": 1, "triangle_id": 2, "t": 1.0},)
        right = ({"ray_id": 1, "triangle_id": 2, "t": 1.0 + 1.0e-6},)
        self.assertTrue(harness._rows_match("ray_triangle_closest_hit_3d", left, right))


if __name__ == "__main__":
    unittest.main()

