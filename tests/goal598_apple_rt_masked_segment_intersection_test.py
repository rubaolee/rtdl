from __future__ import annotations

import platform
import unittest

import rtdsl as rt
from tests.goal582_apple_rt_full_surface_dispatch_test import segment_intersection_kernel


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal598AppleRtMaskedSegmentIntersectionTest(unittest.TestCase):
    def test_zero_and_one_hit_cases_match_cpu_reference(self) -> None:
        left = (
            rt.Segment(1, -1.0, 0.0, 1.0, 0.0),
            rt.Segment(2, -1.0, 5.0, 1.0, 5.0),
        )
        right = (rt.Segment(10, 0.0, -1.0, 0.0, 1.0),)
        actual = rt.run_apple_rt(segment_intersection_kernel, native_only=True, left=left, right=right)
        expected = rt.run_cpu_python_reference(segment_intersection_kernel, left=left, right=right)
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0]["left_id"], 1)
        self.assertEqual(actual[0]["right_id"], 10)

    def test_counts_many_right_segments_across_chunks(self) -> None:
        left = (rt.Segment(1, -1.0, 0.0, 1.0, 0.0),)
        right = tuple(
            rt.Segment(100 + index, -0.9 + index * 0.045, -1.0, -0.9 + index * 0.045, 1.0)
            for index in range(40)
        )
        actual = rt.run_apple_rt(segment_intersection_kernel, native_only=True, left=left, right=right)
        expected = rt.run_cpu_python_reference(segment_intersection_kernel, left=left, right=right)
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 40)

    def test_preserves_left_major_right_order_for_same_point_hits(self) -> None:
        left = (
            rt.Segment(1, -1.0, 0.0, 1.0, 0.0),
            rt.Segment(2, -1.0, 0.5, 1.0, 0.5),
        )
        right = (
            rt.Segment(10, 0.0, -1.0, 0.0, 1.0),
            rt.Segment(11, 0.0, -1.0, 0.0, 1.0),
            rt.Segment(12, 0.5, -1.0, 0.5, 1.0),
        )
        actual = rt.run_apple_rt(segment_intersection_kernel, native_only=True, left=left, right=right)
        expected = rt.run_cpu_python_reference(segment_intersection_kernel, left=left, right=right)
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
