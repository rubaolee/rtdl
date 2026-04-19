from __future__ import annotations

import math
import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import segment_intersection_hiprt


@rt.kernel(backend="rtdl", precision="float_approx")
def lsi_kernel():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


class Goal550HiprtSegmentIntersectionTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[rt.Segment, ...]]:
        return {
            "left": (
                rt.Segment(id=10, x0=0.0, y0=0.0, x1=2.0, y1=2.0),
                rt.Segment(id=20, x0=0.0, y0=1.0, x1=2.0, y1=1.0),
                rt.Segment(id=30, x0=3.0, y0=3.0, x1=4.0, y1=4.0),
            ),
            "right": (
                rt.Segment(id=1, x0=0.0, y0=2.0, x1=2.0, y1=0.0),
                rt.Segment(id=2, x0=1.0, y0=-1.0, x1=1.0, y1=3.0),
                rt.Segment(id=3, x0=5.0, y0=5.0, x1=6.0, y1=6.0),
            ),
        }

    def assert_rows_close(self, left, right) -> None:
        self.assertEqual(len(left), len(right))
        for left_row, right_row in zip(left, right):
            self.assertEqual(left_row["left_id"], right_row["left_id"])
            self.assertEqual(left_row["right_id"], right_row["right_id"])
            self.assertTrue(
                math.isclose(
                    left_row["intersection_point_x"],
                    right_row["intersection_point_x"],
                    rel_tol=1e-6,
                    abs_tol=1e-6,
                ),
                (left_row, right_row),
            )
            self.assertTrue(
                math.isclose(
                    left_row["intersection_point_y"],
                    right_row["intersection_point_y"],
                    rel_tol=1e-6,
                    abs_tol=1e-6,
                ),
                (left_row, right_row),
            )

    @unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
    def test_direct_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assert_rows_close(
            segment_intersection_hiprt(case["left"], case["right"]),
            rt.run_cpu_python_reference(lsi_kernel, **case),
        )

    @unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
    def test_run_hiprt_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assert_rows_close(
            rt.run_hiprt(lsi_kernel, **case),
            rt.run_cpu_python_reference(lsi_kernel, **case),
        )

    @unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
    def test_empty_inputs_return_empty_rows(self) -> None:
        self.assertEqual(rt.run_hiprt(lsi_kernel, left=(), right=self._case()["right"]), ())
        self.assertEqual(rt.run_hiprt(lsi_kernel, left=self._case()["left"], right=()), ())


if __name__ == "__main__":
    unittest.main()
