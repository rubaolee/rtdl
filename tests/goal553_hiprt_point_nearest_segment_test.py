from __future__ import annotations

import math
import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import point_nearest_segment_hiprt


@rt.kernel(backend="rtdl", precision="float_approx")
def point_nearest_segment_kernel():
    points = rt.input("points", rt.Points, role="probe")
    segments = rt.input("segments", rt.Segments, role="build")
    candidates = rt.traverse(points, segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(hits, fields=["point_id", "segment_id", "distance"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


class Goal553HiprtPointNearestSegmentTest(unittest.TestCase):
    def _case(self):
        return {
            "points": (
                rt.Point(id=1, x=0.2, y=0.5),
                rt.Point(id=2, x=3.0, y=0.0),
                rt.Point(id=3, x=0.0, y=2.0),
            ),
            "segments": (
                rt.Segment(id=10, x0=0.0, y0=0.0, x1=1.0, y1=0.0),
                rt.Segment(id=20, x0=2.0, y0=-1.0, x1=2.0, y1=1.0),
                rt.Segment(id=30, x0=0.0, y0=2.0, x1=0.0, y1=2.0),
            ),
        }

    def assert_rows_close(self, left, right) -> None:
        self.assertEqual(len(left), len(right))
        for left_row, right_row in zip(left, right):
            self.assertEqual(left_row["point_id"], right_row["point_id"])
            self.assertEqual(left_row["segment_id"], right_row["segment_id"])
            self.assertTrue(
                math.isclose(left_row["distance"], right_row["distance"], rel_tol=1e-6, abs_tol=1e-6),
                (left_row, right_row),
            )

    @unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
    def test_direct_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assert_rows_close(
            point_nearest_segment_hiprt(case["points"], case["segments"]),
            rt.run_cpu_python_reference(point_nearest_segment_kernel, **case),
        )

    @unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
    def test_run_hiprt_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assert_rows_close(
            rt.run_hiprt(point_nearest_segment_kernel, **case),
            rt.run_cpu_python_reference(point_nearest_segment_kernel, **case),
        )

    @unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
    def test_empty_segments_return_empty_rows(self) -> None:
        self.assertEqual(rt.run_hiprt(point_nearest_segment_kernel, points=self._case()["points"], segments=()), ())


if __name__ == "__main__":
    unittest.main()
