from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import segment_polygon_anyhit_rows_hiprt
from rtdsl.hiprt_runtime import segment_polygon_hitcount_hiprt


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_polygon_hitcount_kernel():
    segments = rt.input("segments", rt.Segments, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_polygon_anyhit_kernel():
    segments = rt.input("segments", rt.Segments, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_anyhit_rows(exact=False))
    return rt.emit(hits, fields=["segment_id", "polygon_id"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


def square(poly_id: int, x0: float, y0: float, size: float) -> rt.Polygon:
    return rt.Polygon(
        id=poly_id,
        vertices=((x0, y0), (x0 + size, y0), (x0 + size, y0 + size), (x0, y0 + size)),
    )


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal554HiprtSegmentPolygonTest(unittest.TestCase):
    def _case(self):
        return {
            "segments": (
                rt.Segment(id=1, x0=-1.0, y0=1.0, x1=3.0, y1=1.0),
                rt.Segment(id=2, x0=0.25, y0=0.25, x1=0.75, y1=0.75),
                rt.Segment(id=3, x0=4.0, y0=4.0, x1=5.0, y1=5.0),
                rt.Segment(id=4, x0=2.0, y0=2.0, x1=3.0, y1=2.0),
            ),
            "polygons": (
                square(10, 0.0, 0.0, 2.0),
                square(20, 2.0, 0.5, 1.0),
            ),
        }

    def test_hitcount_direct_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            segment_polygon_hitcount_hiprt(case["segments"], case["polygons"]),
            rt.run_cpu_python_reference(segment_polygon_hitcount_kernel, **case),
        )

    def test_hitcount_run_hiprt_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_hiprt(segment_polygon_hitcount_kernel, **case),
            rt.run_cpu_python_reference(segment_polygon_hitcount_kernel, **case),
        )

    def test_anyhit_direct_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            segment_polygon_anyhit_rows_hiprt(case["segments"], case["polygons"]),
            rt.run_cpu_python_reference(segment_polygon_anyhit_kernel, **case),
        )

    def test_anyhit_run_hiprt_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_hiprt(segment_polygon_anyhit_kernel, **case),
            rt.run_cpu_python_reference(segment_polygon_anyhit_kernel, **case),
        )

    def test_empty_inputs_match_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_hiprt(segment_polygon_hitcount_kernel, segments=case["segments"], polygons=()),
            rt.run_cpu_python_reference(segment_polygon_hitcount_kernel, segments=case["segments"], polygons=()),
        )
        self.assertEqual(rt.run_hiprt(segment_polygon_hitcount_kernel, segments=(), polygons=case["polygons"]), ())
        self.assertEqual(rt.run_hiprt(segment_polygon_anyhit_kernel, segments=case["segments"], polygons=()), ())
        self.assertEqual(rt.run_hiprt(segment_polygon_anyhit_kernel, segments=(), polygons=case["polygons"]), ())


if __name__ == "__main__":
    unittest.main()
