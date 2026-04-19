from __future__ import annotations

import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def point_nearest_segment_kernel():
    points = rt.input("points", rt.Points, role="probe")
    segments = rt.input("segments", rt.Segments, role="build")
    hits = rt.refine(rt.traverse(points, segments, accel="bvh"), predicate=rt.point_nearest_segment())
    return rt.emit(hits, fields=["point_id", "segment_id", "distance"])


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
class Goal588AdaptiveNativePointNearestSegmentTest(unittest.TestCase):
    def test_native_point_nearest_segment_matches_python_reference(self) -> None:
        inputs = {
            "points": (
                rt.Point(1, 0.25, 0.20),
                rt.Point(2, 2.00, 0.80),
                rt.Point(3, -1.00, -1.00),
            ),
            "segments": (
                rt.Segment(10, 0.0, 0.0, 1.0, 0.0),
                rt.Segment(11, 2.0, 0.0, 2.0, 2.0),
                rt.Segment(12, -2.0, -2.0, -0.5, -0.5),
            ),
        }

        self.assertEqual(
            rt.adaptive_predicate_mode(point_nearest_segment_kernel)["mode"],
            "native_adaptive_cpu_soa_min_distance_2d",
        )
        assert_rows_almost_equal(
            self,
            rt.run_adaptive(point_nearest_segment_kernel, **inputs),
            rt.run_cpu_python_reference(point_nearest_segment_kernel, **inputs),
        )


if __name__ == "__main__":
    unittest.main()
