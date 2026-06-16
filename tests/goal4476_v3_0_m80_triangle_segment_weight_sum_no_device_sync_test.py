from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"


class Goal4476V30M80TriangleSegmentWeightSumNoDeviceSyncTest(unittest.TestCase):
    def test_segmented_route_uses_planned_logical_weight_sum(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertNotIn("_sum_uint64_like(ray_weights)", source)
        self.assertEqual(2, source.count("lowered_ray_weight_sum += int(_two_hop_rows)"))
        self.assertEqual(2, source.count("lowered_ray_weight_sum += int(two_hop_rows)"))

    def test_uint64_sum_helper_is_not_removed_for_other_callers(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("def _sum_uint64_like", source)
        self.assertIn("if hasattr(total, \"get\")", source)


if __name__ == "__main__":
    unittest.main()
