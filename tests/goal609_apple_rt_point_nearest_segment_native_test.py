from __future__ import annotations

import platform
import unittest

import rtdsl as rt


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@rt.kernel(backend="rtdl", precision="float_approx")
def point_nearest_segment_kernel():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(points, segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(hits, fields=["point_id", "segment_id", "distance"])


def _assert_rows_almost_equal(testcase: unittest.TestCase, actual, expected) -> None:
    testcase.assertEqual(len(actual), len(expected))
    for actual_row, expected_row in zip(actual, expected):
        testcase.assertEqual(set(actual_row), set(expected_row))
        for key, expected_value in expected_row.items():
            actual_value = actual_row[key]
            if isinstance(expected_value, float):
                testcase.assertAlmostEqual(float(actual_value), expected_value, places=5)
            else:
                testcase.assertEqual(actual_value, expected_value)


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal609AppleRtPointNearestSegmentNativeTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[object, ...]]:
        return {
            "points": (
                rt.Point(id=1, x=0.0, y=1.0),
                rt.Point(id=2, x=3.0, y=0.0),
                rt.Point(id=3, x=3.0, y=4.0),
            ),
            "segments": (
                rt.Segment(id=20, x0=-1.0, y0=0.0, x1=1.0, y1=0.0),
                rt.Segment(id=10, x0=-1.0, y0=0.0, x1=1.0, y1=0.0),
                rt.Segment(id=30, x0=0.0, y0=0.0, x1=0.0, y1=0.0),
            ),
        }

    def test_native_only_matches_cpu_reference(self) -> None:
        case = self._case()
        _assert_rows_almost_equal(
            self,
            rt.run_apple_rt(point_nearest_segment_kernel, native_only=True, **case),
            rt.run_cpu_python_reference(point_nearest_segment_kernel, **case),
        )

    def test_direct_helper_matches_cpu(self) -> None:
        case = self._case()
        _assert_rows_almost_equal(
            self,
            rt.point_nearest_segment_apple_rt(case["points"], case["segments"]),
            rt.point_nearest_segment_cpu(case["points"], case["segments"]),
        )

    def test_empty_segments_returns_empty_rows(self) -> None:
        points = (rt.Point(id=1, x=0.0, y=0.0),)
        self.assertEqual(rt.point_nearest_segment_apple_rt(points, ()), ())


if __name__ == "__main__":
    unittest.main()
