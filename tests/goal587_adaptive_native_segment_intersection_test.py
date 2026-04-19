from __future__ import annotations

import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_intersection_kernel():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    hits = rt.refine(rt.traverse(left, right, accel="bvh"), predicate=rt.segment_intersection())
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


def assert_rows_almost_equal(testcase: unittest.TestCase, actual, expected) -> None:
    testcase.assertEqual(len(actual), len(expected))
    for actual_row, expected_row in zip(actual, expected):
        testcase.assertEqual(set(actual_row), set(expected_row))
        for key, expected_value in expected_row.items():
            actual_value = actual_row[key]
            if isinstance(expected_value, float):
                testcase.assertAlmostEqual(float(actual_value), float(expected_value), places=7)
            else:
                testcase.assertEqual(actual_value, expected_value)


@unittest.skipUnless(rt.adaptive_available(), "adaptive native backend library is not built")
class Goal587AdaptiveNativeSegmentIntersectionTest(unittest.TestCase):
    def test_native_segment_intersection_matches_python_reference(self) -> None:
        inputs = {
            "left": (
                rt.Segment(1, 0.0, 0.0, 2.0, 2.0),
                rt.Segment(2, 0.0, 3.0, 2.0, 3.0),
                rt.Segment(3, -1.0, 1.0, 3.0, 1.0),
            ),
            "right": (
                rt.Segment(10, 0.0, 2.0, 2.0, 0.0),
                rt.Segment(11, 3.0, 0.0, 3.0, 2.0),
                rt.Segment(12, 10.0, 10.0, 11.0, 11.0),
            ),
        }

        self.assertEqual(rt.adaptive_predicate_mode(segment_intersection_kernel)["mode"], "native_adaptive_cpu_soa_2d")
        assert_rows_almost_equal(
            self,
            rt.run_adaptive(segment_intersection_kernel, **inputs),
            rt.run_cpu_python_reference(segment_intersection_kernel, **inputs),
        )


if __name__ == "__main__":
    unittest.main()
