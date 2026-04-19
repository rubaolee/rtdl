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
def segment_polygon_hitcount_kernel():
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_polygon_anyhit_kernel():
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_anyhit_rows(exact=False))
    return rt.emit(hits, fields=["segment_id", "polygon_id"])


def _square(polygon_id: int, x0: float, y0: float, x1: float, y1: float) -> rt.Polygon:
    return rt.Polygon(id=polygon_id, vertices=((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal608AppleRtSegmentPolygonNativeTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[object, ...]]:
        return {
            "segments": (
                rt.Segment(id=1, x0=-1.0, y0=0.5, x1=3.0, y1=0.5),
                rt.Segment(id=2, x0=0.2, y0=0.2, x1=0.8, y1=0.8),
                rt.Segment(id=3, x0=4.0, y0=4.0, x1=5.0, y1=4.0),
            ),
            "polygons": (
                _square(10, 0.0, 0.0, 1.0, 1.0),
                _square(20, 2.0, 0.0, 3.0, 1.0),
            ),
        }

    def test_hitcount_native_only_matches_cpu(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_apple_rt(segment_polygon_hitcount_kernel, native_only=True, **case),
            rt.run_cpu_python_reference(segment_polygon_hitcount_kernel, **case),
        )

    def test_anyhit_rows_native_only_matches_cpu(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_apple_rt(segment_polygon_anyhit_kernel, native_only=True, **case),
            rt.run_cpu_python_reference(segment_polygon_anyhit_kernel, **case),
        )

    def test_direct_helpers_match_cpu(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.segment_polygon_hitcount_apple_rt(case["segments"], case["polygons"]),
            rt.segment_polygon_hitcount_cpu(case["segments"], case["polygons"]),
        )
        self.assertEqual(
            rt.segment_polygon_anyhit_rows_apple_rt(case["segments"], case["polygons"]),
            rt.segment_polygon_anyhit_rows_cpu(case["segments"], case["polygons"]),
        )


if __name__ == "__main__":
    unittest.main()
